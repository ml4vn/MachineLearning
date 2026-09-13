# Hoàn tất Bài 04

Đã hoàn thành sáu bước. Bảy kiểm thử đạt; chạy `--mode all` thành công từ Olist ZIP gốc và chạy thêm thí nghiệm eta = 1,8 để kiểm hành vi phân kỳ minh họa.

- Bảng nguồn: 99.441 đơn; 96.394 đơn giao hợp lệ; giữ 79.686 đơn theo cửa sổ/nhãn. Train/validation/test = 29.031/10.389/40.266.
- Trong bảng cuối có 398 khoảng cách thiếu và 16 đơn thiếu toàn bộ cân nặng. Con số thiếu trong bảng cuối khác thống kê trên toàn bộ đơn hợp lệ; chương trình ghi rõ phạm vi.
- OLS một biến: b = 7,9081917851; w = 0,005639148534 ngày/km. Test MAE = 5,9396449703; RMSE = 9,3515358694, khớp slide.
- GD 100 bước có chênh lệch hệ số tối đa 0,00030327 so OLS trong hệ chuẩn hóa. Các baseline và mô hình sáu đặc trưng cũng tái tạo đúng số liệu.
- Đã xem cả bốn PNG 3840 × 2160; điều chỉnh màu thứ sáu của đồ thị learning rate để phân biệt các đường.

Môi trường: Python 3.12.14, scikit-learn 1.6.1, Matplotlib 3.10.3. Kết quả chi tiết ở `outputs/bai04/`; thí nghiệm eta lớn có thư mục riêng.
