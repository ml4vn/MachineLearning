# Kế hoạch bộ thực hành Python 10 bài

Nguồn chuẩn: slide v2 và các kiểm tra khoa học đã lưu cùng bộ bài giảng.
Thực hiện tuần tự 01→10; hoàn tất một bài trước khi xây dựng bài tiếp.

Mỗi bài có sáu bước:
1. Đọc mục tiêu, slide, notes, dữ liệu và mã kiểm chứng của đúng bài.
2. Lưu kế hoạch nội dung, đầu ra, phép kiểm và liên hệ slide trong PLAN.md.
3. Viết thuật toán, lệnh chạy và hình minh họa; có ví dụ nhỏ và case thật.
4. Chạy từ dữ liệu gốc, đối chiếu phép tính và kết quả thư viện.
5. Viết hướng dẫn cho sinh viên, bài tập tự thử và đáp án; đọc hình sinh ra.
6. Ghi biên bản hoàn tất, rồi mới sang bài sau.

## Quy ước chung
- Mã chạy bằng Python 3.12; các thư viện trong requirements.txt.
- Mỗi bài chạy được bằng main.py hoặc python -m lessons.baiNN.main.
- --mode toy chạy ngoại tuyến; --mode real chạy case thật; --mode all chạy cả hai.
- Thư mục data/raw dùng chung để tránh nhân bản bộ dữ liệu; mọi bài có thể chạy độc lập.
- Mỗi bài tự tạo kết quả cần dùng, không bắt buộc đã chạy bài trước.
- Hình PNG mặc định 3840×2160, chữ Việt, màu rõ, nhãn trục và chú thích đúng phạm vi.
- README giải thích mục tiêu, dữ liệu, lệnh chạy, các bước, kết quả, giới hạn và bài tập.
- Git chỉ chứa mã, tài liệu, cấu hình và hình xem trước được chọn; dữ liệu tải và kết quả chạy được bỏ qua.
- Xác nhận repository GitHub đích trước khi đưa mã lên; không suy đoán tài khoản hoặc chế độ hiển thị.
