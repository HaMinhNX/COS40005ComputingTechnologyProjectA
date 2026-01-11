# Patient Scheduling Feature - Implementation Summary

**Date**: 2025-11-27  
**Feature**: Lịch hẹn cho bệnh nhân (Patient Appointment Scheduling)

## 📋 Overview

Đã triển khai thành công tính năng đặt lịch hẹn cho bệnh nhân, cho phép:
- Bệnh nhân xem lịch hẹn với bác sĩ
- Bệnh nhân tự đặt lịch hẹn mới
- Hiển thị lịch theo dạng tháng, tuần, ngày
- Tự động tạo thông báo cho bệnh nhân khi có lịch hẹn mới

## 🔧 Backend Changes

### 1. API Endpoints Added (`api_dashboard.py`)

#### GET `/api/schedules/{doctor_id}`
- Lấy tất cả lịch hẹn của bác sĩ
- Trả về danh sách lịch hẹn với thông tin bệnh nhân
- Format: ISO datetime cho `start` và `end`

#### GET `/api/patient-schedules/{patient_id}`
- Lấy tất cả lịch hẹn của bệnh nhân
- Trả về danh sách lịch hẹn với thông tin bác sĩ
- Format: ISO datetime cho `start` và `end`

#### POST `/api/schedules`
- Tạo lịch hẹn mới
- Payload:
  ```json
  {
    "patient_id": "uuid",
    "doctor_id": "uuid",
    "start_time": "ISO datetime",
    "end_time": "ISO datetime",
    "notes": "string"
  }
  ```
- Tự động tạo notification cho bệnh nhân

#### DELETE `/api/schedules/{schedule_id}`
- Xóa lịch hẹn theo ID

### 2. Database Schema

Sử dụng bảng `schedules` đã có sẵn trong `main.py`:
```sql
CREATE TABLE schedules (
    schedule_id SERIAL PRIMARY KEY,
    patient_id UUID REFERENCES users(user_id),
    doctor_id UUID REFERENCES users(user_id),
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    notes TEXT,
    status VARCHAR(20) DEFAULT 'scheduled',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

Bảng `notifications` được tạo tự động khi startup:
```sql
CREATE TABLE notifications (
    notification_id SERIAL PRIMARY KEY,
    user_id UUID,
    title VARCHAR(100),
    message TEXT,
    type VARCHAR(20) DEFAULT 'info',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 🎨 Frontend Changes

### 1. New Component: `PatientScheduling.vue`

**Location**: `/frontend/src/components02/PatientScheduling.vue`

**Features**:
- 📅 **Calendar Views**: Tháng, Tuần, Ngày
- ➕ **Create Appointment**: Modal để đặt lịch hẹn mới
- 🎨 **Modern UI**: Gradient emerald/teal theme
- 📱 **Responsive**: Hoạt động tốt trên mobile và desktop
- ⏰ **Time Slots**: Click vào time slot để tạo lịch nhanh

**Key Functions**:
- `loadData()`: Fetch schedules từ API
- `saveEvent()`: Tạo lịch hẹn mới
- `selectDate()`: Chọn ngày để đặt lịch
- `selectTimeSlot()`: Chọn giờ cụ thể
- Calendar navigation: `prev()`, `next()`, `today()`

### 2. Updated Component: `PatientTabs.vue`

**Changes**:
- ✅ Import `PatientScheduling.vue`
- ✅ Import `Calendar` icon từ `lucide-vue-next`
- ✅ Thêm tab mới: `{ id: 'scheduling', label: 'Lịch hẹn', iconComponent: Calendar }`
- ✅ Thêm routing trong `currentComponent` computed

**Tab Order**:
1. Tổng quan (Dashboard)
2. Tập luyện (Workout)
3. Trí tuệ (Brain)
4. Thể thao (Sports)
5. **Lịch hẹn (Scheduling)** ← NEW
6. Liên hệ (Contact)

## 🚀 How to Use

### For Patients:

1. **Đăng nhập** với tài khoản bệnh nhân
2. **Chuyển sang tab "Lịch hẹn"**
3. **Xem lịch hẹn** theo tháng/tuần/ngày
4. **Đặt lịch mới**:
   - Click nút "Đặt lịch hẹn" hoặc
   - Click vào ngày/giờ trên calendar
   - Điền thông tin: Ngày, Giờ, Loại cuộc hẹn, Ghi chú
   - Click "Đặt Lịch"

### For Doctors:

Bác sĩ có thể xem lịch hẹn của mình qua component `Scheduling.vue` (đã có sẵn).

## 📊 Data Flow

```
Patient Browser
    ↓
PatientScheduling.vue
    ↓
API: GET /api/patient-schedules/{patient_id}
    ↓
api_dashboard.py
    ↓
PostgreSQL (schedules table)
    ↓
Return JSON with schedule data
    ↓
Display in Calendar View
```

## 🎯 Testing Checklist

- [ ] Bệnh nhân có thể xem lịch hẹn
- [ ] Bệnh nhân có thể tạo lịch hẹn mới
- [ ] Calendar hiển thị đúng events
- [ ] Time slots hoạt động đúng
- [ ] Notifications được tạo khi đặt lịch
- [ ] Responsive trên mobile
- [ ] Không có lỗi console

## 🔮 Future Enhancements

1. **Edit Appointment**: Cho phép sửa lịch hẹn đã tạo
2. **Cancel/Reschedule**: Hủy hoặc đổi lịch
3. **Reminders**: Gửi nhắc nhở trước cuộc hẹn
4. **Video Call Integration**: Tích hợp gọi video cho tư vấn trực tuyến
5. **Doctor Availability**: Hiển thị thời gian bác sĩ rảnh
6. **Conflict Detection**: Cảnh báo khi trùng lịch

## 📝 Notes

- API endpoint sử dụng `schedule_id` (SERIAL) làm primary key
- Frontend sử dụng `id` để tương thích với calendar logic
- Timezone được xử lý bằng `getTimezoneOffset()` ở frontend
- Default appointment duration: 1 giờ
- Color coding: Khám (blue), Tái khám (emerald), Tư vấn (teal)

## ✅ Status

**COMPLETED** - Feature is ready for testing and demo.
