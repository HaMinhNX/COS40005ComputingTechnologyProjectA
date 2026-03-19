from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import google.generativeai as genai
import os
import json
from datetime import datetime
from typing import AsyncGenerator
from uuid import UUID

from database import get_db
from models import User, MedicalRecord, WorkoutSession, SessionDetail, PatientNote
from dependencies import get_current_user, verify_patient_access
from schemas.communication import AIChatRequest

router = APIRouter(
    prefix="/api/ai",
    tags=["ai"]
)

# Gemini Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def get_patient_context(db: Session, patient_id: UUID) -> str:
    # Fetch medical record
    record = db.query(MedicalRecord).filter(MedicalRecord.patient_id == patient_id).first()
    # Fetch recent workout sessions
    sessions = db.query(WorkoutSession).filter(WorkoutSession.user_id == patient_id).order_by(WorkoutSession.start_time.desc()).limit(10).all()
    # Fetch patient notes
    notes = db.query(PatientNote).filter(PatientNote.patient_id == patient_id).all()
    
    # NEW: Fetch health metrics (simulated or from a metrics table if exists)
    # For now, we'll use historical data from WorkoutSession to build a performance summary
    total_reps = sum(s.total_reps_completed for s in sessions if s.total_reps_completed)
    workout_count = len([s for s in sessions if s.avg_accuracy is not None])
    avg_accuracy = sum(s.avg_accuracy for s in sessions if s.avg_accuracy is not None) / workout_count if workout_count > 0 else 0

    context = f"DỮ LIỆU BỆNH NHÂN (ID: {patient_id}):\n"
    if record:
        context += f"--- THÔNG TIN Y TẾ ---\n"
        context += f"- Chẩn đoán: {record.diagnosis}\n"
        context += f"- Triệu chứng: {record.symptoms}\n"
        context += f"- Kế hoạch điều trị: {record.treatment_plan}\n"
        bmi = round(record.weight_kg / ((record.height_cm/100)**2), 1) if record.height_cm and record.weight_kg else 'N/A'
        context += f"- Chỉ số cơ bản: Cao {record.height_cm}cm, Nặng {record.weight_kg}kg, BMI {bmi}, Nhóm máu {record.blood_type}\n"
        context += f"- Tiền sử bệnh: {getattr(record, 'medical_history', 'Không có dữ liệu')}\n"
    
    context += f"\n--- THỐNG KÊ TẬP LUYỆN (10 buổi gần nhất) ---\n"
    context += f"- Tổng số Reps hoàn thành: {total_reps}\n"
    context += f"- Độ chính xác trung bình: {round(float(avg_accuracy), 1)}%\n"
    
    if sessions:
        context += "- Chi tiết các buổi tập:\n"
        for s in sessions:
            context += f"  + Ngày: {s.start_time.strftime('%Y-%m-%d %H:%M')}, Bài tập: {s.exercise_type}, Reps: {s.total_reps_completed}, Chính xác: {s.avg_accuracy}%\n"
            
    if notes:
        context += f"\n--- GHI CHÚ CHUYÊN MÔN ---\n"
        for n in notes:
            context += f"  + [{n.created_at.strftime('%Y-%m-%d')}] {n.title}: {n.content}\n"
            
    return context

@router.post("/chat")
async def ai_chat(
    request: AIChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chưa cấu hình Gemini API Key. Vui lòng thêm vào file .env"
        )
    
    # Determine target patient
    target_patient_id = request.patient_id
    if current_user.role == 'patient':
        target_patient_id = current_user.user_id
    
    if not target_patient_id:
        raise HTTPException(status_code=400, detail="Cần cung cấp Patient ID")
    
    # Verify access
    patient = verify_patient_access(target_patient_id, current_user, db)
    
    # Build context
    context = get_patient_context(db, target_patient_id)
    
    # System Prompt (translated to Vietnamese for consistency)
    system_prompt = f"""
    Bạn là một trợ lý y tế AI cao cấp tích hợp trong nền tảng MEDIC1, có khả năng phân tích dữ liệu chuyên sâu tương tự như các mô hình ngôn ngữ tiên tiến nhất năm 2026.
    
    Bạn đang hỗ trợ một {current_user.role} trong việc quản lý và theo dõi bệnh nhân: {patient.full_name}.
    
    NHIỆM VỤ CỦA BẠN:
    1. Phân tích dữ liệu: Dựa trên ngữ cảnh được cung cấp, hãy đưa ra các nhận xét về tiến độ phục hồi, xu hướng nhịp tim/độ chính xác, và các cảnh báo nếu có.
    2. Tóm tắt: Cung cấp bản tóm tắt nhanh về tình trạng sức khỏe nếu được yêu cầu.
    3. Thống kê: Trình bày các con số cụ thể về hiệu suất tập luyện một cách trực quan (sử dụng bảng markdown nếu cần).
    4. Trả lời câu hỏi: Giải đáp mọi thắc mắc về bệnh nhân này dựa trên dữ liệu thật.
    
    DỮ LIỆU NGỮ CẢNH:
    {context}
    
    QUY TẮC PHẢN HỒI:
    - Ngôn ngữ: Tiếng Việt.
    - Phong cách: Chuyên nghiệp, đồng cảm, chính xác, súc tích nhưng đầy đủ thông tin.
    - Định dạng: Sử dụng Markdown (bold, tables, lists) để thông tin dễ đọc.
    - Bảo mật: Tuyệt đối không tiết lộ thông tin của bệnh nhân khác. Nếu không có dữ liệu cho câu hỏi cụ thể, hãy thành thật trả lời là không có dữ liệu.
    - Giới hạn: Chỉ trả lời các vấn đề liên quan đến y tế và phục hồi chức năng của bệnh nhân này.
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        async def generate_response() -> AsyncGenerator[str, None]:
            response = model.generate_content(
                [system_prompt, request.message],
                stream=True
            )
            for chunk in response:
                if chunk.text:
                    yield f"data: {json.dumps({'text': chunk.text}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(generate_response(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi AI: {str(e)}")
