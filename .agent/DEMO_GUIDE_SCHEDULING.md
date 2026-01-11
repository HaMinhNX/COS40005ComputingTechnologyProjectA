# 🎯 Quick Demo Guide - Patient Scheduling Feature

## 🚀 Cách Demo Tính Năng Lịch Hẹn

### Bước 1: Đăng nhập với tài khoản bệnh nhân

1. Mở trình duyệt: `http://localhost:5173`
2. Click "Chọn người dùng demo"
3. Chọn một tài khoản **bệnh nhân** (role: patient)
4. Click "Đăng nhập"

### Bước 2: Truy cập tab Lịch Hẹn

1. Sau khi đăng nhập, bạn sẽ thấy giao diện bệnh nhân
2. Tìm và click vào tab **"Lịch hẹn"** (icon Calendar 📅)
3. Calendar sẽ hiển thị với view mặc định là "Tháng"

### Bước 3: Khám phá các tính năng

#### 📅 Chuyển đổi View
- Click các nút: **Tháng** / **Tuần** / **Ngày**
- Mỗi view có cách hiển thị khác nhau

#### 🔍 Navigation
- Click **"Hôm nay"** để quay về ngày hiện tại
- Dùng mũi tên **◀ ▶** để di chuyển tháng/tuần/ngày

#### ➕ Tạo Lịch Hẹn Mới

**Cách 1: Từ nút chính**
1. Click nút **"Đặt lịch hẹn"** (góc trên bên phải)
2. Modal sẽ mở ra
3. Điền thông tin:
   - **Ngày**: Chọn ngày muốn hẹn
   - **Giờ**: Chọn giờ (mặc định 09:00)
   - **Loại cuộc hẹn**: Khám bệnh / Tái khám / Tư vấn trực tuyến
   - **Ghi chú**: Mô tả triệu chứng hoặc câu hỏi
4. Click **"Đặt Lịch"**

**Cách 2: Click trực tiếp vào Calendar**
- **View Tháng**: Click vào ngày bất kỳ
- **View Tuần/Ngày**: Click vào time slot (ô giờ)
- Modal sẽ tự động điền ngày/giờ đã chọn

### Bước 4: Xem kết quả

1. Sau khi tạo thành công, lịch hẹn sẽ hiển thị trên calendar
2. Màu sắc:
   - 🔵 **Xanh dương**: Khám bệnh
   - 🟢 **Xanh lá**: Tái khám
   - 🔷 **Xanh ngọc**: Tư vấn trực tuyến
3. Click vào lịch hẹn để xem chi tiết

## 🎨 UI Highlights

### Calendar View - Tháng
- Grid 7x6 hiển thị cả tháng
- Ngày hôm nay có viền màu emerald
- Mỗi ngày hiển thị tối đa 3 events, còn lại hiển thị "+X thêm"

### Calendar View - Tuần
- Hiển thị 7 ngày từ T2-CN
- Time slots từ 00:00 đến 23:00
- Events hiển thị đúng vị trí giờ

### Calendar View - Ngày
- Focus vào 1 ngày cụ thể
- Time slots lớn hơn, dễ đọc hơn
- Hiển thị đầy đủ thông tin event

## 🔔 Notifications

Khi tạo lịch hẹn mới, hệ thống tự động:
1. Lưu vào database (`schedules` table)
2. Tạo notification cho bệnh nhân (`notifications` table)
3. Notification có thể xem ở tab khác (nếu đã implement)

## 🧪 Test Cases

### ✅ Nên test:
1. Tạo lịch hẹn cho ngày hôm nay
2. Tạo lịch hẹn cho tuần sau
3. Chuyển đổi giữa các view
4. Navigation qua các tháng
5. Click vào ngày/time slot để tạo lịch nhanh
6. Kiểm tra responsive trên mobile (F12 → Device toolbar)

### ❌ Known Limitations:
- Chưa có chức năng sửa/xóa lịch hẹn từ patient side
- Chưa kiểm tra conflict (trùng lịch)
- Chưa hiển thị thời gian bác sĩ rảnh

## 📱 Screenshots Checklist

Khi demo, nên chụp:
1. Calendar view - Tháng (có events)
2. Calendar view - Tuần
3. Calendar view - Ngày
4. Modal tạo lịch hẹn
5. Event detail khi click vào lịch hẹn

## 🎬 Demo Script (30 giây)

```
"Đây là tính năng Lịch Hẹn cho bệnh nhân.
Bệnh nhân có thể xem lịch theo tháng, tuần, hoặc ngày.
Để đặt lịch mới, chỉ cần click vào ngày muốn hẹn...
Điền thông tin: ngày, giờ, loại cuộc hẹn, và ghi chú...
Click Đặt Lịch, và lịch hẹn sẽ xuất hiện trên calendar!
Hệ thống cũng tự động gửi thông báo cho bệnh nhân."
```

## 🐛 Troubleshooting

### Lỗi: "Lỗi kết nối"
- Kiểm tra backend đang chạy: `http://localhost:8001`
- Kiểm tra database connection

### Lỗi: Không thấy tab "Lịch hẹn"
- Đảm bảo đã đăng nhập với tài khoản **bệnh nhân**
- Refresh trang (F5)

### Lỗi: Lịch hẹn không hiển thị
- Kiểm tra console (F12) xem có lỗi API không
- Kiểm tra `patient_id` có đúng không

## ✨ Bonus Features

- **Smooth animations**: Fade transitions giữa các view
- **Hover effects**: Events có hiệu ứng khi hover
- **Keyboard friendly**: Có thể dùng Tab để navigate
- **Auto-fill**: Click vào time slot tự động điền giờ

---

**Ready to demo!** 🎉
