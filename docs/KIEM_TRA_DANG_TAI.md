# Kiểm tra bộ học liệu để đăng GitHub

**Biên bản lịch sử của lần đóng gói v2 (13/09/2026).** Các số liệu 12 trang/bài và 120 trang bên dưới thuộc bản cũ. Trạng thái phát hành tài liệu đọc trước hiện tại được ghi trong [cập nhật v3](CAP_NHAT_DOC_TRUOC_V3.md) và [manifest hiện tại](reading_manifest.json).

Đích phát hành: `ml4vn/MachineLearning`. Mô tả khóa học, giảng viên và đơn vị dùng đúng thông tin do chủ repository cung cấp.

## Nội dung và tính toàn vẹn

- Đủ 10 bài đọc trước; mỗi bài có Markdown, PDF 12 trang, Word, hình, nguồn công thức và các bảng tham chiếu đi kèm.
- 20 tệp PDF/Word khớp SHA256 với biên bản xuất đã kiểm tra. Tổng cộng 120 trang PDF; số bảng/hình trong DOCX khớp biên bản gốc.
- Giữ nguyên 345 tệp nguồn đi kèm trong `readings/`; manifest lưu checksum từng tệp. Quy tắc Git giữ nguyên byte của các bản xuất này, kể cả xuống dòng và khoảng trắng trong SVG sinh tự động.
- Bản Markdown chứa đủ 86 bảng, 55 hình minh họa, 86 công thức và 60 câu tự kiểm. Đã dùng bộ phân tích GitHub Flavored Markdown để đối chiếu số bảng, số hàng/cột của từng bảng và các khối công thức với nguồn JSON.
- Đã kiểm 351 liên kết nội bộ, gồm đường dẫn PDF/Word, hình, mục lục và liên kết đọc trước ↔ Python; không có liên kết nội bộ bị thiếu tại thời điểm kiểm.

## Khả năng chạy từ gói bàn giao

Gói ZIP được tạo từ danh sách tệp Git theo dõi, không gồm `.git`, `.venv`, thư mục output và các archive dữ liệu tải để chạy Python. Đã kiểm CRC, nội dung từng tệp trong ZIP khớp tệp nguồn, sau đó giải nén sang thư mục khác và chạy thành công:

```bash
python tools/check_course.py
python run_tests.py
```

Cả 60 kiểm thử toán học/trường hợp biên đạt từ bản giải nén. Mã thuật toán của 10 bài giữ nguyên so với lần chạy đầy đủ đã kiểm trong [biên bản thực hành](KIEM_TRA_TONG_THE.md); lần ghép học liệu bổ sung điều hướng, tài liệu và công cụ xuất/kiểm Markdown.

## Công cụ đăng tải

`tools/publish_course.ps1` đã được kiểm cú pháp và chạy chế độ `-CheckOnly` trên Windows PowerShell: xác nhận đúng URL đích, kiểm nhánh/lịch sử và nhận diện trường hợp chưa có tên/email commit. Script chỉ tin cậy chính thư mục học liệu trong từng lệnh Git để xử lý trường hợp thư mục được tạo bởi tài khoản sandbox; không đổi cấu hình tin cậy toàn máy.

GitHub yêu cầu xác thực bằng tài khoản có quyền ghi. Kiểm tra local và chế độ `-CheckOnly` không tương đương với việc đã push thành công. Kết quả GitHub Actions chỉ được xác nhận sau khi workflow thực sự chạy trên repository. Hướng dẫn đăng nhập, push và đặt About ở [GITHUB.md](GITHUB.md).
