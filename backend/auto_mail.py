import smtplib
import random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

# ─────────────────────────────────────────
#  CONFIGURATION
# ─────────────────────────────────────────
SMTP_SERVER   = "smtp.gmail.com"
SMTP_PORT     = 465  # SSL port (dùng với SMTP_SSL)
SMTP_EMAIL   = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD    = os.getenv("SMTP_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")  # Configure to your mail   


# # ─────────────────────────────────────────
# #  STATISTIC LOGIC
# # ─────────────────────────────────────────

def gen_health_data(name: str = "Người dùng") -> dict:
    """Tạo dữ liệu sức khỏe cơ bản ngẫu nhiên."""
    return {
        "name":           name,
        "age":            random.randint(18, 60),
        "weight_kg":      round(random.uniform(45.0, 100.0), 1),
        "height_cm":      random.randint(150, 190),
        "heart_rate_bpm": random.randint(55, 100),
        "blood_pressure": f"{random.randint(100, 140)}/{random.randint(60, 90)}",
        "bmi":            None,   # tính bên dưới
        "sleep_hours":    round(random.uniform(4.0, 9.0), 1),
        "water_liters":   round(random.uniform(1.0, 3.5), 1),
        "calories_consumed": random.randint(1400, 3000),
        "date":           datetime.today().strftime("%d/%m/%Y"),
    }


def calc_bmi(data: dict) -> dict:
    """Tính BMI và thêm nhận xét."""
    h = data["height_cm"] / 100
    bmi = round(data["weight_kg"] / (h ** 2), 1)
    data["bmi"] = bmi
    if bmi < 18.5:
        data["bmi_status"] = "Thiếu cân"
    elif bmi < 25:
        data["bmi_status"] = "Bình thường ✅"
    elif bmi < 30:
        data["bmi_status"] = "Thừa cân ⚠️"
    else:
        data["bmi_status"] = "Béo phì 🔴"
    return data


# ─────────────────────────────────────────
#  REHAB WORKOUT STAT
# ─────────────────────────────────────────

EXERCISES = [
    "Giãn cơ nhẹ", "Tập cơ cơ bản", "Tập linh hoạt", "Tập cân bằng", "Tập trợ lực",
    "Tập phục hồi chuyển động", "Tập hô hấp", "Tập thư giãn cơ", "Tập phục hồi khớp", "Tập tập thể dục trị liệu"
]

def gen_workout_data() -> dict:
    """Tạo dữ liệu buổi tập phục hồi ngẫu nhiên."""
    exercise = random.choice(EXERCISES)
    duration = random.randint(20, 60)            # phút
    recovery_score = random.randint(60, 100)    # % cải thiện
    max_hr = random.randint(100, 140)
    avg_hr = random.randint(80, max_hr - 10)
    pain_level = random.randint(0, 10)          # mức độ đau (0-10)

    return {
        "exercise":       exercise,
        "duration_min":   duration,
        "recovery_score": recovery_score,
        "avg_heart_rate": avg_hr,
        "max_heart_rate": max_hr,
        "pain_level":     pain_level,
        "intensity":      _intensity_label(recovery_score),
        "session_date":   (datetime.today() - timedelta(days=random.randint(0, 6)))
                          .strftime("%d/%m/%Y"),
    }

def _intensity_label(recovery_score: int) -> str:
    if recovery_score < 70:
        return "Nhẹ 🟢"
    elif recovery_score < 85:
        return "Trung bình 🟡"
    else:
        return "Cao 🔴"


def gen_weekly_sessions(n: int = 5) -> list[dict]:
    """Tạo danh sách n buổi tập phục hồi trong tuần."""
    return [gen_workout_data() for _ in range(n)]


# ─────────────────────────────────────────
#  AUTO_MAIL
# ─────────────────────────────────────────

def build_email_html(health: dict, sessions: list[dict]) -> str:
    total_duration = sum(s["duration_min"] for s in sessions)
    avg_recovery = round(sum(s["recovery_score"] for s in sessions) / len(sessions), 1) if sessions else 0
    avg_pain = round(sum(s["pain_level"] for s in sessions) / len(sessions), 1) if sessions else 0

    session_rows = ""
    for s in sessions:
        pain_indicator = "🟢" if s["pain_level"] < 3 else ("🟡" if s["pain_level"] < 7 else "🔴")
        session_rows += f"""
        <tr>
            <td>{s['session_date']}</td>
            <td>{s['exercise']}</td>
            <td>{s['duration_min']} phút</td>
            <td>{s['recovery_score']}%</td>
            <td>{s['pain_level']}/10 {pain_indicator}</td>
            <td>{s['avg_heart_rate']} bpm</td>
            <td>{s['intensity']}</td>
        </tr>"""

    return f"""
    <html><body style="font-family:Arial,sans-serif;background:#f4f6f9;padding:20px;">
    <div style="max-width:700px;margin:auto;background:#fff;border-radius:12px;
                box-shadow:0 2px 10px rgba(0,0,0,.1);overflow:hidden;">

      <!-- Header -->
      <div style="background:linear-gradient(135deg,#2ecc71,#27ae60);color:#fff;padding:30px;">
        <h1 style="margin:0;font-size:24px;">🏥 Báo Cáo Tiến Độ Phục Hồi Chức Năng</h1>
        <p style="margin:5px 0 0;opacity:.85;">Ngày: {health['date']} &nbsp;|&nbsp; Bệnh nhân: {health['name']}</p>
      </div>

      <div style="padding:25px;">

        <!-- Chỉ số sức khỏe -->
        <h2 style="color:#2ecc71;border-bottom:2px solid #d5f4e6;padding-bottom:8px;">
          ❤️ Chỉ Số Sức Khỏe Cơ Bản
        </h2>
        <table style="width:100%;border-collapse:collapse;">
          <tr style="background:#f8f9fa;">
            <td style="padding:10px;"><b>Cân nặng</b></td>
            <td style="padding:10px;">{health['weight_kg']} kg</td>
            <td style="padding:10px;"><b>Chiều cao</b></td>
            <td style="padding:10px;">{health['height_cm']} cm</td>
          </tr>
          <tr>
            <td style="padding:10px;"><b>BMI</b></td>
            <td style="padding:10px;">{health['bmi']} — {health['bmi_status']}</td>
            <td style="padding:10px;"><b>Nhịp tim</b></td>
            <td style="padding:10px;">{health['heart_rate_bpm']} bpm</td>
          </tr>
          <tr style="background:#f8f9fa;">
            <td style="padding:10px;"><b>Huyết áp</b></td>
            <td style="padding:10px;">{health['blood_pressure']} mmHg</td>
            <td style="padding:10px;"><b>Giấc ngủ</b></td>
            <td style="padding:10px;">{health['sleep_hours']} giờ</td>
          </tr>
          <tr>
            <td style="padding:10px;"><b>Nước uống</b></td>
            <td style="padding:10px;">{health['water_liters']} lít</td>
            <td style="padding:10px;"><b>Calo nạp vào</b></td>
            <td style="padding:10px;">{health['calories_consumed']} kcal</td>
          </tr>
        </table>

        <!-- Tổng kết tuần -->
        <h2 style="color:#2ecc71;border-bottom:2px solid #d5f4e6;padding-bottom:8px;margin-top:30px;">
          📊 Tổng Kết Tuần Tập Phục Hồi
        </h2>
        <div style="display:flex;gap:15px;flex-wrap:wrap;margin-bottom:20px;">
          {"".join([
            f'<div style="flex:1;min-width:130px;background:#d5f4e6;border-radius:8px;padding:15px;text-align:center;">'
            f'<div style="font-size:28px;font-weight:bold;color:#2ecc71;">{val}</div>'
            f'<div style="color:#555;font-size:13px;margin-top:4px;">{lbl}</div></div>'
            for val, lbl in [
                (len(sessions), "Buổi tập"),
                (f"{total_duration} phút", "Tổng thời gian"),
                (f"{avg_recovery}%", "Cải thiện trung bình"),
            ]
          ])}
        </div>

        <!-- Chi tiết từng buổi -->
        <h2 style="color:#2ecc71;border-bottom:2px solid #d5f4e6;padding-bottom:8px;">
          🗓️ Chi Tiết Từng Buổi Tập Phục Hồi
        </h2>
        <table style="width:100%;border-collapse:collapse;font-size:13px;">
          <thead>
            <tr style="background:#2ecc71;color:#fff;">
              <th style="padding:10px;text-align:left;">Ngày</th>
              <th style="padding:10px;text-align:left;">Bài tập phục hồi</th>
              <th style="padding:10px;text-align:left;">Thời gian</th>
              <th style="padding:10px;text-align:left;">Cải thiện</th>
              <th style="padding:10px;text-align:left;">Mức độ đau</th>
              <th style="padding:10px;text-align:left;">Nhịp tim TB</th>
              <th style="padding:10px;text-align:left;">Cường độ</th>
            </tr>
          </thead>
          <tbody>{session_rows}</tbody>
        </table>

      </div>

      <!-- Footer -->
      <div style="background:#f4f6f9;text-align:center;padding:15px;
                  font-size:12px;color:#888;">
        Báo cáo tự động được tạo bởi <b>Hệ Thống Quản Lý Phục Hồi Chức Năng</b> — {datetime.today().strftime("%d/%m/%Y %H:%M")}
      </div>
    </div>
    </body></html>
    """


# ─────────────────────────────────────────
#  SMTP MAIL
# ─────────────────────────────────────────

def send_health_email(receiver: str = RECEIVER_EMAIL, name: str = "Bệnh nhân") -> bool:
    """Tổng hợp dữ liệu phục hồi, tạo email HTML và gửi qua SMTP."""
    # 1. Gen dữ liệu
    health   = calc_bmi(gen_health_data(name))
    sessions = gen_weekly_sessions(n=random.randint(3, 6))

    # 2. Parse multiple receivers
    if not receiver:
        print("❌ Chưa cấu hình RECEIVER_EMAIL.")
        return False
    receivers = [email.strip() for email in receiver.split(",") if email.strip()]

    # 3. Tạo nội dung email
    html_content = build_email_html(health, sessions)

    # 4. Gửi qua SMTP tới tất cả receivers
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, 465) as server:
            # server.starttls()  # StartTLS is not used when connecting via SSL directly
            server.login(SENDER_EMAIL, SENDER_PASS)
            for email in receivers:
                # Tạo message mới cho mỗi recipient
                msg = MIMEMultipart("alternative")
                msg["Subject"] = f"🏥 Báo Cáo Phục Hồi Chức Năng Tuần — {health['date']} — {name}"
                msg["From"]    = SENDER_EMAIL
                msg["To"]      = email
                msg.attach(MIMEText(html_content, "html", "utf-8"))
                
                server.sendmail(SENDER_EMAIL, email, msg.as_string())
                print(f"✅ Email đã gửi thành công tới {email}")
        return True
    except smtplib.SMTPAuthenticationError:
        print("❌ Lỗi xác thực: kiểm tra email / App Password.")
    except smtplib.SMTPException as e:
        print(f"❌ Lỗi SMTP: {e}")
    except Exception as e:
        print(f"❌ Lỗi không xác định: {e}")
    return False

# ─────────────────────────────────────────
#  TEST GỬI EMAIL (TÂM CONFIGURE BUTTON cho chạy ở dưới)
# ─────────────────────────────────────────

PATIENT_NAMES = [
    "Nguyễn Văn A", "Trần Thị B", "Phạm Minh C", "Hoàng Đức D", "Võ Thị E",
    "Bùi Văn F", "Đặng Thị G", "Ngo Minh H", "Lê Tiến I", "Dương Thị K",
    "Mai Văn L", "Tô Thị M", "Hà Minh N", "Cao Văn O", "Từ Thị P"
]

if __name__ == "__main__":
    random_patient = random.choice(PATIENT_NAMES)
    send_health_email(name=random_patient)