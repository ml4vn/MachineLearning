# Bài 06 — Kế hoạch và rà soát trước khi biên soạn

## Bước 1

Đợt 2 bắt đầu từ bài 6 sau khi bài 1–5 đã bàn giao. Đối chiếu 68 slide v2, notes, báo cáo khoa học, model_policy.json, tree_lab.py, các bảng 12 đơn mô phỏng và Olist. Tham khảo tài liệu CART và cost-complexity chính thức của scikit-learn 1.6.1. Giữ nhãn, tập chia và cấu hình của slide; viết thành tài liệu tự đọc cho sinh viên trung bình.

Mục tiêu: lần đúng đường đi của một đơn; tính tần suất lá, Gini và gain có trọng số; phân biệt gain trong nút với đóng góp toàn tập; dựng cây toy; hiểu dừng/cắt tỉa và kết luận kết quả thật có giới hạn.

| Trang | Mục thống nhất | Nội dung và hình/bảng | Slide bám sát |
|---|---|---|---|
| 1 | Vấn đề | Cùng câu hỏi giao trễ, thay mô hình bằng chuỗi điều kiện; sơ đồ quy trình | 1–9 |
| 2 | Tiên quyết | Đếm lớp, tỷ lệ, bình phương và trọng số; hai kiểm nhanh | 13–18 |
| 3 | Dữ liệu | Bốn đơn thật có mã, sáu đặc trưng, nhãn lịch và tập thời gian; phân biệt toy | 3–5,45 |
| 4 | Ý tưởng | Cây ba lá và đường đi M11; điều kiện chỉ áp trong vùng của nút | 7–8,25–30 |
| 5 | Khái niệm/công thức | Tần suất lá, Gini nhị phân, tạp chất sau chia, gain; đồ thị Gini | 13–21,28 |
| 6 | Quy trình | Quét trung điểm, chọn gain lớn nhất hợp lệ trong nút, lặp và dừng; bảng hai split | 22–24,33,35–36 |
| 7 | Ví dụ đầy đủ | 12 hàng toy; root ngày hẹn ≤15, nút phải khoảng cách ≤10; kiểm tổng gain | 10–12,19–32 |
| 8 | Kết quả và giới hạn | Validation chọn depth6 và τ0,10; test so cây/logistic/baseline, lá thật 33/297 | 45–55 |
| 9 | Tự kiểm | Sáu câu về Gini, gain, đường đi, ngưỡng, độ phức tạp và kết luận | Q1–Q6,58–59 |
| 10 | Ghi nhớ | Glossary, checklist, nguồn, nối bài kế tiếp theo slide | 57,60,68 |
| 11 | Phụ lục A | Đáp án giải thích sáu câu và hai kiểm nhanh, chỗ cần ôn | Nội dung chính |
| 12 | Phụ lục B | Cắt tỉa ba cây con; R khác tỷ lệ lỗi, α khác ngưỡng cảnh báo; phạm vi bất biến | 41–44,61–67 |

### Ràng buộc khoa học

- late dùng ngày lịch và chỉ đặc trưng giả định sẵn có lúc duyệt. Mẫu đã hoàn tất; cutoff nhãn train/validation; 16 trường hợp thiếu khối lượng bị tổng hợp thành 0 không là đo được 0 gram.
- Không gọi p tại lá là bảo đảm cho từng đơn. Dùng p≥τ rõ ràng; khi hòa 0,5 có thể khác predict mặc định của thư viện.
- Gini nhị phân tối đa 0,5; sau chia phải cân theo số mẫu trong nút. Gain thứ hai 0,375 tính trên 8 mẫu, đóng góp toàn tập 8/12×0,375=0,25.
- Root toy có 12 ngưỡng ứng viên: ngày hẹn15 tốt nhất gain0,25; sau đó nhánh phải có 7 ngưỡng khoảng cách, chọn10, cây có3 lá. Cắt lần hai chỉ trong vùng hẹn>15.
- Cây tham lam không bảo đảm tối ưu toàn cục. Train hoàn hảo không tự chứng minh quá khớp; không khẳng định mọi cây đều khớp train hoàn hảo.
- Cắt tỉa dùng R là tạp chất lá có trọng số. Không lẫn α với learning rate, ngưỡng cảnh báo hoặc chi phí FP/FN.
- Olist: hai ứng viên depth3/6, min_samples_leaf200, seed42, cùng imputer/scaler train. Chọn cấu trúc theo validation AP; ngưỡng theo FP+5FN trên lưới đã định, không refit. Test đã được xem trong pilot, không là phép kiểm độc lập mới.
- Test cây depth6 tại0,10: TN34659 FP2129 FN3046 TP432. Cây tăng recall nhưng chi phí17359 vẫn cao hơn logistic16944. Không suy giải thích cây thành nhân quả.

## Bước 2 sau khi chốt kế hoạch

Tạo DOCX/PDF/Markdown, nguồn LaTeX, PNG/SVG và dữ liệu. Tính lại mọi split toy, đường đi, Gini/gain và pruning; fit lại hai cây Olist, đối chiếu điểm dự đoán, số đếm và tần suất lá. Xuất chính DOCX bằng Word, dựng PNG từ PDF và xem từng trang; sửa rồi đóng gói trước khi bắt đầu bài7. Giữ thiết kế A4, màu/icon và footer PGS.TS Nguyễn Văn Hậu như bài1–5. Thời lượng đọc chỉ là ước lượng, chưa đo trên sinh viên.
