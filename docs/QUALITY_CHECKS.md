# Kiểm chứng bản học liệu hiện hành

Ngày kiểm tra: **29/10/2026**. Môi trường cục bộ: Windows, Python 3.12, scikit-learn 1.6.1. Các kiểm tra trên GitHub Actions chạy thêm Windows và Linux; trạng thái CI của commit là nguồn xác nhận riêng.

| Kiểm tra cục bộ | Kết quả |
|---|---|
| Kiểm thử toán và trường hợp biên | 60/60 đạt |
| Ví dụ nhỏ của 10 bài, chạy tuần tự | 10/10 đạt |
| Notebook bài học sau khi chuẩn hóa đường dẫn | 9/9 chạy hết; Bài 7 dùng ví dụ Python riêng |
| Kiểm chứng khoa học độc lập Bài 5, 6, 8, 9, 10 | Đạt trên bằng chứng đã lưu |
| Notebook dự án: schema, cú pháp, TODO, ô kiểm thử | 5/5 đạt |
| Dự án với lời giải tham chiếu riêng | 5/5 chạy hết trên dữ liệu thật |
| Liên kết nội bộ Markdown/HTML | Kiểm tra tự động bằng `tools/check_materials.py` |
| PowerPoint trong cây xuất bản và các ZIP dữ liệu | Không có |

## Phạm vi chạy dự án

- MovieLens: tính cosine, xếp hạng, xuất bảng/hình, truy vấn thứ hai.
- SMS: khử trùng, train/validation/test, chọn ngưỡng, xuất mô hình và nạp lại để dự đoán.
- Olist: đọc ZIP gốc, kiểm cutoff nhãn, học cây, so baseline, xuất và nạp mô hình.
- Online Retail: đọc Excel trong ZIP, tạo RFM, so các k, kiểm độ ổn định giữa seed, xuất hồ sơ nhóm.
- Fashion-MNIST: đọc ảnh gốc, PCA train-only, so logistic/MLP trên validation, đánh giá test sau khi khóa cấu hình, xuất và nạp mô hình.

Lời giải tham chiếu và notebook đã điền đáp án không nằm trong repository công khai. Notebook sinh viên cố ý dừng ở TODO; không tuyên bố các notebook chưa hoàn thiện có thể Run All thành công.

Chạy được không đồng nghĩa mô hình phù hợp triển khai. Test công khai và snapshot cũ chỉ phục vụ tái lập. Các giới hạn về quần thể, dữ liệu trùng, nhãn và đơn vị được nêu trong từng dự án.
