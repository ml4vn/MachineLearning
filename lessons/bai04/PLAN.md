# Kế hoạch Bài 04 — Hồi quy tuyến tính và Gradient Descent

## 1. Đối chiếu bài giảng

Đã rà soát 68 tiêu đề slide v2, `lab_bai04.py`, kiểm định toán `audit_science.py`, số liệu `olist_pilot.json` và quy trình ghép Olist gốc dùng trong khóa học. Giữ câu hỏi: tại thời điểm duyệt đơn, ước lượng bao nhiêu ngày đến khi giao thành công?

## 2. Các chặng thực hành

| Chặng | Nội dung chính | Sản phẩm |
|---|---|---|
| Mô hình | Đường thẳng, b và w, đơn vị x/y | Hình bốn điểm mô phỏng và residual |
| Hàm mất mát | J = MSE/2, sai số có dấu | Bảng từng dòng, đồ thị loss |
| Thuật toán | Gradient, cập nhật một/hai tham số, learning rate | Lịch sử CSV, quỹ đạo GD và loss |
| Dữ liệu thật | Sáu bảng Olist → một dòng/đơn; nhãn và split thời gian | Loader từ ZIP, bảng đã chuẩn bị, báo cáo lọc/thiếu |
| Huấn luyện | Median và StandardScaler chỉ fit train; GD so với OLS | Hệ số, loss, dự đoán từng đơn |
| Đánh giá | Mean/median baseline, OLS 1/6 đặc trưng; MAE/RMSE | Biểu đồ test, residual, bảng so sánh |

## 3. Rà soát khoa học

Đơn vị khoảng cách thật km; ví dụ nhỏ dùng đơn vị 100 km. Thời gian giao tính số giây/86400, không làm tròn ngày. Giữ trung tâm y=5 chỉ là bài toán một tham số đã căn giữa; chương trình thật cập nhật đồng thời b,w từ gradient tại cùng tham số cũ. Khoảng 0 < eta < 1,6 chỉ áp dụng bài toán một tham số cụ thể. Chuẩn hóa không đổi nghiệm OLS khi đổi hệ số về đúng đơn vị.

Khoảng cách là trung bình khoảng cách đường chim bay từ tâm mã bưu chính của từng người bán đến khách. Giữ quy tắc trọng lượng thiếu cộng thành 0 của pilot để đối chiếu, nhưng báo rõ đó không phải phép đo khối lượng bằng 0. Chỉ dùng đơn giao thành công và nhãn quan sát được trước các mốc chia; phải trình bày rủi ro chọn mẫu và snapshot tĩnh.

## 4–6. Điều kiện hoàn tất

Kiểm gradient bằng sai phân hữu hạn, đối chiếu nghiệm giải tích/sklearn, kiểm khoảng learning rate và MAE/RMSE. Dựng bảng từ dữ liệu gốc, đối chiếu 29.031/10.389/40.266 đơn, OLS một biến có MAE 5,939645 và RMSE 9,351536. Viết hướng dẫn và câu hỏi tự kiểm; xem toàn bộ hình 3840 × 2160, ghi kiểm định rồi mới chuyển Bài 05.
