# Bài 9 · Lộ trình thực hành

[Hướng dẫn chi tiết](README.md) · [Đọc trước](../../readings/bai09/README.md) · [Kiểm tra học liệu](../../docs/MAINTAINING.md)

**Định tâm, chiếu, rồi tái tạo.** Lộ trình ví dụ nhỏ dự kiến 35–50 phút. Không cần dữ liệu thật để hoàn thành ví dụ nhỏ.

## 1. Dự đoán trước khi chạy

Với x=(4,3), μ=(5,5), w=(1,1)/√2, score và điểm tái tạo là gì?

Ghi câu trả lời bằng số và một câu giải thích. Chưa mở đáp án bên dưới; mục tiêu là kiểm cách hiểu, không chỉ chép đầu ra.

## 2. Chạy ví dụ nhỏ

Chạy từ thư mục gốc repository, sau khi cài thư viện theo README chung:

```bash
python -m examples.bai09.main --mode toy --output-dir outputs/toy/bai09
```

PNG mặc định 3840×2160. Công thức trong hình dùng Matplotlib mathtext; nguồn Markdown dùng LaTeX. `--dpi 80` dùng xem thử nhanh, không phải bản 4K.

## 3. Đọc theo ba chặng

### 1. Học hướng từ train

Dời tâm; covariance đo biến thiên; eigenvector cho hướng chính.

```math
S=X_c^TX_c/n
```

### 2. Phân biệt đầu ra

Score là một số; tái tạo là một điểm trong không gian gốc.

```math
z=(x-\mu)^Tw
```

### 3. Đọc phần mất đi

Giữ 90% phương sai không có nghĩa accuracy 90%.

```math
\hat x=\mu+zw
```

![Tổng kết thực hành Bài 9](../../docs/figures/illustrations/bai09_summary.png)

![Minh họa tính từng bước Bài 9](../../docs/figures/illustrations/bai09_toy_covariance.png)

## 4. Mở đúng đầu ra

Các tệp nằm trong thư mục `--output-dir` của lần chạy. Tên bắt đầu `toy_` thuộc ví dụ nhỏ; `real_` thuộc thí nghiệm thật. `results.json` lưu số liệu và cấu hình phiên bản.

- `toy_projection.png`
- `toy_covariance.png`
- `toy_projection.csv`

- `summary.png`: tổng kết ví dụ chuẩn và giới hạn diễn giải.

## 5. Đối chiếu và giải thích

<details>
<summary>Mở sau khi đã tự tính</summary>

z=−3/√2; điểm tái tạo=(3,5; 3,5). Đây là một số so với một vector hai chiều.

</details>

**Điều cần mang theo:** Toy chia n, sklearn chia n−1: eigenvalue khác hệ số nhưng EVR và không gian chiếu giống nhau.

Bài nộp ngắn: ghi cấu hình đã chạy, một kết quả tính tay khớp mã, một hình kèm lời giải thích và một điều kết quả chưa chứng minh. Khi số khác, kiểm dữ liệu, seed, tham số, mẫu số và quy tắc làm tròn trước khi kết luận mã sai.

## 6. Nối với slide và tài liệu đọc trước

| Slide | Điểm bắt đầu | Điểm kết thúc |
|---|---|---|
| 12–22 | Thu nhỏ bài toán: bốn điểm, hai chiều | Chiếu rồi tái tạo: ba thao tác cốt lõi |
| 23–38 | Đo độ trải rộng của các score | PCA: học một lần, áp dụng nhất quán |
| 42–63 | Trở lại ảnh thời trang: quy trình không đổi | PCA · Bản đồ toàn bài |

Bảng đối chiếu giúp giảng viên nối ví dụ với nội dung giảng dạy; repository không phân phối PowerPoint.

## 7. Mở rộng sang dữ liệu thật

Chuẩn bị đúng dữ liệu theo [README của bài](README.md), rồi chạy:

```bash
python -m examples.bai09.main --mode all --output-dir outputs/bai09
```

Đọc ví dụ trước, chạy cấu hình chuẩn sau; cuối cùng mới thay một yếu tố và lưu sang thư mục khác. Giữ nguyên tập chấm khi so mô hình; chọn cấu hình trên validation, không chọn lại bằng test. Với phân tích mô tả ở Bài 1 và 8, giới hạn kết luận ở snapshot và cách biểu diễn đã dùng.

Phần tính tay và giải thích hình là yêu cầu cơ bản. Vét cạn, chứng minh, nhiều seed, nested CV và các kiểm tra thư viện sâu là phần mở rộng phù hợp từng bài. Bài 10 mặc định chạy 3 seed × 50 epoch trên CPU; không coi cấu hình chạy nhanh là phép tái lập đầy đủ.
