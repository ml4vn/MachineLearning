# Hoàn tất Bài 08

Đã hoàn thành sáu bước; 6 kiểm thử đạt và `--mode all` chạy thành công từ Online Retail XLSX gốc.

- SHA256 khớp; 541.909 dòng gốc → 397.884 dòng giữ → 4.338 khách. Đối chiếu R/F/M độc lập cho toàn bộ khách; chênh tiền lớn nhất 3,64×10⁻¹² bảng Anh.
- SSE ví dụ 39 → 12 → 11,625 → 22/3; nghiệm K=2 và K=3 được xác nhận bằng vét cạn; đủ 20 bộ khởi tạo K=3.
- SSE K=2…6 và silhouette cùng mẫu khớp case_audit.json của slide. K=4 có 877/1.579/720/1.162 khách; profile khớp.
- K=2 RFM thô cho silhouette toàn bộ 0,9844890543 nhưng chia 4.330/8 khách. Phân biệt rõ với silhouette tính trên mẫu của dữ liệu đã xử lý.
- 5.192 dòng trùng hợp lệ; thí nghiệm bỏ trùng làm đổi M của 951 khách. Khách 12755 có R=281, F=2, M=3.811,95 trên 4 dòng; predict khớp tâm gần nhất.
- Đã xem đủ 6 PNG 3840×2160; điều chỉnh nhãn Dung để không chồng tâm cụm, xem lại bản sửa. Có tên giảng viên và chú thích phạm vi.

Python 3.12.14, scikit-learn 1.6.1, Matplotlib 3.10.3. Kết quả: `outputs/bai08/`. K=4 phục vụ diễn giải; chưa chứng minh hiệu quả kinh doanh hay dự báo ngoài mẫu.
