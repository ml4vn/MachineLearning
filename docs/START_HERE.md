# Bắt đầu trong 10 phút

[← Trang chủ](../README.md)

Tải **Code → Download ZIP**, giải nén toàn bộ; hoặc `git clone https://github.com/ml4vn/MachineLearning.git`. Cài Python 3.12 64-bit. Mở terminal tại thư mục có `requirements.txt`.

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m jupyterlab
```

macOS/Linux:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m jupyterlab
```

Mở `course/bai01/Bai01_Thuc_hanh.ipynb`. Chọn kernel thuộc môi trường vừa tạo, chạy từng ô từ trên xuống. Trên Windows, thay `python` trong lệnh tiếp theo bằng `.\.venv\Scripts\python.exe` nếu chưa kích hoạt môi trường.

## Chọn đúng tài liệu

- `course/`: học liệu chính; Bài 7 được dẫn tới tài liệu tương ứng.
- `examples/`: ví dụ thuật toán nhỏ có kiểm thử; `readings/` hỗ trợ các ví dụ này.
- `projects/`: dự án cần tự hoàn thiện. Điền TODO, chạy kiểm thử rồi mới đi tiếp.
- `outputs/`: sản phẩm bạn tạo, không đưa dữ liệu cá nhân lên GitHub.

| Hiện tượng | Cách xử lý |
|---|---|
| `ModuleNotFoundError` | Cài requirements bằng đúng Python của kernel |
| Không tìm thấy dữ liệu | Tải toàn bộ repository, không tải riêng notebook |
| TODO chưa hoàn thành | Điểm dừng có chủ đích; đọc gợi ý và kiểm thử |
| Kết quả thay đổi | Restart Kernel, chạy theo thứ tự; giữ seed và cách chia tập |
| Huấn luyện chậm | Đóng notebook chạy nền; dùng cấu hình nhỏ được cung cấp |

Markdown hiển thị công thức LaTeX. HTML dùng KaTeX ngoại tuyến; tải repository rồi mở HTML tại máy vì GitHub không chạy HTML tương tác. Các dự án dùng CPU, không yêu cầu GPU.
