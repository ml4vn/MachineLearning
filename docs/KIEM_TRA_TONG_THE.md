# Biên bản kiểm tra bộ thực hành

Ngày chuẩn bị: **13/09/2026**. Mười bài được triển khai theo thứ tự, mỗi bài lưu PLAN trước xây dựng và VALIDATION sau chạy/đọc hình. Các tệp bài giảng gốc được giữ riêng; bộ Python không cần thư mục nguồn v2 để chạy.

## Phạm vi đã kiểm tra

| Bài | Unit tests | PNG | Mốc đối chiếu chính |
|---|---:|---:|---|
| 01 | 5 | 2 | 9.742 phim, 19 nhãn; đồng hạng và vector thiếu |
| 02 | 6 | 4 | 5.574 SMS → 5.159 sau khử trùng; F1 test≈0,884462 |
| 03 | 5 | 5 | TN/FP/FN/TP=892/12/17/111; AUC≈0,969061 |
| 04 | 7 | 4 | OLS slope≈0,00563915 ngày/km; GD gần nghiệm OLS |
| 05 | 6 | 5 | Ngưỡng 0,1; chi phí test=16.944 |
| 06 | 6 | 7 | Depth 6; chi phí=17.359; suy luận thủ công khớp dự đoán cả 40.266 đơn test |
| 07 | 6 | 5 | 1.490 nhãn có sau cutoff; 363 khách lặp; nested/rolling CV bổ sung |
| 08 | 6 | 6 | 397.884 dòng, 4.338 khách; K4 SSE≈3.924,459699 |
| 09 | 6 | 8 | k90=82; logistic pixel/PCA64 đúng 2.500/2.511 ảnh validation |
| 10 | 7 | 9 | 3×50 epoch thật; checkpoint 40/27/40; test đúng 8.277/8.544 |
| **Tổng** | **60** | **55** | **Đủ 10 bài** |

Đã chạy thành công toàn bộ case thật trong môi trường đối chiếu. `validate_outputs.py` kiểm **91 điều kiện**, gồm cấu hình mặc định, số hình, kích thước 3840×2160 và các mốc khoa học của cả mười bài; tất cả đạt. Đã mở xem đủ 55 hình, sửa các chỗ chữ/chú giải chồng lấn được phát hiện và xem lại bản sửa.

Các unit tests kiểm toán học, kết quả thư viện và trường hợp biên. Kiểm tra khi chạy thật còn bao gồm hash dữ liệu, số lượng, ánh xạ dòng nguồn, pipeline, phép suy luận độc lập và kiểm định nghĩa. Các phương pháp kiểm được ghi cụ thể trong VALIDATION của mỗi bài; không quy tất cả thành một phép so số cuối.

## Môi trường

| Thành phần | Lượt đối chiếu slide | Venv cài mới từ requirements |
|---|---|---|
| Python | 3.12.14 | 3.12.14 |
| NumPy | 2.5.3 | 2.5.3 |
| pandas | 3.0.1 | 3.0.5 |
| SciPy | 1.18.1 | 1.18.1 |
| scikit-learn | 1.6.1 | 1.6.1 |
| Matplotlib | 3.10.3 | 3.10.3 |
| openpyxl | Có sẵn trong môi trường đối chiếu | 3.1.5 |

Venv được tạo mới trong repository, cài bằng pip; `pip check` không có dependency hỏng và 60 unit tests đều đạt. Tắt PYTHONPATH riêng của môi trường biên soạn khi kiểm. `requirements-tested.txt` lưu đầy đủ phiên bản của venv; đây là snapshot phiên bản, không phải khóa hash mọi wheel hay bảo đảm kết quả bit-for-bit giữa các hệ điều hành/BLAS.

Lượt chạy đầy đủ từ venv đã hoàn tất **cả 10 bài, tất cả mã thoát bằng 0**, chạy tuần tự trong khoảng **14 phút 11 giây** trên máy kiểm tra (không gồm thời gian cài thư viện và tải dữ liệu). Kiểm tra lại đầu ra của chính lượt này đạt **91/91 điều kiện**, gồm **55/55 PNG đúng 3840×2160**. Chênh lệch phiên bản pandas nêu trên không làm thay đổi các mốc được đối chiếu.

Log đầy đủ nằm tại `outputs/clean_run/`, mỗi bài có log riêng và `run_summary.json` tổng hợp; báo cáo máy đọc được của lượt sạch nằm trong `outputs/clean_validation.json`. Bản tóm tắt được đưa kèm mã tại [validation_summary.json](validation_summary.json). Báo cáo đối chiếu tách biệt nằm trong `outputs/reference_validation.json`; số liệu lớp học nằm trong `outputs/bai01/` đến `outputs/bai10/`. Các thư mục output có trên máy bàn giao nhưng không nằm trong ZIP mã nguồn hoặc phần theo dõi Git; có thể sinh lại bằng các lệnh trong README.

## Khả năng dùng độc lập

- Đã thử main.py từ thư mục làm việc khác và thử `predict.py` Bài 10 bằng mô hình đã lưu; kết quả suy luận khớp bản ghi gốc.
- Đã phân tích cú pháp đủ **53 tệp Python**; không phát hiện đường dẫn tuyệt đối Windows cố định trong mã phát hành.
- Đã thử tải mới đủ **8 tệp dữ liệu** từ Internet, SHA256 đều khớp; không chỉ kiểm bản cache có sẵn.
- Đã kiểm `.gitignore` thực sự loại tệp raw, output và venv. Hình xem trước được đưa riêng vào `docs/figures/`.
- `run_all.py` dừng khi một bài lỗi và dùng cùng split Fashion giữa Bài 09–10 khi thay seed chung. Đã chạy thử nhánh lựa chọn bài và seed riêng.

## Giới hạn của việc kiểm

Đã kiểm thực thi local trên Windows. Workflow cho Ubuntu và Windows đã được chuẩn bị, nhưng chưa gọi là GitHub CI đã chạy. Tại lần bàn giao Python ban đầu, repository đích chưa được cung cấp; đích hiện đã được chỉ định là `ml4vn/MachineLearning`. Xem [hướng dẫn đăng tải](GITHUB.md) để phân biệt trạng thái chuẩn bị local với việc công bố và kết quả CI trên GitHub.

Các con số mặc định nhằm tái lập case đã duyệt trong slide. Nếu đổi seed, dữ liệu, tham số hoặc phiên bản thư viện, cần báo cấu hình mới và phân tích kết quả; không sửa số liệu đầu ra để khớp mốc cũ. Test công khai đã xuất hiện trong pilot của giáo trình; việc chạy lại không tạo một phép đánh giá mới chưa từng được xem.
