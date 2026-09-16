# Bài 01 · Vector và độ tương đồng cosine


**Lộ trình thực hành cập nhật:** [Dự đoán → chạy → đối chiếu → giải thích](HUONG_DAN_V3.md). Tài liệu đọc trước v3; slide v3.

[← Mục lục khóa học](../../README.md) · [📖 Tài liệu đọc trước Bài 01](../../readings/bai01/README.md)

**Câu hỏi:** Sau The Matrix, những phim nào giống về các nhãn đã mã hóa?
Ta chưa có bằng chứng về sở thích của một người cụ thể.

## Mục tiêu và chuẩn bị
Sau bài này, bạn chuyển nhãn thành vector, giải thích dot/chuẩn/cosine,
tính một ví dụ bằng tay, kiểm bằng thư viện và đọc giới hạn của kết quả.
Cần biết phép cộng, nhân, căn bậc hai và danh sách Python.
Đối chiếu slide v3 theo bảng trong hướng dẫn thực hành mới.

## Chạy từ thư mục gốc repository
```bash
python -m pip install -r requirements.txt
python -m lessons.bai01.main --mode toy
python -m mlcourse.data fetch --dataset movielens
python -m lessons.bai01.main --mode all
python -m unittest lessons.bai01.tests -v
```
Cũng có thể chạy `python lessons/bai01/main.py --mode all`.
Ví dụ nhỏ chạy ngoại tuyến. Case thật cần `data/raw/movielens.zip`.
Có tệp gốc đúng snapshot ở nơi khác: dùng
`python -m mlcourse.data fetch --dataset movielens --source-dir DUONG_DAN`.
Tệp tải được kiểm SHA256; nếu nguồn thay đổi, chương trình báo khác snapshot.

## Dữ liệu thật nhìn thấy được
MovieLens latest-small, snapshot tạo ngày 26/09/2018: 9.742 phim,
100.836 lượt đánh giá từ 610 người. Lab dùng movies.csv, không dùng ratings để học sở thích.

| Cột | Ý nghĩa | Sử dụng |
|---|---|---|
| movieId | Khóa phim | Truy vết và ổn định hiển thị khi đồng điểm |
| title | Tên phim | Giải thích kết quả |
| genres | Các nhãn phân cách bằng dấu thẳng đứng | Tạo multi-hot |

IMAX được giữ như nhãn metadata của nguồn. Token thiếu thể loại được loại khỏi bộ trục.
Ba trục tính tay là Action, Comedy, Sci-Fi; bản đầy đủ có 19 nhãn.

## Đi từng bước
1. Mở `algorithms.py`: đọc `genre_set`, rồi `multi_hot`. Cùng tọa độ phải có cùng ý nghĩa.
2. Với u=(1,0,1), v=(1,1,1): các tích là (1,0,1), dot=2,
   chuẩn của u là √2, chuẩn của v là √3; cosine=2/√6≈0,816497.
3. Đọc `cosine`: đầu vào hữu hạn, cùng số chiều và khác vector 0 là điều kiện của công thức.
4. Chạy toy: xem CSV từng bước và hình so hướng với độ xa.
5. Chạy real: mở `real_source_rows.csv`, rồi so `real_movie_comparison.csv`.
6. Mở bảng xếp hạng toàn kho; tìm lý do nhiều phim có cùng điểm cao nhất.

$$\operatorname{cos}(u,v)=\frac{u^Tv}{\|u\|_2\|v\|_2}.$$

## Kết quả mong đợi với cấu hình mặc định
| Phim | Cosine 3 trục | Cosine 19 nhãn |
|---|---:|---:|
| Star Wars (260) | 1 | 0,666667 |
| Men in Black (1580) | 0,816497 | 0,666667 |
| Jurassic Park (480) | 1 | 0,866025 |
| Alien (1214) | 0,707107 | 0,408248 |
| Toy Story (1) | 0 | 0 |

Kho có 34 phim thiếu nhãn; sau loại query và các vector 0, còn 9.707 ứng viên.
Có 42 phim cùng bộ nhãn với The Matrix. Thứ tự movieId chỉ để hiển thị ổn định.

## Đầu ra
Trong `outputs/bai01/`: results.json, toy_steps.csv, real_source_rows.csv,
real_movie_comparison.csv, real_ranked_movies.csv, toy_vectors.png, real_metadata.png.
PNG mặc định 3840×2160; dùng `--dpi 100` nếu cần hình nhẹ.
results.json ghi seed, phiên bản thư viện và phạm vi kết luận.

## Tự khám phá và đáp án
1. Nhân u với 3 rồi với −3. **Đáp án:** hệ số dương giữ cosine; hệ số âm đảo dấu.
2. Mã hóa Drama, Romance trên ba trục hiện tại. Có phải thiếu dữ liệu?
   **Đáp án:** vector chiếu bằng 0 nhưng metadata vẫn có; khác token thiếu.
3. Chạy `--query-id 1`. Vì sao top-10 đổi?
   **Đáp án:** đổi phim tham chiếu làm đổi nhãn cần so. Không có đáp án “phim hay nhất” phổ quát.

## Những kết luận cần tránh
- Cosine 0,8 không là xác suất thích 80%.
- Vector 0 làm cosine toán học không xác định; None trong hàm tự viết khác quy ước 0 của sklearn.
- Bình phương cosine có thể đảo xếp hạng khi cosine âm.
- Tính giống metadata không thay thế đánh giá gợi ý bằng dữ liệu sở thích và giao thức thích hợp.

## Nguồn
- [GroupLens MovieLens](https://grouplens.org/datasets/movielens/latest/).
- Harper & Konstan (2015), [The MovieLens Datasets](https://doi.org/10.1145/2827872).
- [scikit-learn 1.6: cosine_similarity](https://scikit-learn.org/1.6/modules/generated/sklearn.metrics.pairwise.cosine_similarity.html).
- Điều kiện sử dụng dữ liệu nằm trong README của gói MovieLens; không suy giấy phép mã nguồn thành giấy phép dữ liệu.
