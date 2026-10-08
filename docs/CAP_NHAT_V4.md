# Cập nhật học liệu Học máy v4

Đợt cập nhật ngày **08/10/2026** dành cho Bài **1, 2, 3, 4, 5, 6, 8, 9, 10** của PGS.TS. Nguyễn Văn Hậu. Bài 7 giữ nguyên toàn bộ tài liệu và mã hiện có.

## Học liệu được phát hành

- Chín tài liệu kiến thức nền đọc trước: giữ bản HTML v4 đã xây dựng, bổ sung bản Markdown đầy đủ để đọc ngay trên GitHub với bảng, hình, công thức và tự kiểm.
- Chín notebook Python cùng mã thuật toán, dữ liệu gốc, bảng đã chuẩn bị, arrays/checkpoint và các báo cáo tham chiếu cần để chạy độc lập từng bài.
- Chín file PowerPoint v4 có **621 slide và 621 trang notes**, các hình tổng kết sau chặng và tài liệu bổ trợ hiện có.
- Hướng dẫn cài Python/JupyterLab, trình chạy tuần tự và kiểm chứng; nguồn dữ liệu, giấy phép đi kèm và checksum.

[Mục lục v4](../v4/README.md) là điểm bắt đầu cho sinh viên. Word/PDF và bộ CLI cũ vẫn ở vị trí cũ, được nhận diện là [học liệu v3](../README_V3.md). Không đổi nhãn tài liệu v3 thành v4.

## Đối chiếu theo bài

| Bài | Nội dung thực hành v4 | Điểm cần đọc cùng kết quả |
|---|---|---|
| 01 | Vector thể loại phim, chuẩn, dot product và cosine | Chọn không gian đặc trưng làm đổi thứ hạng; vector không và đồng hạng phải xử lý rõ. |
| 02 | SMS thật, kNN và chuẩn hóa | Khử trùng trước khi chia; fit scaler trên train; chọn cấu hình bằng validation. |
| 03 | Confusion, precision/recall/F1, AP, chi phí và ngưỡng | Mẫu số, lớp dương, trường hợp chưa xác định và phạm vi các chính sách được so sánh. |
| 04 | Batch Gradient Descent, learning rate và Olist | Cập nhật đồng thời từ gradient cũ; quy ước J=MSE/2; so nghiệm GD với OLS. |
| 05 | Logistic, sigmoid, BCE và lựa chọn ngưỡng | Cân nặng đơn không được xem là 0 khi có thành phần chưa biết; xác suất khác quyết định. |
| 06 | Cây quyết định, Gini, cắt tỉa và đường đi | So Logistic/cây trên cùng cohort; importance không chứng minh quan hệ nhân quả. |
| 08 | Hóa đơn → RFM → log1p/scaler → K-means | RFM là mô tả lịch sử; silhouette, ổn định và khả năng diễn giải đều cần kiểm. |
| 09 | Pixel → centered data → PCA → reconstruction/baseline | Phân biệt covariance, phương sai và score; MSE dùng ảnh tái tạo chưa clip; không chọn chiều bằng test. |
| 10 | XOR, forward, backprop, Adam và checkpoint | Giữ optimizer liên tục qua epoch; checkpoint theo validation; ba seed chỉ là mô tả độ biến động. |

## Điều chỉnh để chạy từ repository

Mã và nội dung được nhập từ bộ `MLv4`. Các file PowerPoint, HTML, ảnh và dữ liệu được sao chép giữ nguyên nội dung. Notebook giữ nguyên mã và văn bản; output được chạy lại trong môi trường phát hành, metadata được bổ sung như ghi dưới đây. Dữ liệu và kết quả suy ra có thể được tính lại bởi chính mã v4; mọi khác biệt byte được ghi trong manifest. Các thay đổi về đóng gói được ghi rõ:

1. Mã chuẩn bị/kiểm chứng Olist ở Bài 4–6 đọc một archive dùng chung tại `v4/datasets/olist.zip`, thay cho ba bản sao ở `data/raw/`. Các phép tính, seed, chia tập và quy tắc chọn mô hình được giữ nguyên.
2. Bổ sung README, trang bắt đầu tối giản và bản đọc Markdown cho GitHub. Trình chạy mới mở kernel trong thư mục bài bằng Python hiện tại; không phụ thuộc đường dẫn Python hoặc thư mục của máy tác giả.

3. Chạy lại và cập nhật output của chín notebook; bổ sung ID ổn định cho 16 ô notebook Bài 3 theo schema nbformat 4.5. Mã và văn bản giải thích không đổi. Giữ byte của tài liệu nguồn bằng `.gitattributes`, tránh sai checksum do tự chuyển CRLF/LF trên các hệ điều hành.

[Manifest nguồn](../v4/source_manifest.json) lưu đường dẫn tương đối trong bộ nguồn, SHA256 gốc và SHA256 sau điều chỉnh. Tệp trong `data/` và `results/` có thể được tính lại khi chạy; trình kiểm cấu trúc kiểm checksum của các tài liệu và đầu vào bất biến, không yêu cầu mọi kết quả số thực phải giữ nguyên từng byte.

## Kiểm chứng đợt phát hành

**Đã đạt kiểm tra tại máy trước phát hành:** chín notebook, **81 ô mã**, chạy tuần tự và không có ô lỗi; năm script kiểm chứng khoa học độc lập đều đạt. Bài 4 tái tạo Olist từ archive dùng chung và fit lại GD; Bài 10 huấn luyện lại đầy đủ **ba seed × 50 epoch**, đạt **511 phép kiểm**. Bộ cũ vẫn vượt qua **60 kiểm thử và 10 ví dụ toy**. `pip check`, đối chiếu tài liệu cũ, công thức/hình/liên kết v4 và bản Markdown đều đạt.

| Bài | Ô mã đã chạy | Kiểm chứng độc lập sau notebook |
|---|---|---|
| 01 | 6 | Phép kiểm nằm trong lab/notebook |
| 02 | 7 | Phép kiểm nằm trong lab/notebook |
| 03 | 8 | Phép kiểm nằm trong lab/notebook |
| 04 | 10 | Phép kiểm nằm trong lab/notebook |
| 05 | 10 | 75 phép kiểm đạt |
| 06 | 10 | 169 phép kiểm đạt |
| 08 | 10 | 117 phép kiểm đạt |
| 09 | 10 | 181 phép kiểm đạt |
| 10 | 10 | 146 phép kiểm đạt |

Bản đọc trực tiếp gồm **127 bảng, 83 công thức LaTeX và 40 hình/sơ đồ**. Bài 10 giữ notebook mặc định nhanh, có bước kiểm checkpoint và suy luận; việc huấn luyện lại đầy đủ đã được chạy riêng bằng `--force`. Xem [biên bản máy đọc được và phiên bản thư viện](../v4/VALIDATION.json).

Các lệnh kiểm:

```bash
python -m pip check
python tools/check_course.py
python tools/check_v4.py
python tools/build_v4_readings.py --check
python run_tests.py
python v4/run_labs.py
```

Trình chạy notebook xóa output trong bộ nhớ trước khi thực thi; bản chạy mới lưu trong `outputs/v4/`. Chín notebook được phát hành đã nhận output mới từ lần kiểm này. Kiểm chứng khoa học độc lập chạy tiếp cho các bài có script tương ứng. Bài 10 phân biệt rõ kiểm checkpoint đã lưu với huấn luyện lại bằng `--force`.

## Giới hạn sử dụng kết quả

Các con số là kết quả của snapshot và cấu hình giảng dạy đã công bố. Olist dùng cohort lịch sử đơn hoàn tất và các giả định về khả năng biết metadata. Fashion-MNIST có benchmark công khai đã được xem ở phiên bản trước; không gọi test này là mới hoặc chưa từng nhìn thấy. Không suy ra chất lượng triển khai chỉ từ kết quả benchmark hoặc từ ba seed.

[Nguồn và điều kiện sử dụng dữ liệu](../v4/DATA_SOURCES.md). Không tự gán giấy phép mới cho toàn bộ khóa học trong đợt phát hành này.
