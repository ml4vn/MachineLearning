# Kế hoạch tài liệu đọc trước Bài 3

## Bước 1 Rà soát

Bài 2 đã hoàn tất. Đọc Bai03_v2 gồm 64 slide (56 chính, 8 mở rộng), notes, rà soát khoa học, mã metrics_lab, test_predictions, validation_predictions, toy_scores và case_audit. Đối chiếu tài liệu đánh giá mô hình scikit-learn 1.6.1 và nguồn UCI đã kiểm ở bài 2. Tiếp tục cùng SMS, giữ spam=1 và hàng thật/cột dự đoán.

## Kế hoạch nội dung trước biên soạn

| Trang | Mục và nội dung | Trực quan | Slide bám theo |
|---|---|---|---|
| 1 | Vấn đề, mốc luôn ham 87,60%, mục tiêu | Biểu đồ so mốc và kNN | 1–5 |
| 2 | Điều kiện đầu vào, nhãn/điểm/quyết định, tỷ lệ và nhóm mẫu số | Bảng thuật ngữ đầu vào, kiểm nhanh | 6–7,19,33 |
| 3 | Dữ liệu thật: cùng 1.032 SMS, schema và hai lỗi có mã, trích nguyên văn | Bảng FP/FN và văn bản thật | 2,6,8–9 |
| 4 | Ý tưởng: mỗi dòng vào một trong bốn ô; giữ tổng và lề | Sơ đồ ma trận có tên trục, nhãn và số thật | 11–15,45 |
| 5 | Accuracy, precision, recall, F1, điều kiện mẫu số | LaTeX kèm câu hỏi bằng tiếng Việt | 16–29 |
| 6 | Quy trình đọc báo cáo và chọn ngưỡng; validation/test không tráo vai | Sơ đồ bước, bảng chính sách | 33–44,49–52 |
| 7 | Ví dụ 10 ID mô phỏng, score và nhãn; ngưỡng 0,5; tính mọi chỉ số | Bảng A–J cùng bốn nhóm | 11–31 |
| 8 | Ngưỡng 0,85 và 0,9; phản ví dụ precision; quay lại chỉ số SMS thật | Đồ thị score với đường ngưỡng, bảng kết quả | 34–48 |
| 9 | Sáu câu tự kiểm: đặt tên lỗi, mẫu số, tính ma trận, đổi ngưỡng, chọn tập, giới hạn | Quiz độc lập | 10,20,30,37,42,50,54 |
| 10 | Tóm tắt, từ vựng, nguồn, liên hệ hồi quy và logistic | Bảng đọc báo cáo | 49,56,64 |
| 11 | Đáp án giải thích K1/K2 và sáu câu, hướng ôn | Công thức tính và phản biện phương án | Notes |
| 12 | Mở rộng tùy chọn: hai chi phí giả định, bảng validation; không cảnh báo, AUC/AP và hiệu chỉnh ở mức định hướng | Bảng ngưỡng m4/m6/m8 với chi phí | 38–44,57–63 |

## Điều chỉnh cần giữ trong tài liệu

- Không nói accuracy vô dụng; chỉ rõ câu hỏi nó chưa trả lời. Không gọi positive là tốt.
- Điểm kNN là phiếu/11, còn điểm mô phỏng không phải phiếu/11. Điểm bằng ngưỡng được cảnh báo.
- TP cùng là tử số của precision và recall nhưng mẫu số khác. F1 không chứa TN và không tự là chi phí.
- Nâng ngưỡng với điểm cố định làm cảnh báo và recall không tăng, nhưng precision có thể giảm.
- Test lịch sử đã xem ở bài 2. Không quảng cáo việc áp dụng chính sách ở bài 3 là phép kiểm độc lập mới. Chọn ngưỡng bằng validation; chi phí 5FP+FN và FP+5FN là giả định, không phải tiền đo được.
- ROC/AUC/AP chỉ nằm trong phần tùy chọn; không đòi học trước để giải được phần chính. Không đồng nhất AP với diện tích hình thang của PR.

## Kiểm tra để hoàn tất

Tái tính bốn ô từ CSV bằng điều kiện logic và đối chiếu thư viện; kiểm mọi ID mô phỏng ở các ngưỡng, hai dạng F1, hai chính sách validation và mẫu số bằng 0. Tạo PDF/DOCX 12 trang dự kiến, 10 mục và hai phụ lục, hình màu, icon, footer giảng viên. Xem mọi trang PDF xuất từ chính DOCX, giữ bản nguồn và kết quả kiểm. Chỉ sau hoàn tất mới bắt đầu bài 4.
