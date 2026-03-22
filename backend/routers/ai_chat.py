from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
from typing import AsyncGenerator
from uuid import UUID

from database import get_db
from models import User, MedicalRecord, WorkoutSession, PatientNote
from dependencies import get_current_user, verify_patient_access
from schemas.communication import AIChatRequest

router = APIRouter(
    prefix="/api/ai",
    tags=["ai"]
)

# Gemini Configuration
load_dotenv()
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
    total_reps = 0
    accuracies = []
    session_details_list = []
    
    for s in sessions:
        # Sum reps and collect exercises from details
        session_reps = sum(d.reps_completed for d in s.details if d.reps_completed)
        total_reps += session_reps
        
        exercises = list(set(d.exercise_type for d in s.details if d.exercise_type))
        exercise_str = ", ".join(exercises) if exercises else "Unknown"
        
        # Calculate session accuracy if details exist
        session_acc = 0
        if s.details:
            valid_details = [d for d in s.details if d.accuracy_score is not None]
            if valid_details:
                session_acc = sum(float(d.accuracy_score) for d in valid_details) / len(valid_details)
                accuracies.append(session_acc)
        
        session_details_list.append(
            f"  + [{s.start_time.strftime('%Y-%m-%d %H:%M')}] {exercise_str}: {session_reps} reps, Accuracy: {session_acc:.1f}%"
        )

    avg_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0

    context = f"DỮ LIỆU BỆNH NHÂN (ID: {patient_id}):\n"
    if record:
        context += "--- THÔNG TIN Y TẾ ---\n"
        context += f"- Chẩn đoán: {record.diagnosis}\n"
        context += f"- Triệu chứng: {record.symptoms}\n"
        context += f"- Kế hoạch điều trị: {record.treatment_plan}\n"
        bmi = 'N/A'
        if record.height_cm and record.weight_kg and record.height_cm > 0:
            try:
                bmi = round(record.weight_kg / ((record.height_cm/100)**2), 1)
            except ZeroDivisionError:
                bmi = 'N/A'
        context += f"- Chỉ số cơ bản: Cao {record.height_cm}cm, Nặng {record.weight_kg}kg, BMI {bmi}, Nhóm máu {record.blood_type}\n"
        context += f"- Tiền sử bệnh: {getattr(record, 'medical_history', 'Không có dữ liệu')}\n"
    
    context += "\n--- THỐNG KÊ TẬP LUYỆN (10 buổi gần nhất) ---\n"
    context += f"- Tổng số Reps hoàn thành: {total_reps}\n"
    context += f"- Độ chính xác trung bình: {'%.1f' % float(avg_accuracy)}%\n"
    
    if session_details_list:
        context += "- Chi tiết các buổi tập:\n"
        context += "\n".join(session_details_list) + "\n"
            
    if notes:
        context += "\n--- GHI CHÚ CHUYÊN MÔN ---\n"
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
            detail="Chưa cấu hình Gemini API Key. Vui lòng kiểm tra file .env"
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
    
    5. ACTION PROTOCOL (MỚI): Nếu bạn nhận thấy bệnh nhân gặp khó khăn (độ chính xác thấp < 50% hoặc bỏ lỡ nhiều buổi tập), bạn CÓ QUYỀN đề xuất các hành động cụ thể như:
       - "Đề xuất bài tập phục hồi nhẹ hơn"
       - "Nhắc nhở lịch hẹn với bác sĩ"
       - "Gợi ý tăng thời gian nghỉ ngơi"
       Khi đề xuất, hãy giải thích lý do dựa trên dữ liệu.
    
    DỮ LIỆU NGỮ CẢNH:
    {context}
    
    QUY TẮC PHẢN HỒI:
    - Ngôn ngữ: Tiếng Việt.
    - Phong cách: Chuyên nghiệp, đồng cảm, chính xác, súc tích nhưng đầy đủ thông tin.
    - Định dạng: Sử dụng Markdown (bold, tables, lists) để thông tin dễ đọc.
    - Bảo mật: Tuyệt đối không tiết lộ thông tin của bệnh nhân khác. Nếu không có dữ liệu cho câu hỏi cụ thể, hãy thành thật trả lời là không có dữ liệu.
    - Giới hạn: Chỉ trả lời các vấn đề liên quan đến y tế và phục hồi chức năng của bệnh nhân này.
    - Action Integration: Luôn kết thúc bằng một câu hỏi gợi mở hoặc một "Hành động đề xuất" nếu thấy cần thiết để thúc đẩy sự phục hồi.
    """
    
    try:
        model = genai.GenerativeModel('gemini-3-flash-preview')
        
        async def generate_response() -> AsyncGenerator[str, None]:
            try:
                # Revert to V1 streaming
                response = model.generate_content(
                    [system_prompt, request.message],
                    stream=True
                )
                for chunk in response:
                    # In V1, we check if text is available to avoid errors on empty chunks
                    try:
                        if chunk.text:
                            yield f"data: {json.dumps({'text': chunk.text}, ensure_ascii=False)}\n\n"
                    except ValueError:
                        # Some chunks (like safety filters) don't have text
                        continue
                yield "data: [DONE]\n\n"
            except Exception as stream_err:
                yield f"data: {json.dumps({'error': str(stream_err)}, ensure_ascii=False)}\n\n"
                yield "data: [DONE]\n\n"

        return StreamingResponse(generate_response(), media_type="text/event-stream")
    except Exception as e:
        # Provide much more detail for the 500 error
        error_detail = f"Lỗi AI ({type(e).__name__}): {str(e)}"
        print(f"ERROR PATH /chat: {error_detail}")
        raise HTTPException(status_code=500, detail=error_detail)
