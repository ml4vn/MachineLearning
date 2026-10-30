> **Học liệu hiện hành: [Bài 08 ](../../course/bai08/README.md).** Trang này giữ hướng dẫn CLI của bộ Python ; notebook  và số liệu  nằm ở liên kết trên.

# Bài 08 · K-means: từ hóa đơn thật đến nhóm khách hàng


**Lộ trình thực hành cập nhật:** [Dự đoán → chạy → đối chiếu → giải thích](HUONG_DAN.md). Tài liệu đọc hỗ trợ ví dụ Python.

[← Mục lục khóa học](../../README.md) · [📖 Tài liệu đọc trước Bài 08](../../readings/bai08/README.md)

**Mục tiêu:** tự lập RFM, giải thích từng bước Lloyd, chọn cách biểu diễn và đọc cụm một cách có cơ sở. Bám sát Bài08: dữ liệu → RFM → thuật toán → đánh giá → giới hạn. Cần biết vector, khoảng cách và trung bình; ôn Bài 01–02 khi cần.

## 1. Chạy bài

Từ thư mục gốc repository, sau khi cài `requirements.txt`:

```bash
python -m examples.bai08.main --mode toy
python -m mlcourse.data fetch --dataset retail
python -m examples.bai08.main --mode all
python -m unittest examples.bai08.tests
```

`--customer-id 12755` chọn khách để truy vết; `--seed 42` điều khiển khởi tạo và mẫu silhouette; `--dpi 240` tạo PNG 3840×2160. `--data-dir` và `--output-dir` nhận đường dẫn riêng. Chạy được trực tiếp `python examples/bai08/main.py`. Chế độ toy không cần dữ liệu hay Internet. Đổi seed có thể đổi nghiệm và số hiệu cụm.

## 2. Dữ liệu có thật ở đâu?

[UCI Online Retail](https://archive.ics.uci.edu/dataset/352/online+retail) gồm giao dịch một nhà bán lẻ trực tuyến tại Anh trong giai đoạn 2010–2011. Chương trình kiểm SHA256, đọc XLSX ngay trong ZIP và xử lý lại từ 541.909 dòng. Sau các điều kiện giữ: có CustomerID, Quantity > 0, UnitPrice > 0, mã hóa đơn không bắt đầu C, còn 397.884 dòng của 4.338 khách.

| Trường gốc | Ý nghĩa | Dùng để làm gì? |
|---|---|---|
| CustomerID | Mã khách | Khóa gom nhóm, không đưa vào khoảng cách |
| InvoiceNo | Mã hóa đơn | Đếm hóa đơn khác nhau |
| InvoiceDate | Thời điểm mua | Xác định lần mua cuối |
| Quantity, UnitPrice | Số lượng, giá đơn vị (£) | Tính tiền từng dòng |

Khách 12755 có 4 dòng nhưng chỉ **2 hóa đơn**. CSV `raw_customer_invoices.csv` cho phép mở từng dòng và tự cộng tiền. Bộ dữ liệu lịch sử này không đại diện tự động cho hành vi khách hàng hiện nay.

## 3. Định nghĩa trước khi tính

Tại ảnh chụp **10/12/2011**:

| Biến | Công thức/ý nghĩa | Ví dụ khách 12755 |
|---|---|---|
| R | Ngày ảnh chụp trừ ngày lịch mua cuối | 281 ngày |
| F | Số InvoiceNo khác nhau | 2 |
| M | Tổng Quantity × UnitPrice của dòng giữ lại | £3.811,95 |

Chuẩn hóa ngày mua về đầu ngày trước khi trừ. M là tiền của các giao dịch mua dương được giữ, **không phải lợi nhuận hoặc doanh thu ròng sau hoàn trả**. Giá có thể có phần nhỏ hơn một penny: không làm tròn từng dòng tùy tiện. Mỗi khách được đối chiếu lại bằng ngày Python, tập hóa đơn và Decimal, độc lập với groupby.

## 4. Khoảng cách quyết định cách nhìn

Theo slide: $r$ là RFM thô, $u=\log(1+r)$, $x=(u-m)/s$; $\mu_k$ chỉ tâm cụm. Mã dùng `X0`, `np.log1p(X0)`, `X` tương ứng. Dùng `log1p(R,F,M)`, sau đó StandardScaler với trung bình và độ lệch chuẩn của 4.338 khách. Đây là phân tích mô tả một ảnh chụp dữ liệu: chưa có mục tiêu đánh giá khả năng dự báo tương lai. Nếu xây dựng đánh giá ngoài mẫu, phải fit cả biến đổi trên tập huấn luyện.

Log giảm ảnh hưởng đuôi dài; chuẩn hóa đặt ba tọa độ trên thang so sánh được. Với RFM thô, phương sai tiền chiếm gần toàn bộ tổng phương sai; silhouette cao vẫn có thể chỉ tách vài khách chi tiêu đặc biệt lớn. Không so trực tiếp SSE thô với SSE đã chuẩn hóa vì chúng thuộc hai không gian khác nhau.

## 5. Theo dõi Lloyd bằng tay

Mục tiêu $J=\sum_i\|x_i-\mu_{c_i}\|^2$.

1. Giữ tâm cố định, gán mỗi điểm về tâm gần nhất.
2. Giữ nhãn cố định, thay tâm bằng trung bình các điểm trong cụm.
3. Lặp đến khi tâm không đổi.

Ví dụ 6 điểm, tâm ban đầu tại An và Chi: SSE qua bốn nửa bước là **39 → 12 → 11,625 → 7,3333**. Tâm cuối là (2; 5/3) và (6; 14/3). Tại lần gán thứ hai, Chi so sánh khoảng cách bình phương 6,25 với 6,625 và chuyển cụm.

Mã giảng dạy chọn chỉ số cụm nhỏ nhất khi hòa; gặp cụm rỗng thì báo lỗi và yêu cầu khởi tạo lại, không âm thầm bỏ cụm. Vét cạn chỉ giới hạn tối đa 9 điểm. Với 6 điểm, thử hết 20 bộ tâm ban đầu K=3 cho thấy nhiều nghiệm địa phương; nghiệm tốt nhất được kiểm bằng vét cạn mọi phân hoạch.

## 6. Chọn K và đọc profile

Chạy K=2…6, `n_init=20`, seed 42. Vẽ SSE và silhouette trên **cùng 2.000 khách**; khoảng cách silhouette được tính trong mẫu này, không phải tính toàn bộ rồi lấy trung bình một phần. Với điểm i, $s_i=(b_i-a_i)/\max(a_i,b_i)$; a là khoảng cách trung bình tới các điểm khác cùng cụm, b là giá trị nhỏ nhất trong các khoảng cách trung bình tới cụm khác. Singleton có s=0 theo quy ước sklearn; K=1 hoặc K=n không hợp lệ.

K=4 là **lựa chọn để minh họa cách đọc profile**, không khẳng định tối ưu. Trong cấu hình tham chiếu, K=2 có silhouette mẫu cao hơn. Profile hiển thị trung vị R/F/M trong đơn vị gốc, cùng số khách. Số hiệu cụm không có thứ bậc và có thể hoán vị giữa các lần chạy. Gợi ý chăm sóc khách là giả thuyết cần đánh giá thêm bằng chi phí, phản hồi hoặc thử nghiệm có đối chứng.

## 7. Đọc các tệp đầu ra

Trong `outputs/bai08/`:

| Tệp | Cách dùng |
|---|---|
| `toy_lloyd_history.json`, `toy_20_starts.csv` | Từng nửa bước và ảnh hưởng khởi tạo |
| `rfm_customers.csv`, `filters.csv` | RFM từng khách và số dòng qua bộ lọc |
| `raw_customer_invoices.csv` | Truy vết ví dụ về hóa đơn thật |
| `k_grid.csv`, `silhouette_sample_ids.csv` | So sánh K có thể tái lập |
| `cluster_profiles.csv`, `initialization_stability.csv` | Diễn giải cụm, ARI giữa các nghiệm |
| `duplicate_sensitivity.csv` | Ảnh hưởng khi bỏ dòng trùng hoàn toàn |
| `kmeans_model.json` | Mean, scale, tâm cụm; dữ liệu số, không dùng pickle |
| 6 ảnh PNG và `results.json` | Minh họa và toàn bộ số liệu tóm tắt |

Các dòng trùng được **giữ** để khớp cấu hình slide: không có đủ bằng chứng mọi dòng trùng đều là lỗi. Thí nghiệm phụ loại trùng cho thấy M thay đổi ở 951 khách; đây là độ nhạy của quy tắc làm sạch, không chứng minh một cách là đúng tuyệt đối. Khách truy vết được transform bằng đúng scaler và predict bằng tâm đã fit; không fit riêng một khách. Khi thay ngày ảnh chụp cần một quy trình cập nhật nhất quán.

## 8. Dừng lại tự kiểm tra

| Câu hỏi | Đáp án và giải thích |
|---|---|
| 4 dòng cùng một InvoiceNo làm F tăng 4? | Sai. Chúng chỉ góp 1 hóa đơn. |
| SSE giảm khi tăng K có đủ để chọn K lớn nhất? | Không. K=n có thể cho SSE=0 nhưng không tạo sự cô đọng hữu ích. |
| Đổi mã cụm 0↔1 có đổi phân hoạch? | Không; ARI giữa hai cách đặt tên là 1. |
| Silhouette của điểm 2 trong {0,2}, {10,12}? | a=2, b=9, nên s=7/9. |
| K=4 tốt hơn K=2 vì có nhiều nhóm hơn? | Chưa đủ cơ sở; cần độ ổn định, profile và mục tiêu sử dụng. |

## 9. Thực hành mở rộng

Thử seed 7, so sánh kích thước cụm và ARI; giải thích tại sao gần bằng SSE không đồng nghĩa nhãn hoàn toàn giống nhau. Thay `n_init=20` bằng 1 ở một bản sao và quan sát độ nhạy. Vẽ hai vành trăng bằng màu nhãn gốc để đối chiếu với K-means. Thử chuẩn hóa mà không log, báo cáo cả profile và các khách cực trị; không chỉ chọn cấu hình có một chỉ số cao nhất.

## 10. Kết nối bài tiếp theo

K-means gán nhóm theo hình học của đặc trưng. Bài 09 tiếp tục câu hỏi: nếu số chiều rất lớn, có thể tìm một hệ tọa độ ít chiều hơn nhưng giữ lại phần lớn biến thiên không? Đó là vai trò của PCA; giảm chiều và phân cụm là hai mục tiêu khác nhau.
