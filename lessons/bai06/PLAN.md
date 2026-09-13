# Kế hoạch Bài 06 — Cây quyết định

## 1. Rà soát

Đã đối chiếu 68 slide Bài 06 v2 và `tree_lab.py`. Tiếp tục Olist với đúng nhãn, sáu đặc trưng và split Bài 05; thay biểu diễn tuyến tính bằng chuỗi câu hỏi. Giữ các phản ví dụ về gain, overfitting và bất biến.

## 2. Các chặng và sản phẩm

| Chặng | Nội dung | Minh chứng |
|---|---|---|
| Dựng cây nhỏ | 12 đơn mô phỏng, quét mọi midpoint, Gini có trọng số | Bảng ứng viên, vùng quyết định, cây 3 lá |
| Đọc thuật toán | Duyệt cây tự viết, điểm lá từ tỷ lệ lớp | Đường đi từng nút và đối chiếu thư viện |
| Độ phức tạp | Moons có nhiễu, train/validation; cost-complexity | Hình vùng cây nông/sâu, đường accuracy, bảng pruning |
| Phản ví dụ | XOR gain đầu bằng 0; biến đổi bình phương | Kiểm thử và bảng mô phỏng |
| Olist thật | Cây sâu 3/6, lá tối thiểu 200; chọn AP validation | Bảng ứng viên, file toàn bộ nút, hình đầu cây |
| Chính sách/giải thích | Ngưỡng FP+5FN; MDI và permutation AP validation | Test, so logistic, đường đi đơn thật, tầm quan trọng |

## 3. Quy ước khoa học

Gain cục bộ nhân tỷ lệ số mẫu nút khi cộng cho toàn cây. Điểm lá là tỷ lệ nhãn train trong lá, chưa chắc đã hiệu chuẩn. `predict` của sklearn xử lý hòa khác quy tắc p >= 0,5; viết rõ quy tắc đang dùng. Cây Olist giữ scale để tái lập pilot; cây không cần scale theo cùng lý do như kNN, nhưng triển khai số và midpoint không bảo đảm bất biến trên mọi điểm mới. Permutation đo mức giảm AP trên validation, độ lệch chuẩn qua năm lần không phải khoảng tin cậy.

## 4–6. Kiểm chứng và hoàn tất

Đối chiếu gain 0,25 và 0,375; tổng có trọng số = 0,5; cây nhỏ 3 lá/5 nút. Kiểm duyệt toàn test so sklearn, tần suất lá, MDI, pruning, XOR và phản ví dụ. Real chọn độ sâu 6 và ngưỡng 0,10; test TN/FP/FN/TP = 34.659/2.129/3.046/432. Viết hướng dẫn từng bước, xem mọi PNG 3840 × 2160, lưu xác nhận hoàn tất trước khi sang Bài 07.
