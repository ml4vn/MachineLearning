> Kế hoạch gốc của phiên bản trước. Kế hoạch đối chiếu hiện tại: [Hướng dẫn v3](HUONG_DAN_V3.md) và [phạm vi cập nhật](../../docs/PYTHON_V3.md).

# Kế hoạch Bài 03 — Đánh giá bộ phân loại

## 1. Rà soát bài giảng

Đối chiếu 64 slide `Bai03_v2`, mã `metrics_lab.py` và `case_audit.json`. Nối với Bài 02 bằng cùng SMS, đặc trưng, loại trùng và phân chia. Mô hình tham chiếu cố định StandardScaler fit train + kNN(11); bài này tập trung đánh giá, không chọn lại mô hình bằng test.

## 2. Nội dung và sản phẩm dự kiến

| Chặng | Thực hành | Sản phẩm kiểm được |
|---|---|---|
| Nhãn → quyết định | 10 điểm mô phỏng; ngưỡng 0,50/0,85/0,90 | Bảng từng dòng, ma trận nhầm lẫn |
| Quyết định → chỉ số | Đếm TN/FP/FN/TP, accuracy, precision, recall, F1 | Hàm tự viết và đối chiếu sklearn |
| Xếp hạng | AUC bằng cặp dương/âm, xử lý điểm bằng nhau; AP | Hình ROC/PR, số liệu CSV |
| Chọn ngưỡng | Quét số phiếu spam tối thiểu 1…12 trên validation | Hai chính sách chi phí 5FP+FN và FP+5FN |
| Đánh giá thực | Áp dụng chính sách đã khóa vào test SMS | Bảng chi phí, ma trận, ví dụ SMS sai |
| Tự kiểm tra | Precision không đơn điệu, chỉ số không xác định | Kiểm thử và bài tập có gợi ý đáp án |

## 3. Quy ước khoa học

- Spam là lớp dương; hàng là nhãn thật, cột là dự đoán. Ngưỡng dùng `score >= t`.
- Không dự đoán dương thì precision không xác định: JSON ghi `null`, không diễn giải giá trị quy ước 0 thành đo lường thực.
- Quét ngưỡng trên validation; hòa chi phí thì chọn ít cảnh báo hơn, rồi ngưỡng lớn hơn. m=12 tương ứng không cảnh báo. Mô hình có đúng 11 phiếu nên dùng số nguyên tránh lỗi biên số thực.
- Chi phí chỉ là giả định giảng dạy; test là holdout lịch sử đã dùng trong Bài 02. AP không bằng diện tích hình thang PR nói chung. Tỷ lệ phiếu chưa chứng minh hiệu chuẩn.

## 4–6. Kiểm chứng và hoàn thiện

Chạy ví dụ nhỏ, kiểm thử trường hợp biên và đối chiếu sklearn; chạy lại dữ liệu gốc; đối chiếu ma trận 892–12–17–111, ngưỡng 8/4 phiếu và chi phí test 56/93. Viết README đủ bước chạy, bài tập và giới hạn; xem từng hình PNG 3840 × 2160 rồi mới ghi hoàn tất và sang Bài 04.
