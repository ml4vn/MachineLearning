# Project Bài 2 · Bộ lọc tin rác bằng kNN tự cài đặt

**Học máy cơ bản · Bài 2 · PGS.TS Nguyễn Văn Hậu**

## Tình huống

Một nhóm vận hành muốn biết: chỉ với hai đặc trưng rẻ nhất (độ dài tin và tỷ lệ chữ số), kNN lọc được bao nhiêu tin rác? Câu trả lời giúp họ quyết định có nên đầu tư một mô hình đọc nội dung hay không. Bạn xây trọn quy trình, tự viết kNN, chọn cấu hình đúng quy trình và viết kết luận có phạm vi.

## Dữ liệu

- `data/SMSSpamCollection` (UCI SMS Spam Collection; Almeida và cộng sự, 2011): 5.574 dòng, mỗi dòng `nhãn` ⟶ tab ⟶ `văn bản`.
- Corpus tiếng Anh, công bố năm 2011. Kết quả không áp dụng thẳng cho tin nhắn tiếng Việt hiện nay.
- Chỉ dùng để học: không gọi số, không truy cập liên kết trong nội dung tin.

## Các bước (mỗi bước gắn với một chặng của buổi học)

| Bước | Việc cần làm | Chặng | Ô tự kiểm |
|---|---|---|---|
| 1 | Đọc tệp, đánh mã bản ghi, bỏ trùng, đếm nhãn | 1 | 5.574 → 5.159 tin; 642 spam |
| 2 | Hai đặc trưng; chia ba tập phân tầng (seed 42, mã đã cho) | 1 | bản ghi 3 = (155; 25/155); 3.095 / 1.032 / 1.032 |
| 3 | Tự viết `knn_du_doan` với quy ước đồng hạng (không dùng scikit-learn) | 2 | ví dụ P1–P5, gồm trường hợp đồng d² ở ranh giới |
| 4 | μ, σ chỉ từ train; tin 4500 trước và sau chuẩn hoá | 3 | μ, σ; hai bộ láng giềng |
| 5 | Chọn cấu hình trên validation: thô/chuẩn hoá × k ∈ {3; 5; 11}; tiêu chí: ít tin sai nhất, hoà thì k nhỏ hơn | 4 | bảng 6 cấu hình; cấu hình được chọn |
| 6 | Khoá cấu hình; chấm test một lần; so mốc “luôn ham”; đọc 3 tin sai; (khá) đối chiếu scikit-learn | 4 | `cham_test` gọi đúng một lần |

## Ba mốc nộp

| Mốc | Nội dung | Hạn gợi ý |
|---|---|---|
| M1 | Bước 1–2 và hai câu hỏi M1 | ngay sau buổi học |
| M2 | Bước 3–4 và hai câu hỏi M2 | tuần sau |
| M3 | Bước 5–6 và báo cáo một trang | cuối đợt |

## Ba mức

- **Cơ bản** (tối đa 8/10): bước 1–4 và 6 với cấu hình chuẩn hoá, k = 3; đặt `LAM_BUOC_5 = False`.
- **Khá**: đủ 6 bước, kèm đối chiếu scikit-learn và giải thích nếu lệch.
- **Nâng cao**: thêm đặc trưng thứ ba (ví dụ tỷ lệ chữ in hoa), so StandardScaler với MinMax, hoặc bỏ phiếu theo khoảng cách; mọi so sánh chỉ trên validation.

## Nộp gì

1. Notebook đã chạy từ đầu đến cuối (Restart & Run All), mọi ô tự kiểm của mức đã chọn in ✅.
2. Báo cáo một trang theo khung ở cuối notebook (bài toán, phương pháp, kết quả, ba tin sai, giới hạn, việc làm tiếp).

## Rubric 10 điểm

| Hạng mục | Điểm |
|---|---:|
| Tái lập và quy trình dữ liệu | 3 |
| Cài đặt và đối chiếu | 3 |
| Đánh giá | 2 |
| Diễn giải và giới hạn | 2 |

## Quy tắc trung thực

- μ, σ chỉ tính trên **train**; dùng lại cho validation, test và tin mới.
- Chọn cấu hình bằng **validation**, theo tiêu chí ghi trước khi chạy.
- **Test chấm một lần** (hàm `cham_test` chặn lần thứ hai). Muốn thử thêm: quay lại validation và ghi rõ trong báo cáo.
- Ô tự kiểm in ✅ chỉ cho biết phép tính khớp; không thay cho phần diễn giải.
