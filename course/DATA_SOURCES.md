# Dữ liệu và nguồn cho học liệu 

Các tệp là snapshot dùng để tái lập số liệu trong slide và notebook. Điều kiện sử dụng dữ liệu theo nguồn gốc, tách biệt với quyền tác giả của bài giảng và mã. Xem [bảng nguồn và điều kiện sử dụng toàn khóa](../docs/DU_LIEU_VA_NGUON.md).

| Bài | Nguồn gốc | Tệp để chạy | Ghi nhận và phạm vi |
|---|---|---|---|
| 01 | [MovieLens / GroupLens](https://grouplens.org/datasets/movielens/latest/) | `bai01/data/movies.csv`, archive và bảng ví dụ | Điều kiện MovieLens đi kèm [`MovieLens_README.md`](bai01/data/MovieLens_README.md); cosine ở đây dùng metadata thể loại, không phải dự đoán sở thích cá nhân từ rating. |
| 02–03 | [UCI SMS Spam Collection](https://archive.ics.uci.edu/dataset/228/sms+spam+collection) | `baiNN/data/sms.zip` và các bảng đặc trưng/dự đoán | Almeida và Hidalgo; CC BY 4.0 theo nguồn UCI. Giữ bản README gốc trong mỗi bài. Khử trùng và cách chia tập được kiểm lại bởi mã lab. |
| 04–06 | [Olist Brazilian E-Commerce / Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) | [`datasets/olist.zip`](datasets/olist.zip), các bảng `data/prepared/` | Olist; CC BY-NC-SA 4.0 theo metadata nguồn được ghi nhận trong bộ học liệu. Cohort đơn hoàn tất, mốc thời gian và khả năng biết metadata cần được đọc cùng kết quả. |
| 08 | [UCI Online Retail](https://archive.ics.uci.edu/dataset/352/online+retail) | `bai08/data/online_retail.zip`, RFM và arrays | Daqing Chen; CC BY 4.0. Bộ lọc, dòng trùng, giá trị tiền và recency được kiểm lại từ hóa đơn gốc. |
| 09–10 | [Fashion-MNIST / Zalando Research](https://github.com/zalandoresearch/fashion-mnist) | Bốn IDX gzip, subset và checkpoint/arrays của từng bài | MIT; giữ nguyên [`Fashion_MNIST_LICENSE.txt`](bai09/data/Fashion_MNIST_LICENSE.txt). Bài 10 kèm baseline tham chiếu từ Bài 9, không cần chạy Bài 9 trước để mở notebook. |

Olist chỉ được lưu một lần để Bài 4–6 dùng chung. Các tệp IDX và tham chiếu Fashion-MNIST cần cho kiểm chứng được giữ ở từng bài. Archive lớn nhất nhỏ hơn 50 MiB; không cần Git LFS để dùng gói này.

Các thư mục `data/` còn chứa CSV/NPZ suy ra từ nguồn trên; `source_manifest.json` của đợt phát hành và manifest dữ liệu từng bài lưu checksum để truy nguồn. File NPZ lưu mảng số, không cần tải mô hình pickle hoặc chạy đối tượng Python từ dữ liệu không rõ nguồn.

KaTeX được kèm để hiển thị công thức ngoại tuyến; giấy phép MIT có trong thư mục `source/assets/katex/` của các bài. Phông chữ đi kèm giữ các tệp giấy phép tương ứng trong assets. Không tự gán một giấy phép mới cho toàn bộ bài giảng hoặc repository trong đợt cập nhật này.
