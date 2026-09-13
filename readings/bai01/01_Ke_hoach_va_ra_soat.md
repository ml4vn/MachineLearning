# Kế hoạch tài liệu đọc trước Bài 1

## Phạm vi và nguồn

Bám bản Bai01_v2 gồm 64 slide, đã đọc mục tiêu, notes, bảng ví dụ và báo cáo khoa học. Chủ đề: vector và độ tương đồng cosine qua MovieLens. Đối tượng: sinh viên trung bình, biết nhân cộng, bình phương và căn; không cần Python. Giữ The Matrix làm tham chiếu và thứ tự Action, Comedy, Sci-Fi.

Đã đối chiếu nguồn GroupLens và tài liệu cosine_similarity scikit-learn 1.6.1. Dùng snapshot movies.csv kèm slide, không tải lại nhánh latest. Ví dụ phim là bản ghi thật được chọn có chủ đích; hình học 2D là mô phỏng có nhãn.

## Kế hoạch từng phần trước khi biên soạn

| Trang | Mục | Nội dung cụ thể | Hình hoặc bảng | Slide bám theo |
|---|---|---|---|---|
| 1 | 1 Vấn đề và mục tiêu | Tương tự theo metadata; 4 năng lực sau đọc; cách dùng tài liệu | Sơ đồ phim → nhãn → vector → điểm | 1–4 |
| 2 | 2 Kiến thức đầu vào | Tọa độ, bình phương, căn, ký hiệu tổng; kiểm nhanh có đáp án ở phụ lục | Tam giác 3–4–5, bảng phép tính | 12–15 |
| 3 | 3 Dữ liệu thật | Thẻ MovieLens; movieId là định danh; 6 dòng thật; multi-hot cùng thứ tự | Bảng ID, tên, nhãn và bit; nguồn | 5–10 |
| 4 | 4 Trực giác | Hướng khác độ dài; cùng dot chưa cùng cosine; giữ đúng góc trên hình 2D | Các góc 0, 45, 90 độ; minh họa chuẩn hóa | 16–18 |
| 5 | 5 Công thức | Dot, chuẩn L2, cosine; nghĩa ký hiệu và điều kiện; miền giá trị | 4 công thức LaTeX, bảng ký hiệu | 13–21 |
| 6 | 6 Quy trình | Cố định schema, mã hóa, kiểm chuẩn, tính, xếp hạng có đồng hạng; không có bước học tham số ở case này | Sơ đồ tính và quyết định vector 0 | 23–24, 30, 38, 50 |
| 7 | 7 Ví dụ hoàn chỉnh | Matrix so Men in Black; tính từng tích, hai chuẩn, phân số và diễn giải; bảng 5 ứng viên | Bảng trung gian và kết quả đúng số | 25–34 |
| 8 | 8 Đọc kết quả và giới hạn | 3 trục so 19 nhãn; cosine không là xác suất thích; Casablanca và Toy Story | Biểu đồ so 2 biểu diễn; bảng hiểu nhầm | 36–49 |
| 9 | 9 Tự kiểm tra | 6 câu mới theo năng lực, gồm tính và đọc hình; nhiệm vụ trước lớp; nơi ghi vướng mắc | Câu hỏi rõ lựa chọn, không lộ đáp án | 11,22,32,43,49,52–54 |
| 10 | 10 Những điều cần nhớ | Tóm tắt quy trình, từ vựng, điều kiện, nguồn và liên kết bài 2 | Bảng thuật ngữ ngắn | 42,55–56,64 |
| 11 | Phụ lục A | Giải cả câu ôn đầu vào và 6 câu; chỉ nguồn lỗi, hướng ôn lại | Lời giải phân bước | Notes tương ứng |
| 12 | Phụ lục B | Bất biến nhân dương, quan hệ L2 sau chuẩn hóa; hệ số âm và zero | 3 công thức; bài mở rộng nhỏ | 57–63 |

## Điểm khoa học cần giữ

- 0/1 biểu thị nhãn trong dữ liệu, không biểu thị mức thích. ID không phải tọa độ để đo khoảng cách.
- Cosine cần hai vector khác 0, cùng schema. Vector thực có miền [-1,1]; không âm thì [0,1].
- Không dùng hình 2D thay cho góc chính xác của vector phim 3D.
- Cosine bằng 1 ở các bit nhị phân khác 0 nghĩa là cùng vector; với vector thực nói chung chỉ cùng hướng.
- Cùng dot không bảo đảm cùng cosine. Thêm nhãn có thể tăng hoặc giảm điểm. Giữ nhóm đồng hạng.
- Đối chiếu số tính được chỉ kiểm phép tính, không chứng minh chất lượng gợi ý cá nhân.

## Tiêu chí hoàn tất bước 2

PDF và DOCX cùng nội dung, chữ tiếng Việt đọc được, footer giảng viên và số trang; màu navy–amber cùng icon có nhãn. Mỗi công thức có diễn giải và điều kiện, hình có chú thích nguồn. Đáp án tách khỏi câu hỏi. Tính lại bảng phim từ CSV; kiểm mọi công thức số và đáp án; render DOCX và xem đủ mọi trang, sửa rồi xem lại trang thay đổi. Lưu mã nguồn, LaTeX, ảnh và kết quả kiểm trước khi bắt đầu bài 2.

Thời gian tự học 30–40 phút là ước lượng thiết kế, chưa đo trên lớp; phụ lục B tùy chọn.
