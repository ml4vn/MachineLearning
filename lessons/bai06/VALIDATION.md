# Hoàn tất Bài 06

Đã thực hiện đủ sáu bước. Sáu kiểm thử đơn vị đạt và lệnh `--mode all` chạy từ Olist gốc thành công.

- Cây mô phỏng: nhát cắt gốc hứa giao ≤ 15, gain 0,25; nhát cắt con khoảng cách ≤ 10, gain cục bộ 0,375; tổng theo toàn cây = 0,5. Cây đầy đủ có 3 lá/5 nút; MDI = [0,5;0,5].
- Pruning, XOR, trường hợp hòa lớp và phản ví dụ biến đổi bình phương đều qua kiểm thử.
- Validation AP chọn độ sâu 6; cấu hình mặc định có 23 lá/45 nút, ngưỡng 0,10.
- Test TN/FP/FN/TP = 34.659/2.129/3.046/432; cost FP+5FN = 17.359. Logistic tự fit đối chiếu có cost 16.944, khớp bài giảng.
- Duyệt cây tự viết so toàn bộ 40.266 dòng test với sklearn, dung sai tuyệt đối 1e-15. Tần suất từng lá, tổng gain và MDI được kiểm độc lập.
- Permutation AP validation qua năm lần khớp số tham chiếu. Các sai số hiển thị là SD hoán vị, không phải khoảng tin cậy.
- Đã xem bảy PNG 3840 × 2160. Chú thích cây phân biệt `value` dạng số lượng lớp trong hình với xác suất `p` trong tệp xuất nút.

Môi trường: Python 3.12.14, scikit-learn 1.6.1, Matplotlib 3.10.3. Kết quả và đường đi đơn thật ở `outputs/bai06/`.
