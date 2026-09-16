> Biên bản của phiên bản gốc; số hình và hướng dẫn đã được cập nhật. Xem [kiểm tra Python v3](../../docs/KIEM_TRA_PYTHON_V3.md) để biết kết quả mới.

# Hoàn tất Bài 03

Đã thực hiện đủ sáu bước; năm kiểm thử đơn vị đạt và lệnh `--mode all` chạy thành công từ SMS gốc. Mô hình cố định tái tạo đúng TN/FP/FN/TP = 892/12/17/111. Ngưỡng được chọn trên validation: 8 phiếu cho 5FP+FN và 4 phiếu cho FP+5FN; chi phí test tương ứng 56 và 93.

AUC tính bằng cặp = 0,9690611173; AP tính theo bước recall = 0,9267043812; cả hai đối chiếu đúng scikit-learn. Precision không xác định được ghi `null` khi không có cảnh báo. Đã xem cả năm hình PNG 3840 × 2160, gồm bảng lỗi truy về SMS thật.

Môi trường tham chiếu: Python 3.12.14, scikit-learn 1.6.1, Matplotlib 3.10.3. Chi tiết tái tạo tự ghi trong `outputs/bai03/`.
