# Bài 1 · Lộ trình thực hành v3

[Hướng dẫn chi tiết](README.md) · [Đọc trước](../../readings/bai01/README.md) · [Toàn bộ cập nhật](../../docs/PYTHON_V3.md)

**Biểu diễn quyết định độ gần.** Tài liệu đọc trước v3; đối chiếu slide **v3**. Lộ trình cơ bản dự kiến 35–50 phút, tùy tốc độ người học. Không cần chạy dữ liệu thật để hoàn thành ví dụ nhỏ.

## 1. Dự đoán trước khi chạy

Nhân vector phim tham chiếu với 3 có đổi cosine không? Vector 0 có được dùng không?

Ghi câu trả lời bằng số và một câu giải thích. Chưa mở đáp án bên dưới; mục tiêu là kiểm cách hiểu, không chỉ chép đầu ra.

## 2. Chạy ví dụ nhỏ

Chạy từ thư mục gốc repository, sau khi cài thư viện theo README chung:

```bash
python -m lessons.bai01.main --mode toy --output-dir outputs/v3_toy/bai01
```

PNG mặc định 3840×2160. Công thức trong hình dùng Matplotlib mathtext; nguồn Markdown dùng LaTeX. `--dpi 80` dùng xem thử nhanh, không phải bản 4K.

## 3. Đọc theo ba chặng

### 1. Mã hóa

Cùng thứ tự Action, Comedy, Sci-Fi cho mọi phim.

```math
u=(1,0,1),\ v=(1,1,1)
```

### 2. Tính cosine

Nhân cùng vị trí, cộng; chia cho tích hai chuẩn.

```math
\cos(u,v)=2/\sqrt{6}
```

### 3. Đọc giới hạn

Điểm khoảng 0,8165 đo độ giống theo nhãn đã chọn.

```math
\|u\|>0,\ \|v\|>0
```

![Tổng kết thực hành Bài 1](../../docs/figures/v3/bai01_summary.png)

## 4. Mở đúng đầu ra

Các tệp nằm trong thư mục `--output-dir` của lần chạy. Tên bắt đầu `toy_` thuộc ví dụ nhỏ; `real_` thuộc thí nghiệm thật. `results.json` lưu số liệu và cấu hình phiên bản.

- `toy_steps.csv`
- `real_movie_comparison.csv`

- `summary_v3.png`: tổng kết ví dụ chuẩn và giới hạn diễn giải.

## 5. Đối chiếu và giải thích

<details>
<summary>Mở sau khi đã tự tính</summary>

Hệ số dương 3 triệt tiêu giữa tử và mẫu; vector 0 không thỏa điều kiện của công thức.

</details>

**Điều cần mang theo:** Cosine không phải xác suất thích phim; đổi bộ nhãn có thể đổi thứ hạng.

Bài nộp ngắn: ghi cấu hình đã chạy, một kết quả tính tay khớp mã, một hình kèm lời giải thích và một điều kết quả chưa chứng minh. Khi số khác, kiểm dữ liệu, seed, tham số, mẫu số và quy tắc làm tròn trước khi kết luận mã sai.

## 6. Nối với slide và tài liệu đọc trước

| Slide | Điểm bắt đầu | Điểm kết thúc |
|---|---|---|
| 7–12 | Ba trục được chọn để tính bằng tay | Tổng kết · Nhãn phim thành vector |
| 13–35 | Một vector vừa là bảng số vừa là mũi tên | Tổng kết · Tính và đọc một điểm cosine |
| 37–56 | Nhân độ dài với số dương: cosine không đổi | Tổng quan · Biểu diễn quyết định cách so sánh |

Các số slide ở bảng trên thuộc phiên bản đã ghi ở đầu hướng dẫn. `teaching.json` lưu mã SHA256 của danh mục slide dùng đối chiếu; không lấy số slide v2 thay cho v3.

## 7. Mở rộng sang dữ liệu thật

Chuẩn bị đúng dữ liệu theo [README của bài](README.md), rồi chạy:

```bash
python -m lessons.bai01.main --mode all --output-dir outputs/v3/bai01
```

Đọc ví dụ trước, chạy cấu hình chuẩn sau; cuối cùng mới thay một yếu tố và lưu sang thư mục khác. Giữ nguyên tập chấm khi so mô hình; chọn cấu hình trên validation, không chọn lại bằng test. Với phân tích mô tả ở Bài 1 và 8, giới hạn kết luận ở snapshot và cách biểu diễn đã dùng.

Phần tính tay và giải thích hình là yêu cầu cơ bản. Vét cạn, chứng minh, nhiều seed, nested CV và các kiểm tra thư viện sâu là phần mở rộng phù hợp từng bài. Bài 10 mặc định chạy 3 seed × 50 epoch trên CPU; không coi cấu hình chạy nhanh là phép tái lập đầy đủ.
