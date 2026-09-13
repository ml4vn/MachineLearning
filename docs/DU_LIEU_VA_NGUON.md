# Dữ liệu, nguồn khoa học và điều kiện sử dụng

Các ví dụ nhỏ do bộ thực hành xây dựng được ghi rõ là mô phỏng. Các case thật đọc từ dữ liệu bên dưới, kiểm SHA256 theo `mlcourse/datasets.json`. Các archive dữ liệu gốc tải để chạy Python và output mới được loại khỏi Git. Thư mục `readings/` có các trích dữ liệu, bảng đã xử lý và kết quả tham chiếu đi kèm tài liệu đọc trước; đây là các bản lưu phục vụ kiểm ví dụ, chịu điều kiện tương ứng của nguồn dữ liệu.

## Nguồn dữ liệu

| Dữ liệu | Nguồn chính và đường dẫn giới thiệu | Điều kiện được kiểm tra |
|---|---|---|
| MovieLens latest-small, snapshot 2018 | [GroupLens](https://grouplens.org/datasets/movielens/latest/), [README nguồn](https://files.grouplens.org/datasets/movielens/ml-latest-small-README.html), [bản Kaggle dùng trong pipeline](https://www.kaggle.com/datasets/grouplens/movielens-latest-small) | Điều khoản nghiên cứu riêng của GroupLens; ghi nhận nguồn, không hàm ý bảo chứng; phân phối lại cả dữ liệu biến đổi theo cùng điều khoản; mục đích thương mại cần sự cho phép của chủ nguồn |
| SMS Spam Collection | [UCI](https://archive.ics.uci.edu/dataset/228/sms+spam+collection) | Trang UCI ghi CC BY 4.0; ghi công Almeida và Hidalgo |
| Brazilian E-Commerce Public Dataset by Olist | [Olist trên Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) | Metadata API chính thức được đọc lúc chuẩn bị ghi **CC BY-NC-SA 4.0**; ghi nguồn, điều kiện phi thương mại và chia sẻ tương tự theo giấy phép dữ liệu |
| Online Retail | [UCI](https://archive.ics.uci.edu/dataset/352/online+retail) | Trang UCI ghi CC BY 4.0; ghi công Daqing Chen |
| Fashion-MNIST | [Zalando Research](https://github.com/zalandoresearch/fashion-mnist), [Kaggle giới thiệu](https://www.kaggle.com/datasets/zalando-research/fashionmnist), [LICENSE nguồn](https://github.com/zalandoresearch/fashion-mnist/blob/master/LICENSE) | Repository nguồn ghi MIT, Copyright 2017 Zalando SE; bản thông báo được giữ trong `third_party/FASHION_MNIST_LICENSE.txt` |

Thông tin nguồn kiểm tra ngày 13/09/2026. Metadata website không thay thế kiểm tra nội dung tệp: ví dụ trang Online Retail ghi không có thiếu dữ liệu, nhưng tệp thực tế có CustomerID thiếu; chương trình báo theo dữ liệu đã đọc. Các số lượng và quy tắc lọc nằm trong README/VALIDATION của bài tương ứng.

## Ghi nhận và trích dẫn

- F. Maxwell Harper, Joseph A. Konstan (2015). *The MovieLens Datasets: History and Context*. [DOI](https://doi.org/10.1145/2827872).
- Tiago Almeida, José María Gómez Hidalgo. *SMS Spam Collection*. [DOI của dữ liệu UCI](https://doi.org/10.24432/C5CC84).
- Olist. *Brazilian E-Commerce Public Dataset by Olist*. [Nguồn Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).
- Daqing Chen (2015). *Online Retail*. [DOI của dữ liệu UCI](https://doi.org/10.24432/C5BW33).
- Han Xiao, Kashif Rasul, Roland Vollgraf (2017). *Fashion-MNIST: a Novel Image Dataset for Benchmarking Machine Learning Algorithms*. [Bài báo của tác giả](https://arxiv.org/abs/1708.07747).

Các ảnh Fashion-MNIST được đọc từ IDX, chuẩn hóa hoặc tái tạo theo phương pháp mô tả; hình có ghi nguồn và mã ảnh. Thống kê Olist/Online Retail được lọc, tổng hợp và mô hình hóa trong mã. Tên giảng viên trên hình xác định bộ thực hành, không thay thế ghi nhận quyền của chủ dữ liệu.

`readings/bai01/movies.csv` giữ metadata MovieLens của bản bài học; [README nguyên bản của GroupLens](../third_party/MOVIELENS_README.txt) đi kèm các điều khoản và trích dẫn. Các bảng dẫn xuất Olist trong `readings/bai04/` đến `readings/bai07/` giữ điều kiện **CC BY-NC-SA 4.0** của dữ liệu Olist. Việc xử lý được ghi trong kế hoạch và tài liệu từng bài: lọc đơn, tính đặc trưng, chia tập và bổ sung dự đoán; chúng không phải bảng dữ liệu gốc chưa biến đổi. Bảng trích SMS/Online Retail giữ ghi nguồn theo CC BY 4.0; ảnh Fashion-MNIST giữ thông báo MIT trong `third_party/`.

## Tài liệu kỹ thuật chính

- [scikit-learn 1.6: tiền xử lý và các lỗi thường gặp](https://scikit-learn.org/1.6/common_pitfalls.html).
- [Nearest neighbors](https://scikit-learn.org/1.6/modules/neighbors.html) và [đánh giá mô hình](https://scikit-learn.org/1.6/modules/model_evaluation.html).
- [Linear models](https://scikit-learn.org/1.6/modules/linear_model.html), [decision trees](https://scikit-learn.org/1.6/modules/tree.html), [cross-validation](https://scikit-learn.org/1.6/modules/cross_validation.html).
- [KMeans](https://scikit-learn.org/1.6/modules/generated/sklearn.cluster.KMeans.html), [PCA](https://scikit-learn.org/1.6/modules/generated/sklearn.decomposition.PCA.html), [MLPClassifier](https://scikit-learn.org/1.6/modules/generated/sklearn.neural_network.MLPClassifier.html).
- [GitHub setup-python v6](https://github.com/actions/setup-python/tree/v6) và [checkout v6](https://github.com/actions/checkout/tree/v6) cho cấu hình CI.

## Tải và bảo toàn snapshot

```bash
python -m mlcourse.data fetch --dataset all
```

Đã thử tải thực tế đủ tám tệp từ các endpoint công khai và kiểm checksum khớp bản dùng trong bài. Mỗi tệp được tải vào `.part`, xác minh rồi mới đổi thành tên chính. Giới hạn tải 200 MB mỗi tệp; không giải nén tùy ý từ ZIP. Nếu mạng lỗi, tệp `.part` của lần tải đó được dọn, có thể chạy lại lệnh.

Có dữ liệu đúng snapshot sẵn ở máy giảng viên: chép nguyên tệp gốc vào một thư mục, rồi dùng `--source-dir`. Không cần mở rộng quyền truy cập dữ liệu riêng, cung cấp token trong mã hoặc đẩy dữ liệu thật vào Git để chạy bài.

## Quyền đối với bộ mã và giáo trình

Chưa áp một giấy phép mở mặc định cho toàn bộ mã/giáo trình do chủ bộ bài chưa chọn giấy phép phát hành. Điều này không thay đổi các giấy phép dữ liệu bên thứ ba ở trên. Khi công bố, có thể bổ sung giấy phép cho phần mã thuộc quyền của chủ bộ bài; giữ các thông báo và điều kiện nguồn dữ liệu riêng.
