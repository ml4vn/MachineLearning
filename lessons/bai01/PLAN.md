# Bài 01 — Vector và độ tương đồng cosine

## 1. Rà soát
Đối chiếu 64 slide v2; nguồn cosine_lab.py, audit_case.py, case_audit.json.
Case là MovieLens latest-small 2018, không phải MovieLens 1M trong bản cũ.

## 2. Kế hoạch nội dung
| Khối | Thực hành | Slide | Đầu ra |
|---|---|---|---|
| Biểu diễn | Nhãn → multi-hot; cùng thứ tự trục | 5–11 | Ma trận 3 trục/19 nhãn |
| Hình học | Dot, chuẩn L2, cosine; vector 0 | 12–21, 36–43 | Hình vector và bảng tính |
| Tính từng bước | Ví dụ tổng hợp nhỏ; kiểm tay và sklearn | 23–34, 50–52 | Bảng đóng góp, kiểm tra độc lập |
| Dữ liệu thật | The Matrix và 5 phim; xếp hạng toàn kho | 44–49 | CSV so sánh, top-10, đồng hạng |
| Giới hạn | Đổi chiều, đổi thang, missing khác zero | 38–42, 57–63 | Lời giải và phản ví dụ |

## 3–6. Xây dựng, kiểm tra và hoàn tất
- cosine tự viết kiểm shape, NaN/Inf; trả None cho vector 0.
- So công thức từ tập nhãn với NumPy/sklearn, không đọc điểm tính sẵn.
- Kỳ vọng 9.742 phim, 19 nhãn, 34 thiếu nhãn, 42 phim cùng vector với query.
- Không dùng movieId như đặc trưng; ID chỉ ổn định hiển thị khi đồng điểm.
- Kiểm toy ngoại tuyến, real từ ZIP gốc, lệnh từ thư mục khác, mọi hình PNG.
- README có ba bài tập với gợi ý/đáp án và nguồn dữ liệu.
