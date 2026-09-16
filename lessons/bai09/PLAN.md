> Kế hoạch gốc của phiên bản trước. Kế hoạch đối chiếu hiện tại: [Hướng dẫn v3](HUONG_DAN_V3.md) và [phạm vi cập nhật](../../docs/PYTHON_V3.md).

# Kế hoạch Bài 09 — PCA và biểu diễn ảnh

Nguồn chuẩn: 60 slide Bài09_v2, pca_lab.py và case_audit.json. Tiếp nối hình học của Bài 08; kết nối ảnh Fashion-MNIST với Bài 10.

| Bước | Việc làm | Đầu ra/điều kiện |
|---|---|---|
| 1. Rà soát | Định tâm, ràng buộc trực chuẩn, phương sai/projection/reconstruction, 1/n so với 1/(n−1), MSE theo điểm và tọa độ | Công thức nhất quán; xác định split gốc |
| 2. Kế hoạch | Lưu trước triển khai; toy 4 điểm và phản ví dụ mất nhãn; Fashion 12.000 train/3.000 validation | Tài liệu này |
| 3. Xây dựng | Đọc IDX gốc; truy vết ảnh và nhãn; PCA full SVD train; EVR; k90; tái tạo k=2,16,64,128; logistic pixel và PCA64 | Python, model số NPZ, CSV, JSON và PNG |
| 4. Kiểm tra | Trực chuẩn, đổi dấu, bảo toàn năng lượng, residual bằng tổng trị riêng bỏ; tách train/validation; kiểm nội dung trùng; đối chiếu sklearn | unittest và assertions dữ liệu thật |
| 5. Sư phạm | Hình phép chiếu, đường phương sai/sai số theo góc, ảnh gốc/khôi phục, biểu đồ EVR, so sánh phân loại; quiz có giải thích | README và PNG 3840×2160 |
| 6. Hoàn tất | Chạy đủ, xem hình và lưu VALIDATION trước Bài 10 | Không tính metric test trong Bài 09 |

Giữ split seed 42 và phép chia 255; cho phép --seed thay split có ghi rõ. Pixel cùng đơn vị là lựa chọn thiết kế; không nói rằng chuẩn hóa luôn sai. PCA không dùng nhãn; nhãn chỉ dùng để minh họa/đánh giá sau. 45.000 ảnh train chính thức còn lại không dùng trong thí nghiệm giảng dạy. MSE trên số thực chưa clip; clip chỉ cho hình và chỉ số phụ có tên riêng.
