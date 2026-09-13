# Hoàn tất Bài 10

Đã hoàn thành sáu bước; 7 kiểm thử đạt. `--mode all` tự xử lý IDX, fit baseline và thực sự huấn luyện đủ 3 seed × 50 epoch.

- XOR có gradient (0,1/8,0), bước η=8 giảm BCE về 0,5981758073. Nghiệm dựng đúng 4/4 được ghi tách khỏi kết quả học một bước.
- Đủ 9 gradient mạng nhỏ khớp sai phân trung tâm; sai khác tối đa khoảng 4,12×10⁻¹¹. BCE được viết theo dạng softplus ổn định số, nên sai số sai phân có chênh rất nhỏ với biểu thức tương đương trong slide.
- Split và checksum giữ cùng Bài 09; mọi kiểm tra giao ID/hash ảnh train/validation/test đều bằng 0.
- Đủ 50.890 tham số; forward NumPy khớp predict_proba của sklearn ở mọi checkpoint được chọn. Không có cảnh báo huấn luyện.
- Seed 42/43/44 chọn epoch 40/27/40, đúng validation 2.581/2.590/2.597. Các giá trị khớp slide.
- Đã ghi protocol trước fit và quyết định trước metric test. Baseline tự fit lại cho test 8.277/10.000; MLP chính 8.544/10.000, CE=0,4325136893348614. Chênh 267 ảnh khớp tham chiếu.
- Đã xem đủ 9 PNG 3840×2160: XOR, bước GD, backprop, kiến trúc, đường học, confusion, ảnh lỗi, một ảnh qua mạng và kết quả test.
- Lệnh suy luận bằng NPZ + ảnh NPY xuất ra lớp Shirt (6), khớp dự đoán khi huấn luyện; không cần fit lại.

Python 3.12.14, scikit-learn 1.6.1, Matplotlib 3.10.3. Kết quả trong `outputs/bai10/`. Ba seed chỉ mô tả độ nhạy; 50 epoch là ngân sách; test công khai đã từng được xem ở pilot. Không kết luận cho ảnh cửa hàng tùy ý.
