# Bài 6 · Lộ trình thực hành

[Hướng dẫn chi tiết](README.md) · [Đọc trước](../../readings/bai06/README.md) · [Kiểm tra học liệu](../../docs/MAINTAINING.md)

**Từ đếm lớp đến một cây có kiểm soát.** Lộ trình ví dụ nhỏ dự kiến 35–50 phút. Không cần dữ liệu thật để hoàn thành ví dụ nhỏ.

## 1. Dự đoán trước khi chạy

Nút gốc có 6/12 đơn trễ. Sau chia: trái 4/4, phải 2/8. Tính Gini sau chia và mức giảm.

Ghi câu trả lời bằng số và một câu giải thích. Chưa mở đáp án bên dưới; mục tiêu là kiểm cách hiểu, không chỉ chép đầu ra.

## 2. Chạy ví dụ nhỏ

Chạy từ thư mục gốc repository, sau khi cài thư viện theo README chung:

```bash
python -m examples.bai06.main --mode toy --output-dir outputs/toy/bai06
```

PNG mặc định 3840×2160. Công thức trong hình dùng Matplotlib mathtext; nguồn Markdown dùng LaTeX. `--dpi 80` dùng xem thử nhanh, không phải bản 4K.

## 3. Đọc theo ba chặng

### 1. Đo mức lẫn

Tại mỗi nút, p là tỷ lệ lớp trễ; p=0,5 lẫn nhiều nhất.

```math
G=1-p^2-(1-p)^2
```

### 2. Chọn và lặp

Quét nhát cắt; chọn giảm Gini lớn nhất rồi lặp tại các nút con.

```math
\Delta G=G-\sum_c(n_c/n)G_c
```

### 3. Kiểm soát cây

So độ sâu hoặc cắt tỉa bằng validation; L(T) là tập các lá.

```math
R_\alpha(T)=R(T)+\alpha|L(T)|
```

![Tổng kết thực hành Bài 6](../../docs/figures/illustrations/bai06_summary.png)

![Minh họa tính từng bước Bài 6](../../docs/figures/illustrations/bai06_toy_gini_trace.png)

## 4. Mở đúng đầu ra

Các tệp nằm trong thư mục `--output-dir` của lần chạy. Tên bắt đầu `toy_` thuộc ví dụ nhỏ; `real_` thuộc thí nghiệm thật. `results.json` lưu số liệu và cấu hình phiên bản.

- `toy_gini_trace.png`
- `toy_tree.png`
- `toy_complexity.png`
- `toy_root_candidates.csv`

- `summary.png`: tổng kết ví dụ chuẩn và giới hạn diễn giải.

## 5. Đối chiếu và giải thích

<details>
<summary>Mở sau khi đã tự tính</summary>

Gốc 0,5; trái 0; phải 0,375. Sau chia = (4/12)×0+(8/12)×0,375=0,25; mức giảm=0,25.

</details>

**Điều cần mang theo:** CART tham lam tại từng nút; nhiều lá hơn chưa bảo đảm tốt hơn trên dữ liệu mới.

Bài nộp ngắn: ghi cấu hình đã chạy, một kết quả tính tay khớp mã, một hình kèm lời giải thích và một điều kết quả chưa chứng minh. Khi số khác, kiểm dữ liệu, seed, tham số, mẫu số và quy tắc làm tròn trước khi kết luận mã sai.

## 6. Nối với slide và tài liệu đọc trước

| Slide | Điểm bắt đầu | Điểm kết thúc |
|---|---|---|
| 13–20 | Gini: mức lẫn nhãn tại một nút | Tổng kết: cách tính và so sánh Gini |
| 21–34 | Q3 · Mẫu số và trọng số | CART chạy trên 12 đơn như thế nào? |
| 36–46 | Độ sâu, số lá và tổng số nút | Tổng kết: CART, độ phức tạp và cắt tỉa |
| 48–67 | Trở lại dữ liệu Olist: ba tập theo thời gian | Tổng quan Bài 6 |

Bảng đối chiếu giúp giảng viên nối ví dụ với nội dung giảng dạy; repository không phân phối PowerPoint.

## 7. Mở rộng sang dữ liệu thật

Chuẩn bị đúng dữ liệu theo [README của bài](README.md), rồi chạy:

```bash
python -m examples.bai06.main --mode all --output-dir outputs/bai06
```

Đọc ví dụ trước, chạy cấu hình chuẩn sau; cuối cùng mới thay một yếu tố và lưu sang thư mục khác. Giữ nguyên tập chấm khi so mô hình; chọn cấu hình trên validation, không chọn lại bằng test. Với phân tích mô tả ở Bài 1 và 8, giới hạn kết luận ở snapshot và cách biểu diễn đã dùng.

Phần tính tay và giải thích hình là yêu cầu cơ bản. Vét cạn, chứng minh, nhiều seed, nested CV và các kiểm tra thư viện sâu là phần mở rộng phù hợp từng bài. Bài 10 mặc định chạy 3 seed × 50 epoch trên CPU; không coi cấu hình chạy nhanh là phép tái lập đầy đủ.
