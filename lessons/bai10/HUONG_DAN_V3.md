# Bài 10 · Lộ trình thực hành v3

[Hướng dẫn chi tiết](README.md) · [Đọc trước](../../readings/bai10/README.md) · [Toàn bộ cập nhật](../../docs/PYTHON_V3.md)

**Từ một đường gradient đến học biểu diễn.** Tài liệu đọc trước v3; đối chiếu slide **v3**. Lộ trình cơ bản dự kiến 35–50 phút, tùy tốc độ người học. Không cần chạy dữ liệu thật để hoàn thành ví dụ nhỏ.

## 1. Dự đoán trước khi chạy

Vì sao gradient của w₁₁ cần nhân với x₁ và v₁? Giá trị cập nhật là bao nhiêu?

Ghi câu trả lời bằng số và một câu giải thích. Chưa mở đáp án bên dưới; mục tiêu là kiểm cách hiểu, không chỉ chép đầu ra.

## 2. Chạy ví dụ nhỏ

Chạy từ thư mục gốc repository, sau khi cài thư viện theo README chung:

```bash
python -m lessons.bai10.main --mode toy --output-dir outputs/v3_toy/bai10
```

PNG mặc định 3840×2160. Công thức trong hình dùng Matplotlib mathtext; nguồn Markdown dùng LaTeX. `--dpi 80` dùng xem thử nhanh, không phải bản 4K.

## 3. Đọc theo ba chặng

### 1. Forward

Tính a, ReLU thành h, score s rồi xác suất p.

```math
s=v^Th+b,\ p=\sigma(s)
```

### 2. Backprop

Đi ngược theo một đường, dùng các trọng số cũ.

```math
\partial L/\partial w_{11}=\delta v_1 1_{a_1>0}x_1
```

### 3. Cập nhật và kiểm

η=0,1: w₁₁ từ 0,5 thành 0,518865; chọn checkpoint bằng validation.

```math
w\leftarrow w-\eta g
```

![Tổng kết thực hành Bài 10](../../docs/figures/v3/bai10_summary.png)

![Minh họa tính từng bước Bài 10](../../docs/figures/v3/bai10_toy_backprop_path.png)

## 4. Mở đúng đầu ra

Các tệp nằm trong thư mục `--output-dir` của lần chạy. Tên bắt đầu `toy_` thuộc ví dụ nhỏ; `real_` thuộc thí nghiệm thật. `results.json` lưu số liệu và cấu hình phiên bản.

- `toy_backprop_path.png`
- `toy_backprop.png`
- `toy_backprop.csv`

- `summary_v3.png`: tổng kết ví dụ chuẩn và giới hạn diễn giải.

## 5. Đối chiếu và giải thích

<details>
<summary>Mở sau khi đã tự tính</summary>

Đó là các đạo hàm cục bộ dọc đường w₁₁→a₁→h₁→s→L. Gradient≈−0,188654; w mới≈0,518865.

</details>

**Điều cần mang theo:** Backprop tính gradient; GD hoặc Adam dùng gradient để cập nhật. Test không dùng chọn checkpoint.

Bài nộp ngắn: ghi cấu hình đã chạy, một kết quả tính tay khớp mã, một hình kèm lời giải thích và một điều kết quả chưa chứng minh. Khi số khác, kiểm dữ liệu, seed, tham số, mẫu số và quy tắc làm tròn trước khi kết luận mã sai.

## 6. Nối với slide và tài liệu đọc trước

| Slide | Điểm bắt đầu | Điểm kết thúc |
|---|---|---|
| 8–30 | XOR: bốn điểm, một khó khăn thật rõ | Tổng kết · Forward rồi cập nhật |
| 32–45 | Bây giờ cho phép lớp ẩn thay đổi | Tổng kết · Thuật toán huấn luyện MLP |
| 46–63 | Cố định thí nghiệm trước khi đọc kết quả | Bài 10 · Từ biểu diễn đến bằng chứng |

Các số slide ở bảng trên thuộc phiên bản đã ghi ở đầu hướng dẫn. `teaching.json` lưu mã SHA256 của danh mục slide dùng đối chiếu; không lấy số slide v2 thay cho v3.

## 7. Mở rộng sang dữ liệu thật

Chuẩn bị đúng dữ liệu theo [README của bài](README.md), rồi chạy:

```bash
python -m lessons.bai10.main --mode all --output-dir outputs/v3/bai10
```

Đọc ví dụ trước, chạy cấu hình chuẩn sau; cuối cùng mới thay một yếu tố và lưu sang thư mục khác. Giữ nguyên tập chấm khi so mô hình; chọn cấu hình trên validation, không chọn lại bằng test. Với phân tích mô tả ở Bài 1 và 8, giới hạn kết luận ở snapshot và cách biểu diễn đã dùng.

Phần tính tay và giải thích hình là yêu cầu cơ bản. Vét cạn, chứng minh, nhiều seed, nested CV và các kiểm tra thư viện sâu là phần mở rộng phù hợp từng bài. Bài 10 mặc định chạy 3 seed × 50 epoch trên CPU; không coi cấu hình chạy nhanh là phép tái lập đầy đủ.
