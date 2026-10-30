# Dự án thực hành: xây một sản phẩm nhỏ

[← Khóa học](../README.md) · [Cài môi trường](../docs/START_HERE.md)

Notebook cung cấp đọc dữ liệu, biểu đồ và đóng gói; bạn hoàn thiện phép toán và quyết định quan trọng. Mỗi TODO có yêu cầu, gợi ý, kiểm thử nhỏ và ứng dụng trên dữ liệu thật. Đây là hoạt động bổ sung ngoài 150 phút/bài, có thể làm theo cặp.

| Dự án | Điều kiện | Thời gian | Phần bạn tự làm |
|---|---|---|---|
| [Gợi ý phim](01_movie_recommender/README.md) | Bài 1 | 2–3 giờ | Cosine, xếp hạng, giải thích |
| [Bộ lọc SMS](02_sms_filter/README.md) | Bài 2–3 | 3–4 giờ | Chi phí lỗi, chọn ngưỡng |
| [Dự báo giao hàng](03_delivery_estimator/README.md) | Bài 4–7 | 4–5 giờ | MAE, pipeline cây, đánh giá thời gian |
| [Chân dung khách hàng](04_customer_segments/README.md) | Bài 8 | 3–4 giờ | RFM, chọn k, diễn giải nhóm |
| [Phòng thử ảnh](05_fashion_lab/README.md) | Bài 9–10 | 4–5 giờ | MSE, PCA không rò rỉ, phân tích lỗi |

## Cách làm

1. Đọc tình huống, xác định sản phẩm. Dự đoán ví dụ nhỏ trước khi chạy.
2. Chạy mã mẫu; hoàn thiện TODO và qua kiểm thử rồi mới chạy dữ liệu thật.
3. Chốt cấu hình trên validation, không đổi lựa chọn dựa vào test.
4. Kiểm tra tệp đã xuất và demo với đầu vào khác.
5. Restart Kernel, chạy lại từ đầu và nộp báo cáo.

`NotImplementedError` là điểm dừng cố ý. Viết thêm ít nhất hai kiểm thử biên; không xóa assert để “qua bài”. Mã đầy đủ trong bài học chỉ là tham khảo, không thay cho phần giải thích dự án.

## Sản phẩm phải nộp

- Notebook đã hoàn thiện, có đầu ra và trả lời bằng lời.
- Tệp trong `outputs/projects/<dự án>/`: bảng, hình, metrics/model card, mô hình nếu có.
- `REPORT.md` 1–2 trang theo [mẫu](REPORT_TEMPLATE.md), có nguồn và giới hạn.
- Demo cục bộ: một đầu vào → kết quả → giải thích. Không bắt buộc web app/cloud.

Chỉ nạp joblib do chính bạn tạo. Không commit dữ liệu cá nhân, token hoặc artifact lớn. Không đưa dự đoán minh họa thành lời khuyên kinh doanh.

## Tiêu chí đánh giá

| Tiêu chí | Điểm |
|---|---:|
| Vấn đề, nguồn, đơn vị và phạm vi kết luận | 15 |
| Thuật toán đúng, kiểm thử trường hợp biên | 25 |
| Đánh giá không rò rỉ hoặc phân cụm đúng phạm vi | 25 |
| Sản phẩm chạy lại được, bảng/hình và demo | 20 |
| Giải thích lỗi, giới hạn, mở rộng có lý do | 15 |

Không chấm theo accuracy cao nhất. Mô hình đơn giản được đánh giá đúng tốt hơn mô hình phức tạp có rò rỉ.
