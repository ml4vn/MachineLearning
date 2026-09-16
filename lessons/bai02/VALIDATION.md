> Biên bản của phiên bản gốc; số hình và hướng dẫn đã được cập nhật. Xem [kiểm tra Python v3](../../docs/KIEM_TRA_PYTHON_V3.md) để biết kết quả mới.

# Hoàn tất Bài 02

Đã hoàn thành đủ sáu bước: đối chiếu slide v2, lưu kế hoạch, lập trình, kiểm thử, biên soạn hướng dẫn và kiểm tra trực quan.

- Sáu kiểm thử đơn vị đạt: phép tính kNN, hòa phiếu, khoảng cách bằng 0, đối chiếu scikit-learn, đặc trưng Unicode, chuẩn hóa và đầu vào sai.
- Dữ liệu SMS gốc có 5.574 bản ghi, còn 5.159 sau quy tắc loại trùng đã công bố. Train/validation/test: 3.095/1.032/1.032.
- Validation chọn k = 11, có chuẩn hóa chỉ fit trên train. F1 validation = 0,896.
- Test: TN = 892, FP = 12, FN = 17, TP = 111; F1 = 0,8844621514, khớp bài giảng.
- SMS nguồn 4500 được minh họa bằng văn bản thật, đặc trưng, biểu đồ và bảng các láng giềng trước/sau chuẩn hóa.
- Đã xem cả bốn hình PNG 3840 × 2160; bảng cập nhật số spam/ham theo dữ liệu chạy.

Môi trường tham chiếu: Python 3.12.14, scikit-learn 1.6.1, Matplotlib 3.10.3. Kết quả chi tiết do chương trình tự ghi trong `outputs/bai02/`.
