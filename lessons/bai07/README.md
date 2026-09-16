# Bài 07 · Đánh giá đáng tin cậy


**Lộ trình thực hành cập nhật:** [Dự đoán → chạy → đối chiếu → giải thích](HUONG_DAN_V3.md). Tài liệu đọc trước v3; slide v2.

[← Mục lục khóa học](../../README.md) · [📖 Tài liệu đọc trước Bài 07](../../readings/bai07/README.md)

**PGS.TS Nguyễn Văn Hậu** · 90 phút phần chính, 45 phút mở rộng.

Một mô hình đạt 100% có thể đang dùng đáp án từ tương lai. Bài này giúp bạn kiểm **cách tạo ra điểm số**, tiếp nối Olist ở Bài 04–06 và bám 60 slide Bài 07 v2.

## 1. Mục tiêu và cách chạy

Bạn sẽ phân biệt rò rỉ, quá khớp và dịch chuyển dữ liệu; fit pipeline trong từng fold; chọn cách chia theo thời gian/nhóm; giải thích vai trò nested CV. Cần biết train/validation/test, chuẩn hóa và chỉ số phân loại.

Tại thư mục gốc kho mã, dùng Python 3.12 đã cài `requirements.txt`:

```bash
python -m lessons.bai07.main --mode toy
python -m mlcourse.data fetch --dataset olist
python -m lessons.bai07.main --mode all
python -m unittest lessons.bai07.tests -v
```

Bài tự chuẩn bị Olist từ ZIP; không cần đầu ra của bài trước. `--dpi 240` tạo ảnh 3840 × 2160. `--seed 42` điều khiển chia nhóm và dữ liệu/outer split nested CV. Nhãn mô phỏng nhóm dùng seed 73; mô phỏng chọn nhiều ứng viên dùng seed 2026 cố định để đối chiếu slide.

## 2. Phân biệt ba vấn đề

| Vấn đề | Cơ chế | Ví dụ |
|---|---|---|
| Rò rỉ dữ liệu | Quy trình học/chọn thấy thông tin chưa được phép dùng | Ngày giao thực tế làm đầu vào khi dự đoán lúc duyệt |
| Quá khớp | Học cả chi tiết/ngẫu nhiên không tổng quát tốt | Cây nhiều lá ghi nhớ nhiễu train |
| Dịch chuyển phân phối | Dữ liệu đánh giá/triển khai khác phân phối học | Tỷ lệ trễ Olist thay đổi theo thời kỳ |

Các vấn đề có thể đồng thời xảy ra. Điểm tăng mạnh hoặc tương quan cao chỉ là dấu hiệu cần kiểm, không tự chứng minh rò rỉ. Rò rỉ cũng không bảo đảm mọi lần chạy đều tăng điểm.

## 3. Fit và transform bằng ba số

Train = [0,2], điểm mới = 10. StandardScaler dùng phương sai với mẫu số n:

| Quy trình | Trung bình | Độ lệch chuẩn | z của điểm 10 |
|---|---:|---:|---:|
| Fit chỉ train | 1 | 1 | 9 |
| Fit sai cả train và điểm mới | 4 | sqrt(56/3) ≈ 4,320494 | ≈ 1,388730 |

`fit` học tham số; `transform` áp dụng tham số đã học. Với dữ liệu đánh giá độc lập theo giao thức này, không đưa điểm mới vào `fit`. Tuy nhiên, một phép biến đổi affine dương chung trong 1D vẫn giữ thứ tự khoảng cách đến láng giềng; giá trị z thay đổi không có nghĩa nhãn kNN nhất thiết thay đổi. Kiểm thử giữ phản ví dụ này.

## 4. Pipeline bên trong từng fold

Sáu dòng mô phỏng được chia K-fold = 3; mỗi lần có 4 dòng train và 2 validation, mỗi dòng làm validation đúng một lần. Mã fit pipeline mới cho từng fold rồi kiểm trung bình scaler bằng trung bình của **train fold**.

```python
pipe = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler()),
    ('model', LogisticRegression(solver='newton-cg')),
])
pipe.fit(X[train_ids], y[train_ids])
pred = pipe.predict(X[validation_ids])
```

Đặt pipeline vào `GridSearchCV` để mỗi inner fold fit lại các bước. Fit scaler trước rồi đưa dữ liệu đã chuẩn hóa vào CV vẫn có thể rò rỉ. Pipeline không tự sửa một cột chứa tương lai hoặc một phép chia không phù hợp.

## 5. Khi một nhóm xuất hiện nhiều lần

Mô phỏng 200 nhóm, mỗi nhóm 4 dòng có cùng nhãn. Bộ ghi nhớ lưu nhãn của nhóm đã thấy; nhóm mới dùng lớp đa số train, hòa thì chọn 0. Không có thuật toán phức tạp hoặc thông tin ngữ nghĩa nào ở đây.

| Chia dữ liệu | Nhóm chung train/validation | Accuracy |
|---|---:|---:|
| Chia theo dòng | 118 | 97,5% |
| GroupShuffleSplit | 0 | 42,5% |

Hai cách chia trả lời câu hỏi khác nhau: gặp lại nhóm quen hay dự đoán nhóm mới. Nhóm lặp không tự động là lỗi trong mọi ứng dụng. Với Olist, chương trình kiểm có 363 `customer_unique_id` xuất hiện ở cả train/test; cần dựa vào đích triển khai để quyết định đây là điều chấp nhận được hay cần chia theo khách.

## 6. Chọn nhiều lần và nested CV

Mỗi ứng viên mô phỏng chỉ có khả năng ngẫu nhiên 50%; đo trên 100 phép thử nhị phân. Lặp toàn thí nghiệm 500 lần; chọn tốt nhất trong 1, 10 hoặc 100 ứng viên, rồi đo ứng viên đã chọn trên mẫu mới độc lập.

Với 100 ứng viên, điểm dùng để chọn trung bình khoảng 0,62396, còn điểm mẫu mới khoảng 0,49926. Hiệu ứng chọn làm điểm tốt nhất lạc quan dù bản thân các ứng viên không tốt hơn ngẫu nhiên. Không cần gọi `fit(test)` mới khiến test mất vai trò độc lập; dùng điểm test để đổi cấu hình cũng đủ.

Phần **bổ sung chạy được** dùng 300 dòng/12 đặc trưng mô phỏng, outer StratifiedKFold = 3, inner = 3, grid C = [0,1;1;10]. Trong từng outer-train, inner CV chọn C, refit pipeline trên outer-train, rồi chấm outer-validation. Outer không tham gia lựa chọn trong lần đó. Tệp membership cho phép kiểm ID; mỗi outer có 200 dòng train và 100 dòng đánh giá.

Điểm outer đánh giá thủ tục chọn trong thiết lập này, không phải bảo đảm triển khai. Điểm inner và outer của từng fold không bắt buộc có thứ tự cố định. SD giữa fold không tự là khoảng tin cậy vì các mô hình có tập train chồng lấp.

## 7. Olist: kiểm cột tương lai và lúc biết nhãn

Nguồn [Olist trên Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce); nhãn trễ theo ngày lịch, cùng tập 29.031/10.389/40.266 đơn của Bài 04–06.

Chương trình cố ý tạo cột **KHÔNG HỢP LỆ**: số ngày lịch giao thực tế trừ ngày hứa giao. Quy tắc `future_late_days > 0` tái tạo đáp án, đạt ma trận test [[36.788,0],[0,3.478]]. Tên tệp `INVALID_future_column_predictions.csv` và tiêu đề hình nhắc rõ đây là ví dụ để phê bình, không phải một mô hình tốt.

Từ orders gốc, có **1.490** đơn duyệt trong 01/01–31/10/2017 nhưng giao từ 01/11/2017 trở đi. Chỉ nhìn ngày duyệt sẽ đưa nhãn chưa biết vào train tại cutoff. Con số này tính trên orders gốc trước toàn bộ lọc đủ điều kiện mô hình.

Đơn `66e4624ae69e7dc89bd50222b59f581f` được duyệt 09/03/2018, hứa giao 02/04 và giao 03/04. Tại mốc minh họa 01/04, chưa biết kết quả. Timeline dùng cutoff này để giải thích; đây không phải mốc chia train/test chính của khóa học.

`column_provenance.csv` tách sáu đặc trưng dự kiến có ở thời điểm duyệt khỏi cột kết quả tương lai. Snapshot sản phẩm/địa lý tĩnh chưa chứng minh lịch sử sẵn có; thông tin được giả định phải ghi rõ là giả định.

## 8. Cửa sổ thời gian và phạm vi kết luận

Phần **bổ sung** chạy ba cửa sổ trong giai đoạn train lịch sử; mỗi lần fit mới pipeline logistic C = 1, không dùng holdout test để chọn:

| Train bắt đầu | Cutoff train | Cửa sổ validation | Thời điểm cần biết nhãn validation |
|---|---|---|---|
| 01/01/2017 | 01/05/2017 | Tháng 5–6 | Trước 01/07/2017 |
| 01/01/2017 | 01/07/2017 | Tháng 7–8 | Trước 01/09/2017 |
| 01/01/2017 | 01/09/2017 | Tháng 9–10 | Trước 01/11/2017 |

Train mỗi fold chỉ chứa đơn duyệt và giao trước cutoff. Chương trình xuất số mẫu, ngày nhãn cuối, AP và danh sách ID theo vai trò. Cách lọc nhãn biết trước cuối cửa sổ loại các đơn chưa hoàn tất; kết quả vẫn điều kiện trên nhóm đã giao, chưa giải quyết đầy đủ kiểm duyệt phải/chọn mẫu.

Tỷ lệ trễ chính của train/validation/test lần lượt khoảng 3,24%/6,10%/8,64%. Cần đọc chỉ số cùng thay đổi thời kỳ và tỷ lệ lớp. Điểm số dự báo hoặc giảm cost giả định không chứng minh một hành động can thiệp sẽ hiệu quả. Test lịch sử đã được xem trong pilot khóa học; không gọi là test mới độc lập.

## 9. Tệp kết quả và câu hỏi tự kiểm tra

`outputs/bai07/` có năm PNG: `toy_scaler_folds`, `toy_group_selection`, `toy_nested_cv`, `real_leakage`, `real_timeline`. CSV/JSON lưu phép chuẩn hóa, fold, nhóm và dự đoán, 500 lần chọn, dữ liệu nested/inner grid/outer membership, thống kê thật, các nhãn sau cutoff, khách lặp, provenance và các cửa sổ rolling.

1. Bỏ cột ngày giao nhưng giữ số ngày trễ tính từ ngày giao có hết rò rỉ? **Không**, cột dẫn xuất vẫn chứa tương lai.
2. Pipeline fit trước chia fold có hợp lệ theo bài này? **Không**, phải fit trong mỗi train fold.
3. Duyệt 30/10, giao 02/11 có được dùng nhãn để học tại 01/11? **Không**.
4. Khách lặp giữa train/test luôn sai? **Không**, phụ thuộc mục tiêu; cần phân biệt khách quen và khách mới.
5. Chọn trong 100 mô hình bằng điểm test có giữ test độc lập? **Không**, test đã tham gia lựa chọn.

## 10. Bài tập, kiểm chứng và nguồn

- Mở bảng fold, xác minh mỗi dòng toy làm validation đúng một lần và không nằm trong train cùng fold.
- Dùng một đơn trong `labels_after_cutoff.csv`, viết một câu vì sao ngày duyệt chưa đủ.
- Đọc `rolling_membership.csv`, kiểm từng train đều giao trước cutoff và phân tích một fold có AP khác fold kia.
- Đổi seed nested CV, so C được chọn. Không biến dao động qua ba fold thành khẳng định độ tin cậy thống kê.
- Rà một notebook theo năm câu: dự đoán lúc nào; cột biết lúc nào; preprocessing fit đâu; cách chia phù hợp ai/thời kỳ nào; test đã dùng để quyết định gì?

Sáu kiểm thử kiểm phép tính scaler, thứ tự láng giềng 1D, coverage/disjointness, fit pipeline từng fold, mô phỏng nhóm, thời điểm nhãn, hiệu ứng chọn và đầu vào sai. Lệnh real kiểm thêm quy tắc tương lai tái tạo nhãn và chạy ba pipeline thời gian từ dữ liệu gốc.

Nguồn: [tránh rò rỉ dữ liệu](https://scikit-learn.org/1.6/common_pitfalls.html#data-leakage), [cross-validation](https://scikit-learn.org/1.6/modules/cross_validation.html), [nested CV](https://scikit-learn.org/1.6/auto_examples/model_selection/plot_nested_cross_validation_iris.html). Xem `PLAN.md` và `VALIDATION.md` cho phạm vi kiểm định.
