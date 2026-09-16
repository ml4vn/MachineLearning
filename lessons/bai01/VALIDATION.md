> Biên bản của phiên bản gốc; số hình và hướng dẫn đã được cập nhật. Xem [kiểm tra Python v3](../../docs/KIEM_TRA_PYTHON_V3.md) để biết kết quả mới.

# Kiểm tra hoàn tất Bài 01

- Đã chạy chế độ all từ ZIP MovieLens gốc có SHA256 đúng registry.
- 9.742 phim; 19 nhãn; 34 thiếu metadata; 9.707 ứng viên; 42 đồng bộ nhãn: khớp slide.
- Năm phim minh họa và toàn bộ điểm cosine được tính lại, đối chiếu công thức tập nhãn và sklearn.
- 5 kiểm thử độc lập đạt: hình học, vector 0, dữ liệu sai, độ lớn cực trị và phản ví dụ.
- Đã chạy trực tiếp main.py từ ngoài thư mục repository với output-dir khác.
- Hai hình 3840×2160 đã được đọc: nhãn, trục, màu và chú thích không chồng/cắt.
- Python 3.12.14; NumPy 2.5.3; pandas 3.0.1; scipy 1.18.1; sklearn 1.6.1; matplotlib 3.10.3.
- Trạng thái: hoàn tất trước khi bắt đầu Bài 02.
