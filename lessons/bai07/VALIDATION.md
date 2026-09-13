# Hoàn tất Bài 07

Đã hoàn thành sáu bước, sáu kiểm thử đạt và lệnh `--mode all` chạy thành công từ Olist gốc.

- Chuẩn hóa đúng cho điểm 10 có z = 9; fit sai cả dữ liệu cho z = 1,3887301497. Pipeline từng fold được kiểm tham số train riêng.
- Mô phỏng nhóm tái tạo 118/0 nhóm giao nhau và accuracy 97,5%/42,5%.
- Chọn 100 ứng viên ngẫu nhiên cho điểm chọn trung bình 0,62396, điểm mới 0,49926, khớp slide.
- Audit raw có 1.490 đơn duyệt trước/giao sau cutoff; 363 khách lặp train/test. Cột tương lai tái tạo ma trận hoàn hảo đúng như ví dụ rò rỉ cần phê bình.
- Nested CV bổ sung chạy đủ 3 outer × 3 inner với pipeline trong từng fold; outer accuracy 0,70/0,74/0,74, không gán các số bổ sung này cho slide cũ.
- Ba cửa sổ thời gian bổ sung chạy thành công. Train/validation lần lượt 5.850/5.660; 12.824/6.737; 20.580/7.117. Nhãn train cuối luôn trước cutoff; membership được xuất để kiểm lại.
- Đã xem đủ năm PNG 3840 × 2160; timeline phân biệt cutoff minh họa 01/04/2018 với split chính.

Môi trường: Python 3.12.14, scikit-learn 1.6.1, Matplotlib 3.10.3. Dữ liệu, membership, số liệu và hình trong `outputs/bai07/`.
