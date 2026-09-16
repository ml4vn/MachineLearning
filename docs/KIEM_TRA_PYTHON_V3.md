# Kiểm tra Python thực hành v3

Ngày kiểm tra: 16/09/2026. Đã chạy đủ ví dụ nhỏ và thí nghiệm thật của Bài 1–10 trên dữ liệu có checksum, seed 42 và cấu hình mặc định.

## Kết quả

- 60/60 kiểm thử thuật toán và trường hợp biên đạt.
- 107/107 điều kiện kiểm đầu ra đạt, gồm đủ 71 PNG kích thước 3840×2160 và các mốc số liệu thật.
- 22/22 điều kiện đối chiếu ví dụ mới và đầu ra trong hướng dẫn đạt.
- Giữ nguyên cả 10 tệp algorithms.py so với phiên bản trước cập nhật.
- Đã xem 16 hình mới và 5 hình cũ có thay đổi ký hiệu/chú thích/dấu sai số; sửa vị trí chữ Gini và nhãn đạo hàm trên đường backprop.
- 16 hình xem trước đã đưa vào hướng dẫn Markdown; hình được sao chép từ kết quả chạy.

## Từng bài

| Bài | Chạy all | Thời gian (giây) |
|---|---|---:|
| 1 | Đạt | 27.14 |
| 2 | Đạt | 27.51 |
| 3 | Đạt | 24.48 |
| 4 | Đạt | 62.89 |
| 5 | Đạt | 67.98 |
| 6 | Đạt | 82.60 |
| 7 | Đạt | 78.37 |
| 8 | Đạt | 204.77 |
| 9 | Đạt | 137.61 |
| 10 | Đạt | 265.96 |

Bài 8 từng dừng ở cú pháp phân số của hình mới; đã sửa, chạy lại Bài 8–10 đầy đủ và đạt. Bài 1–7 không cần huấn luyện lại sau sửa lỗi biểu diễn đó. Các hình tổng kết được kết xuất lại sau chỉnh chú thích, không thay kết quả mô hình.

## Mốc đối chiếu

Bài 3 giữ confusion test (TN,FP,FN,TP)=(892,12,17,111). Bài 4 giữ hệ số OLS và GD gần OLS; hai cột sai số ngược dấu được kiểm trên mọi dòng test. Bài 5 giữ chi phí test 16.944; Bài 6 giữ 17.359 và suy luận thủ công khớp toàn test. Bài 8 giữ SSE K=4 bằng 3924,4596992758034. Bài 9 giữ k90=82 và chỉ đánh giá validation. Bài 10 chạy 3×50 epoch, chọn checkpoint 40/27/40; test baseline 8.277/10.000 và MLP chính 8.544/10.000 như mốc đã duyệt.

## Tái tạo và bằng chứng

Xem [quy trình tái tạo](PYTHON_V3.md), [biên bản máy đọc được](python_v3_validation.json), [107 kiểm đầu ra](python_v3_output_checks.json) và [22 kiểm ví dụ](python_v3_example_checks.json).

Các biên bản VALIDATION cũ của từng bài vẫn được giữ với nhãn lịch sử. Bài 7 chưa có slide v3 nên tiếp tục đối chiếu slide v2 và tài liệu đọc trước v3. Kết quả trên không phải bằng chứng về khả năng tổng quát ngoài dữ liệu đã dùng.
