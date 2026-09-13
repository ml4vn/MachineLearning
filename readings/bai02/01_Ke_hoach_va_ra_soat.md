# Kế hoạch tài liệu đọc trước Bài 2

## Bước 1 Rà soát trước khi biên soạn

Bám Bai02_v2 gồm 68 slide, 60 slide chính và 8 mở rộng. Đã đối chiếu bản đồ, notes, case_audit, mã sms_lab và các bảng dữ liệu. Nguồn xác minh: UCI SMS Spam Collection, tài liệu Nearest Neighbors và preprocessing scikit-learn 1.6.1. Bài 1 đã hoàn tất trước khi bắt đầu bài 2.

Giữ một tình huống SMS xuyên suốt, nhưng tách năm điểm mô phỏng tính tay khỏi SMS thật. Dữ liệu gốc 5.574 hàng, bỏ 415 hàng trùng theo quy tắc cố định còn 5.159. Train 3.095, validation 1.032, test 1.032. Hai đặc trưng tính trên văn bản gốc; không tính trên bản dịch hoặc bản rút gọn. Mã dòng không phải thời gian hoặc người gửi. Spam không đồng nghĩa hành vi lừa đảo đã xác minh.

## Kế hoạch 12 trang

| Trang và mục | Nội dung cụ thể | Bảng hoặc hình | Slide tham chiếu |
|---|---|---|---|
| 1 Vấn đề | Dự đoán ham/spam từ ví dụ có nhãn, mục tiêu và cách đọc | Sơ đồ SMS đến phiếu | 1–9 |
| 2 Kiến thức đầu vào | Vector, chênh lệch, bình phương, căn, tỷ lệ; kiểm nhanh | Bảng thao tác số và một công thức mẫu | 8, 11, 21, 37 |
| 3 Dữ liệu thật | Nguồn và phiên bản; hai SMS nguyên văn, diễn nghĩa; đếm số và vector | Bảng dữ liệu, phần chữ số có thể kiểm | 2–7, 11–17 |
| 4 Trực giác kNN | Năm điểm mô phỏng; chọn hàng xóm trước, đọc nhãn sau; so k3/k5 | Đồ thị cùng tỷ lệ và bảng d² | 19–30 |
| 5 Khái niệm và công thức | Khoảng cách, phiếu đều, z-score; ý nghĩa ký hiệu; điều kiện | LaTeX và bảng phân biệt L2 theo hàng với chuẩn hóa theo cột | 21, 27, 36–38 |
| 6 Quy trình | Bỏ trùng, chia tập, fit scaler train, lưu mẫu, chọn k validation, khóa test | Sơ đồ ba vai trò và thống kê train thật | 5–7, 39–43, 48–50 |
| 7 Ví dụ trọn vẹn | Query 4500 nguyên văn, đếm 123/14, tính z, so 6 láng giềng thật | Bảng khoảng cách trước/sau và nhãn, kết luận đúng phạm vi | 43–46 |
| 8 Đọc kết quả | Toàn validation, k minh họa khác k đã chọn; 29 lỗi test và giới hạn | Biểu đồ số lỗi sáu cấu hình, bảng hiểu nhầm | 47–56, 60 |
| 9 Tự kiểm tra | Sáu câu: đặc trưng, khoảng cách, lá phiếu, chuẩn hóa, chọn k, kết luận | Câu hỏi không kèm đáp án | 10,18,30,34,42,49,56–58 |
| 10 Ghi nhớ | Quy trình, từ vựng, nguồn và nối đánh giá bài 3 | Bảng thuật ngữ | 53,59–60,68 |
| 11 Phụ lục A | Giải kiểm nhanh và sáu câu; vì sao phương án nhiễu sai | Lời giải và hướng ôn | Notes câu hỏi |
| 12 Phụ lục B tùy chọn | Đổi đơn vị làm đảo láng giềng; z-score bất biến đổi đơn vị dương; điểm xa và hòa | Phản ví dụ số, khoảng cách có điều kiện | 31–33,38,41,61–67 |

## Kiểm soát khoa học và sư phạm

- Tỷ lệ chữ số chỉ là đặc trưng, tỷ lệ phiếu chưa là xác suất được hiệu chỉnh.
- k lẻ tránh hòa phiếu chỉ với hai lớp và phiếu đều; hòa khoảng cách tại ranh giới là việc khác.
- StandardScaler dùng trung bình và độ lệch chuẩn mẫu số n trên train; không ép mỗi hàng về độ dài 1 hay ép mọi giá trị vào [0,1].
- k3 giúp minh họa; mô hình chấm test đã khóa là k11 có scaler, chọn bằng F1 spam validation trong các cấu hình đã thử. Không thay mô hình sau khi xem test.
- Query 4500 chọn có chủ đích; không dùng nó làm bằng chứng hiệu năng toàn bộ. Không đo Euclid thô bằng mắt trên trục khác tỷ lệ.
- Kiểm lại số đếm trên văn bản, các khoảng cách và phiếu, thống kê scaler, bảng lỗi validation, ma trận test từ CSV. Dữ liệu thật giữ mã truy vết; hình mô phỏng có nhãn.

## Điều kiện hoàn tất bước 2

Đủ 10 mục chung, đáp án tách riêng, phần mở rộng không bắt buộc. PDF và DOCX có chữ Việt, màu và icon có ý nghĩa, PGS.TS Nguyễn Văn Hậu và số trang. Có nguồn LaTeX, ảnh PNG/SVG, CSV ví dụ, mã tái lập. Render chính DOCX bằng Word đã được phép và xem mọi trang; sửa trước khi đóng gói, sau đó mới bắt đầu bài 3. Thời gian đọc 30–40 phút chỉ là ước lượng thiết kế.
