# Project độc lập · Bài 1 · Gợi ý phim cho nhóm người xem để dành

Học máy cơ bản · Bài 1 · Vector và độ tương đồng cosine · PGS.TS Nguyễn Văn Hậu

## Mục tiêu

Lặp lại toàn bộ chuỗi của bài trên người xem **chưa xuất hiện trên slide**: tự viết cosine an toàn, dựng vector nhãn, tìm phim giống với quy tắc đồng hạng; xây hồ sơ theo nhãn và theo hành vi; đánh giá trung thực (chỉ dữ liệu trước thời điểm giấu, so mốc phổ biến theo cặp); ghi quy tắc chọn trước rồi chấm nhóm kiểm tra cuối đúng một lần.

## Dữ liệu

`data/raw/movielens.zip` (MovieLens latest-small, GroupLens; giấy phép cho nghiên cứu và giảng dạy, không thương mại). Nhóm người trong `data/project_users_bai01.json`, chia theo seed 2027 trong số 597 người đủ điều kiện: bài giảng 300 (đã dùng trên slide), phát triển 149, kiểm tra cuối 148.

## Tệp

- `Bai01_Project_khoi_dau.ipynb`: phát cho sinh viên; có ô TODO và ô tự kiểm.
- `Bai01_Project_loi_giai.ipynb`: giảng viên; đã chạy, mọi ô tự kiểm đạt.
- Mở notebook từ thư mục bài. Hàm `cham_cuoi` ghi dấu vết vào `.project_bai01_cham_cuoi.json` (chuỗi cấu hình và mã băm gợi ý trên nhóm phát triển); đây là cơ chế nhắc kỷ luật, không phải bảo mật.

## Ba mức

| Mức | Điểm | Việc phải làm |
|---|---:|---|
| Cơ bản | 5 | Bước 1–3: cosine an toàn; ma trận 19 nhãn; top 10 cho Toy Story, Pulp Fiction, Inception với quy tắc đồng hạng; đối chiếu scikit-learn |
| Khá | +3 | Bước 4–5: gợi ý theo nhãn và theo hành vi; hit@20 trên nhóm phát triển; so theo cặp với mốc phổ biến; quy tắc chọn ghi trước; chấm nhóm cuối một lần; báo cáo một trang |
| Nâng cao | +2 | Một trong: A · trọng số IDF; B · vector từ tags.csv; C · trộn nhãn và hành vi với α chọn trên nhóm phát triển |

## Luật chơi

1. Không đọc nhóm kiểm tra cuối trực tiếp; chỉ chấm bằng `cham_cuoi`, một lần.
2. Mọi lựa chọn (cách gợi ý, α, trọng số) làm trên nhóm phát triển.
3. Không sửa ô tự kiểm. Notebook nộp phải chạy được từ đầu (Restart & Run All).
4. Báo cáo đọc kết quả đúng mức: cosine không phải xác suất; hit@20 là tỷ lệ người; chênh lệch nhỏ trên nhóm nhỏ thì nói “chưa phân biệt được”.

## Báo cáo một trang

Bốn mục, mỗi mục 2–4 câu: dữ liệu và giao thức; cài đặt và đối chiếu; đánh giá (bảng ba cách, so theo cặp, quy tắc chọn, kết quả nhóm cuối); diễn giải và giới hạn (ít nhất ba).

## Rubric

Xem `Bai01_Dap_an_va_rubric.md` (dành cho giảng viên).
