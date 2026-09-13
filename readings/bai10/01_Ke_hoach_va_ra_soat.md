# Bài 10 — Bước 1: rà soát và kế hoạch tài liệu đọc trước

## Căn cứ và mục tiêu

Bắt đầu sau khi bài 09 hoàn tất và đóng gói. Đã đối chiếu 68 tiêu đề slide Bài10_v2 (60 chính, 8 mở rộng), notes các khối XOR, forward, loss, gradient và kiến trúc; bản rà soát khoa học, mã mlp_lab.py, case_audit.json, protocol_before_fit.json và frozen_decision_before_test.json. Nguồn chính thức: Fashion-MNIST, tài liệu MLP và MLPClassifier scikit-learn 1.6.

Giữ một case thật Fashion-MNIST nối bài 9 và toy XOR được ghi rõ là mô phỏng. Mục tiêu tối thiểu: đọc được mạng một tầng ẩn, giải thích vai trò phi tuyến, tính một lượt forward–loss–gradient–update đơn giản, chọn checkpoint đúng tập và đọc kết quả có điều kiện. Đọc 30–40 phút là dự kiến, chưa đo trên sinh viên; đạo hàm đầy đủ ở phụ lục tùy chọn.

## Rà soát khoa học và quyết định biên soạn

- Flatten theo thứ tự đã biết giữ mọi pixel, có thể reshape. MLP không áp đặt cấu trúc trọng số cục bộ dùng chung như CNN; không nói flatten làm mất dữ liệu hình ảnh.
- Neuron = affine rồi activation. ReLU(a)=max(0,a); đầu vào a có thể âm, đầu ra không âm. Chồng affine không activation vẫn affine. XOR không tách bởi một ngưỡng affine trong hai tọa độ gốc; phát biểu không áp dụng mọi biểu diễn.
- Trong phép tính tay XOR, h1=ReLU(x1+x2), h2=ReLU(x1+x2−1) được cho sẵn; chỉ học v1,v2,c. Tách rõ khả năng biểu diễn của bộ trọng số dựng (2,−4,−1) với điều bảo đảm thuật toán học tìm được.
- BCE trung bình bốn điểm không L2; p ban đầu 1/2, gradient (0,1/8,0), bước eta=8 cho (0,−1,0), loss 0,693147→0,598176. Eta=8 là ví dụ riêng, không là khuyến nghị cho mạng thật. Gradient bằng 0 của một tham số tại một điểm không chứng minh tham số vô ích.
- Backprop tính gradient; optimizer dùng gradient để cập nhật. Tính toàn bộ gradient tại tham số cũ trước khi cập nhật. ReLU không khả vi tại 0; phép kiểm sai phân dùng ví dụ khác có preactivation 0,32 và 0,44.
- Sigmoid/BCE dành ví dụ nhị phân; case thật 10 nhãn loại trừ nhau dùng softmax/cross-entropy. Loss lấy xác suất của nhãn thật; accuracy dùng argmax, hai chỉ số không tương đương.
- Mạng 784→64→10 có 50.890 tham số gồm bias. Giữ split 12k/3k/10k và pixel/255, Adam, batch 256, 50 epoch; 47 batch/epoch nếu giữ batch cuối. Không tuyên bố hội tụ.
- Chọn checkpoint theo cross-entropy validation; seed chính 42 chốt trước, epoch 40. Không chọn seed 44 sau khi thấy accuracy cao hơn. Ba seed chỉ mô tả dao động, không là khoảng tin cậy.
- Đánh giá lại forward mô hình cố định trên test là phép kiểm số, không phải thí nghiệm test mới. Benchmark công khai và pilot trước đã xem test; không gọi là tập chưa từng được dùng trong toàn dự án. Không dùng số mới để chọn lại mô hình.
- Ảnh minh họa gồm mẫu đầu tiên theo thứ tự validation của ba nhóm: logistic sai/MLP đúng; cả hai sai; logistic đúng/MLP sai. Đây là minh họa có chủ đích, không là mẫu ngẫu nhiên ước lượng tỷ lệ lỗi.

## Bước 2 — kế hoạch 12 trang

| Trang | Mục thống nhất | Nội dung, hình và kiểm tra |
|---|---|---|
| 1 | Vấn đề | Từ pixel tới đặc trưng học theo nhãn; sơ đồ 784→64→10; mục tiêu đọc. |
| 2 | Tiên quyết | Affine, ReLU, sigmoid, đạo hàm, loss; đồ thị ReLU; K1–K2. |
| 3 | Dữ liệu thật | Ba ảnh có source ID và nhãn/predictions; bảng split, đơn vị, giữ kết nối bài 9. |
| 4 | Trực giác | XOR trước/sau biến đổi h1,h2; bảng bốn điểm; đường phân tách và giới hạn kết luận. |
| 5 | Công thức | Forward 2→2→1, sigmoid, BCE trung bình, softmax và CE 10 lớp; giải thích ký hiệu. |
| 6 | Quy trình học | Forward→loss→backprop→update; mini-batch/epoch; phân biệt Adam và GD; checkpoint. |
| 7 | Ví dụ xuyên suốt | Bảng đóng góp gradient XOR; tính update, loss mới; nghiệm dựng 4/4 vẫn có loss dương. |
| 8 | Đọc kết quả | Đường CE train/validation và recall theo lớp; bảng validation/test baseline–MLP; seed và test có điều kiện. |
| 9 | Tự kiểm | Sáu câu: ReLU, tham số, gradient/update, BCE/accuracy, checkpoint, giới hạn kết luận. |
| 10 | Ghi nhớ | Checklist, bảng nối các nhóm bài toàn khóa, nguồn và hiện vật. |
| 11 | Phụ lục A | Giải thích K1–K2 và sáu câu, phương án nhiễu và chỉ dẫn ôn tập. |
| 12 | Phụ lục B | Tính forward/backprop hai tầng trên x=(0,6;0,2), nhãn 1; kiểm sai phân và khuyến nghị đọc sâu. |

## Sản phẩm và cổng chất lượng

DOCX chỉnh được văn bản/bảng, PDF đọc/in, Markdown và JSON nội dung, LaTeX nguồn, hình PNG/SVG, bảng dữ liệu ví dụ, mã và báo cáo kiểm tra. Thiết kế A4 cùng 10 mục, 2 phụ lục, màu navy/teal/amber và icon có nhãn; PGS.TS Nguyễn Văn Hậu ở mọi trang.

Tính độc lập toy và sai phân 9 tham số; đếm tham số và batch; tính lại logits/predictions/confusion/CE từ mảng trọng số lưu cho validation và test; chạy lại đúng seed chính 42 trong ngân sách 50 epoch để đối chiếu checkpoint và lịch sử, không mở rộng tìm kiếm. Đọc ba seed còn lại từ kết quả lưu và ghi rõ phạm vi xác minh. Xuất Word→PDF, render toàn bộ trang và kiểm bằng mắt; chỉ đánh dấu hoàn tất sau khi trang, mục, footer, phép tính và bố cục đạt. Cuối cùng đóng gói bài 6–10 và cập nhật mục lục cả 10 bài.

Nguồn: https://github.com/zalandoresearch/fashion-mnist ; https://scikit-learn.org/1.6/modules/neural_networks_supervised.html ; https://scikit-learn.org/1.6/modules/generated/sklearn.neural_network.MLPClassifier.html
