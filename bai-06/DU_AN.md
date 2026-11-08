# Project độc lập · Bài 6 · Tự viết cây quyết định dự báo đơn trễ

Học máy cơ bản · Bài 6 · Cây quyết định · PGS.TS Nguyễn Văn Hậu

## Mục tiêu

Tự viết thuật toán CART phân lớp (Gini, quét ngưỡng bằng tổng tích luỹ, dựng cây đệ quy, dự đoán), chọn độ sâu và ngưỡng đúng quy trình, chấm test một lần, so với logistic Bài 5, và viết báo cáo một trang có giới hạn.

## Dữ liệu

`data/olist_model_table.csv`: 79.686 đơn Olist (Kaggle), cùng sáu đặc trưng và ba tập với Bài 4–5: train 29.031 (3,24% trễ), validation 10.389 (6,10%), test 40.266 (8,64%). Test đã được xem ở bản thử nghiệm, v2 và Bài 5 (test lịch sử).

## Tệp

- `Bai06_Project_khoi_dau.ipynb`: phát cho sinh viên; có ô TODO và ô tự kiểm.
- `Bai06_Project_loi_giai.ipynb`: giảng viên; đã chạy, mọi ô tự kiểm đạt.
- Mở notebook từ thư mục bài (notebook đọc `data/`).

## Ba mức

| Mức | Điểm | Việc phải làm |
|---|---:|---|
| Đạt | 5 | Bước 1–3 (`gini`, `diem_chia`, `quet_mot_cot`), bước 5 (chọn trên validation, chấm test một lần; được dùng `DecisionTreeClassifier`, `LAM_MUC_KHA = False`) và báo cáo một trang |
| Khá | +3 | Bước 4: `dung_cay`, `du_doan` tự viết, trùng scikit-learn từng nút ở sâu 6; dùng cây tự viết ở bước 5 |
| Nâng cao | +2 | A: phân tích theo vùng so với logistic Bài 5; hoặc B: tự viết cắt tỉa theo α và so với scikit-learn |

## Luật chơi

1. Không dùng scikit-learn để dựng cây của bài nộp ở mức khá; chỉ dùng để đối chiếu ở ô có ghi rõ.
2. Chọn độ sâu và τ **chỉ trên validation**, theo lưới và quy tắc hoà cho sẵn.
3. Chấm test **một lần** bằng `cham_test`.
4. Không sửa ô tự kiểm. Notebook nộp phải chạy được từ đầu (Restart & Run All).
5. Chi phí FP + 5·FN là giả định lớp học; không quy ra tiền.

## Báo cáo một trang

Năm mục, mỗi mục 2–4 câu: dữ liệu; thuật toán; chọn trên validation; test một lần và so với logistic; giới hạn (ít nhất ba). Không diễn giải ngưỡng hay tầm quan trọng là nhân quả.

## Rubric

Xem `Bai06_Dap_an_va_rubric.md` (dành cho giảng viên).
