# Quy tắc triển khai website qua Cloudflare Tunnel

Tài liệu này dùng khi chép dự án sang máy khác hoặc đổi hostname. Thay các giá trị mẫu sau:

- `<HOSTNAME>`: hostname công khai, ví dụ `web.vnpthis.io.vn`.
- `<PROJECT_DIR>`: thư mục dự án, ví dụ `D:\Work\AntiGravity\website`.
- `<TUNNEL_NAME>`: tên Cloudflare Tunnel đang dùng.
- `<TUNNEL_ID>`: ID của Cloudflare Tunnel.
- `<USER>`: tài khoản Windows chạy `cloudflared`.

Không chép mật khẩu, token, `cert.pem`, file credentials của tunnel hoặc Django secret vào Git.

## 1. Mô hình cổng

- Frontend tĩnh: `http://127.0.0.1:4173`
- Backend Django: `http://127.0.0.1:8002`
- Cloudflare phục vụ cả frontend và backend trên cùng một hostname HTTPS.

Frontend dùng URL tương đối như `/api/v1/dvkt/`. Vì vậy Cloudflare phải phân luồng theo đường dẫn, không được chuyển toàn bộ hostname vào cổng `4173`.

## 2. Quy tắc ingress bắt buộc

Trong `config.yml`, rule backend phải nằm trước rule frontend:

```yaml
tunnel: <TUNNEL_ID>
credentials-file: C:\Users\<USER>\.cloudflared\<TUNNEL_ID>.json

ingress:
  - hostname: <HOSTNAME>
    path: ^/(api|admin|media|static)(/.*)?$
    service: http://127.0.0.1:8002

  - hostname: <HOSTNAME>
    service: http://127.0.0.1:4173

  - service: http_status:404
```

Ý nghĩa:

- `/api/*`, `/admin/*`, `/media/*`, `/static/*` đi vào Django ở cổng `8002`.
- Các đường dẫn còn lại như `/`, `/dich-vu.html` đi vào frontend ở cổng `4173`.
- Rule `http_status:404` luôn nằm cuối cùng.

Nếu đặt rule frontend trước rule backend, mọi yêu cầu `/api/*` sẽ bị server tĩnh xử lý và trang sẽ không tải được dữ liệu database.

## 3. Cấu hình Django cho hostname mới

Tạo file `<PROJECT_DIR>\backend\.env`:

```env
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,<HOSTNAME>
CORS_ALLOWED_ORIGINS=http://127.0.0.1:4173,http://localhost:4173,https://<HOSTNAME>
```

File `.env` chứa cấu hình riêng của máy và không được commit. Sau khi sửa `.env`, phải khởi động lại backend để Django đọc cấu hình mới.

## 4. Tạo DNS route cho hostname

Sau khi đăng nhập Cloudflare CLI trên máy mới:

```powershell
C:\cloudflared\cloudflared.exe tunnel route dns -f <TUNNEL_NAME> <HOSTNAME>
```

Lệnh này tạo hoặc cập nhật CNAME để hostname đi qua tunnel.

## 5. Kiểm tra cấu hình trước khi nạp

```powershell
C:\cloudflared\cloudflared.exe tunnel --config C:\cloudflared\config.yml ingress validate

C:\cloudflared\cloudflared.exe tunnel --config C:\cloudflared\config.yml ingress rule https://<HOSTNAME>/api/v1/dvkt/

C:\cloudflared\cloudflared.exe tunnel --config C:\cloudflared\config.yml ingress rule https://<HOSTNAME>/dich-vu.html
```

Kết quả mong đợi:

- URL `/api/v1/dvkt/` khớp rule backend `127.0.0.1:8002`.
- URL `/dich-vu.html` khớp rule frontend `127.0.0.1:4173`.

Nếu máy có cả hai file cấu hình dưới đây, phải cập nhật đồng nhất:

- `C:\cloudflared\config.yml`
- `C:\Users\<USER>\.cloudflared\config.yml`

Luôn sao lưu hai file trước khi ghi đè.

## 6. Khởi động dịch vụ

Mở ConEmu tại thư mục dự án và chạy:

```text
run_web4173.bat start
```

File này khởi động:

- frontend chạy nền ở `127.0.0.1:4173`;
- backend chạy nền ở `127.0.0.1:8002`;
- migrate database và collect static trước khi chạy backend.
- không mở thêm cửa sổ CMD; log và PID được lưu tại `%TEMP%\bvlp_web4173`.

Các lệnh quản lý trong ConEmu:

```text
run_web4173.bat start
run_web4173.bat stop
run_web4173.bat restart
run_web4173.bat status
run_web4173.bat logs
run_web4173.bat open
```

Sau đó khởi động lại Cloudflare Tunnel để nạp ingress mới:

```powershell
C:\cloudflared\cloudflared.exe tunnel --config C:\cloudflared\config.yml run <TUNNEL_NAME>
```

Launcher kiểm tra cổng trước khi chạy để tránh tạo trùng tiến trình. Dùng lệnh `restart` thay vì nhấp đúp launcher nhiều lần.

## 7. Kiểm tra sau khi triển khai

Kiểm tra local trước:

```powershell
Invoke-WebRequest http://127.0.0.1:4173/
Invoke-WebRequest http://127.0.0.1:8002/api/v1/health/
Invoke-WebRequest http://127.0.0.1:8002/api/v1/dvkt/
```

Kiểm tra public sau:

```powershell
Invoke-WebRequest https://<HOSTNAME>/
Invoke-WebRequest https://<HOSTNAME>/api/v1/health/
Invoke-WebRequest https://<HOSTNAME>/api/v1/dvkt/
Invoke-WebRequest https://<HOSTNAME>/admin/
```

Tất cả phải trả HTTP 200. `/admin/` có thể chuyển hướng đến `/admin/login/?next=/admin/` và vẫn là hoạt động bình thường.

Nếu local có dữ liệu nhưng public không có:

1. Kiểm tra `/api/v1/dvkt/` công khai có trả JSON hay không.
2. Kiểm tra rule `/api/*` có nằm trước rule frontend hay không.
3. Kiểm tra `<HOSTNAME>` đã có trong `DJANGO_ALLOWED_HOSTS`.
4. Khởi động lại backend sau khi đổi `.env`.
5. Khởi động lại tunnel sau khi đổi `config.yml`.
6. Nhấn `Ctrl + F5` trên trình duyệt để bỏ cache.

## 8. Lưu ý về database khi pull hoặc chuyển máy

Repo hiện có thể chứa `backend\data\development.sqlite3`. Trước khi `git pull`, clone lại hoặc chép sang máy khác:

1. Dừng backend.
2. Sao lưu `backend\data\development.sqlite3`.
3. Thực hiện pull/chép source.
4. Quyết định dùng database cũ hay database mẫu từ repo.
5. Chạy migrate.
6. Kiểm tra lại tài khoản superuser và dữ liệu dịch vụ.

Không lưu mật khẩu tài khoản admin trong tài liệu này.
