# Bài 7 · Lộ trình thực hành

[Hướng dẫn chi tiết](README.md) · [Đọc trước](../../readings/bai07/README.md) · [Kiểm tra học liệu](../../docs/MAINTAINING.md)

**Đánh giá cả quy trình học.** Lộ trình ví dụ nhỏ dự kiến 35–50 phút. Không cần dữ liệu thật để hoàn thành ví dụ nhỏ.

## 1. Dự đoán trước khi chạy

Đơn được duyệt trước mốc chia nhưng chỉ giao xong sau mốc có nhãn để huấn luyện tại mốc đó chưa?

Ghi câu trả lời bằng số và một câu giải thích. Chưa mở đáp án bên dưới; mục tiêu là kiểm cách hiểu, không chỉ chép đầu ra.

## 2. Chạy ví dụ nhỏ

Chạy từ thư mục gốc repository, sau khi cài thư viện theo README chung:

```bash
python -m examples.bai07.main --mode toy --output-dir outputs/toy/bai07
```

PNG mặc định 3840×2160. Công thức trong hình dùng Matplotlib mathtext; nguồn Markdown dùng LaTeX. `--dpi 80` dùng xem thử nhanh, không phải bản 4K.

## 3. Đọc theo ba chặng

### 1. Chốt thời điểm

Chỉ dùng thông tin có sẵn khi cần dự đoán.

```math
t_{feature}\leq t_{prediction}
```

### 2. Tách vai trò

Train học tham số; validation chọn cấu hình; test báo kết quả.

```math
train\ \to\ validation\ \to\ test
```

### 3. Kiểm rò rỉ

Fit biến đổi trong từng fold, kiểm nhóm lặp và thời gian nhãn.

```math
fit(train),\ transform(test)
```

![Tổng kết thực hành Bài 7](../../docs/figures/illustrations/bai07_summary.png)

## 4. Mở đúng đầu ra

Các tệp nằm trong thư mục `--output-dir` của lần chạy. Tên bắt đầu `toy_` thuộc ví dụ nhỏ; `real_` thuộc thí nghiệm thật. `results.json` lưu số liệu và cấu hình phiên bản.

- `results.json`

- `summary.png`: tổng kết ví dụ chuẩn và giới hạn diễn giải.

## 5. Đối chiếu và giải thích

<details>
<summary>Mở sau khi đã tự tính</summary>

Chưa; thời điểm có đặc trưng và thời điểm nhãn khả dụng khác nhau. Cần kiểm cả hai.

</details>

**Điều cần mang theo:** Đánh giá cả quy trình học; nested CV và rolling CV là phần mở rộng.

Bài nộp ngắn: ghi cấu hình đã chạy, một kết quả tính tay khớp mã, một hình kèm lời giải thích và một điều kết quả chưa chứng minh. Khi số khác, kiểm dữ liệu, seed, tham số, mẫu số và quy tắc làm tròn trước khi kết luận mã sai.

## 6. Nối với slide và tài liệu đọc trước

| Slide | Điểm bắt đầu | Điểm kết thúc |
|---|---|---|
| 8–18 | Nhãn trễ và cột tạo nhãn | Q2 · Pipeline có cứu cột tương lai? |
| 19–28 | Vai trò train, validation, test | Tóm tắt trước giờ nghỉ |
| 30–47 | Chia Olist theo thời gian | Phiếu kiểm năm câu |

Bảng đối chiếu giúp giảng viên nối ví dụ với nội dung giảng dạy; repository không phân phối PowerPoint.

## 7. Mở rộng sang dữ liệu thật

Chuẩn bị đúng dữ liệu theo [README của bài](README.md), rồi chạy:

```bash
python -m examples.bai07.main --mode all --output-dir outputs/bai07
```

Đọc ví dụ trước, chạy cấu hình chuẩn sau; cuối cùng mới thay một yếu tố và lưu sang thư mục khác. Giữ nguyên tập chấm khi so mô hình; chọn cấu hình trên validation, không chọn lại bằng test. Với phân tích mô tả ở Bài 1 và 8, giới hạn kết luận ở snapshot và cách biểu diễn đã dùng.

Phần tính tay và giải thích hình là yêu cầu cơ bản. Vét cạn, chứng minh, nhiều seed, nested CV và các kiểm tra thư viện sâu là phần mở rộng phù hợp từng bài. Bài 10 mặc định chạy 3 seed × 50 epoch trên CPU; không coi cấu hình chạy nhanh là phép tái lập đầy đủ.
