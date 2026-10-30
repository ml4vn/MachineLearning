# Học liệu theo bài

[← Lộ trình 10 bài](../README.md) · [Cài môi trường](../docs/START_HERE.md) · [Dự án sinh viên](../projects/README.md)

Học liệu chính gồm tài liệu đọc có công thức, hình trực quan, notebook, dữ liệu và mã kiểm chứng. Bài 7 sử dụng [tài liệu đọc](../readings/bai07/README.md) và [ví dụ Python](../examples/bai07/README.md).

```bash
python -m jupyterlab
python course/run_labs.py --lesson 1
python course/run_labs.py --lesson 4 --lesson 5
python course/run_labs.py --audit-only
```

Không truyền `--lesson` sẽ chạy chín notebook tuần tự. Bài 7: `python -m examples.bai07.main --mode toy`. Bài 8/9 cần thời gian đọc hóa đơn/PCA; Bài 10 mặc định dùng checkpoint tham chiếu. Huấn luyện lại Bài 10: `python course/bai10/source/mlp_lab.py --force` (ba seed, 50 epoch).

Notebook đã chạy và nhật ký lưu trong `outputs/`. Mã lab có thể cập nhật bảng/arrays trong thư mục bài: chạy trên bản sao nếu cần giữ nguyên bản tham chiếu. `--audit-only` kiểm bằng chứng đã lưu, không thay thế huấn luyện lại.

HTML tương tác cần tải toàn bộ repository rồi mở tại máy; GitHub chỉ đọc mã HTML. Bản `READING.md` đọc trực tiếp trên GitHub.

## Đánh giá đúng phạm vi

Các phép biến đổi học tham số dùng train; ngưỡng và cấu hình dùng validation. RFM là mô tả lịch sử. Test công khai đã được dùng trong học liệu nên kết quả là tái lập, không phải đánh giá trên test vừa niêm phong. Không suy rộng thành cam kết triển khai thực tế.

[Nguồn dữ liệu và giấy phép](DATA_SOURCES.md) · [Kiểm tra chất lượng](../docs/MAINTAINING.md)
