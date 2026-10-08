# Học liệu Học máy v4

**PGS.TS. Nguyễn Văn Hậu** · Khoa Công nghệ Thông tin, Trường Đại học Công nghệ Kỹ thuật Hưng Yên

Bộ v4 gồm **Bài 1–6 và 8–10**. Mỗi bài có tài liệu kiến thức nền để đọc trước, notebook Python, mã thuật toán, dữ liệu, kết quả tham chiếu, slide PowerPoint có notes và tài liệu bổ trợ. Bài 7 giữ phiên bản hiện có và không thuộc đợt cập nhật này.

| Bài | Nội dung và case xuyên suốt | Kiến thức nền đọc trước | Thực hành, slide và tài liệu bổ trợ |
|---|---|---|---|
| 01 | Vector, cosine · MovieLens | [Đọc](bai01/READING.md) | [Mở bài](bai01/README.md) |
| 02 | kNN, khoảng cách, chuẩn hóa · SMS | [Đọc](bai02/READING.md) | [Mở bài](bai02/README.md) |
| 03 | Đánh giá phân loại, chi phí và ngưỡng · SMS | [Đọc](bai03/READING.md) | [Mở bài](bai03/README.md) |
| 04 | Hồi quy tuyến tính, Gradient Descent · Olist | [Đọc](bai04/READING.md) | [Mở bài](bai04/README.md) |
| 05 | Logistic, BCE và quyết định · Olist | [Đọc](bai05/READING.md) | [Mở bài](bai05/README.md) |
| 06 | Cây quyết định, Gini và pruning · Olist | [Đọc](bai06/READING.md) | [Mở bài](bai06/README.md) |
| 08 | RFM, Lloyd/K-means và kiểm cụm · Online Retail | [Đọc](bai08/READING.md) | [Mở bài](bai08/README.md) |
| 09 | PCA, phép chiếu và tái tạo · Fashion-MNIST | [Đọc](bai09/READING.md) | [Mở bài](bai09/README.md) |
| 10 | Mạng neural, MLP, backprop và checkpoint · Fashion-MNIST | [Đọc](bai10/READING.md) | [Mở bài](bai10/README.md) |

[Bài 7 hiện có: đọc trước](../readings/bai07/README.md) · [Thực hành](../lessons/bai07/README.md) · [Mục lục toàn khóa](../README.md).

## Cài đặt một lần

Tải **Code → Download ZIP** và giải nén toàn bộ repository, hoặc clone bằng Git. Có sẵn dữ liệu để chạy v4 ngoại tuyến sau khi cài thư viện; không cần tài khoản Kaggle hoặc GPU. Dữ liệu thật và checkpoint khiến gói tải lớn hơn một bộ mã ví dụ đơn giản.

Mở terminal tại thư mục gốc có `requirements-v4.txt`. Dùng **Python 3.12 64-bit**.

**Windows PowerShell**:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-v4.txt
.\.venv\Scripts\python.exe v4/run_labs.py --lesson 1
```

**macOS/Linux**:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-v4.txt
python v4/run_labs.py --lesson 1
```

Trong các lệnh tiếp theo, `python` phải là Python của môi trường vừa tạo. Trên Windows dùng `.\.venv\Scripts\python.exe` nếu chưa kích hoạt venv. Công thức hiển thị bằng KaTeX/Matplotlib; không cần cài LaTeX hệ thống.

## Học và chạy theo từng bài

Đọc tài liệu nền trước, làm ví dụ tính tay và câu tự kiểm, theo dõi slide rồi chạy từng ô notebook. Các trang HTML có bố cục, công thức và tương tác được mở tại máy sau khi tải **toàn bộ cây thư mục**; GitHub chỉ hiển thị mã HTML, không chạy JavaScript của các trang này.

```bash
python -m jupyterlab v4/bai04/Bai04_Thuc_hanh_v4.ipynb
python v4/run_labs.py --lesson 4
python v4/run_labs.py --lesson 5 --lesson 6
python v4/run_labs.py
```

`run_labs.py` chạy **tuần tự**, dùng đúng môi trường Python hiện tại và dừng khi một bài lỗi. Các notebook có 6–10 ô mã xen kẽ giải thích, tổng cộng 81 ô mã. Notebook đã chạy lại và nhật ký kiểm chứng nằm trong `outputs/v4/`; bảng, tham số và báo cáo khoa học của bài có thể được cập nhật trong `v4/baiNN/data/` và `results/`. Muốn giữ nguyên bản tham chiếu, chạy trên một bản sao repository.

Bài 8 tính lại RFM từ hóa đơn gốc và thử nhiều cấu hình K-means. Bài 9 fit lại full PCA cùng các baseline. Hai bài này cần nhiều thời gian hơn ví dụ tính tay. Bài 10 mặc định kiểm gradient, forward và kết quả từ checkpoint đã lưu; muốn huấn luyện lại **ba seed × 50 epoch**, chạy:

```bash
python v4/bai10/source/mlp_lab.py --force
```

## Kiểm tra và truy nguồn

```bash
python tools/check_v4.py
python tools/build_v4_readings.py --check
python v4/run_labs.py --audit-only
```

`--audit-only` kiểm các bằng chứng đã lưu bằng script khoa học độc lập của Bài 5, 6, 8, 9, 10; không huấn luyện lại mô hình và không thay thế việc chạy notebook. Bài 1–4 đặt các phép kiểm trong mã lab/notebook.

Mã học thuật và số liệu gốc được giữ từ bộ v4 đã xây dựng. Mã Bài 4–6 được điều chỉnh đường dẫn để đọc archive Olist dùng chung tại `datasets/olist.zip`; notebook Bài 3 bổ sung ID ô theo schema Jupyter hiện tại. [Manifest nguồn](source_manifest.json) ghi SHA256 và những điều chỉnh này. [Biên bản phát hành](../docs/CAP_NHAT_V4.md) giải thích kiểm tra thực tế, kết nối với v3 và giới hạn tái lập.

Đặc trưng học tham số được fit trên train; ngưỡng và checkpoint chọn trên validation. RFM là phân tích mô tả lịch sử. Fashion-MNIST có test công khai đã được xem trong các phiên bản trước, vì vậy đây là tái lập bài giảng với cấu hình cố định, không phải đánh giá trên test vừa được niêm phong.

[Nguồn dữ liệu và điều kiện sử dụng](DATA_SOURCES.md) · [Bộ CLI và tài liệu Word/PDF v3](../README_V3.md).
