# Bài 05 — Kế hoạch và rà soát trước khi biên soạn

## Bước 1: đối chiếu và chốt tuyến học

Bài 4 đã hoàn tất và đóng gói trước khi bắt đầu bước này. Đối chiếu 68 slide Bài05_v2 (60 chính, 8 tùy chọn), notes, báo cáo điều chỉnh khoa học, case_audit.json, model_policy.json, logistic_lab.py, CSV mô hình/dự đoán và bốn hàng tính tay. Tham khảo nguồn Olist trên Kaggle, Stanford CS229 và scikit-learn 1.6.1.

Mục tiêu: tự đi từ đặc trưng tới logit, xác suất mô hình và quyết định; phân biệt xác suất với odds; tính BCE và một bước gradient; đọc kết quả có giới hạn, nhất là mô hình có accuracy cao nhưng recall thấp.

## Kế hoạch 12 trang theo 10 mục chung

| Trang | Mục | Nội dung và cách minh họa | Slide đối chiếu |
|---|---|---|---|
| 1 | Vấn đề | Cùng Olist nhưng đổi nhãn từ số ngày sang trễ 0/1; bốn bước X→z→p→nhãn | 1–2,9,12 |
| 2 | Tiên quyết | Vector, tổ hợp tuyến tính, số mũ/log, xác suất/nhãn; bảng và 2 kiểm nhanh | 11–19 |
| 3 | Dữ liệu | Hai bản ghi thật minh họa ngày lịch, sáu đặc trưng, bảng train/val/test và số trễ | 3–8,42–43 |
| 4 | Ý tưởng | Sigmoid trên hình, ví dụ z=−0,8; một điểm p nhưng hai ngưỡng khác quyết định | 11–15,19 |
| 5 | Khái niệm/công thức | Odds, logit, BCE hai nhánh và trung bình; đồ thị phạt dự đoán tự tin sai | 16–18,21–25 |
| 6 | Quy trình | Gradient p−y theo logit, theo w/b; cập nhật đồng thời; tách GD tính tay với Newton-CG/L2 thật | 27–30,36,42–44 |
| 7 | Ví dụ | Toy A–D x=[−1,0,1,2], y=[0,0,1,1]; bảng gradient, bước đầu b=0,w=0,5, p và loss mới | 26–38 |
| 8 | Kết quả | Quét sáu ngưỡng validation theo FP+5FN, test tại 0,5 và 0,1, chỉ ra recall thấp | 45–55 |
| 9 | Tự kiểm | 6 câu nhãn/ngưỡng, odds, gradient, BCE và kết luận case | Q1–Q6 và 57–58 |
| 10 | Ghi nhớ | Glossary, checklist, nguồn, giới hạn và nối sang cây quyết định bài 6 | 54,59–60,68 |
| 11 | Phụ lục A | Giải thích đáp án, phương án nhiễu và chỗ cần ôn | Phần chính |
| 12 | Phụ lục B | 19 quan sát thiết kế với odds gấp đôi; phân tách hoàn toàn, L2/C, Brier và hiệu chuẩn | 61–66 |

## Điểm khoa học bắt buộc giữ

- late=1 khi ngày lịch giao thực tế lớn hơn ngày lịch hẹn; giao trong ngày hẹn vẫn là 0. Đây là quy ước của case, không phải xác minh SLA từng đơn.
- Nhãn ngày lịch khác delivery_days của bài 4. Không lấy ngày giao thực tế hoặc delivery_days làm đầu vào tại lúc duyệt đơn.
- Chia thời gian và dùng nhãn train/validation đã biết trước ranh giới. 29.031/10.389/40.266 hàng, số trễ 941/634/3.478; tỷ lệ có thay đổi giữa các tập. Giữ giới hạn chọn mẫu đã hoàn tất.
- Xác suất từ sigmoid thuộc (0,1) với logit hữu hạn, nhưng chưa tự được hiệu chuẩn. Logistic giả định log-odds tuyến tính; tính đơn điệu không xác định duy nhất sigmoid.
- Odds nhân exp(w) khi tăng một tọa độ một đơn vị và giữ các tọa độ khác; xác suất không nhân theo cùng hệ số, và hệ số không chứng minh nhân quả.
- BCE dùng log tự nhiên; p−y là đạo hàm theo logit, không phải toàn bộ vector gradient. Học toy bằng BCE trung bình không phạt; case thật dùng L2, C=1, solver Newton-CG, không phải GD minh họa.
- Quét ngưỡng [0,05;0,10;0,15;0,20;0,30;0,50] trên validation theo chi phí giả định FP+5FN; hòa chọn ít cảnh báo rồi ngưỡng lớn hơn. Khóa 0,10; test lịch sử không là kiểm độc lập mới.
- Test ngưỡng 0,5: TN 36.788, FP 0, FN 3.478, TP 0. Ngưỡng 0,1: TN 36.429, FP 359, FN 3.317, TP 161. Trình bày cả việc tìm thêm đơn trễ và phần lớn đơn trễ vẫn bỏ lọt; không tuyên bố hiệu quả triển khai.
- 16 đơn thiếu toàn bộ khối lượng đã bị tổng hợp thành 0 trong bảng đóng băng; giữ để so khớp slide nhưng không diễn giải là đo được 0 gram. Cải tiến xử lý thiếu cần thí nghiệm mới.
- Bốn toy phân tách hoàn toàn không có nghiệm MLE hữu hạn không phạt; 19 quan sát là dữ liệu thiết kế cho kiểm đại số, không phải Olist hoặc chứng minh giả định trên dữ liệu thật.

## Bước 2: biên soạn, tính lại, xuất và kiểm

Tạo DOCX/PDF/Markdown, PNG/SVG và LaTeX; dùng cùng màu, icon và footer PGS.TS Nguyễn Văn Hậu. Tái tính nhãn từ timestamps; fit lại logistic bằng đúng cấu hình để đối chiếu toàn bộ điểm test/validation; quét ngưỡng và tính số đếm; kiểm toy bằng sai phân hữu hạn và kiểm 19 quan sát. Xuất từ chính DOCX bằng Word, dựng PNG PDF và xem từng trang. Chỉ đóng gói khi nội dung, phép tính và hình thức đạt; sau đó lập mục lục và gói chung cho 5 bài đầu.
