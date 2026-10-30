> **Học liệu hiện hành: [Bài 02 ](../../course/bai02/README.md).** Trang này giữ hướng dẫn CLI của bộ Python ; notebook  và số liệu  nằm ở liên kết trên.

# Bài 02 · kNN: nhìn SMS thật, đo gần và bỏ phiếu


**Lộ trình thực hành cập nhật:** [Dự đoán → chạy → đối chiếu → giải thích](HUONG_DAN.md). Tài liệu đọc hỗ trợ ví dụ Python.

[← Mục lục khóa học](../../README.md) · [📖 Tài liệu đọc trước Bài 02](../../readings/bai02/README.md)

**Câu hỏi:** Một tin nhắn có hình thức gần spam trong tập train có được kNN dự đoán là spam?
Bạn sẽ nhìn văn bản gốc, đếm đặc trưng và truy tới từng láng giềng.

## Mục tiêu và kiến thức cần có
Biết dùng vector, khoảng cách Euclid, trung bình và độ lệch chuẩn.
Sau lab, bạn giải thích kNN bằng bốn bước và biết vì sao thang đo, k và cách chia tập quan trọng.
Đối chiếu slide  theo bảng trong hướng dẫn thực hành mới.

## Chạy
```bash
python -m examples.bai02.main --mode toy
python -m mlcourse.data fetch --dataset sms
python -m examples.bai02.main --mode all
python -m unittest examples.bai02.tests -v
python -m examples.bai02.main --mode toy --k 5 --weighted
```
Cài thư viện theo README chung. Có thể chạy trực tiếp `python examples/bai02/main.py`.
Chế độ toy không cần mạng. `--k` và `--weighted` là thử nghiệm bổ sung trên toy;
grid dữ liệu thật vẫn là k=3/5/11 để khớp bài giảng.

## Dữ liệu và định nghĩa
Nguồn UCI SMS Spam Collection: nhãn ham/spam và văn bản.
Bộ đọc của bài cho 5.574 bản ghi; sau gộp trùng văn bản chuẩn hóa còn 5.159.
Không suy số này từ mô tả trang web: chính ZIP và cách đọc đã được kiểm.
Train/validation/test lần lượt 3.095/1.032/1.032, phân tầng theo nhãn, seed 42.

| Trường | Cách tính | Chú ý |
|---|---|---|
| source_record | Số thứ tự bản ghi đọc từ nguồn | Truy vết được văn bản |
| n_chars | len(text) | Gồm dấu câu và khoảng trắng |
| n_digits | Tổng c.isdigit() | Đếm ký tự, không đếm cụm số; theo Unicode |
| digit_fraction | n_digits/n_chars | Tỷ lệ trong [0,1], chưa là phần trăm |
| y | 1 nếu spam, 0 nếu ham | Nhãn để học/đánh giá; không là đặc trưng |

Chuỗi normal chỉ phục vụ loại trùng; các đặc trưng được đếm từ text gốc.
Source record 4500 là query minh họa mặc định, không được cho vào tập láng giềng.
Nếu đổi seed khiến bản ghi ấy vào train, chương trình chọn một query validation khác và ghi lại ID.

## Từng bước cần đọc trong mã
1. `mlcourse/sms.py: text_features`: tự đếm một SMS rồi so với CSV.
2. `load_sms`: loại trùng trước chia tập; train/validation/test không giao nhau.
3. `algorithms.py: knn_steps`: tính d², xếp hạng, chọn k và lấy phiếu.
4. `fit_sms`: fit StandardScaler chỉ trên train; dùng lại mean/scale cho mọi tập.
5. So sáu cấu hình trên validation theo F1 của spam. Nếu hòa, ưu tiên k nhỏ rồi không scale.
6. Sau lựa chọn, tính dự đoán test một lần. Không chọn lại k từ test.

$$d^2(x,q)=\sum_j(x_j-q_j)^2,\qquad z_j=\frac{x_j-\mu_{j,train}}{\sigma_{j,train}}.$$

StandardScaler dùng độ lệch chuẩn theo mẫu số n. Xếp theo d² tương đương xếp theo d,
nhưng bỏ phiếu theo nghịch đảo khoảng cách phải dùng d, không dùng d².

## Kết quả và cách đọc
- Toy: P1…P5 có d² = 2,2,5,18,9 đến (1,1); k=3 cho spam, k=5 cho ham.
- Mean train xấp xỉ (79,310178; 0,018052), scale (59,103962; 0,047065).
- Cấu hình được chọn: k=11, có scale; F1 validation=0,896.
- Test, hàng là nhãn thật, cột là dự đoán:

| | Dự đoán ham | Dự đoán spam |
|---|---:|---:|
| Thật ham | 892 | 12 |
| Thật spam | 17 | 111 |

Hai đặc trưng cho kết quả này trên snapshot và giao thức đã nêu; chưa hiểu ngữ nghĩa SMS.

## File sinh ra trong outputs/bai02
- `real_features.csv`: nguyên văn, ID, hai đặc trưng và split của từng tin.
- `real_query_source.csv`, `real_query_neighbors.csv`: theo dấu query và 3 láng giềng.
- `validation_grid.csv`, `validation_predictions.csv`, `test_predictions.csv`.
- `toy_neighbors.csv`, `results.json`.
- Bốn PNG: vị trí toy, train trước/sau scale, bảng láng giềng và văn bản SMS cùng số đếm.

## Tự khám phá và đáp án
1. Đổi tỷ lệ sang phần trăm. **Đáp án:** Euclid thô có thể đổi thứ tự; chuẩn hóa tương ứng sẽ triệt tiêu đổi đơn vị dương.
2. Cho query trùng một điểm train, dùng weighted. **Đáp án:** chỉ các láng giềng khoảng cách 0 nhận trọng số trong quy ước của hàm.
3. Dùng k=2 và số phiếu cân bằng. **Đáp án:** hàm này chọn nhãn 0 khi hòa; không được nói kNN luôn có đa số duy nhất.
4. Có thể gọi phiếu 8/11 là xác suất đúng 72,7% không? **Đáp án:** chưa; cần kiểm tra hiệu chỉnh và phạm vi dữ liệu.

Hòa khoảng cách tại biên k có thể làm thư viện chọn láng giềng khác quy tắc ổn định của hàm minh họa.
Đừng coi sự khác đó tự động là sai công thức.

## Nguồn
[UCI SMS Spam Collection](https://archive.ics.uci.edu/dataset/228/sms+spam+collection);
[kNN scikit-learn 1.6](https://scikit-learn.org/1.6/modules/neighbors.html);
[StandardScaler](https://scikit-learn.org/1.6/modules/generated/sklearn.preprocessing.StandardScaler.html).
