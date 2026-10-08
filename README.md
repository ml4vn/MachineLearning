# Khóa học Học máy

**PGS.TS. Nguyễn Văn Hậu**

Khoa Công nghệ Thông tin, Trường Đại học Công nghệ Kỹ thuật Hưng Yên

Học liệu hiện hành của **Bài 1–6 và 8–10 đã cập nhật v4**: kiến thức nền đọc trước, notebook và mã Python đầy đủ, dữ liệu thật, slide PowerPoint có notes, hình tổng kết và tài liệu bổ trợ. **Bài 7 giữ nguyên phiên bản hiện có**.

Sinh viên có nền toán trung bình nên đọc tài liệu nền, làm ví dụ tính tay và câu tự kiểm, rồi chạy từng ô notebook. Bài học nối liên tục từ dữ liệu → biểu diễn → mô hình/thuật toán → đánh giá và giới hạn.

## Chọn bài học

| Bài | Nội dung · case | Đọc trước | Thực hành, slide và tài liệu |
|---|---|---|---|
| 01 · v4 | Vector và cosine · MovieLens | [Đọc](v4/bai01/READING.md) | [Mở bài](v4/bai01/README.md) |
| 02 · v4 | kNN và chuẩn hóa · SMS | [Đọc](v4/bai02/READING.md) | [Mở bài](v4/bai02/README.md) |
| 03 · v4 | Đánh giá phân loại và ngưỡng · SMS | [Đọc](v4/bai03/READING.md) | [Mở bài](v4/bai03/README.md) |
| 04 · v4 | Hồi quy tuyến tính và Gradient Descent · Olist | [Đọc](v4/bai04/READING.md) | [Mở bài](v4/bai04/README.md) |
| 05 · v4 | Logistic, BCE và quyết định · Olist | [Đọc](v4/bai05/READING.md) | [Mở bài](v4/bai05/README.md) |
| 06 · v4 | Cây quyết định · Olist | [Đọc](v4/bai06/READING.md) | [Mở bài](v4/bai06/README.md) |
| 07 · giữ nguyên | Chia dữ liệu và đánh giá đáng tin cậy | [Đọc](readings/bai07/README.md) | [Mở bài](lessons/bai07/README.md) |
| 08 · v4 | RFM và K-means · Online Retail | [Đọc](v4/bai08/READING.md) | [Mở bài](v4/bai08/README.md) |
| 09 · v4 | PCA trên ảnh · Fashion-MNIST | [Đọc](v4/bai09/READING.md) | [Mở bài](v4/bai09/README.md) |
| 10 · v4 | Mạng neural, MLP và học biểu diễn · Fashion-MNIST | [Đọc](v4/bai10/READING.md) | [Mở bài](v4/bai10/README.md) |

## Bắt đầu thực hành v4

Tải **Code → Download ZIP** và giải nén toàn bộ repository, hoặc dùng `git clone https://github.com/ml4vn/MachineLearning.git`. Cài Python 3.12 64-bit và mở terminal ở thư mục gốc.

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

[Hướng dẫn v4 đầy đủ](v4/README.md) giải thích mở JupyterLab, chạy từng bài hoặc cả chín bài tuần tự, kiểm chứng và huấn luyện lại Bài 10. Dữ liệu đã kèm để chạy ngoại tuyến sau khi cài thư viện; không cần tài khoản Kaggle hoặc GPU. Bản HTML tương tác mở tại máy sau khi tải toàn bộ repository; bản Markdown đọc được ngay trên GitHub.

## Phiên bản, kiểm chứng và nguồn

- [Biên bản cập nhật v4](docs/CAP_NHAT_V4.md): phạm vi, đối chiếu và kết quả chạy lại.
- [Nguồn dữ liệu v4](v4/DATA_SOURCES.md): tác giả, snapshot và điều kiện sử dụng.
- [Manifest nguồn v4](v4/source_manifest.json): SHA256 và điều chỉnh đường dẫn để đóng gói.
- [Bộ v3 được giữ lại](README_V3.md): Word/PDF, tài liệu đọc trước và CLI `lessons/`; các tệp này giữ nhãn phiên bản cũ.

```bash
python tools/check_v4.py
python tools/build_v4_readings.py --check
python v4/run_labs.py --audit-only
```

Các phép biến đổi học tham số dùng train; ngưỡng/checkpoint chọn trên validation. Dữ liệu và test công khai đã được xem trong các phiên bản trước: kết quả v4 là tái lập học liệu với cấu hình và giới hạn đã công bố.
