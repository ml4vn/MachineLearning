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

## Bản đọc trực tiếp trên GitHub

Mỗi README trong `readings/` được tạo từ toàn bộ `content.json`: đủ 10 mục và hai phụ lục, 86 bảng, 55 hình minh họa, 86 công thức và 60 câu tự kiểm của cả bộ. Câu tự kiểm này thuộc tài liệu đọc trước; bộ quiz 40 câu/bài là học liệu riêng, không thuộc gói đăng tải hiện tại.

Đã sửa cách xuất Markdown: các hàng bảng liền nhau, ký tự `|` trong nhãn thể loại được escape, công thức dùng khối `math`, nguồn và liên kết chuyển sang đường dẫn phù hợp. Nội dung gốc trong PDF/DOCX không bị viết lại. Các tệp nhị phân được đối chiếu SHA256 với biên bản xuất trước đó; cả 10 PDF có 12 trang.

Để tái tạo hoặc kiểm bản Markdown sau khi chủ động sửa `content.json`:

```bash
python tools/build_readings.py
python tools/build_readings.py --check
python tools/check_course.py
```

Lệnh trên chỉ xử lý Markdown; không tự cập nhật Word/PDF. Nếu thay nội dung học thuật, cần cập nhật và kiểm tra đồng bộ các định dạng trước khi phát hành phiên bản mới. GitHub hỗ trợ công thức qua [Markdown và MathJax](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/writing-mathematical-expressions).
