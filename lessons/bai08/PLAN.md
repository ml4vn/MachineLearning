# Kế hoạch Bài 08 — K-means và phân nhóm khách hàng

Đối chiếu 60 slide Bài08_v2, mã nguồn thí nghiệm và case_audit.json. Mục tiêu: nối hóa đơn thật → RFM → hình học khoảng cách → Lloyd → đánh giá và giới hạn của phân nhóm.

| Bước | Nội dung cụ thể | Bằng chứng hoàn thành |
|---|---|---|
| 1. Rà soát | R theo ngày lịch; F là số hóa đơn khác nhau; M là tổng tiền mua dương, không phải lợi nhuận; phân biệt SSE và silhouette | Đối chiếu số liệu gốc và định nghĩa |
| 2. Lập kế hoạch | Ví dụ 6 điểm; 20 khởi tạo K=3; vét cạn phân hoạch; dữ liệu Online Retail; kiểm tra trùng lặp | Tài liệu này lưu trước khi xây dựng |
| 3. Xây dựng | Thuật toán Lloyd có lịch sử từng nửa bước; RFM từ XLSX gốc; log1p và chuẩn hóa; K=2…6; profile K=4; silhouette; độ ổn định; dự đoán một khách hàng | Python độc lập, CSV, JSON, PNG |
| 4. Kiểm tra | SSE không tăng; nghiệm vét cạn; silhouette tính tay so với sklearn; đối chiếu R/F/M bằng ngày lịch, tập hóa đơn và Decimal; kích thước cụm; so sánh trước/sau xử lý trùng | unittest và kiểm tra trong chạy thật |
| 5. Sư phạm và hình thức | Hình mỗi nửa bước, biểu đồ chọn K, bảng hóa đơn, profile dễ đọc, ví dụ hai vành trăng; bài tập có đáp án | README tiếng Việt; PNG 3840×2160 có công thức và tên giảng viên |
| 6. Chốt | Chạy đầy đủ, xem ảnh, ghi kết quả và giới hạn | VALIDATION.md rồi mới sang Bài 09 |

Không gọi K=4 là tối ưu: đây là lựa chọn minh họa để đọc profile. Silhouette dùng cùng mẫu 2.000 khách hàng cho mọi K; điểm mẫu được tính trong chính mẫu đó. Phân cụm là phân tích mô tả toàn bộ ảnh chụp lịch sử, không phải đánh giá khả năng dự báo trên test. Trùng dòng được giữ trong cấu hình tham chiếu và phân tích độ nhạy riêng. Không diễn giải số hiệu cụm thành thứ hạng.
