# Kế hoạch Bài 10 — MLP từ XOR đến ảnh thật

Nguồn: 68 slide Bài10_v2, mlp_lab.py, case_audit.json. Giữ nguyên split Fashion-MNIST của Bài 09 nhưng tự tạo lại từ IDX; không phụ thuộc kết quả chạy bài trước.

| Bước | Nội dung | Tiêu chí hoàn thành |
|---|---|---|
| 1. Rà soát | XOR và giới hạn affine; ReLU; BCE/softmax CE ổn định; backprop; Adam khác GD; checkpoint validation | Đối chiếu từng ví dụ và quy trình nguồn |
| 2. Lập kế hoạch | Lưu tài liệu này trước triển khai | Toy XOR, mạng 2–2–1, MLP 784–64–10 |
| 3. Xây dựng | Mã từng bước gradient; finite differences; baseline logistic tự fit; 3 seed × 50 epoch thực; checkpoint theo CE validation; đóng băng trước test | CSV history, NPZ tham số, ảnh, JSON, chương trình suy luận |
| 4. Kiểm tra | Đủ 9 đạo hàm, giảm loss một bước; softmax shift; đếm 50.890 tham số; forward thủ công khớp sklearn; split và hash; argmin checkpoint | unittest và kiểm tra trong chạy thật |
| 5. Sư phạm | Sơ đồ tính, miền quyết định XOR, bảng gradient, quá trình học, ảnh đúng/sai có ID, confusion và xác suất từng ảnh; quiz giải thích | Hướng dẫn tiếng Việt, PNG 3840×2160 |
| 6. Chốt | Huấn luyện thật cả 3 seed; đối chiếu mốc tham chiếu; xem hình, lưu VALIDATION | Hoàn tất bài 10 rồi kiểm tra và đóng gói toàn repo |

Seed chính 42 được quy định trước, không chọn seed theo test. Checkpoint CE nhỏ nhất, hòa chính xác lấy epoch sớm nhất. Ba seed mô tả biến động, không gọi là khoảng tin cậy. 50 epoch là ngân sách, không tuyên bố hội tụ. Test công khai đã được xem ở pilot bài giảng, không gọi là test mới niêm phong. Ví dụ XOR có tầng ẩn cố định và nghiệm tự dựng phải được phân biệt với mạng thật học tất cả trọng số.
