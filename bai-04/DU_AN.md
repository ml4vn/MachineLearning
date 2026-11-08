# Project Bài 4 · Dự báo số ngày giao hàng bằng Gradient Descent tự cài đặt

Học máy cơ bản · PGS.TS Nguyễn Văn Hậu · project độc lập của Bài 4

## Bài toán

Một sàn thương mại điện tử muốn báo cho người mua **số ngày dự kiến từ lúc xác nhận đơn đến lúc nhận hàng**. Bạn xây một mô hình hồi quy tuyến tính, **tự cài đặt Gradient Descent**, đánh giá đúng quy trình và viết kết luận có phạm vi. Đây là bài toán lịch sử trên dữ liệu Brazil; sản phẩm của bạn là một phân tích, chưa phải hệ thống hứa ngày giao.

## Dữ liệu

`data/prepared/olist_model_table.csv`: 79.686 đơn đã giao, mỗi dòng một đơn, đã chia theo thời điểm xác nhận: train 01–10/2017 (29.031 đơn), validation 11–12/2017 (10.389), test 01–06/2018 (40.266). Nguồn gốc: [Olist Brazilian E-Commerce, Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce); bảng đã chuẩn bị theo mã của bài giảng.

| Cột | Được làm đầu vào? | Lý do |
|---|---|---|
| `distance_km`, `price`, `freight_value`, `n_items`, `weight_g` | Có | Có sẵn lúc xác nhận đơn (giả định của case) |
| `promised_days` | Có, với giả định | Ngày giao dự kiến phải là bản đã có lúc xác nhận |
| `order_estimated_delivery_date` | Không dùng trực tiếp | Đã được dùng gián tiếp qua `promised_days` |
| `order_delivered_customer_date`, `late` | **Không** | Chỉ biết sau khi giao |
| `delivery_days` | Nhãn | Đại lượng cần dự đoán |
| `order_id`, `order_approved_at`, `split` | Không | Định danh, thời điểm, cột chia tập |

## Sáu bước

| Bước | Việc phải làm | Học ở |
|---|---|---|
| 1 | Định nghĩa bài toán; chọn ≥ 3 đặc trưng hợp lệ (có `distance_km`) | Chặng 1 |
| 2 | Mốc trung bình train; MAE, RMSE trên validation | Chặng 4 |
| 3 | GD hai tham số với khoảng cách chuẩn hoá theo train; thử 3 giá trị η trên train; đối chiếu nghiệm bình phương tối thiểu | Chặng 2–3 |
| 4 | GD dạng vector cho các đặc trưng đã chọn | Chặng 3 |
| 5 | So sánh trên validation, chọn một mô hình; chấm test **một lần**; vẽ phân phối sai số | Chặng 4 |
| 6 | Báo cáo một trang theo khung trong notebook | Chặng 4 |

## Ba mốc và ô tự kiểm

| Mốc | Bước | Ô tự kiểm trong notebook |
|---|---|---|
| M1 (sau buổi học) | 1–2 | Không dùng cột tương lai; MAE mốc trên validation ≈ 5,364 ngày |
| M2 | 3 | Một bước GD từ (0,5; 1) với η = 0,05 ra (0,9; 1,1375) như slide; GD khớp nghiệm với sai khác < 0,001 |
| M3 | 4–6 | GD vector khớp nghiệm; mô hình chọn là mô hình có MAE validation nhỏ nhất; `cham_test` được gọi đúng một lần |

Ô tự kiểm chỉ xác nhận phép tính. Diễn giải và giới hạn được chấm theo rubric.

## Ba mức

- **Cơ bản (tối đa 8/10):** bước 1–3, 5 và 6 với một đặc trưng (khoảng cách). Đặt `LAM_BUOC_4 = False` ở bước 4 để notebook vẫn chạy đến cuối.
- **Khá:** thêm bước 4 với ít nhất 3 đặc trưng.
- **Nâng cao (tuỳ chọn):** mini-batch GD và so sánh với GD toàn bộ train; hoặc phân tích MAE theo bốn nhóm khoảng cách trên validation.

## Sản phẩm nộp

1. `Bai04_Project_khoi_dau.ipynb` đã hoàn thành, chạy được từ đầu đến cuối (Kernel → Restart & Run All).
2. Báo cáo một trang (Markdown hoặc PDF) theo khung ở bước 6.
3. Một hình chính có trục, đơn vị và chú thích.

## Rubric 10 điểm

| Tiêu chí | Điểm |
|---|---:|
| Tái lập; đúng quy trình dữ liệu (fit trên train, đặc trưng hợp lệ) | 3 |
| Cài đặt GD đúng; đối chiếu nghiệm bình phương tối thiểu | 3 |
| Đánh giá đúng: mốc, chọn bằng validation, test một lần | 2 |
| Diễn giải có đơn vị, phạm vi và giới hạn | 2 |

## Quy tắc trung thực

- Không chọn η, đặc trưng hay mô hình dựa trên điểm test. Nếu đã xem test rồi đổi ý, ghi rõ trong báo cáo.
- Không dùng ngày giao thực tế hoặc nhãn trễ làm đầu vào.
- Ghi nguồn dữ liệu và mọi công cụ hỗ trợ đã dùng.
