# Bài 05 v4 — Hồi quy Logistic

**PGS.TS. Nguyễn Văn Hậu** · Khoa Công nghệ Thông tin, Trường Đại học Công nghệ Kỹ thuật Hưng Yên

[← Mục lục v4](../README.md) · [Đọc trước trên GitHub](READING.md) · [Notebook](Bai05_Thuc_hanh_v4.ipynb) · [Slide PowerPoint có notes](PowerPoint/Bai05_v4_Logistic_da_ra_soat.pptx)

## Học theo trình tự

1. Đọc mục tiêu, kiến thức nền và dữ liệu trong [tài liệu đọc trước](READING.md). Làm ví dụ tính tay và câu tự kiểm trước khi mở đáp án.
2. Theo dõi slide và notes; sau mỗi chặng đối chiếu hình tổng kết trong thư mục ảnh của bài.
3. Mở [Bai05_Thuc_hanh_v4.ipynb](Bai05_Thuc_hanh_v4.ipynb), đọc từng ô Markdown rồi chạy từng ô mã. Các ảnh, bảng và số liệu có thể truy lại từ dữ liệu.
4. Đọc giả định, giới hạn và kết quả kiểm chứng; tránh suy luận chất lượng mô hình chỉ từ một biểu đồ hoặc một lần chạy.

## Chạy bằng Python 3.12

Cài môi trường theo [hướng dẫn chung](../README.md). Tại thư mục gốc repository:

```bash
python v4/run_labs.py --lesson 05
```

Lệnh trên chạy notebook bằng chính môi trường Python đang dùng, rồi chạy kiểm chứng khoa học độc lập nếu bài có script tương ứng. Notebook đã chạy lại được lưu trong `outputs/v4/`; CSV, checkpoint và báo cáo tính lại nằm trong `v4/baiNN/data/` và `results/`. Các tệp tham chiếu này sẽ được cập nhật khi chạy lại; dùng một bản sao repository nếu muốn giữ nguyên toàn bộ bản đã phát hành.

Có thể mở notebook để học tương tác:

```bash
python -m jupyterlab v4/bai05/Bai05_Thuc_hanh_v4.ipynb
```

Hoặc chạy trực tiếp mã thuật toán:

```bash
python v4/bai05/source/logistic_lab.py
```

Archive Olist nằm tại [`../datasets/olist.zip`](../datasets/olist.zip), dùng chung cho Bài 4–6; đã kèm trong repository nên không cần tài khoản Kaggle để chạy.

## Tài liệu bổ trợ

- [Bản đọc trước HTML gốc](Tai_lieu_doc_truoc/Bai05_Kien_thuc_nen_tang_va_doc_truoc_v4.html): tải toàn bộ repository rồi mở tại máy để xem bố cục và KaTeX ngoại tuyến.
- [Bai05 Dap an v4](Tai_lieu/Bai05_Dap_an_v4.html)
- [Bai05 Phieu v4](Tai_lieu/Bai05_Phieu_v4.html)
- [Bai05 Quiz v4](Tai_lieu/Bai05_Quiz_v4.html)
- [Huong dan va mo rong v4](Tai_lieu/Huong_dan_va_mo_rong_v4.html)

[Dữ liệu, nguồn và điều kiện sử dụng](../DATA_SOURCES.md) · [Phạm vi cập nhật và đối chiếu](../../docs/CAP_NHAT_V4.md).
