# Kiểm tra chất lượng học liệu

[← Trang chủ](../README.md)

- Dùng tên ổn định, không gắn số phiên bản vào tên học liệu.
- Không commit PowerPoint, kể cả trong ZIP; CI kiểm tra ngoài `.gitignore`.
- Giữ nguồn, giấy phép và checksum dữ liệu.
- Notebook dự án sinh viên giữ TODO, gợi ý, kiểm thử; không kèm đáp án riêng.
- Không fit scaler, PCA hoặc chọn ngưỡng/siêu tham số từ test.

```bash
python tools/check_materials.py
python tools/build_course_readings.py --check
python run_tests.py
python run_all.py --mode toy --dpi 80
python course/run_labs.py --audit-only
python tools/check_projects.py
```

Kiểm tra cấu trúc không chứng minh lời giải sinh viên đúng. Kiểm chứng bằng chứng đã lưu cũng không thay thế huấn luyện lại. Cần đọc diễn giải và kiểm tra sản phẩm thực tế.

Xóa tệp ở nhánh hiện hành không xóa commit cũ. Không tự viết lại lịch sử hoặc force-push: cần chấp thuận riêng vì ảnh hưởng các bản clone. Không sửa hoặc xóa bản giảng dạy gốc ngoài repository.
