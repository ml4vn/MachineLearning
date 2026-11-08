# Project độc lập · Bài 7 · Có nên thêm tỷ lệ trễ của người bán vào cảnh báo lúc duyệt đơn?

Học máy cơ bản · Bài 7 · Đánh giá đáng tin cậy · PGS.TS Nguyễn Văn Hậu

## Câu hỏi

Hệ thống cảnh báo đơn trễ của Bài 5 dùng sáu đặc trưng có lúc duyệt. Đồng nghiệp đề xuất thêm r, tỷ lệ trễ lịch sử của người bán. Hãy trả lời bằng một đánh giá trung thực: kiểm cột, fit trong fold, chia theo thời gian, so theo cặp, ghi quy tắc chọn trước, chấm tập cuối một lần.

## Dữ liệu

`data/olist_extended_v3.csv.gz` (Olist, Kaggle; SHA-256 bắt đầu bằng ce93d20c): 63.953 đơn đủ điều kiện duyệt 01/2017–03/2018, nhãn cuối cùng, kèm người bán (dòng hàng đầu), khách, đánh giá, ngày giao hãng.
- **Phát triển:** 43.345 đơn duyệt năm 2017; 8 fold cuốn theo tháng T5–T12/2017 (phần học: đơn đã giao trước ngày 1 của tháng; phần chấm: mọi đơn duyệt trong tháng).
- **Tập cuối:** 20.608 đơn duyệt 01–03/2018, chỉ chấm qua `cham_cuoi`, đúng một lần. Giai đoạn này thuộc test lịch sử của Olist (đã xem ở các bài trước), nhưng chưa từng được dùng để chọn logistic + r.

## Tệp

- `Bai07_Project_khoi_dau.ipynb`: phát cho sinh viên; có ô TODO và ô tự kiểm.
- `Bai07_Project_loi_giai.ipynb`: giảng viên; đã chạy, mọi ô tự kiểm đạt; chứa kết quả tập cuối.
- Mở notebook từ thư mục bài. Hàm `cham_cuoi` ghi dấu vết vào `.project_bai07_cham_cuoi.json`; đây là cơ chế nhắc kỷ luật, không phải bảo mật.

## Sáu bước, ba mức, ba mốc

| Bước | Việc | Mức | Mốc |
|---|---|---|---|
| 1 | Kiểm cột theo thời điểm duyệt; ghi giả định | cơ bản | M1 |
| 2 | Chia theo tháng; dựng r chỉ từ phần học (m = 10); r của dòng học tính chéo | cơ bản | M1 |
| 3 | Vòng K-fold tự viết khớp cross_validate; r trong và ngoài fold | cơ bản | M2 |
| 4 | Cuốn theo 8 tháng: LOG so với LOG + r, so theo cặp, kiểm định dấu | cơ bản | M2 |
| 5 | Ghi quy tắc chọn trước khi xem tập cuối | khá | M3 |
| 6 | `cham_cuoi` một lần; báo cáo một trang | khá | M3 |

**Điểm:** cơ bản 5, khá 3, nâng cao 2. **Nâng cao** (chọn một): A · người bán mới (chia theo nhóm kết hợp thời gian); B · chọn m bằng đánh giá lồng theo thời gian; C · dự đoán lúc giao hãng, đánh đổi với thời gian can thiệp.

## Luật chơi

1. Không đọc `_CUOI` trực tiếp; chỉ chấm bằng `cham_cuoi`, một lần.
2. Mọi lựa chọn (thêm r hay không, m, cách chia) làm trên dữ liệu phát triển.
3. Không sửa ô tự kiểm. Notebook nộp phải chạy được từ đầu (Restart & Run All).
4. Báo cáo đúng mức: AP kèm tỷ lệ nền; so theo cặp; “chưa phân biệt được” là một câu trả lời hợp lệ.

## Báo cáo một trang

Theo mẫu báo cáo có điều kiện của bài: bài toán và thời điểm; quy trình; đánh giá (bảng 8 tháng, so theo cặp, quy tắc chọn, kết quả tập cuối); kết luận và ít nhất ba giới hạn.

## Rubric

Tái lập 3 · cài đặt và đối chiếu 3 · đánh giá 2 · diễn giải và giới hạn 2. Chấm cách làm, không chấm con số AP cao hay thấp. Chi tiết trong `Bai07_Dap_an_va_rubric.md` (giảng viên).
