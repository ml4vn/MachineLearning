> **Học liệu hiện hành: [Bài 04 v4](../../v4/bai04/README.md).** Trang này giữ hướng dẫn CLI của bộ Python v3; notebook v4 và số liệu v4 nằm ở liên kết trên.

# Bài 04 · Hồi quy tuyến tính và Gradient Descent


**Lộ trình thực hành cập nhật:** [Dự đoán → chạy → đối chiếu → giải thích](HUONG_DAN_V3.md). Tài liệu đọc trước v3; slide v3.

[← Mục lục khóa học](../../README.md) · [📖 Tài liệu đọc trước Bài 04](../../readings/bai04/README.md)

**PGS.TS Nguyễn Văn Hậu** · 90 phút phần chính, 30–45 phút mở rộng.

Tại lúc duyệt một đơn hàng, ta có thể ước lượng thời gian giao thành công từ khoảng cách không? Bài thực hành đi từ bốn điểm tính tay đến dữ liệu Olist thật, bám slide Bài 04 v3.

## 1. Mục tiêu và chuẩn bị

Bạn cần biết vector, trung bình, đạo hàm cơ bản và cách chia train/validation/test. Sau bài này, bạn có thể phân biệt **mô hình** đường thẳng, **hàm mất mát** J và **thuật toán** Gradient Descent; tự tính một bước học; đọc MAE/RMSE cùng giới hạn của dữ liệu.

Tại thư mục gốc kho mã, dùng môi trường Python 3.12 đã cài `requirements.txt`:

```bash
python -m lessons.bai04.main --mode toy
python -m mlcourse.data fetch --dataset olist
python -m lessons.bai04.main --mode all
python -m unittest lessons.bai04.tests -v
```

Thử nghiệm có thư mục riêng:

```bash
python -m lessons.bai04.main --mode toy --toy-eta 1.8 --output-dir outputs/bai04_eta18
python -m lessons.bai04.main --mode real --real-eta 0.1 --steps 100 --distance 400
```

`--seed` chỉ đổi mẫu điểm hiển thị, không đổi split thời gian. Mặc định dự đoán cho 600 km. `--dpi 240` xuất hình 3840 × 2160. Tệp lớn được đọc từ ZIP, không cần giải nén thủ công.

## 2. Mô hình, sai số và đơn vị

$$\hat y=b+wx,\qquad e_i=\hat y_i-y_i,\qquad J=\frac1{2n}\sum_i e_i^2.$$

| Thành phần | Ví dụ nhỏ | Olist thật |
|---|---|---|
| x | Khoảng cách, đơn vị 100 km | Khoảng cách km, sau đó chuẩn hóa để học GD |
| y | Số ngày mô phỏng | Giây từ duyệt đến giao / 86.400 |
| b | Ngày khi x = 0 theo mô hình | Không phải thời gian xử lý được đo trực tiếp |
| w | Ngày trên một đơn vị x | Khi đổi về hệ gốc: ngày/km |
| J | Ngày²; bằng MSE/2 | Mục tiêu dùng khi học |

Sai số `e` trong GD là **dự đoán − thực tế**. Biểu đồ sai số thật cũng dùng **dự đoán − thực tế**; giá trị dương nghĩa là dự đoán thời gian dài hơn thực tế. CSV giữ thêm cột residual ngược dấu để tương thích với bản cũ. Cộng sai số có dấu có thể triệt tiêu, nên không dùng tổng đó thay MAE/MSE.

## 3. Bốn điểm để tính tay

| x | y | z = x − 2,5 | Dự đoán khi w = 0 | e | z × e |
|---:|---:|---:|---:|---:|---:|
| 1 | 3 | −1,5 | 5 | 2 | −3 |
| 2 | 4 | −0,5 | 5 | 1 | −0,5 |
| 3 | 6 | 0,5 | 5 | −1 | −0,5 |
| 4 | 7 | 1,5 | 5 | −2 | −3 |

Dùng $\hat y=5+wz$. Trung bình z bằng 0, nên với bài toán bình phương sai số này mức trung tâm tối ưu là trung bình y = 5. Đây là cách rút gọn để luyện một tham số, không phải quy tắc giữ b = 5 cho mọi dữ liệu.

$$J'(w)=\frac1n\sum_i z_i(5+wz_i-y_i)=1,25w-1,75.$$

Tại w = 0, J = 1,25 và gradient = −1,75. Với eta = 0,4: w₁ = 0,7; J₁ = 0,33125; w₂ = 1,05; J₂ = 0,1015625. Nghiệm w* = 1,4 vẫn có J* = 0,025 vì các điểm không nằm chính xác trên một đường thẳng.

## 4. Thuật toán học nhìn từng bước

```python
error = X @ theta - y
gradient = X.T @ error / len(y)
theta = theta - eta * gradient
```

Nếu X có cột toàn 1, theta chứa cả hệ số chặn. Mọi gradient phải tính tại **cùng theta cũ** rồi cập nhật đồng thời. Với mô hình wx+b, x = [1,2,3,4], y = [3,4,6,7], w = 0,5 và b = 1: gradient theo [w,b] là [−8,−2,75]. Bước eta = 0,05 cho [0,9;1,1375].

Trong ví dụ một tham số, $w_{t+1}-w^*=(1-1,25\eta)(w_t-w^*)$. Vì vậy 0 < eta < 1,6 bảo đảm hội tụ từ mọi khởi tạo; eta = 0,8 đến nghiệm trong một bước; eta = 1,6 dao động nếu chưa ở nghiệm. Không áp dụng con số 1,6 cho một dữ liệu hay ma trận X khác. Hình learning rate luôn dùng bộ giá trị cố định để so sánh; `--toy-eta` điều khiển hình/bảng GD chính.

## 5. Dữ liệu thật được tạo như thế nào?

Nguồn: [Olist Brazilian E-Commerce trên Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce). Loader `mlcourse/olist.py` đọc sáu bảng: orders, items, products, customers, sellers và geolocation; kiểm khóa khi ghép.

1. Lấy trung vị tọa độ cho mỗi tiền tố mã bưu chính.
2. Ghép tọa độ người bán và khách vào từng dòng hàng.
3. Tính khoảng cách Haversine đường chim bay cho từng dòng; lấy trung bình theo đơn.
4. Cộng giá, cước, cân nặng và đếm dòng hàng theo đơn.
5. Tạo nhãn `delivery_days`; giữ đơn giao thành công có mốc thời gian hợp lệ.
6. Chia theo thời gian duyệt và yêu cầu nhãn đã quan sát được ở các mốc train/validation.

| Tập | Thời gian duyệt đơn | Điều kiện quan sát nhãn | Số đơn |
|---|---|---|---:|
| Train | 01/01–31/10/2017 | Giao trước 01/11/2017 | 29.031 |
| Validation | 01/11–31/12/2017 | Giao trước 01/01/2018 | 10.389 |
| Test | 01/01–30/06/2018 | Các đơn cuối cùng giao thành công | 40.266 |

Từ 99.441 đơn gốc có 96.394 đơn giao hợp lệ trước khi áp dụng cửa sổ split; bảng cuối có 79.686 đơn. Khoảng cách thiếu được bù bằng median **train**. Snapshot trọng lượng thiếu hoàn toàn có tổng 0 theo quy tắc pilot; `known_weights` và báo cáo chuẩn bị giúp phát hiện, không diễn giải 0 này là khối lượng đo được. `prepared_orders.csv` lưu tất cả cột và ID để kiểm lại.

## 6. Huấn luyện và đối chiếu

Chỉ fit imputer và StandardScaler trên train. GD mặc định 100 bước, eta = 0,1, khởi tạo b = w = 0 trong hệ chuẩn hóa. OLS của scikit-learn là phép đối chiếu độc lập; báo cáo ghi khoảng cách hệ số GD–OLS và có đạt sai số 0,001 hay không. Nếu bạn đổi eta hoặc số bước, báo cáo phản ánh kết quả mới, không tự nhận đã hội tụ.

Đổi về đơn vị gốc: $w_{km}=w_z/\sigma$, $b_{km}=b_z-w_z\mu/\sigma$. Nghiệm OLS tham chiếu:

$$\hat y\approx 7,908192+0,005639149\times distance_{km}.$$

600 km cho dự đoán khoảng 11,2917 ngày. Đây là ước lượng của mô hình, không phải cam kết hay tác động nhân quả của việc tăng khoảng cách. Kiểm tra khoảng cách truy vấn có gần miền dữ liệu đã học không trước khi diễn giải.

## 7. Đánh giá và giới hạn

| Mô hình | MAE test (ngày) | RMSE test (ngày) |
|---|---:|---:|
| Trung bình y train | 6,851264 | 10,167486 |
| OLS khoảng cách | 5,939645 | 9,351536 |
| OLS sáu đặc trưng | 5,730232 | 9,169105 |

Mã còn xuất baseline trung vị train và mô hình chỉ dùng thời gian hứa giao. Trung bình tối ưu MSE trong các hằng số trên train; trung vị tối ưu MAE trên train. Không bảo đảm cùng thứ hạng trên test. RMSE phạt sai số lớn mạnh hơn MAE: [2,2,2,2] và [0,0,0,8] đều MAE = 2 nhưng RMSE lần lượt 2 và 4.

Kết quả điều kiện trên đơn đã giao thành công, loại đơn hủy/chưa rõ kết quả; yêu cầu nhãn trước cutoff có thể loại nhiều đơn giao lâu. Dữ liệu địa lý/sản phẩm tĩnh không chứng minh lịch sử sẵn có tại lúc duyệt. Khoảng cách tâm bưu chính không phải quãng đường vận chuyển. Dữ liệu Brazil 2017–2018 không đại diện mặc nhiên cho giao hàng Việt Nam hiện tại. Không tái fit train+validation trong phép so sánh này.

## 8. Hình và tệp để tự khám phá

Trong `outputs/bai04/` có bốn PNG: `toy_gd`, `toy_learning_rates`, `real_regression`, `real_metrics`; mỗi hình có công thức/nhãn và tên giảng viên. CSV lưu từng bước GD, gradient đầu, nhiều learning rate, bảng đơn đã chuẩn bị, bốn đơn gần khoảng cách minh họa, mọi dự đoán test và chỉ số mô hình. `results.json` có hệ số, sai số, truy vấn và phiên bản thư viện; `preparation_audit.json` có số dòng, split và tình trạng thiếu.

Đọc mã theo thứ tự `algorithms.py` → `toy()` → `mlcourse/olist.py` → `real()` → `tests.py`. Không cần chạy bài trước, cũng không phụ thuộc đường dẫn máy của giảng viên.

## 9. Câu hỏi và bài tập

1. J = MSE/2 thì nghiệm tối ưu khác MSE không? **Không**, nhân bởi hằng số dương giữ nguyên nghiệm, nhưng gradient và khoảng eta phù hợp đổi.
2. Gradient âm có nghĩa phải giảm w không? **Không**, w mới = w − eta × gradient nên w tăng khi eta > 0.
3. MAE = 5,94 ngày có nghĩa mọi đơn sai tối đa 5,94 ngày? **Không**, đây là trung bình trị tuyệt đối.
4. Cho x mới = 3 ở mô hình $5+0,7(x-2,5)$: dự đoán bao nhiêu? **5,35 ngày**.
5. Dùng ngày giao thực tế làm đầu vào tại lúc duyệt có hợp lệ? **Không**, đó là thông tin tương lai.

**Bài tập:** tự tính bước GD thứ hai; thử eta = 1,8 và giải thích loss tăng; chạy real với 10 rồi 100 bước trong thư mục khác và so hệ số với OLS; so mean/median baseline; chọn một dòng có residual lớn để nêu một yếu tố có thể còn thiếu, phân biệt giả thuyết với điều dữ liệu chứng minh. Thử eta trên train/validation, không tối ưu bằng test.

## 10. Kiểm chứng và nguồn

Bảy kiểm thử bao phủ tính tay, sai phân hữu hạn, cập nhật đồng thời, biên learning rate, nghiệm sklearn, khoảng cách Haversine, nhãn theo ngày lịch và tính sẵn có của nhãn. Chạy đầy đủ real để kiểm cả xử lý nguồn và kết quả bài giảng.

Nguồn kỹ thuật: [LinearRegression](https://scikit-learn.org/1.6/modules/generated/sklearn.linear_model.LinearRegression.html), [StandardScaler](https://scikit-learn.org/1.6/modules/generated/sklearn.preprocessing.StandardScaler.html), [đánh giá hồi quy](https://scikit-learn.org/1.6/modules/model_evaluation.html#regression-metrics). Phạm vi và kết quả kiểm định nằm trong `PLAN.md` và `VALIDATION.md`.
