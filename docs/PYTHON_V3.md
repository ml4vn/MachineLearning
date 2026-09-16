# Đồng bộ Python với slide và tài liệu đọc trước

Ngày cập nhật: 16/09/2026. Bài 1–6 và 8–10 đối chiếu slide v3; Bài 7 đối chiếu slide v2 hiện có và tài liệu đọc trước v3.

## Phạm vi thực hiện

Giữ nguyên thuật toán trong `lessons/bai*/algorithms.py`, dữ liệu gốc, cách chia tập, seed và quy trình chọn mô hình đã kiểm chứng. Cập nhật ví dụ, hình, ký hiệu và hướng dẫn thực hành. Mỗi bài có `HUONG_DAN_V3.md`, nguồn `teaching.json`, ba chặng học, câu hỏi trước khi chạy, đáp án giải thích và `summary_v3.png` được sinh khi chạy bài.

| Bài | Điểm đồng bộ chính |
|---|---|
| 1 | Nối nhãn → vector → cosine → giới hạn; phân biệt ba trục tính tay với 19 nhãn thật |
| 2 | Nối đếm ký tự → khoảng cách → bỏ phiếu; nhấn mạnh dùng chung scaler train |
| 3 | Ngưỡng ví dụ chuẩn 0,80 thay 0,85; giữ nguyên điểm 0,85 của tin C; đối chiếu thay đổi FP/FN |
| 4 | Bổ sung một bước cập nhật đồng thời w,b, mặt 3D và đường đồng mức; thống nhất e = dự đoán − thực tế |
| 5 | Nối sigmoid/BCE/GD với quyết định; phân biệt K chi phí với C của regularization |
| 6 | Bổ sung Gini từ đếm lớp, đồ thị p và trọng số hai nhánh; dẫn sang CART, số lá và cắt tỉa |
| 7 | Phân tầng phần cơ bản và mở rộng; giữ đúng nguồn slide v2, nhấn thời điểm nhãn khả dụng |
| 8 | Thống nhất r → u → x và μ tâm cụm; bổ sung tính silhouette từ bốn điểm |
| 9 | Bổ sung hình covariance → hướng riêng; phân biệt score/tái tạo và mẫu số n với n−1 |
| 10 | Bổ sung một đường gradient w11; đối chiếu tên tham số slide với mã, rồi mới đọc toàn bộ chín gradient |

## Tương thích kết quả

Bài 4 bổ sung cột `error_prediction_minus_actual` và dùng cột này để vẽ hình. Cột cũ `residual_actual_minus_prediction` vẫn được giữ để các tệp phân tích trước tiếp tục đọc được. Hai cột ngược dấu; mô hình và dự đoán không đổi.

Bài 10 bổ sung `slide_parameter` trong bảng backprop, giữ cột `parameter` và thứ tự tham số cũ. Hàm thuật toán giữ giao diện cũ; hướng dẫn ánh xạ rõ ký hiệu. Hình tổng kết dùng ví dụ chuẩn của bài, không đại diện kết quả mới khi người học tự đổi tham số.

Các hình được sinh từ chương trình ở 3840×2160 theo cấu hình mặc định; chỉ đưa 16 hình xem trước vào hướng dẫn GitHub, không commit toàn bộ output dữ liệu lớn. Chạy bài để tái tạo PNG, CSV và JSON. Số hình của gói `--mode all` hiện là 71; bộ kiểm tham chiếu được cập nhật tương ứng.

## Kiểm tra và tái tạo

```bash
python tools/build_lab_guides.py --check
python tools/build_readings.py --check
python tools/check_course.py
python run_tests.py
python run_all.py --mode all --output-dir outputs/v3
python validate_outputs.py --output-dir outputs/v3 --report outputs/v3/validation.json
python tools/check_v3_examples.py --output-dir outputs/v3 --report outputs/v3/examples_validation.json
```

`validate_outputs.py` dành cho cấu hình mặc định. Báo cáo kết quả thực chạy và phạm vi kiểm hình được lưu trong [biên bản v3](KIEM_TRA_PYTHON_V3.md).
