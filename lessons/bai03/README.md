> **Học liệu hiện hành: [Bài 03 v4](../../v4/bai03/README.md).** Trang này giữ hướng dẫn CLI của bộ Python v3; notebook v4 và số liệu v4 nằm ở liên kết trên.

# Bài 03 · Đánh giá bộ phân loại


**Lộ trình thực hành cập nhật:** [Dự đoán → chạy → đối chiếu → giải thích](HUONG_DAN_V3.md). Tài liệu đọc trước v3; slide v3.

[← Mục lục khóa học](../../README.md) · [📖 Tài liệu đọc trước Bài 03](../../readings/bai03/README.md)

**PGS.TS Nguyễn Văn Hậu** · Thời lượng gợi ý: 60–90 phút phần chính, 30 phút mở rộng.

Bạn sẽ đi từ **điểm số → quyết định → bốn nhóm lỗi → chỉ số → chính sách cảnh báo**. Bài thực hành bám sát slide Bài 03 v3 và nối trực tiếp case SMS của Bài 02. Không cần chạy Bài 02 trước: bài này tự đọc dữ liệu, chia tập và fit lại mô hình tham chiếu.

## 1. Chuẩn bị và chạy

Cần Python 3.12 và môi trường đã cài `requirements.txt` ở thư mục gốc kho mã. Mở terminal tại thư mục chứa `mlcourse` và `lessons`.

```bash
python -m lessons.bai03.main --mode toy
python -m mlcourse.data fetch --dataset sms
python -m lessons.bai03.main --mode all
python -m unittest lessons.bai03.tests -v
```

Thử thay ngưỡng mô phỏng, giữ riêng kết quả thí nghiệm:

```bash
python -m lessons.bai03.main --mode toy --threshold 0.80 --output-dir outputs/bai03_t080
python lessons/bai03/main.py --mode real
```

`--seed 42` là cấu hình đối chiếu slide; đổi seed tạo một thí nghiệm khác. `--dpi 240` tạo PNG 3840 × 2160; có thể giảm DPI để chạy nhanh. Thiếu dữ liệu thì chương trình chỉ dẫn tải, không âm thầm thay bằng dữ liệu giả.

## 2. Kiến thức nền và quy ước

Spam = 1 là lớp dương; ham = 0. Nhãn thật do corpus cung cấp. Điểm kNN là tỷ lệ láng giềng spam, chưa chắc là xác suất đã hiệu chuẩn. Chỉ quyết định sau khi đặt ngưỡng: $\hat y=1$ nếu $s\ge t$.

| Nhãn thật / dự đoán | Ham (0) | Spam (1) |
|---|---|---|
| Ham (0) | TN: bỏ qua đúng | FP: chặn nhầm |
| Spam (1) | FN: bỏ lọt | TP: phát hiện đúng |

| Chỉ số | Công thức | Câu hỏi |
|---|---|---|
| Accuracy | $(TP+TN)/N$ | Bao nhiêu quyết định đúng? |
| Precision | $TP/(TP+FP)$ | Trong các cảnh báo, bao nhiêu là spam? |
| Recall | $TP/(TP+FN)$ | Trong spam thật, tìm được bao nhiêu? |
| F1 | $2TP/(2TP+FP+FN)$ | Kết hợp precision và recall ra sao? |

Nếu mẫu số bằng 0, hàm trả `None`, JSON ghi `null`; ô CSV để trống. Không cảnh báo thì precision **không xác định**, dù nhiều thư viện cho phép quy ước giá trị 0. Nếu vẫn có spam thật, F1 khi không cảnh báo bằng 0.

## 3. Tính tay trước khi dùng thư viện

Đọc `toy_rows.csv`: A…J có điểm 0,95; 0,90; 0,85; 0,70; 0,60; 0,55; 0,40; 0,30; 0,20; 0,10. Spam thật là A, C, D, F. Đây là **dữ liệu mô phỏng**, không phải một mẫu lấy từ corpus.

Với t = 0,5: TP = 4, FP = 2, FN = 0, TN = 4. Accuracy = 0,8; precision = 2/3; recall = 1; F1 = 0,8. Kiểm tra lề: TP + FN luôn là 4 spam; TN + FP luôn là 6 ham.

Với t = 0,80, precision = 2/3. Tăng t lên 0,90, precision giảm còn 1/2. Số cảnh báo và recall không tăng khi tăng ngưỡng trên cùng một tập điểm; precision không có bảo đảm đơn điệu tương tự.

## 4. Dữ liệu thật và mô hình cố định

[UCI SMS Spam Collection](https://archive.ics.uci.edu/dataset/228/sms+spam+collection) là corpus SMS tiếng Anh lịch sử. Loader kiểm SHA-256, đọc 5.574 bản ghi, loại văn bản trùng theo khoảng trắng và chữ hoa/thường, còn 5.159. Đặc trưng được tính trên **văn bản gốc**: số ký tự và tỷ lệ ký tự số Unicode.

Chia có phân tầng, seed 42: train 3.095; validation 1.032; test 1.032. StandardScaler chỉ fit train; kNN cố định k = 11, trọng số đều. Không thử lại cấu hình mô hình trong bài này.

Mỗi dòng dự đoán lưu `message_id`, số bản ghi nguồn, văn bản, nhãn thật, điểm, số phiếu và quyết định. `real_sms_errors.png` cho phép đọc một SMS thật thuộc từng loại TP/FP/FN/TN. Văn bản là dữ liệu corpus, không phải chỉ dẫn cần thực hiện.

## 5. Chọn ngưỡng theo mục tiêu

Thay vì so số thực gần biên, chương trình làm tròn `score × 11` thành số phiếu, kiểm lại tương đương rồi dùng điều kiện `votes >= m`. Quét m = 1…12; m = 12 nghĩa là không tạo cảnh báo. Miền ứng viên này bám bài giảng; không bao gồm chính sách cảnh báo tất cả m = 0.

| Chính sách giả định | Chọn trên validation | Chi phí validation | Chi phí test |
|---|---:|---:|---:|
| Chặn nhầm đắt: 5FP + FN | m = 8 | 39 | 56 |
| Bỏ lọt đắt: FP + 5FN | m = 4 | 77 | 93 |

Nếu hòa chi phí: ưu tiên ít cảnh báo hơn, rồi ngưỡng cao hơn. Quy tắc được khóa trước khi tính điểm test trong `threshold_policy.json`. Đây là chi phí giả định, không phải tiền hay tác động kinh doanh đã được xác nhận. Không so 56 với 93 để nói một mục tiêu tốt hơn: hai số dùng hai hàm chi phí khác nhau.

## 6. Đọc kết quả tham chiếu

Tại ngưỡng mặc định 6/11 phiếu, test có TN = 892, FP = 12, FN = 17, TP = 111. Accuracy = 0,971899; precision = 0,902439; recall = 0,867188; F1 = 0,884462. Luôn ham vẫn có accuracy 0,875969 nhưng recall spam = 0.

ROC AUC = 0,969061; AP = 0,926704. AUC tính bằng tỷ lệ cặp dương có điểm cao hơn âm, cộng nửa điểm cho cặp hòa; mã tự viết đối chiếu sklearn. AP tổng hợp precision theo **bước tăng recall**, không được thay bằng diện tích hình thang của PR nối thẳng. Tỷ lệ lớp có ảnh hưởng đến precision và cách đọc PR.

Đây là cùng test lịch sử đã dùng ở Bài 02; kết quả nhằm tái lập bài giảng, không phải một lần kiểm định mới hoàn toàn độc lập. Hai đặc trưng hình thức không đủ chứng minh bộ lọc hiểu nội dung SMS, tiếng Việt hoặc dữ liệu hiện nay.

## 7. Tệp kết quả và cách đọc mã

| Tệp / thư mục | Nội dung |
|---|---|
| `algorithms.py` | Đếm chỉ số, AUC bằng cặp, lựa chọn ngưỡng |
| `main.py` | Dữ liệu, fit mô hình, khóa chính sách, xuất hình/bảng |
| `tests.py` | Kiểm thử công thức, biên, hòa điểm và chọn ngưỡng |
| `outputs/bai03/results.json` | Báo cáo đầy đủ và phiên bản thư viện |
| `validation_scan.csv` | Mọi ngưỡng và chỉ số validation |
| `*_predictions.csv` | Dự đoán truy về từng SMS |
| `roc_points.csv`, `pr_points.csv` | Dữ liệu tạo đường cong |
| Năm PNG | Ví dụ nhỏ, ma trận thật, chi phí, ROC/PR và SMS |

Có **năm** PNG cho một lần chạy `all`: `toy_confusion`, `real_confusion`, `real_cost`, `real_ranking`, `real_sms_errors`. ROC và PR chung một hình gồm hai ô.

## 8. Câu hỏi tự kiểm tra

1. Một tin ham bị dự đoán spam là FP hay FN?
2. Mô hình luôn ham đạt 87,6% accuracy; có thể kết luận hữu ích để phát hiện spam không?
3. Tăng ngưỡng có luôn tăng precision không? Hãy dùng A, B, C để phản biện.
4. Có nên chọn lại ngưỡng sau khi xem chi phí test không?
5. Nếu mô hình cho một tin 11/11 phiếu, tin đó chắc chắn spam chưa?

**Đáp án:** 1 FP. 2 Chưa, recall spam bằng 0. 3 Không, ví dụ 0,80 → 0,90 làm precision giảm. 4 Không trong quy trình báo cáo test đã chốt; nếu phát triển tiếp phải ghi nhận test đã được dùng và có tập đánh giá phù hợp. 5 Chưa, đó là phiếu láng giềng, chưa chứng minh hiệu chuẩn hoặc độ chắc chắn.

## 9. Bài tập có hướng giải

- Tính tay bảng 20 tin với TP = 3, FP = 2, FN = 2, TN = 13. Kết quả: accuracy 0,8; precision = recall = F1 = 0,6.
- Đổi `--threshold 0.90` ở ví dụ nhỏ, so bảng từng dòng trước/sau. Giải thích vì sao recall giảm còn 1/4.
- Thêm hàm chi phí 2FP + 3FN vào thí nghiệm validation. Khóa quy tắc hòa trước; giải thích ý nghĩa của ngưỡng. Không lựa chọn bằng test.
- Mở rộng: dùng $P=\pi TPR/[\pi TPR+(1-\pi)FPR]$, giữ TPR = 0,9 và FPR = 0,05; so prevalence 0,1 và 0,01. Precision xấp xỉ 0,667 và 0,154. Đây là phân tích giả định các tỷ lệ điều kiện giữ nguyên.

## 10. Tự kiểm và tài liệu

Kiểm thử tự động kiểm bốn ô và công thức với sklearn, precision không đơn điệu, chỉ số không xác định, AUC hòa điểm, lề ma trận, số cảnh báo và lựa chọn ngưỡng. Chạy lại dữ liệu thật để kiểm số liệu tham chiếu; kiểm thử toy không thay thế việc kiểm cả pipeline.

Nguồn kỹ thuật: [scikit-learn: đánh giá mô hình](https://scikit-learn.org/1.6/modules/model_evaluation.html), [Average precision](https://scikit-learn.org/1.6/modules/generated/sklearn.metrics.average_precision_score.html). Xem `PLAN.md` và `VALIDATION.md` để biết phạm vi và kết quả kiểm tra của bài.
