> Kế hoạch gốc của phiên bản trước. Kế hoạch đối chiếu hiện tại: [Hướng dẫn v3](HUONG_DAN_V3.md) và [phạm vi cập nhật](../../docs/PYTHON_V3.md).

# Bài 02 — kNN và chuẩn hóa đặc trưng

## Rà soát và kế hoạch trước khi viết mã
Nguồn: 68 slide v2; sms_lab.py; case_audit.json. Dùng hai đặc trưng
n_chars, digit_fraction, không dùng bộ bốn đặc trưng của bản thử trước.

| Khối | Thực hành | Slide | Sản phẩm |
|---|---|---|---|
| Dữ liệu thật | Đọc SMS gốc, ID nguồn, loại trùng, chia tập | 2–17 | CSV truy vết, hình văn bản và số đếm |
| Thuật toán | Khoảng cách → xếp hạng → k láng giềng → phiếu | 19–30 | Hàm NumPy, bảng từng bước, sơ đồ |
| Thang đo | Tỷ lệ so với phần trăm; fit StandardScaler trên train | 31–43 | Phản ví dụ, kiểm bất biến đơn vị |
| Case thật | So k=3/5/11 với và không scale trên validation | 44–49 | CSV lựa chọn cấu hình |
| Đánh giá | Khóa cấu hình tốt nhất rồi đo test | 50–56 | Ma trận nhầm lẫn, các lỗi cụ thể |

Kiểm: 5.574 dòng đọc; 5.159 sau loại trùng; split 3.095/1.032/1.032;
seed=42 cho k=11 có scale; test [[892,12],[17,111]].
Phân biệt hòa khoảng cách và hòa phiếu; tỷ lệ phiếu chưa là xác suất đã hiệu chỉnh.
Chạy toy, real, kiểm dữ liệu gốc, các unit test và đọc đủ mọi hình trước khi chốt.
