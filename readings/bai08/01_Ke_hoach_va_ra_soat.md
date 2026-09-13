# Bước 1 — Rà soát và kế hoạch bài 8

PGS.TS Nguyễn Văn Hậu

Bài 7 đã hoàn tất trước khi bắt đầu bài 8. Đã đọc rà soát khoa học, 60 tiêu đề slide v2, notes phần dữ liệu, mã kmeans_lab.py, case_audit.json và bảng giao dịch/RFM. Đã tra nguồn UCI Online Retail, K-means và silhouette chính thức.

## Các điểm chốt

Online Retail là cửa hàng khác Olist. Một dòng hàng, một hóa đơn và một khách là ba đơn vị khác nhau. R dùng ngày lịch với mốc 10/12/2011; F đếm InvoiceNo phân biệt; M cộng tiền mua dương theo bộ lọc, không gọi doanh thu ròng/lợi nhuận. Giữ khách thật 12755 với 4 dòng, 2 hóa đơn, R=281, M=3811,95 GBP. Không trộn R của pilot cũ. Giữ sáu điểm mô phỏng theo slide, từng nửa bước Lloyd và các số J=39,12,93/8,22/3. K4 là hồ sơ minh họa, K2 có silhouette mẫu cao nhất trong phép quét; chưa khẳng định số cụm thật. Không so inertia giữa các thang khác nhau. Silhouette dùng khoảng cách tới các điểm, không tới tâm; cụm không rỗng mới dùng công thức trung bình.

## Kế hoạch 12 trang

|Trang|Mục thống nhất|Nội dung và hình/bảng|Slide|
|---|---|---|---|
|1|Vấn đề|Khách giống nhau theo cách nào? Mục tiêu và chuỗi hóa đơn→RFM→cụm.|1–3|
|2|Tiên quyết|Vector, bình phương khoảng cách, trung bình, log1p; hai kiểm nhanh.|14–18,22,25|
|3|Dữ liệu|Bốn dòng thật khách 12755; bộ lọc, số dòng và số khách; tính RFM.|4–13|
|4|Ý tưởng|Sáu điểm, hai tâm; gán gần nhất và cập nhật tâm; màu/ký hiệu phân biệt.|19–27|
|5|Công thức|R/F/M, biến đổi, J, gán và trung bình; giải thích ký hiệu/điều kiện.|7–9,15–17,31–33|
|6|Quy trình|Lloyd có kiểm dừng, khởi tạo, cụm rỗng; hình J từng nửa bước.|21–38|
|7|Ví dụ đầy đủ|Bảng khoảng cách lần đầu, tâm mới, Chi đổi nhóm, kết quả cuối.|22–31|
|8|Đọc kết quả|Quét K cùng 4.338 khách và mẫu silhouette 2.000; hồ sơ K4/giới hạn.|39–49|
|9|Tự kiểm|6 câu tính/MCQ: F, khoảng cách, trung bình, J, silhouette, kết luận.|10,18,28,34,44,50|
|10|Ghi nhớ|Checklist và thuật ngữ, nguồn, liên hệ biểu diễn nhiều chiều.|51–54|
|11|Phụ lục A|Đáp án giải thích từng lựa chọn và phép tính.|Notes/quiz|
|12|Phụ lục B|Silhouette bốn điểm; khởi tạo và tối ưu toàn cục; ARI/ổn định.|36–38,41–42,55–59|

## Bước 2 — Xây dựng và kiểm

Tính lại RFM từ tệp gốc và đối chiếu bảng slide; tiền ví dụ dùng Decimal từ đơn giá gốc. Kiểm toàn bộ nửa bước toy, quét K theo cấu hình slide và đối chiếu hồ sơ. Lưu DOCX/PDF/Markdown, hình PNG/SVG, công thức LaTeX, CSV và mã. Xem từng trang PDF xuất từ chính DOCX; kiểm footer tên giảng viên, câu hỏi và đáp án riêng. Đóng gói bài 8 trước khi bắt đầu bài 9. Thời lượng đọc chỉ là ước lượng thiết kế.

Nguồn: Chen (2015), Online Retail, UCI, CC BY 4.0: https://archive.ics.uci.edu/dataset/352/online+retail ; bản Kaggle https://www.kaggle.com/datasets/carrie1/ecommerce-data ; https://scikit-learn.org/1.6/modules/clustering.html#k-means ; https://scikit-learn.org/1.6/modules/generated/sklearn.metrics.silhouette_score.html
