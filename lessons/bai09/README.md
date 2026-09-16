# Bài 09 · PCA: ít tọa độ hơn, giữ được điều gì?


**Lộ trình thực hành cập nhật:** [Dự đoán → chạy → đối chiếu → giải thích](HUONG_DAN_V3.md). Tài liệu đọc trước v3; slide v3.

[← Mục lục khóa học](../../README.md) · [📖 Tài liệu đọc trước Bài 09](../../readings/bai09/README.md)

**Sau bài này:** bạn đọc một ảnh thành vector, tính phép chiếu và tái tạo, giải thích EVR/MSE, dùng PCA đúng tập dữ liệu và nhận ra giới hạn của giảm chiều tuyến tính. Ôn vector, dot product, trung bình; phần trị riêng có thể học sau khi đã hiểu hình chiếu.

## 1. Bắt đầu

```bash
python -m lessons.bai09.main --mode toy
python -m mlcourse.data fetch --dataset fashion
python -m lessons.bai09.main --mode all
python -m unittest lessons.bai09.tests
```

Cài thư viện theo README gốc. Chạy từ thư mục repository; cũng hỗ trợ `python lessons/bai09/main.py`. `--seed 42` cố định việc chọn tập con; `--dpi 240` tạo 3840×2160; `--data-dir`, `--output-dir` dùng thư mục riêng. Chế độ thật dùng CPU, không cần GPU. Đổi seed làm thay tập con nên số liệu có thể khác slide. Toy chạy ngoại tuyến.

## 2. Dữ liệu thật và đơn vị quan sát

[Fashion-MNIST của Zalando Research](https://github.com/zalandoresearch/fashion-mnist) có ảnh xám 28×28 thuộc 10 loại sản phẩm. Chương trình đọc file gzip/IDX gốc, kiểm checksum, header, shape, số ảnh và phân bố lớp. Có thể tìm bản giới thiệu trên [Kaggle](https://www.kaggle.com/datasets/zalando-research/fashionmnist); pipeline dùng tệp IDX chính thức để thống nhất ảnh và ID.

| Mã | Loại | Mã | Loại |
|---|---|---|---|
| 0 | T-shirt/top | 5 | Sandal |
| 1 | Trouser | 6 | Shirt |
| 2 | Pullover | 7 | Sneaker |
| 3 | Dress | 8 | Bag |
| 4 | Coat | 9 | Ankle boot |

Một ảnh là 784 số uint8 từ 0 đến 255. Flatten theo hàng dùng $j=28r+c$ với r,c bắt đầu từ 0; thao tác này đổi shape, chưa bỏ pixel. `one_image_pixels.csv` chứa đầy đủ hàng, cột, chỉ số phẳng, số gốc và số đã chia 255. Hình `real_pixels.png` phóng một mảng 6×6 để kiểm từng giá trị.

## 3. Chốt tập dữ liệu trước khi học

| Tập | Số ảnh | Mục đích |
|---|---:|---|
| Train của thí nghiệm | 12.000, mỗi lớp 1.200 | Fit mean, PCA và classifier |
| Validation | 3.000, mỗi lớp 300 | Đọc MSE, so sánh phân loại |
| Train chính thức chưa dùng | 45.000 | Không tham gia thí nghiệm này |
| Test chính thức | 10.000 | Dành cho bài 10; bài 9 không đọc/tính metric test |

Lấy train bằng `train_test_split(..., train_size=12000, stratify=y, random_state=42)` từ 60.000 ảnh; lấy validation bằng cùng seed, phân tầng từ phần còn lại. `source_id=train:24814` là hàng 24814 trong train chính thức, dù vai trò của nó ở thí nghiệm là validation. `split_membership.csv` lưu toàn bộ ID; chương trình kiểm cả ID giao nhau và hash nội dung ảnh. Cấu hình tham chiếu không có ảnh trùng train/validation.

## 4. Ba phép toán cốt lõi

1. **Định tâm:** $x_c=x-\mu$, trong đó μ được tính trên train.
2. **Chiếu:** $z=(x-\mu)^T w$ với hướng đơn vị $\|w\|=1$.
3. **Dựng lại:** $\hat{x}=\mu+zw$.

Nhiều chiều: trong mã `components` có mỗi hàng là một hướng; `Z=(X-mean) @ components[:k].T`, `X_hat=Z @ components[:k]+mean`. Các hướng phải trực chuẩn. Chia pixel cho 255 là phép cố định; mean và hướng PCA là tham số phải học từ train. PCA không dùng nhãn, nhưng vẫn có thể rò rỉ dữ liệu nếu fit cả validation.

## 5. Ví dụ bốn điểm để tự tính

| Điểm | (x₁,x₂) | PC1 score theo hướng (1,1)/√2 | Dựng lại với 1 PC |
|---|---|---|---|
| A | (3,4) | −3/√2 | (3,5; 3,5) |
| B | (4,3) | −3/√2 | (3,5; 3,5) |
| C | (6,7) | 3/√2 | (6,5; 6,5) |
| D | (7,6) | 3/√2 | (6,5; 6,5) |

Mean=(5,5). Hiệp phương sai chia n là `[[2.5,2],[2,2.5]]`. Trị riêng 4,5 và 0,5; PC1 giữ 90% tổng phương sai. A và B ban đầu khác nhau nhưng có cùng score: đó là mất thông tin. Sai số bình phương trung bình **theo điểm** là 0,5; MSE **theo tọa độ** là 0,25 vì mỗi điểm có hai tọa độ.

Sklearn báo trị riêng theo mẫu số n−1: 6 và 2/3. Hướng, không gian chiếu và tỉ lệ EVR không thay đổi. Dấu một PC có thể đảo; nếu score cũng đảo, ảnh dựng lại giữ nguyên. Khi trị riêng lặp, có thể có nhiều cơ sở hợp lệ trong cùng không gian.

## 6. PCA tối ưu cái gì?

PCA tìm hướng đơn vị làm phương sai score lớn nhất. Với nhiều hướng trực chuẩn, điều này tương đương giảm tổng sai số bình phương của phép chiếu tuyến tính đã định tâm. Nếu không khóa độ dài w, nhân w lớn lên sẽ làm phương sai score lớn lên tùy ý.

Hình `toy_projection.png` quét mọi góc: phương sai giữ lại cộng sai số bình phương/điểm bằng 5. Ràng buộc trực chuẩn làm phép tách năng lượng có ý nghĩa. Giữ đủ hai chiều cho ví dụ chỉ đổi hệ tọa độ và có thể dựng lại chính xác; giảm xuống một chiều mới loại một phần thông tin.

## 7. Từ công thức đến ảnh thật

Fit `PCA(svd_solver="full")` trên pixel/255 của train. Không z-score từng pixel trong cấu hình này: cùng đơn vị cường độ sáng là một lựa chọn thiết kế, không phải quy tắc “luôn bỏ chuẩn hóa”.

| k | EVR train | MSE mỗi pixel validation, chưa clip |
|---:|---:|---:|
| 2 | 46,8304% | 0,04661845 |
| 16 | 76,5910% | 0,02070311 |
| 64 | 88,2421% | 0,01056173 |
| 128 | 92,9281% | 0,00649855 |

Số chiều nhỏ nhất đạt 90% là **82**; 81 chiều đạt 89,9272%, 82 đạt 90,0122%. EVR tính trên train. Hình tái tạo hiển thị cùng ảnh với bốn k; ảnh mean và PC được trình bày riêng. Hệ số PC có thể âm, không phải ảnh sản phẩm thật.

Phép chiếu tuyến tính có thể cho pixel dưới 0 hoặc trên 1. Chỉ clip khi vẽ. MSE chính tính trên số thực chưa clip; `validation_mse_clipped` là chỉ số phụ đặt tên riêng. Với cùng các không gian con lồng nhau của PCA, sai số tái tạo chưa clip không tăng khi thêm chiều. Không suy rộng tính đơn điệu này sang accuracy phân loại.

## 8. Vì sao giữ phương sai không đồng nghĩa giữ nhãn?

Trong ví dụ mô phỏng, gán nhãn 1 nếu x₁>x₂. A/B có nhãn khác nhau nhưng cùng PC1; C/D cũng vậy. PC2 chỉ có 10% phương sai nhưng giữ thông tin phân biệt nhãn ở đây. Đó là phản ví dụ cụ thể cho cách hiểu “90% phương sai = 90% thông tin phân loại”.

Thí nghiệm thật dùng cùng LogisticRegression C=1: 784 pixel đúng **2.500/3.000**, 64 PC đúng **2.511/3.000** trên validation. Kết quả này không chứng minh PCA luôn giúp. Cần nhiều split hoặc quy trình đánh giá phù hợp để khái quát; chọn k còn tùy mục tiêu nén, trực quan hay phân loại. Đám mây PC1/PC2 được tô nhãn sau khi fit; các vùng màu chồng nhau không phải lỗi của PCA.

## 9. Tự kiểm tra và thử thêm

| Câu hỏi | Đáp án và giải thích |
|---|---|
| Flatten 28×28 thành 784 có mất pixel? | Không, nếu giữ đúng thứ tự hàng/cột. |
| PCA không dùng y nên được fit cả validation? | Không; mean và hướng vẫn học từ dữ liệu. |
| Đảo dấu w mà quên đảo z có giữ ảnh tái tạo? | Không. Cần đảo cả hai để zw không đổi. |
| MSE 0,25 và sai số/điểm 0,5 có mâu thuẫn? | Không; mẫu số lần lượt nd và n, d=2. |
| 82 PC đạt 90% EVR có đảm bảo accuracy 90%? | Không; EVR không đo nhãn. |

Thử đổi seed và so sánh k90; giải thích thay đổi. Tự tái tạo điểm C bằng tay rồi đối chiếu CSV. Trong bản sao, thêm một điểm xa vào ví dụ và quan sát hướng PC1: phép bình phương khiến ngoại lai có thể tác động mạnh. Với các điểm đều trên đường tròn, phương sai hai trục bằng nhau; PCA tuyến tính một chiều không thể bảo toàn toàn bộ cấu trúc vòng tròn. Các bài thử thêm này không được dùng để thay số tham chiếu mà không ghi cấu hình.

## 10. Đầu ra và cầu nối

`outputs/bai09/` gồm 8 PNG, `results.json`, bảng chia tập, pixel ảnh, score/dự đoán validation, EVR, sai số theo k, mã ảnh minh họa và `pca_model.npz` chứa tham số số học. NPZ được đọc bằng `np.load(..., allow_pickle=False)`; không cần tệp mô hình thực thi. Mỗi hình có tên giảng viên và công thức/chú thích cần thiết.

Bài 10 dùng đúng tập con và ảnh này để học biểu diễn phi tuyến bằng MLP. Bài 09 kết thúc ở các phép đo validation; không đưa test vào lựa chọn k hoặc classifier. Mọi kết quả là thí nghiệm giảng dạy trên tập con, không phải thành tích chuẩn trên toàn bộ Fashion-MNIST.
