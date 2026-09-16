# Cập nhật tài liệu đọc trước v3

Ngày cập nhật: 16/09/2026.

Đủ Bài 1–10, mỗi bài có bản đọc trực tiếp trên GitHub, nguồn Markdown, Word, PDF, hình và nguồn nội dung có cấu trúc. Các liên kết Word/PDF cũ được giữ nguyên để sinh viên tiếp tục sử dụng.

## Nội dung và phiên bản

- Đối chiếu slide v3 cho Bài 1–6 và 8–10. Riêng Bài 7 đối chiếu slide v2 hiện có; “v3” ở đây là phiên bản tài liệu đọc trước.
- Tăng phần giải thích kiến thức nền, định nghĩa ký hiệu, kết nối ví dụ với công thức và tổng kết theo chặng.
- Tổng 141 trang PDF: Bài 6 có 15 trang, các bài còn lại có 14 trang.
- Bản đọc trực tiếp chứa 105 bảng, 56 lượt hình minh họa, 101 công thức và 60 câu tự kiểm.
- Word/PDF giữ nguyên tệp đã duyệt trong bộ v3. Mã SHA256 được kiểm với biên bản nguồn trước khi sao chép; việc đóng gói GitHub không thay bố cục của chúng.

## Phạm vi thực hành Python

Đợt này cập nhật tài liệu đọc trước và công cụ kiểm tra học liệu. Mã thuật toán, dữ liệu thực hành và kết quả huấn luyện giữ phiên bản hiện có. Xem [đối chiếu học liệu](DOI_CHIEU_HOC_LIEU.md) trước khi so các ví dụ giữa tài liệu v3 và Python.

## Kiểm tra và tái tạo

```bash
python tools/build_readings.py --check
python tools/check_course.py
```

Lệnh thứ nhất kiểm bản đọc trực tiếp khớp nguồn cấu trúc. Lệnh thứ hai kiểm mã SHA256 của các tệp phát hành, đủ học liệu cho mười bài và liên kết nội bộ. Khi thay nội dung nguồn, phải xuất và kiểm lại Word/PDF trước khi cập nhật manifest; sinh lại Markdown không tự cập nhật hai định dạng này.

[Biên bản kiểm tra nguồn v3](reading_v3_source_qa.json) ghi kết quả kết xuất và rà trang của bộ tài liệu trước khi đăng tải. [Manifest phát hành](reading_manifest.json) ghi mã SHA256 của các tệp hiện tại. Các báo cáo Python ngày 13/09/2026 là bằng chứng của phiên bản thực hành trước, không phải báo cáo chạy lại dữ liệu thật trong đợt cập nhật này.
