# Bài 05 · Logistic Regression và nguy cơ giao trễ


**Lộ trình thực hành cập nhật:** [Dự đoán → chạy → đối chiếu → giải thích](HUONG_DAN_V3.md). Tài liệu đọc trước v3; slide v3.

[← Mục lục khóa học](../../README.md) · [📖 Tài liệu đọc trước Bài 05](../../readings/bai05/README.md)

**PGS.TS Nguyễn Văn Hậu** · 90 phút phần chính, 30–45 phút mở rộng.

Tiếp nối Bài 04, ta giữ dữ liệu đơn hàng nhưng đổi câu hỏi: **đơn này có nguy cơ giao trễ không?** Mã bám slide Bài 05 v3, gồm ví dụ tính tay, mô hình thật, ngưỡng cảnh báo và kiểm chứng từng phép tính.

## 1. Mục tiêu và cách chạy

Cần biết tích vô hướng, GD, ý nghĩa FP/FN và train/validation/test. Học xong, bạn có thể nối ba bước **logit → xác suất → quyết định**, tính gradient BCE, đọc hệ số và kiểm tra chính sách theo chi phí.

Trong môi trường Python 3.12 đã cài `requirements.txt`, chạy từ thư mục gốc kho mã:

```bash
python -m lessons.bai05.main --mode toy
python -m mlcourse.data fetch --dataset olist
python -m lessons.bai05.main --mode all
python -m unittest lessons.bai05.tests -v
```

Không cần chạy Bài 04 trước. Loader tự dựng bảng từ Olist ZIP; các đường dẫn đều thuộc kho mã, có thể đổi bằng `--data-dir` và `--output-dir`. Mặc định `--dpi 240` tạo PNG 3840 × 2160.

```bash
python -m lessons.bai05.main --mode toy --eta 0.5 --output-dir outputs/bai05_eta05
python -m lessons.bai05.main --mode real --C 0.1 --output-dir outputs/bai05_C01
```

`--eta` điều khiển GD ví dụ nhỏ; `--C` điều khiển nghịch đảo độ mạnh L2 của mô hình thật. `--seed` là tùy chọn chung; bài này có split thời gian và solver tất định, không dùng seed để thay split.

## 2. Nhãn, đầu vào và thời điểm

Nguồn [Olist trên Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), cùng quy trình chuẩn bị đã mô tả ở Bài 04. Mỗi dòng là một đơn giao thành công, nhãn trễ = 1 khi **ngày lịch giao thực tế lớn hơn ngày lịch hứa giao**. Giao lúc 23:59 cùng ngày hứa vẫn đúng hạn theo định nghĩa này.

| Đầu vào | Ý nghĩa và đơn vị |
|---|---|
| `distance_km` | Trung bình khoảng cách đường chim bay giữa các tâm bưu chính người bán–khách, km |
| `promised_days` | Thời gian từ duyệt đến hạn giao, số ngày có phần lẻ |
| `price` | Tổng giá các dòng hàng, BRL |
| `freight_value` | Tổng cước, BRL |
| `n_items` | Số dòng hàng |
| `weight_g` | Tổng cân nặng sản phẩm, gram; thiếu toàn bộ cộng thành 0 theo pilot |

Train/validation/test gồm 29.031/10.389/40.266 đơn, chia theo thời gian duyệt. Nhãn train phải có trước 01/11/2017; nhãn validation phải có trước 01/01/2018. Median và StandardScaler fit **train**. Ngày giao thực tế chỉ tạo nhãn, không thuộc danh sách đầu vào. Snapshot tĩnh và tập đơn đã giao vẫn có giới hạn về tính sẵn có và chọn mẫu.

## 3. Ba bước dự đoán

$$z=b+\sum_j w_jx_j,\qquad p=\sigma(z)=\frac1{1+e^{-z}},\qquad \hat y=\mathbf1[p\ge t].$$

z có thể là mọi số thực; p là xác suất theo mô hình; nhãn dự đoán chỉ có 0/1. p = 0,1 không có nghĩa chắc chắn đúng hạn, cũng không bắt buộc phải dùng ngưỡng 0,5.

Odds = p/(1−p), log-odds = z. Giữ các đầu vào khác cố định, tăng một đơn vị x nhân odds với $e^w$, không cộng w vào xác suất. Khi p = 0,2, gấp đôi odds cho p mới = 1/3, không phải 0,4. Hệ số trong chương trình thật được học sau chuẩn hóa; `coefficients.csv` xuất cả hệ số hệ gốc để đọc đúng đơn vị.

## 4. Học bằng BCE

$$L=-\frac1n\sum_i[y_i\log p_i+(1-y_i)\log(1-p_i)],\qquad \nabla L=\frac1nX^T(p-y).$$

Nếu X gồm cột 1 thì công thức gradient bao gồm cả b. Nhãn 1 phạt p nhỏ, nhãn 0 phạt p lớn; tự tin sai bị phạt nhiều. Mã dùng `np.logaddexp` trực tiếp từ logit để tránh overflow và log(0), không lấy log của xác suất đã làm tròn về 0/1.

| x mô phỏng | y | p trước học | p−y | x(p−y) |
|---:|---:|---:|---:|---:|
| −1 | 0 | 0,5 | 0,5 | −0,5 |
| 0 | 0 | 0,5 | 0,5 | 0 |
| 1 | 1 | 0,5 | −0,5 | −0,5 |
| 2 | 1 | 0,5 | −0,5 | −1 |

Khởi tạo b = w = 0, L = ln 2 ≈ 0,693147. Gradient b = 0, gradient w = −0,5. Eta = 1 cho b₁ = 0, w₁ = 0,5, p ≈ [0,377541;0,5;0,622459;0,731059], L ≈ 0,488641. Mọi tham số cập nhật từ gradient tại cùng tham số cũ.

Đây là bốn điểm thiết kế phân tách hoàn toàn. Loss giảm qua 20 bước không chứng minh có MLE không phạt hữu hạn: tham số có thể tăng vô hạn trong khi loss tiến về 0.

## 5. Mở rộng: nghiệm kiểm được của 19 quan sát

| x | Số quan sát | Số dương | Tỷ lệ dương |
|---:|---:|---:|---:|
| 1 | 9 | 1 | 1/9 |
| 2 | 5 | 1 | 1/5 |
| 3 | 3 | 1 | 1/3 |
| 4 | 2 | 1 | 1/2 |

Với b = −ln 16, w = ln 2, mô hình khớp đúng bốn tỷ lệ. Mã kiểm $X^T(np-y_{count})=0$, Hessian xác định dương và đối chiếu `LogisticRegression(penalty=None)` trên 19 dòng được dựng ra. Đây là ví dụ gộp đặc biệt có nghiệm xác định, không phải công thức đóng tổng quát cho logistic và không phải dữ liệu Olist.

## 6. Mô hình Olist và một đơn cụ thể

Dùng `LogisticRegression(solver='newton-cg', penalty='l2', C=1, max_iter=100)`. Thư viện dùng thuật toán tối ưu khác GD tính tay nhưng cùng hướng mô hình logistic; mục tiêu thật có thêm phạt L2. Chương trình xem cảnh báo chưa hội tụ là lỗi cần giải quyết.

Tệp `one_order_calculation.csv` đưa một đơn train gần 100 km qua giá trị đã bù thiếu, chuẩn hóa, hệ số, đóng góp logit rồi sigmoid. Hình `real_one_order.png` minh họa tổng từng phần. Chọn đơn theo khoảng cách định trước, không chọn theo kết quả nhãn để tạo câu chuyện thuận lợi.

Đổi về hệ gốc: $w_{raw,j}=w_{std,j}/\sigma_j$, $b_{raw}=b_{std}-\sum_jw_{raw,j}\mu_j$. Mã kiểm dự đoán sau đổi hệ số vẫn khớp. Đóng góp logit và dấu hệ số không tự mang ý nghĩa nhân quả.

## 7. Chọn ngưỡng trên validation

Mục tiêu giả định: $K=FP+5FN$ (`cost` trong mã). K khác với `C` là tham số regularization của thư viện. Quét [0,05;0,10;0,15;0,20;0,30;0,50] trên validation. Nếu hòa cost, chọn ít cảnh báo hơn rồi ngưỡng lớn hơn. Lưu chính sách trong `model_policy.json` trước khi tính báo cáo test. Không tái fit train+validation.

| Ngưỡng | FP validation | FN validation | Cost |
|---:|---:|---:|---:|
| 0,05 | 707 | 534 | 3.377 |
| **0,10** | **68** | **608** | **3.108** |
| 0,15 | 8 | 632 | 3.168 |
| 0,50 | 2 | 634 | 3.172 |

Ngưỡng lý thuyết 1/(1+5) = 1/6 áp dụng nếu p là xác suất hậu nghiệm phù hợp, chi phí đúng như giả định và không có ràng buộc khác. Ngưỡng 0,10 được chọn trên lưới hữu hạn từ điểm mô hình thực nghiệm; không mâu thuẫn với công thức có điều kiện ấy, cũng không chứng minh đã hiệu chuẩn.

## 8. Kết quả test và cách kết luận

| Chính sách | TN | FP | FN | TP | Cost |
|---|---:|---:|---:|---:|---:|
| Luôn đúng hạn | 36.788 | 0 | 3.478 | 0 | 17.390 |
| Logistic t = 0,50 | 36.788 | 0 | 3.478 | 0 | 17.390 |
| Logistic t = 0,10 | 36.429 | 359 | 3.317 | 161 | 16.944 |

Giảm ngưỡng phát hiện thêm 161 đơn trễ nhưng tạo 359 cảnh báo sai. Cost giảm 446, khoảng 2,56% theo thước đo giả định; recall vẫn chỉ 4,63%. Không được mô tả đây là bộ cảnh báo trễ đã đủ tốt. Accuracy tại 0,50 đạt 91,36% dù recall bằng 0.

BCE, Brier, AP và ROC AUC dùng cùng điểm p nên không đổi khi chỉ đổi ngưỡng. Chương trình xuất các chỉ số này và histogram chuẩn hóa riêng từng lớp để thấy mức chồng lấp, thay vì để lớp đông che lớp ít. Đây là holdout lịch sử đã xuất hiện trong pilot khóa học, không phải nghiên cứu độc lập mới. Chi phí thấp hơn không chứng minh hiệu quả can thiệp, tiết kiệm thật hay khả năng triển khai.

## 9. Tệp kết quả và tự kiểm tra

Trong `outputs/bai05/` có năm PNG: `toy_learning`, `toy_sigmoid_bce`, `real_confusion`, `real_scores_cost`, `real_one_order`. CSV lưu lịch sử, từng dự đoán toy, dữ liệu gộp 19, bảng Olist đã dựng, validation/test predictions, grid ngưỡng, hệ số và phép tính một đơn. JSON ghi chính sách, chuẩn bị và báo cáo kèm phiên bản thư viện.

Đọc `algorithms.py` trước để hiểu sigmoid/BCE/GD; tiếp theo `main.py`, `mlcourse/classification.py` và `mlcourse/olist.py`. Các phần dùng chung chỉ cần tồn tại trong kho mã, không yêu cầu chạy bài khác trước.

1. p = 0,6, t = 0,7 cho nhãn nào? **0**, vì p < t.
2. Tăng C có nghĩa tăng learning rate không? **Không**, C lớn làm phạt yếu hơn.
3. Đổi ngưỡng có đổi loss xác suất của cùng điểm không? **Không**.
4. Giao 20:00 đúng ngày hứa là trễ theo bài này? **Không**.
5. Nếu odds gấp đôi, xác suất luôn gấp đôi? **Không**, còn phụ thuộc mức ban đầu.

## 10. Bài tập, kiểm chứng và nguồn

- Tính tay BCE sau bước đầu và so `toy_predictions.csv`. Đáp số khoảng 0,488641.
- Thử eta = 0,5, so sau cùng số bước; giải thích vì sao chưa thể quy tốc độ hội tụ cho mọi dữ liệu.
- Tính 359 + 5 × 3.317 = 16.944 và so baseline 5 × 3.478 = 17.390.
- Dùng validation thử C = 0,1 và C = 10, lưu thư mục riêng; báo thay đổi hệ số và cost. Không chọn C bằng test đã xem.
- Mở rộng: giải thích vì sao ở 19 quan sát, x = 4 cho z = 0 và p = 1/2.

Sáu kiểm thử bao phủ sigmoid ở ±1000, BCE ổn định, gradient sai phân, bước cập nhật, nghiệm gộp, odds, tính bất biến của BCE/Brier khi đổi ngưỡng và đầu vào sai. Lệnh real còn đối chiếu sigmoid thư viện, đổi đơn vị và BCE tính từ logit.

Nguồn: [LogisticRegression](https://scikit-learn.org/1.6/modules/generated/sklearn.linear_model.LogisticRegression.html), [log loss](https://scikit-learn.org/1.6/modules/generated/sklearn.metrics.log_loss.html), [hiệu chuẩn xác suất](https://scikit-learn.org/1.6/modules/calibration.html). Xem `PLAN.md` và `VALIDATION.md` cho phạm vi và bằng chứng kiểm tra.
