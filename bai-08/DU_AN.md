# Project độc lập · Bài 8 · Phân khúc khách tại mốc 10/09/2011

Học máy cơ bản · Bài 8 · K-means và khách hàng RFM · PGS.TS Nguyễn Văn Hậu

## Mục tiêu

Tính RFM từ dòng hoá đơn tại một mốc mới, tự viết thuật toán Lloyd và khớp scikit-learn, chọn K có căn cứ (không chỉ một chỉ số), đọc hồ sơ cụm bằng đơn vị gốc, viết đề xuất dưới dạng giả thuyết kèm cách thử nghiệm.

## Dữ liệu

`data/online_retail_lines.csv.gz`: 541.909 dòng hoá đơn (Online Retail, UCI, CC BY 4.0; đọc lại trùng từng ô với tệp xlsx gốc). Chỉ dùng giao dịch trước 10/09/2011 (trừ Nâng cao B). Tại mốc này có 3.370 khách.

## Tệp

- `Bai08_Project_khoi_dau.ipynb`: phát cho sinh viên; có ô TODO và ô tự kiểm.
- `Bai08_Project_loi_giai.ipynb`: giảng viên; đã chạy, mọi ô tự kiểm đạt.
- Mở notebook từ thư mục bài (notebook đọc `data/`).

## Ba mức

| Mức | Điểm | Việc phải làm |
|---|---:|---|
| Đạt | 5 | Bước 1 (RFM tại mốc), bước 2 (log1p + chuẩn hoá), bước 3 (Lloyd tự viết, trùng KMeans cùng khởi tạo), bước 5 (hồ sơ K = 4) và báo cáo một trang |
| Khá | +3 | Bước 4: chọn K bằng inertia, silhouette trên toàn bộ khách và ổn định bootstrap; bảng đánh đổi |
| Nâng cao | +2 | A: k-means++ tự viết (bản gốc, tâm sau rút với xác suất ∝ D²) trên sáu điểm An…Lan, K = 3, chạy 2.000 lần cùng Lloyd tự viết; đếm tỷ lệ dừng ở J = 19/6 và so với chọn đều 3 điểm (40%); hoặc B: khách đổi cụm từ mốc 09/2011 sang 12/2011 |

## Luật chơi

1. Bước 3 không dùng `KMeans` để tính; chỉ dùng để đối chiếu ở ô có ghi rõ.
2. Không dùng dữ liệu từ 10/09/2011 trở đi, trừ Nâng cao B.
3. Không sửa ô tự kiểm. Notebook nộp phải chạy được từ đầu (Restart & Run All).
4. Không có nhãn đúng: không viết “cụm đúng”, “K thật”; viết “cụm tìm được, với căn cứ …”.
5. Mỗi đề xuất hành động phải kèm một cách thử nghiệm có nhóm đối chứng.

## Báo cáo một trang

Năm mục, mỗi mục 2–4 câu: dữ liệu và biểu diễn; thuật toán; chọn K; hồ sơ và đề xuất; giới hạn (ít nhất ba).

## Rubric

Xem `Bai08_Dap_an_va_rubric.md` (dành cho giảng viên).
