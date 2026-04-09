from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
from typing import AsyncGenerator
from uuid import UUID
from datetime import datetime, timedelta

from database import get_db
from models import User, MedicalRecord, WorkoutSession, PatientNote
from dependencies import get_current_user, verify_patient_access
from schemas.communication import AIChatRequest
from enums import ExerciseType

router = APIRouter(
    prefix="/api/ai",
    tags=["ai"]
)

# Gemini Configuration
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def build_supported_exercise_guidance() -> tuple[str, str]:
    """Return supported exercise list in both compact and human-readable formats."""
    supported_values = [exercise.value for exercise in ExerciseType]
    supported_line = ", ".join(supported_values)

    exercise_labels = {
        ExerciseType.BICEP_CURL.value: "Bicep Curl (gập tay)",
        ExerciseType.SHOULDER_FLEXION.value: "Shoulder Flexion (nâng tay trước)",
        ExerciseType.SQUAT.value: "Squat (ngồi xổm)",
        ExerciseType.KNEE_RAISE.value: "Knee Raise (nâng gối)",
    }
    readable_line = "\n".join(
        [f"- {value}: {exercise_labels.get(value, value)}" for value in supported_values]
    )
    return supported_line, readable_line

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
    completed_sessions = 0
    sessions_last_7_days = 0
    active_days = set()
    session_details_list = []
    today = datetime.utcnow().date()
    
    for s in sessions:
        # Sum reps and collect exercises from details
        session_reps = sum(d.reps_completed for d in s.details if d.reps_completed)
        total_reps += session_reps

        if s.start_time:
            session_date = s.start_time.date()
            active_days.add(session_date)
            if session_date >= today - timedelta(days=7):
                sessions_last_7_days += 1

        if (s.status or '').lower() == 'completed':
            completed_sessions += 1
        
        exercises = list(set(d.exercise_type for d in s.details if d.exercise_type))
        exercise_str = ", ".join(exercises) if exercises else "Unknown"
        
        session_details_list.append(
            f"  + [{s.start_time.strftime('%Y-%m-%d %H:%M')}] {exercise_str}: {session_reps} reps, Trạng thái: {s.status or 'unknown'}"
        )

    avg_reps_per_session = total_reps / len(sessions) if sessions else 0

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
    context += f"- Tổng số buổi ghi nhận: {len(sessions)}\n"
    context += f"- Số buổi hoàn thành: {completed_sessions}\n"
    context += f"- Số buổi trong 7 ngày gần nhất: {sessions_last_7_days}\n"
    context += f"- Số ngày có hoạt động: {len(active_days)}\n"
    context += f"- Tổng số Reps hoàn thành: {total_reps}\n"
    context += f"- Reps trung bình mỗi buổi: {avg_reps_per_session:.1f}\n"
    
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
    supported_exercises, supported_exercises_readable = build_supported_exercise_guidance()
    
    # System Prompt (translated to Vietnamese for consistency)
    system_prompt = f"""
    Bạn là một trợ lý y tế AI cao cấp tích hợp trong nền tảng HaminG, có khả năng phân tích dữ liệu chuyên sâu tương tự như các mô hình ngôn ngữ tiên tiến nhất năm 2026.
    
    Bạn đang hỗ trợ một {current_user.role} trong việc quản lý và theo dõi bệnh nhân: {patient.full_name}.
    
    NHIỆM VỤ CỦA BẠN:
    1. Phân tích dữ liệu: Dựa trên ngữ cảnh được cung cấp, hãy đưa ra các nhận xét về tiến độ phục hồi, xu hướng tập luyện, mức độ tuân thủ và các cảnh báo nếu có.
    2. Tóm tắt: Cung cấp bản tóm tắt nhanh về tình trạng sức khỏe nếu được yêu cầu.
    3. Thống kê: Trình bày các con số cụ thể về hiệu suất tập luyện một cách trực quan (sử dụng bảng markdown nếu cần).
    4. Trả lời câu hỏi: Giải đáp mọi thắc mắc về bệnh nhân này dựa trên dữ liệu thật.
    
    5. ACTION PROTOCOL (MỚI): Nếu bạn nhận thấy bệnh nhân gặp khó khăn (bỏ lỡ nhiều buổi tập, gián đoạn tập luyện nhiều ngày, hoặc khối lượng tập giảm rõ rệt), bạn CÓ QUYỀN đề xuất các hành động cụ thể như:
       - "Đề xuất bài tập phục hồi nhẹ hơn"
       - "Nhắc nhở lịch hẹn với bác sĩ"
       - "Gợi ý tăng thời gian nghỉ ngơi"
       Khi đề xuất, hãy giải thích lý do dựa trên dữ liệu.

     6. GỢI Ý BÀI TẬP (ÁP DỤNG KHI NGƯỜI DÙNG LÀ BÁC SĨ):
         - Chỉ được đề xuất bài tập từ danh sách được hệ thống hỗ trợ.
         - Không tự tạo bài tập mới ngoài danh sách này.
         - Nếu bác sĩ yêu cầu "đề xuất bài tập" hoặc "đề xuất assignment", hãy xuất phần "Đề xuất assignment" theo bảng markdown gồm các cột:
            | exercise_type | target_reps | frequency | lý do |
         - exercise_type bắt buộc phải nằm trong danh sách: {supported_exercises}
         - Nếu dữ liệu chưa đủ để đề xuất chắc chắn, hãy nêu rõ thiếu dữ liệu gì và đưa ra đề xuất tạm thời ở mức an toàn.

     DANH SÁCH BÀI TẬP ĐƯỢC HỖ TRỢ:
     {supported_exercises_readable}
    
    DỮ LIỆU NGỮ CẢNH:
    {context}
    
    QUY TẮC PHẢN HỒI:
    - Ngôn ngữ: Tiếng Việt.
    - Phong cách: Chuyên nghiệp, đồng cảm, chính xác, súc tích nhưng đầy đủ thông tin.
    - Định dạng: Sử dụng Markdown (bold, tables, lists) để thông tin dễ đọc.
    - Bảo mật: Tuyệt đối không tiết lộ thông tin của bệnh nhân khác. Nếu không có dữ liệu cho câu hỏi cụ thể, hãy thành thật trả lời là không có dữ liệu.
    - Giới hạn: Chỉ trả lời các vấn đề liên quan đến y tế và phục hồi chức năng của bệnh nhân này.
    - Ràng buộc bài tập: Không đề xuất bài tập ngoài danh sách được hỗ trợ bởi hệ thống.
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
