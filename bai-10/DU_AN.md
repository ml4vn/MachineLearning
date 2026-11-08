# Project độc lập · Bài 10 · Tự viết một mạng nơ-ron cho ảnh thời trang

Học máy cơ bản · Bài 10 · Mạng nơ-ron và ảnh thời trang · PGS.TS Nguyễn Văn Hậu

## Mục tiêu

Viết từ đầu bằng numpy một mạng 784 → H → 10 (ReLU, softmax); tự cài lan truyền ngược và kiểm bằng sai phân; huấn luyện mini-batch có checkpoint; chọn cấu hình bằng validation theo quy tắc ghi trước; chấm tập kiểm tra cuối đúng một lần; so với logistic bằng kiểm định cặp; báo cáo trung thực.

## Dữ liệu

`data/project_subset_bai10.npz`: 10.000 ảnh Fashion-MNIST (Zalando Research, giấy phép MIT) lấy từ 35.000 ảnh train chính thức chưa dùng ở bài giảng Bài 9–10 và project Bài 9, seed 2027: 8.000 fit, 1.000 validation, 1.000 kiểm tra cuối; mỗi loại 10%. Không trùng ảnh nào (kiểm bằng hash) với tập bài giảng và test. Test chính thức đã dùng ở bài giảng.

## Tệp

- `Bai10_Project_khoi_dau.ipynb`: phát cho sinh viên; có ô TODO và ô tự kiểm.
- `Bai10_Project_loi_giai.ipynb`: giảng viên; đã chạy, mọi ô tự kiểm đạt.
- Mở notebook từ thư mục bài (notebook đọc `data/`). Hàm `cham_cuoi` ghi dấu vết (chuỗi cấu hình và mã băm dự đoán trên validation của hai mô hình) vào `.project_bai10_cham_cuoi.json`; gọi lại với cấu hình hoặc mô hình khác sẽ bị chặn. Đây là cơ chế nhắc kỷ luật, không phải bảo mật: giảng viên đối chiếu tệp dấu vết khi chấm. Xoá tệp này trước khi phát lại notebook cho lớp khác.
- Phần nâng cao không có ô tự kiểm; chấm theo rubric. Notebook lời giải có lời giải mẫu cho cả A và B.

## Ba mức

| Mức | Điểm | Việc phải làm |
|---|---:|---|
| Cơ bản | 5 | Bước 1–3: kiểm dữ liệu; forward, cross-entropy, lan truyền ngược khớp sai phân; huấn luyện mini-batch có checkpoint |
| Khá | +3 | Bước 4 (chọn H ∈ {16; 64} theo quy tắc ghi trước; logistic đối chứng), bước 5 (chấm cuối một lần, McNemar) và báo cáo một trang |
| Nâng cao | +2 | A: đơn vị ẩn so với thành phần PCA (độ thuần nhãn, ảnh trung bình); hoặc B: ảnh dịch 1–2 pixel, thêm ảnh dịch khi huấn luyện, đo trước và sau |

## Luật chơi

1. Phần chính không dùng `MLPClassifier`; chỉ dùng để đối chiếu.
2. Mọi lựa chọn làm trên validation; tập kiểm tra cuối chỉ chấm một lần bằng `cham_cuoi`.
3. Không sửa ô tự kiểm. Notebook nộp phải chạy được từ đầu (Restart & Run All).
4. Báo cáo kèm sai số chuẩn và kiểm định cặp; không viết “MLP tốt hơn” khi chênh lệch không có ý nghĩa thống kê.

## Báo cáo một trang

Năm mục, mỗi mục 2–4 câu: dữ liệu; bằng chứng mã đúng (sai phân, đường loss); chọn cấu hình (quy tắc, bảng); kết quả cuối kèm sai số và McNemar; giới hạn (ít nhất ba).

## Rubric

Xem `Bai10_Dap_an_va_rubric.md` (dành cho giảng viên).
