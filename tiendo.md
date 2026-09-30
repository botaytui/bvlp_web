# TIẾN ĐỘ XÂY DỰNG WEBSITE

**Cập nhật:** 26/09/2026

## Trạng thái tổng quan

| Mốc | Trạng thái | Kết quả |
|---|---|---|
| 1. Khảo sát và chốt phương án | Hoàn thành | Báo cáo, sitemap, phạm vi MVP và mockup desktop/mobile |
| 2. Dựng frontend trang chủ | Hoàn thành | HTML semantic, CSS responsive, JavaScript tương tác |
| 3. Kiểm thử trình duyệt | Hoàn thành vòng 1 | Desktop 1440 px, mobile 390 px, menu, dialog, form và lọc tin |
| 4. Backend và API đặt lịch | Đang triển khai | Đã tạo Django, database, API, Admin và nối form local |
| 5. CMS và triển khai production | Chưa thực hiện | PostgreSQL local, CMS, sao lưu, Cloudflare và UAT |

## Đã hoàn thành

- Trang chủ hiện đại bám theo mockup đã duyệt.
- Responsive từ mobile đến desktop, không có cuộn ngang ở 390 px và 1440 px.
- Header sticky, menu mobile và thanh thao tác nhanh.
- Hero, tiện ích nhanh, chuyên khoa, quy trình khám và chương trình chống lao.
- Biểu mẫu đặt lịch có kiểm tra họ tên, điện thoại, ngày, chuyên khoa và đồng ý xử lý dữ liệu.
- Tin tức có bộ lọc Tất cả/Sức khỏe/Thông báo.
- Khu vực giá dịch vụ, liên hệ, bản đồ minh họa và footer.
- Ảnh lớn từ website cũ đã được thu nhỏ từ khoảng 5,9 MB xuống khoảng 300 KB.
- Có 1 thẻ H1; ảnh nội dung có alt; trường nhập có label; hỗ trợ bàn phím và reduced motion.
- Không còn lỗi console sau khi bổ sung favicon.

## Kết quả kiểm thử vòng 1

- Desktop: viewport 1440 px, document width 1440 px.
- Mobile: viewport 390 px, document width 390 px.
- Menu mobile mở/đóng đúng.
- Hộp thoại đặt lịch mở đúng và chuyển đến form.
- Gửi form dữ liệu mẫu thành công ở mức frontend.
- Ảnh kiểm thử: ../output/playwright/bvlbpbl-new-desktop.png và ../output/playwright/bvlbpbl-new-mobile.png.

## Chưa kết nối trong bản hiện tại

- Cơ sở dữ liệu và API nhận lịch khám.
- CMS quản trị bài viết, chuyên khoa, bảng giá và văn bản.
- SMS, email, Zalo OA hoặc HIS.
- Dữ liệu bài viết và thông tin pháp lý chính thức.
- Tên miền, hosting, WAF, sao lưu và giám sát sản xuất.

## Việc tiếp theo

1. Xác nhận thông tin chính thức: tên đơn vị, địa chỉ, hotline, giờ làm việc và logo.
2. Chọn phương án CMS và hạ tầng triển khai.
3. Xây API tiếp nhận đăng ký khám và trang quản trị.
4. Di chuyển, làm sạch nội dung từ website cũ.
5. Kiểm thử bảo mật, hiệu năng và UAT trước khi đưa lên tên miền thật.

## Cập nhật giao diện bám sát mockup

**Hoàn thành:** 25/09/2026

- Thay hero bằng ảnh bác sĩ Việt Nam thăm khám người cao tuổi, đúng bố cục nhân vật bên phải và vùng chữ bên trái.
- Bổ sung ảnh minh họa lá phổi và ảnh khám sàng lọc đồng bộ với mockup.
- Nén ba ảnh mới phục vụ web; hero còn khoảng 137 KB, ảnh tin khoảng 59–91 KB.
- Thu gọn top bar, header, hero, tiện ích, chuyên khoa, quy trình, tin tức và footer theo tỷ lệ mockup.
- Trang chủ desktop vừa đúng viewport 1440 × 1000, document width 1440 px và không tràn ngang.
- Bản mobile 390 px không tràn ngang; tiện ích và chuyên khoa hiển thị lưới hai cột, có thanh thao tác cố định.
- Tách biểu mẫu sang trang **dat-lich.html** để trang chủ giữ bố cục gọn như mockup.
- Ảnh đối chiếu cuối: ../output/playwright/bvlbpbl-mockup-desktop-final.png và ../output/playwright/bvlbpbl-mockup-mobile-v3.png.
- Kiểm tra lại trang chủ và trang đặt lịch: 0 lỗi console.

## Hiệu chỉnh theo ảnh mockup gốc

**Hoàn thành:** 25/09/2026

- Căn lại đúng thứ tự và tỷ lệ các vùng: thanh tiện ích, nhận diện bệnh viện, menu, hero, 5 tiện ích nhanh, 4 chuyên khoa, quy trình khám, tin tức, bản đồ và footer.
- Thay nội dung hero bằng đúng tiêu đề và thông điệp trong `mockup-trang-chu.png`.
- Dùng ảnh bác sĩ khám hô hấp cho người cao tuổi ở đúng vị trí desktop và crop riêng phù hợp mobile.
- Mobile được rút gọn theo mẫu: ẩn thanh tiện ích, hero thấp, lưới tiện ích 2 cột, lưới chuyên khoa 2 cột và thanh thao tác 3 nút cố định dưới màn hình.
- Desktop 1440 × 1000: document width 1440 px, document height 1000 px, không tràn ngang.
- Mobile 390 × 844: document width 390 px, không tràn ngang; menu mở/đóng đúng.
- Không có lỗi hoặc cảnh báo trong console trình duyệt.
- Ảnh đối chiếu mới nhất: `../output/playwright/mockup-khop-desktop-final.png` và `../output/playwright/mockup-khop-mobile-final.png`.

### Chỉnh banner theo hình tham chiếu H2

- Tạo mới ảnh nền `assets/images/hero-banner-v3.jpg` theo đúng bố cục: khoảng sáng bên trái, bác sĩ và người bệnh ở giữa–phải, bảng thông điệp ở mép phải.
- Mở rộng khung nội dung desktop lên tối đa 1680 px để tránh giao diện bị co nhỏ trên màn hình 1900 px.
- Căn lại H1, khẩu hiệu, mô tả và hai nút theo đúng tỷ lệ banner tham chiếu.
- Kiểm thử desktop 1900 × 1000: banner cao 280 px, document width 1900 px, không tràn ngang, 0 lỗi console.
- Kiểm thử mobile 390 × 844: document width 390 px, ảnh nhân vật crop đúng và không tràn ngang.
- Ảnh kiểm thử: `../output/playwright/banner-h2-desktop-1900.png` và `../output/playwright/banner-h2-mobile-390.png`.

### Tăng cỡ chữ và sửa phần ảnh banner bị cắt

- Tăng cỡ chữ nền toàn trang từ 16 px lên 17 px; các thành phần dùng đơn vị `rem` tăng đồng bộ.
- Căn ảnh banner theo mép trên (`center top`) để hiển thị đầy đủ phần đầu bác sĩ và người bệnh.
- Desktop 1900 px và mobile 390 px đều không tràn ngang; console không có lỗi.
- Ảnh kiểm thử mới: `../output/playwright/banner-font-fix-desktop.png` và `../output/playwright/banner-font-fix-mobile.png`.

- Điều chỉnh bổ sung theo yêu cầu: cỡ chữ nền toàn trang tăng từ 17 px lên 20 px.

## Bắt đầu backend và database local-first

**Cập nhật:** 26/09/2026

### Đã triển khai

- Chốt Django 5.2 + PostgreSQL local + Django Admin; SQLite chỉ dùng phát triển.
- Tạo backend trong thư mục `website/backend`.
- Tạo mô hình chuyên khoa, đăng ký khám và lịch sử trạng thái.
- Tạo migration và dữ liệu chuyên khoa mặc định.
- Tạo API health, danh mục chuyên khoa và tiếp nhận đăng ký.
- Kiểm tra dữ liệu phía server, ngày trong 90 ngày, đồng ý xử lý dữ liệu và honeypot.
- Chống gửi lặp bằng idempotency key và chống trùng số điện thoại/chuyên khoa/ngày.
- Tạo trang quản trị Django để tìm kiếm, lọc, phân công và cập nhật trạng thái.
- Nối biểu mẫu trang chủ và trang đặt lịch với API local `127.0.0.1:8000`.
- Frontend không tự gửi dữ liệu ra tên miền production chưa được xác minh.
- Khởi tạo database phát triển và chạy 6 kiểm thử API thành công.
- Cài PostgreSQL 17.11 thành Windows service tự khởi động.
- Tạo database `hospital_website` và role riêng `hospital_app` theo nguyên tắc quyền tối thiểu.
- Chuyển cấu hình mặc định của backend sang PostgreSQL bằng tệp `.env` bảo mật.
- PostgreSQL chỉ lắng nghe trên loopback `127.0.0.1` và `::1`.
- Áp dụng đầy đủ migration trên PostgreSQL và smoke test API qua Waitress thành công.

### Việc kế tiếp

1. Tạo tài khoản quản trị Django, nhóm tiếp nhận và nhóm biên tập.
2. Bổ sung xuất Excel, chính sách lưu/xóa dữ liệu và mã hóa ổ đĩa.
3. Xây CMS bài viết, văn bản, bảng giá và lịch khám.
4. Tạo lịch sao lưu PostgreSQL tự động và kiểm thử phục hồi.
5. Sau khi duyệt tên miền/chính sách dữ liệu, cấu hình Cloudflare Tunnel Free và chống bot.
