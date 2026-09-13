# Bước 1 — Rà soát và kế hoạch bài 7

PGS.TS Nguyễn Văn Hậu

Đã hoàn thành bài 6 trước khi bắt đầu rà soát bài 7. Đối chiếu báo cáo khoa học, toàn bộ 60 tiêu đề slide v2, notes tình huống Olist, mã leakage_lab.py, case_audit.json và CSV ví dụ. Tra cứu nguồn chính thức scikit-learn 1.6 về common pitfalls và cross-validation.

## Quyết định nội dung

Giữ case Olist của bài 4–6, cùng bảng 79.686 đơn và nhãn ngày lịch. Đích đọc trước: kiểm thời điểm thông tin, vai trò của tập dữ liệu, phạm vi fit và phạm vi kết luận. Không thêm thuật toán dự đoán mới. Tách ba hiện tượng rò rỉ, quá khớp, dịch chuyển phân phối; không suy tính hợp lệ từ chiều tăng giảm điểm. Pipeline không phát hiện cột tương lai. Khách lặp không mặc nhiên là lỗi: cách chia phụ thuộc đích khách cũ tương lai hay khách mới. Test lịch sử không trở thành test mới khi viết lại tài liệu.

## Kế hoạch 12 trang, 10 mục chính thống nhất

| Trang | Mục | Nội dung và minh họa | Bám slide |
|---|---|---|---|
|1|Vấn đề|100% có đáng tin? Bốn câu hỏi kiểm một kết quả; nối bài 6.|1–4|
|2|Tiên quyết|Nhãn thật, đầu vào, fit/transform, tập train/validation/test; hai kiểm nhanh.|4,19–21|
|3|Dữ liệu|Đơn thật 66e4624a…; mốc duyệt, ngày hẹn, ngày giao; bảng nguồn gốc cột.|5–8,13–14|
|4|Ý tưởng|Ranh giới thông tin; sơ đồ pipeline và so rò rỉ/quá khớp/dịch chuyển.|10–12,24|
|5|Công thức|Nhãn ngày lịch, z-score dùng train, accuracy; công thức gắn mẫu số và điều kiện.|8,15–16,22–23|
|6|Quy trình|Khóa mục tiêu → chia → fit trong mỗi fold → chọn → đánh giá; 3-fold sáu hàng.|19–27|
|7|Ví dụ hoàn chỉnh|Train [0,2], điểm giữ lại 10; tính hai scaler, chỉ ra luồng thông tin sai và phản ví dụ dự đoán không đổi.|22–24,45–46|
|8|Đọc kết quả|Mốc nhãn của Olist, tỷ lệ trễ theo thời gian, khách trùng; mô phỏng nhóm và giới hạn so sánh.|30–39,43–49|
|9|Tự kiểm|Sáu câu MCQ/tính/sửa quy trình; chưa lộ đáp án.|9,18,27,35,42,48|
|10|Ghi nhớ|Checklist năm câu, thuật ngữ và nguồn; nối phân cụm.|47–54|
|11|Phụ lục A|Giải thích đáp án và lý do phương án nhiễu sai; chỉ mục ôn.|Quiz/notes|
|12|Phụ lục B|Mô phỏng chọn nhiều ứng viên; nested CV và giới hạn SD fold.|40–41,55–58|

## Bước 2 và tiêu chí hoàn tất

Tạo DOCX chỉnh sửa văn bản/bảng, PDF xuất từ chính Word, Markdown, PNG/SVG, nguồn LaTeX, dữ liệu minh họa và mã tính. Màu navy/teal/amber và icon có ý nghĩa; footer tên giảng viên trên mọi trang. Tính lại nhãn và cửa sổ, ví dụ scaler, 3-fold, mô phỏng nhóm, mô phỏng chọn mô hình; đối chiếu số gốc. Xem toàn bộ trang PDF, sửa khi cần và đóng gói bài 7 trước khi bắt đầu bài 8. Không gọi thời lượng đọc dự kiến hoặc chất lượng tiếp thu là kết quả đã dạy thử.

Nguồn: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce ; https://scikit-learn.org/1.6/common_pitfalls.html ; https://scikit-learn.org/1.6/modules/cross_validation.html
