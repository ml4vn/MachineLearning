# Bài 4 · Lộ trình thực hành v3

[Hướng dẫn chi tiết](README.md) · [Đọc trước](../../readings/bai04/README.md) · [Toàn bộ cập nhật](../../docs/PYTHON_V3.md)

**Học w và b từ sai số.** Tài liệu đọc trước v3; đối chiếu slide **v3**. Lộ trình cơ bản dự kiến 35–50 phút, tùy tốc độ người học. Không cần chạy dữ liệu thật để hoàn thành ví dụ nhỏ.

## 1. Dự đoán trước khi chạy

Có được dùng w mới để tính g_b trong cùng một bước GD không? Tại sao?

Ghi câu trả lời bằng số và một câu giải thích. Chưa mở đáp án bên dưới; mục tiêu là kiểm cách hiểu, không chỉ chép đầu ra.

## 2. Chạy ví dụ nhỏ

Chạy từ thư mục gốc repository, sau khi cài thư viện theo README chung:

```bash
python -m lessons.bai04.main --mode toy --output-dir outputs/v3_toy/bai04
```

PNG mặc định 3840×2160. Công thức trong hình dùng Matplotlib mathtext; nguồn Markdown dùng LaTeX. `--dpi 80` dùng xem thử nhanh, không phải bản 4K.

## 3. Đọc theo ba chặng

### 1. Khởi tạo

Bốn điểm (1,3), (2,4), (3,6), (4,7); w=0,5 và b=1.

```math
\hat y=wx+b
```

### 2. Tính cùng điểm cũ

Dùng e = dự đoán − thực tế; g_w=−8, g_b=−2,75.

```math
J=\frac{1}{2n}\sum_i e_i^2
```

### 3. Cập nhật và lặp

η=0,05 cho w mới 0,9 và b mới 1,1375.

```math
\theta\leftarrow\theta-\eta\nabla J
```

![Tổng kết thực hành Bài 4](../../docs/figures/v3/bai04_summary.png)

![Minh họa tính từng bước Bài 4](../../docs/figures/v3/bai04_toy_wb_update.png)

![Minh họa tính từng bước Bài 4](../../docs/figures/v3/bai04_toy_loss_surface.png)

## 4. Mở đúng đầu ra

Các tệp nằm trong thư mục `--output-dir` của lần chạy. Tên bắt đầu `toy_` thuộc ví dụ nhỏ; `real_` thuộc thí nghiệm thật. `results.json` lưu số liệu và cấu hình phiên bản.

- `toy_wb_update.png`
- `toy_loss_surface.png`
- `toy_wb_history.csv`

- `summary_v3.png`: tổng kết ví dụ chuẩn và giới hạn diễn giải.

## 5. Đối chiếu và giải thích

<details>
<summary>Mở sau khi đã tự tính</summary>

Không với GD đồng thời: cả hai gradient phải được tính tại cùng (w,b) cũ. Sau đó mới cập nhật cả hai.

</details>

**Điều cần mang theo:** Một điểm (w,b) là một mô hình. Mặt 3D và đường đồng mức mô tả cùng hàm J.

Bài nộp ngắn: ghi cấu hình đã chạy, một kết quả tính tay khớp mã, một hình kèm lời giải thích và một điều kết quả chưa chứng minh. Khi số khác, kiểm dữ liệu, seed, tham số, mẫu số và quy tắc làm tròn trước khi kết luận mã sai.

## 6. Nối với slide và tài liệu đọc trước

| Slide | Điểm bắt đầu | Điểm kết thúc |
|---|---|---|
| 21–32 | Kiểm tra 2 · Phân biệt J và MSE | Tổng kết · Một bước, hai cách nhìn |
| 35–46 | Nhiều bước cập nhật tạo thành một quá trình học | Vòng lặp GD nhìn thấy từng thao tác |
| 50–65 | Trở lại câu hỏi thời gian giao hàng | Tổng quan · Một đường học từ sai số |

Các số slide ở bảng trên thuộc phiên bản đã ghi ở đầu hướng dẫn. `teaching.json` lưu mã SHA256 của danh mục slide dùng đối chiếu; không lấy số slide v2 thay cho v3.

## 7. Mở rộng sang dữ liệu thật

Chuẩn bị đúng dữ liệu theo [README của bài](README.md), rồi chạy:

```bash
python -m lessons.bai04.main --mode all --output-dir outputs/v3/bai04
```

Đọc ví dụ trước, chạy cấu hình chuẩn sau; cuối cùng mới thay một yếu tố và lưu sang thư mục khác. Giữ nguyên tập chấm khi so mô hình; chọn cấu hình trên validation, không chọn lại bằng test. Với phân tích mô tả ở Bài 1 và 8, giới hạn kết luận ở snapshot và cách biểu diễn đã dùng.

Phần tính tay và giải thích hình là yêu cầu cơ bản. Vét cạn, chứng minh, nhiều seed, nested CV và các kiểm tra thư viện sâu là phần mở rộng phù hợp từng bài. Bài 10 mặc định chạy 3 seed × 50 epoch trên CPU; không coi cấu hình chạy nhanh là phép tái lập đầy đủ.
