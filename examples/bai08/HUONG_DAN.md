# Bài 8 · Lộ trình thực hành

[Hướng dẫn chi tiết](README.md) · [Đọc trước](../../readings/bai08/README.md) · [Kiểm tra học liệu](../../docs/MAINTAINING.md)

**Biểu diễn RFM rồi mới gom cụm.** Lộ trình ví dụ nhỏ dự kiến 35–50 phút. Không cần dữ liệu thật để hoàn thành ví dụ nhỏ.

## 1. Dự đoán trước khi chạy

Với cụm {0,2} và {10,12}, hãy tính a, b và silhouette của điểm 2.

Ghi câu trả lời bằng số và một câu giải thích. Chưa mở đáp án bên dưới; mục tiêu là kiểm cách hiểu, không chỉ chép đầu ra.

## 2. Chạy ví dụ nhỏ

Chạy từ thư mục gốc repository, sau khi cài thư viện theo README chung:

```bash
python -m examples.bai08.main --mode toy --output-dir outputs/toy/bai08
```

PNG mặc định 3840×2160. Công thức trong hình dùng Matplotlib mathtext; nguồn Markdown dùng LaTeX. `--dpi 80` dùng xem thử nhanh, không phải bản 4K.

## 3. Đọc theo ba chặng

### 1. Tạo tọa độ

r là RFM thô; u=log(1+r); x là u đã chuẩn hóa.

```math
r\to u\to x
```

### 2. Lặp hai bước

Giữ tâm để gán cụm; giữ nhãn để tính trung bình cụm.

```math
J=\sum_i\|x_i-\mu_{c_i}\|^2
```

### 3. Đọc chất lượng

Silhouette so gần trong cụm với xa tới cụm khác; không phải accuracy.

```math
s(i)=(b(i)-a(i))/\max(a(i),b(i))
```

![Tổng kết thực hành Bài 8](../../docs/figures/illustrations/bai08_summary.png)

![Minh họa tính từng bước Bài 8](../../docs/figures/illustrations/bai08_toy_silhouette.png)

## 4. Mở đúng đầu ra

Các tệp nằm trong thư mục `--output-dir` của lần chạy. Tên bắt đầu `toy_` thuộc ví dụ nhỏ; `real_` thuộc thí nghiệm thật. `results.json` lưu số liệu và cấu hình phiên bản.

- `toy_half_steps.png`
- `toy_silhouette.png`
- `toy_lloyd_history.json`

- `summary.png`: tổng kết ví dụ chuẩn và giới hạn diễn giải.

## 5. Đối chiếu và giải thích

<details>
<summary>Mở sau khi đã tự tính</summary>

a=2; b=(8+10)/2=9; silhouette=(9−2)/9=7/9≈0,777778.

</details>

**Điều cần mang theo:** μ chỉ tâm cụm; trung bình và độ lệch chuẩn tiền xử lý là m và s. SSE khác hệ tọa độ không so trực tiếp.

Bài nộp ngắn: ghi cấu hình đã chạy, một kết quả tính tay khớp mã, một hình kèm lời giải thích và một điều kết quả chưa chứng minh. Khi số khác, kiểm dữ liệu, seed, tham số, mẫu số và quy tắc làm tròn trước khi kết luận mã sai.

## 6. Nối với slide và tài liệu đọc trước

| Slide | Điểm bắt đầu | Điểm kết thúc |
|---|---|---|
| 5–20 | Bốn dòng mua của khách 12755 | Biểu diễn quyết định cách đo gần |
| 22–40 | K và tâm cụm | Câu 4 · Dừng và tối ưu |
| 44–55 | Silhouette: gần nhóm mình, xa nhóm khác | Đánh giá và lựa chọn số cụm |

Bảng đối chiếu giúp giảng viên nối ví dụ với nội dung giảng dạy; repository không phân phối PowerPoint.

## 7. Mở rộng sang dữ liệu thật

Chuẩn bị đúng dữ liệu theo [README của bài](README.md), rồi chạy:

```bash
python -m examples.bai08.main --mode all --output-dir outputs/bai08
```

Đọc ví dụ trước, chạy cấu hình chuẩn sau; cuối cùng mới thay một yếu tố và lưu sang thư mục khác. Giữ nguyên tập chấm khi so mô hình; chọn cấu hình trên validation, không chọn lại bằng test. Với phân tích mô tả ở Bài 1 và 8, giới hạn kết luận ở snapshot và cách biểu diễn đã dùng.

Phần tính tay và giải thích hình là yêu cầu cơ bản. Vét cạn, chứng minh, nhiều seed, nested CV và các kiểm tra thư viện sâu là phần mở rộng phù hợp từng bài. Bài 10 mặc định chạy 3 seed × 50 epoch trên CPU; không coi cấu hình chạy nhanh là phép tái lập đầy đủ.
