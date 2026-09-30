# Backend đặt lịch và CMS

Backend Django chạy trên máy chủ nội bộ. SQLite chỉ dùng để phát triển; môi trường vận hành dùng PostgreSQL local.

## Chạy phát triển

Từ thư mục `website/backend`:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Ở cửa sổ khác, chạy frontend từ thư mục gốc:

```powershell
python -m http.server 4173 --directory website
```

- API health: http://127.0.0.1:8000/api/v1/health/
- Admin: http://127.0.0.1:8000/admin/
- Form: http://127.0.0.1:4173/dat-lich.html

Sau khi đã cài đặt lần đầu, có thể chạy backend bằng cách nhấp đúp `runserver.bat`.

## API hiện có

- `GET /api/v1/health/`
- `GET /api/v1/specialties/`
- `POST /api/v1/appointments/`

API kiểm tra dữ liệu phía server, yêu cầu đồng ý xử lý dữ liệu, giới hạn ngày trong 90 ngày, chống gửi lặp bằng idempotency key và chống trùng theo số điện thoại/chuyên khoa/ngày.

## Cấu hình PostgreSQL production

Sao chép `.env.example` thành `.env`. Django tự đọc tệp này khi khởi động. Không commit mật khẩu hoặc khóa bí mật.

Các biến bắt buộc:

- `DJANGO_DEBUG=false`
- `DJANGO_SECRET_KEY`
- `DJANGO_ALLOWED_HOSTS`
- `CORS_ALLOWED_ORIGINS`
- `DB_ENGINE=postgresql`
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`

Chạy production trên Windows:

```powershell
waitress-serve --listen=127.0.0.1:8000 hospital_backend.wsgi:application
```

Cloudflare Tunnel chỉ trỏ tới `http://127.0.0.1:8000` sau khi tên miền API, chính sách dữ liệu và cấu hình production đã được duyệt.

## Kiểm thử

```powershell
python manage.py test
python manage.py makemigrations --check --dry-run
python manage.py check --deploy
```

Hai cảnh báo HSTS includeSubDomains/preload được giữ tắt cho tới khi xác minh mọi subdomain đều chỉ hoạt động qua HTTPS.

## Trạng thái máy chủ hiện tại

- PostgreSQL 17.11 chạy bằng Windows service `postgresql-x64-17`, tự khởi động cùng máy.
- Database: `hospital_website`.
- Role ứng dụng: `hospital_app`, không có quyền superuser, tạo database hoặc tạo role.
- PostgreSQL chỉ lắng nghe tại `127.0.0.1:5432` và `::1:5432`.
- Mật khẩu và Django secret nằm trong `.env`; ACL chỉ cho tài khoản quản trị hiện tại, SYSTEM và Administrators.
- SQLite cũ tại `data/development.sqlite3` được giữ lại làm dữ liệu phát triển, backend mặc định hiện dùng PostgreSQL.

Để chạy test mà không cấp quyền tạo database cho role production:

```powershell
$env:DB_ENGINE='sqlite'
.\.venv\Scripts\python.exe manage.py test
Remove-Item Env:DB_ENGINE
```

## Danh mục dịch vụ kỹ thuật (DVKT)

Bảng PostgreSQL `dvkt` lưu 27 cột của `../assets/411_dvkt.xls`, thêm khóa `id` và thời điểm tạo/cập nhật. Mã lưu dạng chuỗi; giá dùng Decimal; ngày Excel `YYYYMMDD` được chuyển thành Date. Ô số/ngày trống được lưu NULL. Trang `../dich-vu.html` tra cứu giá qua `GET /api/v1/dvkt/`, chỉ công bố STT, 12 ký tự đầu mã dịch vụ, tên dịch vụ và đơn giá. Tìm kiếm theo mã/tên không dấu và phân trang 25 dòng được xử lý trên frontend; database giữ nguyên mã gốc.

Tại thư mục `website/backend`:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py import_dvkt ..\assets\411_dvkt.xls --dry-run
.\.venv\Scripts\python.exe manage.py import_dvkt ..\assets\411_dvkt.xls
```

Mặc định đọc sheet đầu; dùng `--sheet Sheet1` để chỉ định. File phải có đủ 27 tiêu đề gốc, có thể đổi thứ tự cột. Nhập lại cập nhật theo `(ma_cskcb, ma_dich_vu, tu_ngay)`, không tạo trùng, không xóa dịch vụ ngoài file. Dòng trùng khóa trong cùng file hoặc dữ liệu không hợp lệ sẽ hủy toàn bộ lượt nhập. `--dry-run` hoàn tác mọi thay đổi sau kiểm tra.

Quản lý tại `/admin/dvkt/dvkt/` với tài khoản có quyền DVKT. Backend local đang dùng cổng 8002 theo cấu hình frontend `app.js`.
