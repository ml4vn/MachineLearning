> Kế hoạch gốc của phiên bản trước. Kế hoạch đối chiếu hiện tại: [Hướng dẫn v3](HUONG_DAN_V3.md) và [phạm vi cập nhật](../../docs/PYTHON_V3.md).

# Kế hoạch Bài 05 — Logistic Regression

## 1. Rà soát

Đã đối chiếu 68 slide Bài 05 v2, `logistic_lab.py` và quy trình Olist thống nhất. Giữ mạch Bài 04 nhưng đổi câu hỏi từ số ngày giao thành công sang xác suất giao trễ theo ngày lịch.

## 2. Nội dung thực hành

| Chặng | Nội dung | Kết quả |
|---|---|---|
| Dự đoán | Điểm tuyến tính → sigmoid → ngưỡng; odds/log-odds | Hình sigmoid và quyết định |
| Học | BCE ổn định từ logit; gradient; bốn hàng mô phỏng | Bảng tính, lịch sử 20 bước, hình loss |
| Đối chiếu mở rộng | 19 quan sát gộp có nghiệm xác định | Kiểm score equation, Hessian và sklearn không phạt |
| Dữ liệu thật | ZIP Olist → nhãn ngày lịch, split cố định, sáu đặc trưng | Bảng đầu vào có ID và báo cáo chuẩn bị |
| Mô hình | Impute/scale train; newton-cg, L2, C=1 | Hệ số chuẩn hóa và hệ gốc, đóng góp từng đặc trưng |
| Chính sách | Grid validation, chi phí FP+5FN; test sau khóa | Ma trận trước/sau, Brier/BCE, phân bố điểm |

## 3. Các điểm cần giữ đúng

Ngày giao cùng ngày hứa vẫn đúng hạn dù muộn hơn giờ 00:00. Logistic có đầu ra xác suất mô hình, không tự bảo đảm calibration. Thay ngưỡng chỉ thay quyết định, không đổi BCE/Brier khi giữ điểm. C là nghịch đảo độ mạnh regularization, không phải eta. Ví dụ bốn hàng phân tách hoàn toàn không có MLE hữu hạn khi không phạt. Mở rộng 19 hàng có nhãn lẫn trong nhóm và Hessian xác định dương.

## 4–6. Kiểm chứng và hoàn tất

Kiểm sigmoid cực trị, gradient bằng sai phân, bước đầu b = 0 và w = 0,5, đối chiếu log-loss và nghiệm gộp; chạy real từ raw. Ngưỡng 0,10 có test TN/FP/FN/TP = 36.429/359/3.317/161; cost 16.944. Viết README dẫn dắt, bài tập/đáp án và giới hạn; kiểm trực quan mọi hình rồi mới sang Bài 06.
