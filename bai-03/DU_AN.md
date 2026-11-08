# Project Bài 3 · Chọn ngưỡng cho bộ lọc tin rác theo mục tiêu vận hành

**Học máy cơ bản · Bài 3 · Đánh giá phân loại · PGS.TS Nguyễn Văn Hậu**

## Tình huống

Bộ lọc kNN của Bài 2 cho mỗi tin một số phiếu spam v (0–11). Nhóm vận hành phải chọn ngưỡng m (gắn cờ khi v ≥ m) theo một mục tiêu đã thống nhất: tránh chặn nhầm tin thật, hay tránh để lọt tin rác. Bạn tự viết các hàm đánh giá, chọn ngưỡng đúng quy trình và viết báo cáo một trang có giới hạn.

## Dữ liệu

- `data/sms_validation_votes_v3.csv` (1.032 tin, 129 spam) và `data/sms_test_votes_v3.csv` (1.032 tin, 128 spam): mã bản ghi, nhãn, số phiếu của kNN Bài 2 v3 (k = 11, chuẩn hoá theo train, đồng hạng theo mã bản ghi).
- `data/SMSSpamCollection` (UCI SMS Spam Collection; Almeida và cộng sự, 2011) để đọc văn bản theo `source_record`.
- Project **độc lập** với project Bài 2: không cần chạy lại kNN.
- Corpus tiếng Anh, công bố năm 2011. Chỉ dùng để học: không gọi số, không truy cập liên kết trong nội dung tin.

## Các bước (mỗi bước gắn với một chặng của buổi học)

| Bước | Việc cần làm | Chặng | Ô tự kiểm |
|---|---|---|---|
| 1 | Đọc hai tệp số phiếu, ghép văn bản, accuracy mốc “luôn ham” trên validation | 1 | 129 và 128 spam; mốc ≈ 0,8750 |
| 2 | Tự viết `ma_tran(y, y_du_doan)` (không dùng scikit-learn) | 1 | 10 tin: (4, 2, 0, 4); validation m = 6 |
| 3 | Tự viết `chi_so(tn, fp, fn, tp)`, trả `None` khi mẫu số bằng 0 | 2 | P = 2/3, R = 1, F1 = 0,8 |
| 4 | Quét m = 1 … 12 trên validation; kiểm quy luật đơn điệu; vẽ FP–FN và P–R | 3 | m = 6: FP 9, FN 16 |
| 5 | `chon_nguong` theo chi phí ghi trước, hoà → ít cảnh báo → m lớn hơn; khoá | 4 | 5·FP + FN → m = 8 |
| 6 | `cham_test` một lần; so với m = 6 (Bài 2 đã báo) và mốc “luôn ham”; đọc 3 tin sai; báo cáo | 4 | `cham_test` gọi đúng một lần |

## Ba mốc nộp

| Mốc | Nội dung | Hạn gợi ý |
|---|---|---|
| M1 | Bước 1–3 và hai câu hỏi M1 (phiếu học tập, phần D) | ngay sau buổi học |
| M2 | Bước 4–5 | tuần sau |
| M3 | Bước 6 và báo cáo một trang | cuối đợt |

## Ba mức

- **Cơ bản:** kịch bản 5·FP + FN (`KICH_BAN = (5, 1)`).
- **Khá:** thêm kịch bản FP + 5·FN: khoá **cả hai** ngưỡng trên validation trước, rồi chấm test **một lần** cho cả hai (`cham_test(m1, m2)`); đối chiếu scikit-learn ở 12 ngưỡng.
- **Nâng cao:** AUC theo định nghĩa so cặp, AP theo bậc recall, precision khi tỷ lệ spam đổi; mọi so sánh trên validation.

## Nộp gì

1. Notebook đã chạy từ đầu đến cuối (Restart & Run All), mọi ô tự kiểm của mức đã chọn in ✅.
2. Báo cáo một trang theo khung ở cuối notebook.

## Rubric 10 điểm

| Hạng mục | Điểm |
|---|---:|
| Tái lập và quy trình dữ liệu | 3 |
| Cài đặt và đối chiếu | 3 |
| Đánh giá | 2 |
| Diễn giải và giới hạn | 2 |

## Quy tắc trung thực

- Ghi hệ số chi phí và quy tắc hoà **trước** khi nhìn kết quả.
- Chọn ngưỡng **chỉ trên validation**.
- **Test chấm một lần** (hàm `cham_test` chặn lần thứ hai). Test này đã được chấm ở Bài 2: báo cáo là “test lịch sử”.
- Ô tự kiểm in ✅ chỉ cho biết phép tính khớp; không thay cho phần diễn giải.
