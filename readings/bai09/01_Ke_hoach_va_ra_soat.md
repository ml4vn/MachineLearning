# Bài 09 — Bước 1: rà soát và kế hoạch tài liệu đọc trước

## Phạm vi và căn cứ

Thực hiện sau khi bài 08 đã hoàn tất. Bám Bài09_v2: 60 slide (54 chính, 6 mở rộng), notes giảng viên, source/pca_lab.py, results/case_audit.json, data/source_manifest.json và các mảng dữ liệu lưu kèm. Đối chiếu nguồn Fashion-MNIST của Zalando và tài liệu PCA scikit-learn 1.6. Không sửa slide gốc.

Mục tiêu cho sinh viên trung bình: nhìn được ảnh thật và giá trị pixel; phân biệt trải phẳng với giảm chiều; tính được phép chiếu/tái tạo hai chiều; đọc phương sai giữ lại, lỗi tái tạo và kết quả phân loại như ba đại lượng riêng. Đọc khoảng 30–40 phút là dự kiến thiết kế, không phải thời gian đo thực nghiệm.

## Các quyết định khoa học trước khi viết

- Một ảnh là một quan sát; 28×28 = 784 đặc trưng. Flatten giữ nguyên 784 giá trị. PCA thay số đặc trưng, không thay số ảnh.
- 12.000 train và 3.000 validation lấy từ tập train chính thức. Mã train:xxxx chỉ tệp nguồn chính thức, không tự động chỉ tập huấn luyện của thí nghiệm. Bài 9 không tính chỉ số trên test chính thức; phần đánh giá test thuộc bài 10.
- Chia 255 là phép đổi thang cố định. Trung bình và trục PCA được fit từ train; không fit lại trên validation. Không chuẩn hóa từng pixel về phương sai 1 trong case này.
- Toy 4 điểm dùng covariance chia n; scikit-learn dùng n−1 cho explained_variance_. Công bố quy ước, không trộn eigenvalue giữa hai quy ước. EVR không thay đổi.
- PCA tối đa phương sai chiếu với vector đơn vị và tối thiểu lỗi tái tạo bình phương trong không gian tuyến tính đã định tâm. Không dùng nhãn để chọn trục, không bảo đảm giữ thông tin phân lớp.
- k90=82 tính từ train; EVR tại 81 là 0,899272 và tại 82 là 0,900122. “90%” không là accuracy, tỷ lệ ảnh đúng hay dung lượng tệp nén.
- Ảnh tái tạo được clip [0,1] chỉ để hiển thị. MSE tính trước clip trên từng tọa độ. Không đồng nhất MSE validation với tổng eigenvalue train bị bỏ.
- Chênh accuracy validation pixel và PCA64 của cùng một lần chia không đủ kết luận PCA luôn cải thiện nhận dạng.

## Bước 2 — thiết kế 12 trang, cùng 10 mục và 2 phụ lục

| Trang | Mục | Nội dung cụ thể và hoạt động |
|---|---|---|
| 1 | Vấn đề và mục tiêu | Câu hỏi lưu biểu diễn ảnh gọn hơn; dải ảnh thật và tái tạo k=2,16,64,128; bốn năng lực đầu ra. |
| 2 | Nền tảng | Vector, trung bình, tích vô hướng, độ dài, phương sai; hai câu kiểm nhanh; khác biệt đặc trưng và quan sát. |
| 3 | Dữ liệu thật | Ảnh với source ID và vùng pixel 5×5 có giá trị; bảng train/validation/test, 10 lớp, đơn vị và phép chia 255. |
| 4 | Trực giác PCA | Bốn điểm thiết kế, trục PC1, chân chiếu và phần dư; câu hỏi về hai điểm có cùng biểu diễn một chiều. |
| 5 | Ký hiệu và công thức | Định tâm, score, tái tạo, ràng buộc đơn vị và EVR; quy ước hàng/cột rõ ràng. |
| 6 | Quy trình | Chia dữ liệu → fit train → biến đổi validation → so mục tiêu; sơ đồ pipeline; fit/transform khác nhau. |
| 7 | Ví dụ tính tay | Trung bình (5,5), bảng điểm/score/tái tạo, eigenvalue, EVR90%; MSE mỗi điểm 0,5 và mỗi tọa độ 0,25. |
| 8 | Đọc kết quả | Hai đồ thị train EVR và validation MSE; bảng k=2,16,64,128; k90=82; accuracy pixel/PCA64 và giới hạn suy luận. |
| 9 | Tự kiểm tra | Sáu câu: chiều dữ liệu, định tâm đúng, score, EVR, nhãn không được bảo toàn, lỗi trước/sau clip. |
| 10 | Ghi nhớ và nguồn | Checklist đọc PCA, bảng thuật ngữ, nguồn chính thức, nối bài 10. |
| 11 | Phụ lục A | Đáp án K1–K2 và sáu câu, giải thích lựa chọn sai và chỉ dẫn ôn tập. |
| 12 | Phụ lục B | Mean image và hai trục có dấu; chia n/n−1, SVD, dấu trục; mở rộng tùy chọn. |

## Hình thức và kiểm chứng

Giữ văn bản/bảng Word có thể sửa, màu xanh navy–xanh lục–hổ phách, icon quan sát/ghi nhớ/thử làm; PGS.TS Nguyễn Văn Hậu và số trang ở mọi trang. Sáu hình khoa học PNG/SVG (ảnh nguồn thật, phép chiếu, pipeline, đường cong, basis); công thức render từ LaTeX, kèm mã nguồn. Tài liệu A4, không dùng ảnh nguyên slide làm trang đọc.

Tính lại PCA từ train, đối chiếu EVR/k90/MSE với audit slide; kiểm raw pixel và mã nguồn ảnh được hiển thị; kiểm toy bằng đại số và NumPy; tính lại dự đoán validation từ hệ số đã lưu và ghi rõ không huấn luyện lại logistic. Lưu bảng số và báo cáo kiểm tra. Xuất PDF từ DOCX bằng Word chạy ẩn, render Poppler và xem đủ từng trang. Chỉ đóng gói và chuyển bài 10 sau khi kiểm tra nội dung, thứ tự, số trang, footer và bố cục đạt.

Nguồn: https://github.com/zalandoresearch/fashion-mnist ; https://scikit-learn.org/1.6/modules/generated/sklearn.decomposition.PCA.html
