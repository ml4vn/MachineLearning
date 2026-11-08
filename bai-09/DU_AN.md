# Project độc lập · Bài 9 · Tìm sản phẩm trông giống với ít con số

Học máy cơ bản · Bài 9 · PCA và ảnh thời trang · PGS.TS Nguyễn Văn Hậu

## Mục tiêu

Tự cài PCA và khớp scikit-learn; đo EVR, k90 và lỗi tái tạo trên validation; chọn số thành phần k cho chức năng “sản phẩm trông giống” (1-NN trên score) dưới ràng buộc lưu trữ, theo một quy tắc ghi trước; chấm tập kiểm tra cuối đúng một lần; báo cáo trung thực.

## Dữ liệu

`data/project_subset.npz`: 10.000 ảnh Fashion-MNIST (Zalando Research, giấy phép MIT) lấy từ 45.000 ảnh train chính thức không dùng trong bài giảng, seed 2026: 8.000 ảnh kho, 1.000 validation, 1.000 kiểm tra cuối; mỗi loại 10%. Không trùng ảnh nào (kiểm bằng hash) với tập bài giảng và tập test. Test chính thức để dành cho Bài 10.

## Tệp

- `Bai09_Project_khoi_dau.ipynb`: phát cho sinh viên; có ô TODO và ô tự kiểm.
- `Bai09_Project_loi_giai.ipynb`: giảng viên; đã chạy, mọi ô tự kiểm đạt.
- Mở notebook từ thư mục bài (notebook đọc `data/`). Hàm `cham_cuoi` ghi dấu vết vào tệp `.project_bai09_cham_cuoi.json`; gọi lại với k khác sẽ bị chặn.

## Ba mức

| Mức | Điểm | Việc phải làm |
|---|---:|---|
| Cơ bản | 5 | Bước 1–3 (kiểm dữ liệu; tự cài PCA; EVR, k90, MSE validation), một k thoả ràng buộc và 1-NN trên validation |
| Khá | +3 | Bước 4 (lưới k, ràng buộc ≤ 10%, quy tắc chọn ghi trước), bước 5 (chấm cuối một lần) và báo cáo một trang |
| Nâng cao | +2 | A: lặp lũy thừa có khử cho 5 PC đầu, so với eigh; hoặc B: ảnh truy vấn dịch 1–2 pixel, đo 1-NN giảm bao nhiêu, thử một cách giảm |

## Luật chơi

1. Bước 2 không dùng `PCA` của thư viện để tính; chỉ để đối chiếu.
2. Mọi lựa chọn làm trên validation; tập kiểm tra cuối chỉ chấm một lần bằng `cham_cuoi`.
3. Không sửa ô tự kiểm. Notebook nộp phải chạy được từ đầu (Restart & Run All).
4. Báo cáo kèm sai số chuẩn; không viết “PCA tốt hơn” khi chênh lệch nằm trong sai số.

## Báo cáo một trang

Năm mục, mỗi mục 2–4 câu: dữ liệu; PCA và bằng chứng khớp thư viện; chọn k (bảng lưu trữ – lỗi – 1-NN, quy tắc); kết quả cuối kèm sai số chuẩn; giới hạn (ít nhất ba).

## Rubric

Xem `Bai09_Dap_an_va_rubric.md` (dành cho giảng viên).
