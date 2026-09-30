# Website Bệnh viện Lao và Bệnh phổi Bạc Liêu

## Chạy thử cục bộ

Tại thư mục gốc dự án, chạy lệnh sau:

    python -m http.server 4173 --directory website

Sau đó mở: [http://127.0.0.1:4173/](http://127.0.0.1:4173/)

## Tệp chính

- **index.html**: cấu trúc trang chủ.
- **dat-lich.html**: trang biểu mẫu đặt lịch riêng.
- **styles.css**: thiết kế và responsive.
- **app.js**: menu, dialog, bộ lọc tin và kiểm tra form.
- **backend/**: Django API, trang quản trị và cấu hình PostgreSQL local.
- **baocao.md**: kế hoạch dự án.
- **tiendo.md**: nhật ký tiến độ.
- **mockup-trang-chu.png**: concept đồ họa đã duyệt.
- **assets/images/hero-mockup-v2.jpg**: ảnh hero dùng trên trang chủ.

## Backend đặt lịch

Biểu mẫu đã kết nối API local tại `http://127.0.0.1:8000`. Xem hướng dẫn trong [backend/README.md](./backend/README.md).

Khi website không chạy ở localhost, frontend không tự gửi dữ liệu ra ngoài. Endpoint production chỉ được khai báo bằng thẻ meta `booking-api-base-url` sau khi tên miền và chính sách dữ liệu được duyệt.
