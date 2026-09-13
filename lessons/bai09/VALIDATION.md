# Hoàn tất Bài 09

Đã hoàn thành sáu bước; 6 kiểm thử đạt và `--mode all` chạy thành công từ IDX gốc. Đã chạy lại sau điều chỉnh bố cục hình, kết quả không thay đổi.

- Ví dụ 4 điểm khớp mean, trị riêng, không gian chiếu sklearn, mẫu số n/n−1, tính bất biến khi đổi dấu và tái tạo đủ chiều. MSE tọa độ 0,25; sai số/điểm 0,5.
- Đọc và kiểm SHA256 hai file train chính thức; split 12.000/3.000, ID và hash nội dung không giao nhau. Bài 09 không đọc test và không tính metric test.
- Full SVD train có basis trực chuẩn; transform thủ công và inverse đủ chiều khớp thư viện. Sai số train cho bốn k khớp tổng phương sai phần bỏ với mẫu số đúng.
- k90=82, EVR=0,9001215026744254; 81 chiều có EVR=0,8992717959390805. Bốn MSE validation khớp case_audit.json của slide tới sai số số học.
- Logistic pixel đúng 2.500/3.000; PCA64 đúng 2.511/3.000. Hai optimizer hội tụ; forward tuyến tính thủ công khớp predict.
- Đã xem đủ 8 PNG 3840×2160. Sửa chú giải che điểm và giảm cỡ tiêu đề PC; xem lại hai ảnh sửa. Có mã ảnh nguồn, thang sáng chung và chú thích clip chỉ để hiển thị.

Python 3.12.14, scikit-learn 1.6.1, Matplotlib 3.10.3. `outputs/bai09/` chứa dữ liệu số, mô hình NPZ và hình. Các kết luận chỉ áp dụng thí nghiệm trên tập con; EVR không thay thế độ đo phân loại.
