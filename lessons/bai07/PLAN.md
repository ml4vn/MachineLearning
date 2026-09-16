> Kế hoạch gốc của phiên bản trước. Kế hoạch đối chiếu hiện tại: [Hướng dẫn v3](HUONG_DAN_V3.md) và [phạm vi cập nhật](../../docs/PYTHON_V3.md).

# Kế hoạch Bài 07 — Đánh giá đáng tin cậy

## 1. Rà soát

Đã đối chiếu 60 slide v2 và `leakage_lab.py`. Giữ Olist để kiểm thời điểm, cột tạo nhãn, quần thể đánh giá và khách hàng lặp. Tách rõ mô phỏng nhóm/chọn mô hình khỏi kết quả Olist.

## 2. Các chặng

| Chặng | Thực hành | Tệp/hình |
|---|---|---|
| Fit/transform | Chuẩn hóa [0,2] rồi điểm 10, so cách fit sai | Bảng số và hình so sánh |
| Pipeline/fold | K-fold 6 dòng; fit pipeline riêng trong từng fold | Bảng chỉ số fold, scaler đã học, sơ đồ phân chia |
| Phụ thuộc nhóm | 200 nhóm × 4 hàng; bộ ghi nhớ nhóm | Accuracy chia dòng/chia nhóm, bảng dự đoán |
| Chọn nhiều lần | 500 lần thử, 1/10/100 ứng viên ngẫu nhiên | Điểm chọn và điểm dữ liệu mới |
| Nested CV | Mô phỏng riêng: inner chọn C, outer đánh giá | Mã GridSearchCV trong mỗi outer fold, kết quả đầy đủ |
| Olist | Cột tương lai tái tạo nhãn; ngày biết nhãn; khách lặp | Audit từ ZIP, timeline, ma trận rò rỉ và bảng provenance |
| Rolling evaluation | Ba cửa sổ trong giai đoạn train, fit lại pipeline mỗi cửa sổ | AP từng fold; lọc nhãn theo cutoff |

## 3. Điểm khoa học

Không diễn giải đổi scaler đồng nghĩa luôn đổi dự đoán hoặc luôn tăng điểm. Nhóm lặp giữa train/test không tự động sai, phải xét đích dự đoán khách quen hay khách mới. Thời điểm duyệt trước cutoff chưa đủ nếu nhãn sau cutoff. Pipeline chỉ tổ chức fit đúng nơi, không làm cột tương lai hợp lệ. Nested CV đánh giá thủ tục chọn; SD fold không tự là khoảng tin cậy. Mô phỏng thêm được ghi rõ là phần thực hành bổ sung, không gán số mới cho slide cũ.

## 4–6. Kiểm chứng và hoàn tất

Tái tạo 1.490 đơn duyệt trước/giao sau cutoff từ orders gốc, 363 khách train/test lặp, ma trận rò rỉ hoàn hảo chỉ để phê bình. Mô phỏng nhóm đạt 97,5%/42,5% ở seed tham chiếu. Kiểm coverage/disjointness của fold, fit riêng từng pipeline, nhãn sẵn có tại cutoff; kiểm nested có inner/outer tách biệt. Viết README, xem mọi PNG 3840 × 2160, ghi hoàn tất trước Bài 08.
