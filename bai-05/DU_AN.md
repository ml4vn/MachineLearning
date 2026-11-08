# Project · Bài 5 · Tự viết bộ phân lớp logistic dự báo đơn trễ

Học máy cơ bản · Bài 5 · Hồi quy logistic · PGS.TS Nguyễn Văn Hậu

**Hình thức.** Cá nhân, ngoài giờ, khoảng 4–6 giờ. Nộp `Bai05_Project_khoi_dau.ipynb` đã chạy từ đầu đến cuối (Restart & Run All) và báo cáo một trang (PDF hoặc Markdown).

**Mục tiêu.** Viết lại toàn bộ cột HỌC của mạch logic (sigmoid, BCE, gradient, gradient descent có L2) bằng mã của chính mình, rồi dùng mô hình đó cho cột QUYẾT ĐỊNH (chọn τ, chấm test một lần, đọc ba lớp đánh giá).

**Dữ liệu.** `data/olist_model_table.csv` (train 29.031, validation 10.389, test 40.266 đơn; cột `late`). Nguồn gốc: Olist, Kaggle (https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).

## Sáu bước

1. Kiểm dữ liệu: số đơn, số đơn trễ, nhãn theo ngày lịch, không có trường kết quả trong đặc trưng.
2. Viết `sigmoid` ổn định số, `bce` (dùng `np.logaddexp`), `gradient`; kiểm bằng sai phân hữu hạn.
3. Viết `gd` có L2 với λ = 1/(nC), C = 1, không phạt b; η = 1, 4.000 vòng; vẽ đường loss.
4. Chọn τ trên validation từ lưới {0,05; 0,10; 0,15; 0,20; 0,30; 0,50} theo chi phí FP + 5·FN; hoà → ít cảnh báo, rồi ngưỡng lớn hơn; khoá τ.
5. Chấm test đúng một lần bằng `cham_test`; báo cáo kèm mốc “không bao giờ cảnh báo”.
6. Báo cáo một trang: dữ liệu và nhãn; thuật toán và bằng chứng hội tụ; ba lớp đánh giá trên test; một đơn minh hoạ chọn theo quy tắc khai báo; ít nhất ba giới hạn.

## Ba mức

| Mức | Yêu cầu |
|---|---|
| Đạt | bước 1–5 qua mọi ô tự kiểm; báo cáo đủ sáu mục |
| Khá | thêm: GD khớp nghiệm scikit-learn giải chặt (sai lệch hệ số dưới 10⁻⁶); giải thích vì sao C không phải tốc độ học |
| Nâng cao | thêm: biểu đồ hiệu chuẩn; so τ* = 1/6 với τ đã chọn trên validation; đo thiên lệch do quy tắc “biết nhãn” từ bảng orders gốc |

## Luật chơi

- Không dùng `LogisticRegression` để học hệ số của bài nộp; chỉ dùng để đối chiếu ở ô ghi rõ.
- Chọn τ chỉ trên validation. Test chỉ chấm một lần; nếu lỡ chấm lại, ghi rõ trong báo cáo.
- Chi phí FP + 5·FN là giả định lớp học; không quy ra tiền tiết kiệm. Hệ số không mang nghĩa nhân quả.
- Test đã được xem ở các bản trước của bài (test lịch sử): báo cáo như minh hoạ việc áp quy tắc đã khoá.

## Rubric (10 điểm)

Xem `Bai05_Dap_an_va_rubric.md`, mục Rubric project; tóm tắt: hàm cơ bản 2 · GD 2 · chọn τ 2 · ba lớp đánh giá 2 · giới hạn 2.
