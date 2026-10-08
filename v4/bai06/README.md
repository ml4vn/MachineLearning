# Bài 06 v4 — Cây quyết định

**PGS.TS. Nguyễn Văn Hậu** · Khoa Công nghệ Thông tin, Trường Đại học Công nghệ Kỹ thuật Hưng Yên

[← Mục lục v4](../README.md) · [Đọc trước trên GitHub](READING.md) · [Notebook](Bai06_Thuc_hanh_v4.ipynb) · [Slide PowerPoint có notes](PowerPoint/Bai06_v4_Cay_quyet_dinh_da_ra_soat.pptx)

## Học theo trình tự

1. Đọc mục tiêu, kiến thức nền và dữ liệu trong [tài liệu đọc trước](READING.md). Làm ví dụ tính tay và câu tự kiểm trước khi mở đáp án.
2. Theo dõi slide và notes; sau mỗi chặng đối chiếu hình tổng kết trong thư mục ảnh của bài.
3. Mở [Bai06_Thuc_hanh_v4.ipynb](Bai06_Thuc_hanh_v4.ipynb), đọc từng ô Markdown rồi chạy từng ô mã. Các ảnh, bảng và số liệu có thể truy lại từ dữ liệu.
4. Đọc giả định, giới hạn và kết quả kiểm chứng; tránh suy luận chất lượng mô hình chỉ từ một biểu đồ hoặc một lần chạy.

## Chạy bằng Python 3.12

Cài môi trường theo [hướng dẫn chung](../README.md). Tại thư mục gốc repository:

```bash
python v4/run_labs.py --lesson 06
```

Lệnh trên chạy notebook bằng chính môi trường Python đang dùng, rồi chạy kiểm chứng khoa học độc lập nếu bài có script tương ứng. Notebook đã chạy lại được lưu trong `outputs/v4/`; CSV, checkpoint và báo cáo tính lại nằm trong `v4/baiNN/data/` và `results/`. Các tệp tham chiếu này sẽ được cập nhật khi chạy lại; dùng một bản sao repository nếu muốn giữ nguyên toàn bộ bản đã phát hành.

Có thể mở notebook để học tương tác:

```bash
python -m jupyterlab v4/bai06/Bai06_Thuc_hanh_v4.ipynb
```

Hoặc chạy trực tiếp mã thuật toán:

```bash
python v4/bai06/source/tree_lab.py
```

Archive Olist nằm tại [`../datasets/olist.zip`](../datasets/olist.zip), dùng chung cho Bài 4–6; đã kèm trong repository nên không cần tài khoản Kaggle để chạy.

## Tài liệu bổ trợ

- [Bản đọc trước HTML gốc](Tai_lieu_doc_truoc/Bai06_Doc_truoc_v4.html): tải toàn bộ repository rồi mở tại máy để xem bố cục và KaTeX ngoại tuyến.
- [Bai06 Dap an va rubric v4](Tai_lieu/Bai06_Dap_an_va_rubric_v4.html)
- [Bai06 Mo rong v4](Tai_lieu/Bai06_Mo_rong_v4.html)
- [Bai06 Notes giang vien v4](Tai_lieu/Bai06_Notes_giang_vien_v4.html)
- [Bai06 Phieu hoc tap v4](Tai_lieu/Bai06_Phieu_hoc_tap_v4.html)
- [Bai06 Quiz va giai thich v4](Tai_lieu/Bai06_Quiz_va_giai_thich_v4.html)
- [Khám phá dữ liệu thật](Bai06_Du_lieu_that_v4.html)

[Dữ liệu, nguồn và điều kiện sử dụng](../DATA_SOURCES.md) · [Phạm vi cập nhật và đối chiếu](../../docs/CAP_NHAT_V4.md).
