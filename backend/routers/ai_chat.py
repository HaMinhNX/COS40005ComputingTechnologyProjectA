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
    sessions = db.query(WorkoutSession).filter(WorkoutSession.user_id == patient_id).order_by(WorkoutSession.start_time.desc()).limit(5).all()
    # Fetch patient notes
    notes = db.query(PatientNote).filter(PatientNote.patient_id == patient_id).all()
    
    context = "DỮ LIỆU BỆNH NHÂN:\n"
    if record:
        context += f"- Chẩn đoán: {record.diagnosis}\n"
        context += f"- Triệu chứng: {record.symptoms}\n"
        context += f"- Kế hoạch điều trị: {record.treatment_plan}\n"
        context += f"- Chỉ số: {record.height_cm}cm, {record.weight_kg}kg, Nhóm máu {record.blood_type}\n"
    
    if sessions:
        context += "- Các buổi tập gần đây:\n"
        for s in sessions:
            context += f"  + Ngày: {s.start_time.strftime('%Y-%m-%d %H:%M')}, Trạng thái: {s.status}\n"
            
    if notes:
        context += "- Ghi chú từ bác sĩ:\n"
        for n in notes:
            context += f"  + {n.title}: {n.content}\n"
            
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
    Bạn là một trợ lý y tế chuyên nghiệp cho nền tảng phục hồi chức năng MEDIC1.
    Bạn đang hỗ trợ một {current_user.role}.
    Nhiệm vụ của bạn là trả lời các câu hỏi về bệnh nhân: {patient.full_name}.
    Hãy sử dụng dữ liệu bệnh nhân dưới đây để làm ngữ cảnh, nhưng tuyệt đối bảo mật thông tin nhạy cảm trừ khi được hỏi cụ thể và luôn giữ thái độ chuyên nghiệp, đồng cảm.
    
    {context}
    
    Nếu bạn không biết câu trả lời dựa trên dữ liệu có sẵn, hãy nói rằng bạn không có đủ thông tin.
    Hãy trả lời bằng tiếng Việt, ngắn gọn, súc tích và hữu ích.
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
