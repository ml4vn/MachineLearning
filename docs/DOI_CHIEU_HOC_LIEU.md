# Đối chiếu tài liệu đọc trước với thực hành Python

Tài liệu đọc trước giúp hiểu bài mà chưa cần lập trình. Bộ Python làm rõ các phép tính, đọc lại dữ liệu thật và tạo kết quả mới. Hai phần cùng lộ trình và case; mức độ chi tiết khác nhau để phù hợp thời điểm học.

| Bài | Đọc trước | Khi chạy Python |
|---|---|---|
| 01 | Mã hóa phim theo ba nhãn để tính tay cosine | Giữ ví dụ nhỏ và mở rộng đủ 19 nhãn; thứ hạng có thể khác khi đổi không gian đặc trưng |
| 02 | Nhìn SMS thật, khoảng cách và chuẩn hóa | Khử trùng, chia tập, chọn k bằng validation, truy vết láng giềng |
| 03 | Đọc confusion và chi phí sai | Tính lại metric, ROC/PR và chọn ngưỡng trên validation của cùng SMS |
| 04 | Tính một bước GD và hiểu learning rate | Vẽ nhiều bước, so nghiệm GD với OLS và đánh giá Olist ngoài mẫu |
| 05 | Từ logit đến sigmoid, BCE và quyết định | Huấn luyện logistic, giải thích một đơn Olist, đối chiếu chi phí ngưỡng 0,1 |
| 06 | Đọc từng phép tách cây | Kiểm Gini, pruning, suy luận từng đường đi và so với logistic trên cùng tập |
| 07 | Hiểu rò rỉ qua thời gian, người dùng và chọn mô hình | Thêm thí nghiệm pipeline, nhóm lặp, nhiều ứng viên, nested CV và rolling CV |
| 08 | Từ hóa đơn đến RFM và các bước K-means | Tính lại RFM, đối chiếu bằng cách độc lập, thử K/khởi tạo và đọc silhouette |
| 09 | Từ pixel đến score PCA và ảnh tái tạo | Fit PCA trên train, đối chiếu EVR, MSE và baseline trên validation; chưa dùng test |
| 10 | XOR, forward, backprop và checkpoint | Kiểm gradient, chạy thật ba seed × 50 epoch, chốt checkpoint rồi đánh giá test |

Các con số cần so cùng dữ liệu, bộ lọc, tập train/validation/test, seed, ngưỡng và cách làm tròn. CSV/JSON trong `readings/` là bản tham chiếu của tài liệu; CSV/JSON trong `outputs/` được sinh bởi lần chạy Python hiện tại. README và VALIDATION của mỗi bài giải thích cấu hình và phạm vi kiểm.

Một khác biệt số học đã được ghi rõ ở Bài 10: tài liệu ghi sai lệch gradient sai phân khoảng **7,55×10⁻¹¹**, còn hàm BCE ổn định số của bộ Python cho khoảng **4,12×10⁻¹¹** trong lần kiểm. Hai biểu thức BCE tương đương về toán học nhưng thứ tự phép tính số thực khác nhau. Cả hai đều xác nhận chín gradient tại điểm đang xét với sai lệch rất nhỏ; không dùng sự khác nhau này làm bằng chứng chất lượng mô hình.

## Bản đọc trực tiếp trên GitHub v3

Mỗi README được tạo từ toàn bộ `content.json` v3, gồm 105 bảng, 56 hình minh họa, 101 công thức và 60 câu tự kiểm. PDF/Word được sao chép nguyên vẹn từ bộ v3 đã duyệt: 141 trang, Bài 6 có 15 trang và các bài còn lại có 14 trang. SHA256 của cả 20 tệp khớp biên bản nguồn.

Tài liệu Bài 7 thuộc đợt cập nhật v3 nhưng đối chiếu slide v2. Python đã được đồng bộ hướng dẫn và minh họa: Bài 3 dùng ngưỡng 0,80; Bài 4 bổ sung mặt 3D J(w,b) và thống nhất dấu sai số; Bài 10 nối ký hiệu và thêm một đường gradient trước khi đọc toàn bộ mạng. Xem [phạm vi và cách tái tạo](PYTHON_V3.md). Mã thuật toán, seed, dữ liệu và cách chia tập được giữ nguyên.

Để tái tạo hoặc kiểm bản Markdown sau khi chủ động sửa `content.json`:

```bash
python tools/build_readings.py
python tools/build_readings.py --check
python tools/check_course.py
```

Lệnh trên chỉ xử lý Markdown; không tự cập nhật Word/PDF. Nếu thay nội dung học thuật, cần cập nhật và kiểm tra đồng bộ các định dạng trước khi phát hành phiên bản mới. GitHub hỗ trợ công thức qua [Markdown và MathJax](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/writing-mathematical-expressions).
