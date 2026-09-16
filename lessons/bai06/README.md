# Bài 06 · Cây quyết định và cảnh báo giao trễ


**Lộ trình thực hành cập nhật:** [Dự đoán → chạy → đối chiếu → giải thích](HUONG_DAN_V3.md). Tài liệu đọc trước v3; slide v3.

[← Mục lục khóa học](../../README.md) · [📖 Tài liệu đọc trước Bài 06](../../readings/bai06/README.md)

**PGS.TS Nguyễn Văn Hậu** · 90–120 phút phần chính; 30 phút mở rộng.

Cùng câu hỏi của Bài 05, ta thay hàm tuyến tính bằng **chuỗi câu hỏi theo thứ tự**. Bạn sẽ tự kiểm một cây 12 đơn mô phỏng, thấy ảnh hưởng của độ sâu, rồi theo một đơn Olist thật qua từng nút. Nội dung bám slide Bài 06 v3.

## 1. Mục tiêu và chạy chương trình

Cần biết tỷ lệ lớp, FP/FN, validation và cách tránh dùng thông tin tương lai. Sau bài này, bạn có thể tính Gini có trọng số, phân biệt gain cục bộ/toàn cây, đọc điểm lá, chọn cấu hình bằng validation và phản biện một báo cáo chỉ dùng accuracy.

Tại thư mục gốc kho mã, dùng Python 3.12 đã cài `requirements.txt`:

```bash
python -m lessons.bai06.main --mode toy
python -m mlcourse.data fetch --dataset olist
python -m lessons.bai06.main --mode all
python -m unittest lessons.bai06.tests -v
```

Bài tự dựng dữ liệu Olist và tự fit cả logistic đối chiếu; không cần chạy Bài 05 trước. `--dpi 240` cho PNG 3840 × 2160. Thử thay số mẫu tối thiểu mỗi lá, lưu riêng:

```bash
python -m lessons.bai06.main --mode real --min-leaf 500 --output-dir outputs/bai06_leaf500
```

`--seed 42` là mặc định để đối chiếu slide; đổi seed có thể thay lựa chọn khi gain hòa hoặc kết quả hoán vị. Các tập Olist vẫn chia theo thời gian. Moons dùng seed dữ liệu 17 và seed chia tập 42 cố định để so các cây trên cùng dữ liệu.

## 2. Từ câu hỏi đến điểm ở lá

Mỗi nút hỏi một đặc trưng có nhỏ hơn hoặc bằng ngưỡng không. Đi sang trái nếu `x[j] <= threshold`, sang phải nếu lớn hơn. Chỉ áp dụng câu hỏi của nút trong vùng dữ liệu đã đến nút đó.

Điểm ở lá là tỷ lệ dương **train** trong lá. Ví dụ 33/297 = 1/9 ≈ 0,1111: ở ngưỡng 0,50 không cảnh báo, ở 0,10 cảnh báo. Đây không phải bảo đảm về nhãn một đơn hoặc xác suất đã hiệu chuẩn.

Quy tắc chính sách trong bài là `p >= t`. Khi hai lớp hòa, `sklearn.predict` trả lớp có chỉ số nhỏ nhất, còn quy tắc p >= 0,5 trả lớp dương. Mã kiểm riêng sự khác biệt này; không dùng hai quy tắc như thể luôn tương đương.

## 3. Mười hai đơn mô phỏng

Khoảng cách x = 1…12, đơn vị 100 km. M01, M04, M07, M10 có `promised_days = 10`, các đơn khác là 20. Nhãn trễ của bốn đơn hứa ngắn này và M11, M12 là 1; các đơn khác là 0. Bảng nguồn được chương trình sinh và lưu nguyên vẹn.

Gini nhị phân: $G=1-p_0^2-p_1^2=2p(1-p)$. Nút gốc 6 trễ/6 đúng hạn có Gini = 0,5. Nút thuần có Gini = 0.

$$G_{sau}=\frac{n_L}{n}G_L+\frac{n_R}{n}G_R,\qquad gain=G_{trước}-G_{sau}.$$

| Câu hỏi | Nhánh trái | Nhánh phải | Gini sau | Gain |
|---|---|---|---:|---:|
| Hứa giao ≤ 15 ngày | 4 đơn, đều trễ | 8 đơn, 2 trễ | 0,25 | 0,25 |
| Trong nhánh phải: khoảng cách ≤ 10 | 6 đúng hạn | 2 trễ | 0 | 0,375 cục bộ |

Gain thứ hai 0,375 được tính trong **8** đơn của nút. Khi cộng cho toàn bộ 12 đơn, nhân 8/12: 0,25 + (8/12) × 0,375 = 0,5. Cây cuối có 3 lá, 5 nút; M11 đi phải ở gốc rồi phải ở nút khoảng cách, vào lá trễ.

## 4. Quét ngưỡng và kiểm thuật toán

`enumerate_splits()` lấy các giá trị khác nhau đã sắp xếp trong từng cột, xét midpoint giữa hai giá trị kề nhau. Mỗi ngưỡng chia tập thành hai phần, đếm lớp, tính Gini và gain. Nếu cột hằng thì không có ứng viên; không tạo nút con rỗng.

```python
left = X[:, feature] <= threshold
after = (left.sum()*gini(y[left]) + (~left).sum()*gini(y[~left])) / len(y)
gain = gini(y) - after
```

CART chọn tham lam ứng viên tốt nhất tại nút hiện tại; không chứng minh cây cuối tối ưu toàn cục. Hàm `walk()` tự duyệt những nút đã xuất từ cây, dùng float32 như sklearn khi dự đoán. Tệp JSON giữ ngưỡng đầy đủ; chỉ hình mới làm tròn. Chương trình so đường duyệt với thư viện trên toàn test.

## 5. Độ phức tạp và cắt tỉa

Moons có 600 điểm, noise = 0,30, chia train/validation 300/300. Chương trình so độ sâu [1,2,3,4,5,6,8,12,không giới hạn], vẽ hai vùng quyết định và đường accuracy. Đây là mô phỏng riêng, không phải dữ liệu giao hàng.

`max_depth` chặn độ sâu; `min_samples_leaf` chặn các vùng quá ít mẫu. Cây khớp hoàn hảo train có thể ghi nhớ nhiễu và kém hơn cây khác trên validation.

Với cây 12 đơn, cắt tỉa xét $R_\alpha(T)=R(T)+\alpha|L(T)|$, R là tổng Gini lá có trọng số theo toàn train; L(T) là tập các lá, |L(T)| là số lá, alpha là mức phạt thêm một lá:

| Cây con | Số lá | R | Mục tiêu khi alpha = 0,30 |
|---|---:|---:|---:|
| Cây đầy đủ | 3 | 0 | 0,90 |
| Chỉ giữ nhát cắt gốc | 2 | 0,25 | 0,85 |
| Gộp thành một lá | 1 | 0,50 | 0,80 |

Ở alpha = 0,25 ba giá trị bằng nhau; đường pruning sklearn trong ví dụ chuyển từ 3 lá đến 1 lá, không nhất thiết đi qua mọi số lá. Cắt tỉa xét cây con của cây đã dựng. Olist chính dùng dừng sớm, không báo cáo một phép tuning alpha chưa thực hiện.

## 6. Phản ví dụ để tránh học thuộc sai

- **XOR:** nhát cắt đầu có gain bằng 0 nhưng cây sâu 2 với `min_impurity_decrease=0` vẫn giải được bốn điểm. Đặt mức tối thiểu 0,01 làm cây dừng và chỉ đạt accuracy 0,5 trong ví dụ.
- **Biến đổi đơn điệu:** train x = [0,2] có nhãn [0,1], midpoint = 1; x mới = 1,2 đi phải. Bình phương train thành [0,4], midpoint = 2; điểm mới 1,44 lại đi trái. Bình phương tăng trên miền không âm và giữ thứ tự train, nhưng dự đoán điểm mới có thể khác.
- **Gain và nhân quả:** một đặc trưng giúp phân lớp không chứng minh thay đổi đặc trưng đó sẽ thay đổi kết quả thật.

Không cần chuẩn hóa cho cây theo cùng lý do như kNN. Case thật vẫn dùng cùng scaler của Bài 05 để tái lập pilot; thao tác số thực và cách đặt midpoint là lý do tránh phát biểu bất biến tuyệt đối cho mọi phép biến đổi/mọi điểm mới.

## 7. Olist: dữ liệu, chọn cấu hình và ngưỡng

Nguồn [Olist trên Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce); 79.686 đơn thuộc ba tập 29.031/10.389/40.266 như Bài 04–05. Trễ theo **ngày lịch**, không theo việc muộn hơn 00:00 cùng ngày. Sáu đặc trưng: khoảng cách, hứa giao, giá, cước, số dòng hàng, cân nặng. Median/scaler fit train; giữ quy tắc cộng cân nặng thiếu của pilot và báo trong audit.

| Cấu hình | AP validation tham chiếu |
|---|---:|
| max_depth = 3, min_samples_leaf = 200 | 0,081666 |
| max_depth = 6, min_samples_leaf = 200 | 0,100478 |

**AP (Average Precision)** tổng hợp precision theo các mức tăng recall trên tập validation; không đồng nhất với accuracy hay diện tích hình thang dưới đường PR. **ROC AUC** đo khả năng xếp điểm dương cao hơn điểm âm (cặp hòa tính nửa điểm); “validation” chỉ tập dữ liệu dùng để tính chỉ số, không phải một thuật toán mới. Case này chọn độ sâu bằng AP, không chọn bằng ROC AUC. Chọn AP validation cao hơn; hòa thì ưu tiên ít lá. Với cấu hình mặc định, chọn độ sâu 6, có 23 lá/45 nút. Sau đó quét cùng lưới ngưỡng Bài 05 theo FP+5FN; validation chọn 0,10. Lưu `model_policy.json` trước khi đánh giá test, không fit lại train+validation.

`real_tree_top.png` chỉ hiển thị ba tầng đầu; dấu (...) nghĩa là còn nhánh. `tree_nodes.json` chứa toàn cây, ngưỡng chuẩn hóa và ngưỡng hệ gốc, số mẫu, số dương, Gini và điểm. `real_one_path.png` và CSV minh họa một đơn đến **tận lá**; ví dụ chọn có chủ đích từ TP nếu có, không dùng thay cho đánh giá toàn bộ test.

## 8. So sánh kết quả theo đúng mục tiêu

| Chính sách test | TP | FP | FN | TN | Cost FP+5FN |
|---|---:|---:|---:|---:|---:|
| Luôn đúng hạn | 0 | 0 | 3.478 | 36.788 | 17.390 |
| Logistic đã chọn ngưỡng | 161 | 359 | 3.317 | 36.429 | 16.944 |
| Cây đã chọn ngưỡng | 432 | 2.129 | 3.046 | 34.659 | 17.359 |

Cây phát hiện nhiều đơn trễ hơn nhưng tạo nhiều cảnh báo sai hơn; cost cao hơn logistic theo giả định này. Không gọi một mô hình tốt nhất chỉ vì recall hay khả năng vẽ sơ đồ. Cả hai có recall còn thấp. Test là holdout lịch sử đã dùng trong pilot, không phải một nghiên cứu mới độc lập.

MDI cộng mức giảm Gini có trọng số trên train rồi chuẩn hóa. Permutation giữ mô hình, hoán vị từng cột validation năm lần và đo AP giảm. Các đặc trưng tương quan có thể thay thế nhau; hoán vị có thể sinh tổ hợp không thực tế. Thanh sai số là SD giữa các lần hoán vị, không phải khoảng tin cậy. Hai biểu đồ có đơn vị khác nhau và không đo tỷ lệ tác động nhân quả.

## 9. Tệp kết quả và câu hỏi tự kiểm tra

Trong `outputs/bai06/` có bảy PNG: `toy_tree`, `toy_regions`, `toy_complexity`, `real_tree_top`, `real_confusion`, `real_importance`, `real_one_path`. CSV gồm dữ liệu toy, ngưỡng ứng viên, pruning, XOR, Moons và split, độ phức tạp, ứng viên thật, ngưỡng validation, dự đoán từng đơn, đường đi và importance. JSON gồm cây, chính sách, chuẩn bị và kết quả.

1. Nút có p = 0,25 thì Gini bằng bao nhiêu? **0,375**.
2. Gain 0,375 ở nút 8/12 mẫu đóng góp toàn cây bao nhiêu? **0,25**.
3. Lá có p = 1/9, ngưỡng 0,10 cho quyết định gì? **Cảnh báo**.
4. Cây có 3 lá đầy đủ nhị phân thì có mấy nút? **5**.
5. Cây có TP lớn hơn logistic có chắc cost nhỏ hơn? **Không**, phải tính cả FP và FN theo đúng chi phí.

## 10. Bài tập, kiểm chứng và nguồn

- Tìm nhát cắt có gain lớn nhất trong `toy_root_candidates.csv`, kiểm lại bằng bốn phép đếm.
- Theo M11 qua cây, rồi tự kiểm một đơn Olist từ `one_order_path.csv`.
- Thử `--min-leaf 500`, so số lá và AP validation; không chọn lại cấu hình bằng test.
- Tính chênh lệch cost cây–logistic: 17.359 − 16.944 = 415. Viết một kết luận có cả lợi ích phát hiện và chi phí cảnh báo sai.
- Mở rộng: đổi tiêu chí Gini sang entropy trong ví dụ nhỏ. Không so trực tiếp trị số Gini với số bit entropy như hai thang điểm giống nhau.

Sáu kiểm thử kiểm weighted gain, duyệt cây, MDI, pruning, XOR, hòa lớp, phản ví dụ biến đổi và trường hợp đầu vào lỗi. Real còn kiểm duyệt tất cả 40.266 đơn test, tần suất nhãn từng lá và phép cộng gain.

Nguồn: [CART trong scikit-learn](https://scikit-learn.org/1.6/modules/tree.html), [DecisionTreeClassifier](https://scikit-learn.org/1.6/modules/generated/sklearn.tree.DecisionTreeClassifier.html), [cost-complexity pruning](https://scikit-learn.org/1.6/auto_examples/tree/plot_cost_complexity_pruning.html), [permutation importance](https://scikit-learn.org/1.6/modules/permutation_importance.html). Xem `PLAN.md` và `VALIDATION.md` cho phạm vi đã kiểm tra.
