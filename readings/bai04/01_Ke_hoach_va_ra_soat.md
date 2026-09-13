# Bài 04 — Kế hoạch và rà soát trước khi biên soạn

## Bước 1: chốt nội dung

Bài 1–3 đã hoàn tất trước khi bắt đầu bài 4. Nguồn đối chiếu: Bài04_v2 (68 slide, 62 chính và 6 mở rộng), notes, báo cáo khoa học, teaching_math.json, lab_bai04.py và bảng Olist đã chuẩn bị. Giữ case, ký hiệu và phép tính của bản slide đã rà soát; viết lại thành tài liệu tự học cho sinh viên trung bình, không yêu cầu Python.

### Mục tiêu quan sát được

Đọc đúng đầu vào và nhãn số ngày; phân biệt mô hình, loss, thuật toán; tính một bước GD từ bảng bốn điểm; diễn giải MAE/RMSE và giới hạn của kết quả thật.

### Kế hoạch 12 trang

| Trang | Mục chung | Nội dung cụ thể và hình/bảng | Đối chiếu slide |
|---|---|---|---|
| 1 | Vấn đề | Tình huống số ngày giao hàng, mục tiêu, tuyến học từ dữ liệu tới đánh giá | 1–5 |
| 2 | Tiên quyết | Đường thẳng, trung bình, sai số có dấu, đạo hàm trực giác; 2 kiểm nhanh | 9–19 |
| 3 | Dữ liệu | Bốn đơn thật có mã tra lại, định nghĩa delivery_days, khoảng cách đại diện, tập thời gian | 5–8, 48–49 |
| 4 | Ý tưởng | Bốn điểm mô phỏng; đường dự đoán và đoạn sai số; mô hình/loss/thuật toán | 16–26 |
| 5 | Khái niệm/công thức | ŷ=wx+b, e=ŷ−y, J=MSE/2; gradient và cập nhật; giải thích ký hiệu | 18–20, 27–30, 40 |
| 6 | Quy trình | Dự đoán → sai số → hai gradient từ cùng tham số cũ → cập nhật; một bước hai tham số | 40–44 |
| 7 | Ví dụ xuyên suốt | Căn giữa z=x−2,5, cố định a=5 có điều kiện; bảng tính g, w=0→0,7; loss giảm | 22–35 |
| 8 | Kết quả/hiểu nhầm | OLS thật và baseline cùng test; MAE/RMSE; phạm vi mẫu, ngoại suy, phi nhân quả | 47–58 |
| 9 | Tự kiểm | 6 câu: nhãn, gradient, thay số, loss khác 0 ở đáy, MAE, leakage | 15,21,36,44,58,60 |
| 10 | Ghi nhớ | Checklist, thuật ngữ, tài liệu nguồn, nối tới logistic bài 5 | 59–62,68 |
| 11 | Phụ lục A | Giải thích 6 đáp án và 2 kiểm nhanh, chỉ chỗ cần ôn | Kiến thức chính |
| 12 | Phụ lục B | Learning rate quá lớn; giới hạn của ví dụ bậc hai; căn giữa và chuẩn hóa | 37–42,63–67 |

### Các ràng buộc khoa học đã chốt

- Nhãn là tổng giây giữa xác nhận và giao thực tế chia 86.400; không phải nhãn trễ hay chênh ngày lịch. Ngày giao dùng tạo nhãn, không làm đặc trưng ở thời điểm xác nhận.
- Khoảng cách là đại diện đường chim bay giữa tâm vùng bưu chính, trung bình theo dòng mặt hàng; không phải tuyến xe chạy. Bốn đơn được chọn theo khoảng cách, không phải mẫu đại diện.
- Train/validation/test lần lượt 29.031/10.389/40.266, ranh giới nhãn train và validation phải có trước mốc tương ứng. Dữ liệu đã lọc đơn hoàn tất gây giới hạn chọn mẫu; ảnh chụp tĩnh chưa xác nhận lịch sử sẵn có của mọi trường.
- Nhất quán e=ŷ−y và J=MSE/2. Không dùng gradient có hệ số 2 từ quy ước J=MSE.
- Căn giữa x chỉ giúp đặt a=mean(y) tối ưu trong OLS không trọng số, có chặn tự do không phạt; b=5−2,5w, không phải b=5.
- Ví dụ toy x=[1,2,3,4] theo 100 km, y=[3,4,6,7]; w0=0, η=0,4, w1=0,7, J1=0,33125; nghiệm w*=1,4 có J*=0,025.
- Gradient của cả w,b phải tính từ cùng bộ cũ. Một bước tốt trong ví dụ không bảo đảm mọi learning rate đều giảm loss.
- MAE/RMSE đơn vị ngày, J/MSE ngày²; MAE không bảo đảm từng đơn. Baseline trung bình phù hợp L2, trung vị phù hợp L1.
- Hồi quy khoảng cách là lựa chọn sư phạm; không tuyên bố là kết quả tối ưu qua tìm siêu tham số. Không gọi lần trình bày lại test lịch sử là phép kiểm độc lập mới.

## Bước 2: xây dựng và nghiệm thu sau kế hoạch

Tạo DOCX, PDF, Markdown, nguồn LaTeX, PNG/SVG, dữ liệu đối chiếu và mã tái dựng. Tính lại nhãn từ timestamps, bốn đơn thật, toy gradient/loss, GD và OLS trên train, sai số test và mốc trung bình. Kiểm các cập nhật hai tham số, learning rate quá lớn và câu hỏi vận dụng. Xuất chính DOCX bằng Word, đọc cấu trúc PDF, xem trực quan từng trang; sửa nếu cần rồi đóng gói trước khi bắt đầu bài 5.

Thiết kế thống nhất A4, màu xanh đậm/vàng/teal, icon có nghĩa, bảng dễ đọc, công thức có diễn giải, footer PGS.TS Nguyễn Văn Hậu. 30–40 phút là thời lượng đọc dự kiến, chưa được đo trên sinh viên. Phần nâng cao tách phụ lục để không cản trở tuyến chính.
