> **Học liệu hiện hành: [Bài 10 ](../../course/bai10/README.md).** Trang này giữ hướng dẫn CLI của bộ Python ; notebook  và số liệu  nằm ở liên kết trên.

# Bài 10 · Mạng neuron: từ một bước tính tay đến nhận dạng ảnh


**Lộ trình thực hành cập nhật:** [Dự đoán → chạy → đối chiếu → giải thích](HUONG_DAN.md). Tài liệu đọc hỗ trợ ví dụ Python.

[← Mục lục khóa học](../../README.md) · [📖 Tài liệu đọc trước Bài 10](../../readings/bai10/README.md)

**Mục tiêu:** giải thích vai trò của phi tuyến, tính forward/loss/backprop, phân biệt gradient với cập nhật Adam, đọc đường học và chọn checkpoint đúng quy trình. Nội dung bám Bài10, tiếp nối cùng dữ liệu Fashion-MNIST của Bài 09. Cần ôn dot product, sigmoid/BCE ở Bài 05 và chia tập ở Bài 07.

## 1. Chạy trọn bài

```bash
python -m examples.bai10.main --mode toy
python -m mlcourse.data fetch --dataset fashion
python -m examples.bai10.main --mode all
python -m unittest examples.bai10.tests
```

Mặc định chạy thật **3 seed × 50 epoch trên CPU**, tự fit lại baseline logistic. Không cần đã chạy bài 09. Có thể chạy trực tiếp `python examples/bai10/main.py`. Khi thử nhanh:

```bash
python -m examples.bai10.main --mode real --epochs 5 --runs 1 --output-dir outputs/bai10_quick
```

Lần chạy nhanh là một cấu hình khác, không dùng để xác nhận số liệu slide. `--seed 42` là seed mạng chính; nếu runs=3 thì thêm 43 và 44. `--split-seed 42` giữ nguyên split Bài 09. `--data-dir`, `--output-dir`, `--dpi 240` có cùng ý nghĩa như các bài trước. Chế độ toy không tải dữ liệu.

## 2. Nhìn thấy dữ liệu và cách chia

[Fashion-MNIST](https://github.com/zalandoresearch/fashion-mnist), Zalando Research: ảnh xám 28×28, 10 lớp. Mã nhãn: 0 T-shirt/top; 1 Trouser; 2 Pullover; 3 Dress; 4 Coat; 5 Sandal; 6 Shirt; 7 Sneaker; 8 Bag; 9 Ankle boot. Tệp IDX được kiểm SHA256 trước khi dùng.

| Tập | Số ảnh | Vai trò |
|---|---:|---|
| Train | 12.000 | Cập nhật mọi trọng số của MLP và fit logistic |
| Validation | 3.000 | Chọn epoch bằng cross-entropy, đọc lỗi |
| Test chính thức | 10.000 | Đánh giá cấu hình chính đã chốt |

45.000 ảnh train chính thức còn lại không dùng trong thí nghiệm tập con. Mỗi ảnh chia 255 sang float64; không fit scaler mới. `split_membership.csv` lưu mã gốc `train:<hàng từ 0>` hoặc `test:<hàng từ 0>`. Chương trình kiểm ID và hash ảnh; không có ID sản phẩm để kết luận chắc chắn về độc lập theo nhóm sản phẩm. Đây là benchmark lịch sử, không đại diện tự động cho ảnh tùy ý ở cửa hàng.

## 3. XOR: tại sao cần hàm phi tuyến?

| x₁ | x₂ | y | h₁=ReLU(x₁+x₂) | h₂=ReLU(x₁+x₂−1) |
|---:|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 | 0 |
| 0 | 1 | 1 | 1 | 0 |
| 1 | 0 | 1 | 1 | 0 |
| 1 | 1 | 0 | 2 | 1 |

Với score affine s=w₁x₁+w₂x₂+b, luôn có s₀₀+s₁₁=s₀₁+s₁₀. Nếu quy tắc dự đoán 1 khi s≥0 phân loại đúng XOR thì vế trái phải âm, vế phải phải không âm: mâu thuẫn. Vì vậy một đường thẳng không thể đúng đủ bốn điểm.

Hai tọa độ ẩn trong bảng được **đặt sẵn** để minh họa. Trong không gian mới, score `2h₁−4h₂−1` cho −1,+1,+1,−1, đúng cả bốn điểm. Đó là một nghiệm **tự dựng**, không phải kết quả mà optimizer vừa học được. Chồng nhiều lớp affine mà không có hàm kích hoạt vẫn chỉ tạo một ánh xạ affine; ReLU tạo thay đổi về năng lực biểu diễn.

## 4. Một bước học tầng ra, tính được bằng tay

Giữ H cố định, đặt v₁=v₂=b=0. Khi đó mọi logit bằng 0, p=0,5; BCE trung bình bằng ln2. Với $\delta_i=p_i-y_i$:

$$\nabla_vL=H^T(p-y)/n,\qquad \partial L/\partial b=\operatorname{mean}(p-y).$$

Gradient là (0; 1/8; 0). GD với η=8 cho tham số mới (0; −1; 0). Logit mới: 0,0,0,−1; xác suất: 0,5; 0,5; 0,5; 0,268941. BCE giảm từ 0,693147 xuống **0,598176**; quy tắc p≥0,5 cho 3/4 đúng.

Gradient v₁ bằng 0 chỉ nói tổng đóng góp tại **vị trí hiện tại** triệt tiêu; không kết luận neuron đó vô ích mãi mãi. η=8 đã được kiểm cho bước cụ thể này, không phải tốc độ học nên dùng chung. Nghiệm dựng đúng 4/4 vẫn có BCE≈0,313262 vì xác suất nhãn đúng chưa bằng 1. Accuracy và loss đo hai khía cạnh khác nhau.

## 5. Backpropagation cho toàn bộ mạng nhỏ

Ví dụ x=(0,6;0,2), y=1; W₁ có các hàng (0,5;−0,4), (0,3;0,8), b₁=(0,1;0,1), v=(0,7;−0,5), b=0,2.

| Đại lượng | Giá trị hoặc công thức |
|---|---|
| a=W₁x+b₁ | (0,32; 0,44) |
| h=ReLU(a) | (0,32; 0,44) |
| s=vᵀh+b (mã: logit) | 0,204 |
| p=σ(s) | 0,550823865 |
| δ=p−y | −0,449176135 |
| δh=δv ⊙ 1(a>0) | (−0,314423295; 0,224588068) |
| ∂L/∂W₁₁=δh₁x₁ | −0,188653977 |

Tính đủ chín gradient tại **cùng bộ tham số cũ**, sau đó mới cập nhật. Với η=0,1, W₁₁ mới≈0,518865398. `toy_backprop.csv` có toàn bộ trọng số trước/sau và hai cách tính đạo hàm.

Kiểm độc lập bằng sai phân trung tâm `[L(θ+εeⱼ)−L(θ−εeⱼ)]/(2ε)`, ε=10⁻⁶. Ví dụ này tránh điểm gãy ReLU; sai khác lớn nhất khoảng 4,12×10⁻¹¹ trong lần chạy đã kiểm. Sai khác nhỏ với mốc finite differences của slide đến từ cách viết BCE tương đương nhưng ổn định số hơn. ReLU tại 0 không khả vi; mã chọn đạo hàm 0 theo quy ước, không dùng điểm gãy để kết luận finite differences thất bại. Trong mạng thật, W1 có shape (đầu vào, neuron), nên mã dùng `X @ W1`; điều này là chuyển quy ước ma trận, không đổi phép tính.

## 6. Từ sigmoid một đầu ra đến softmax mười lớp

Tầng ẩn: `h=ReLU(x @ W1+b1)`. Tầng ra: `z=h @ W2+b2`. Softmax `p_j=exp(z_j−max(z))/sum(exp(z−max(z)))`; trừ max giúp tránh tràn số và không đổi xác suất. Cross-entropy của nhãn y là `logsumexp(z)−z_y`; chương trình tính trên logits để tránh lấy log của xác suất đã tròn về 0.

Xác suất đều ở 10 lớp có CE=ln10. Mô hình có xác suất cao vẫn có thể sai và chưa được hiệu chỉnh độ tin cậy. Backprop là cách tính gradient bằng quy tắc dây chuyền. Adam là thuật toán dùng gradient cùng trạng thái tích lũy để cập nhật; không đồng nhất một bước Adam với `θ−ηg` của GD cơ bản.

## 7. Chốt cấu hình trước khi xem test

| Thành phần | Cấu hình tham chiếu |
|---|---|
| Kiến trúc | 784 → 64 ReLU → 10 softmax |
| Tham số | 784×64+64+64×10+10 = **50.890** |
| Optimizer | Adam, learning_rate_init=0,001; alpha L2=0,0001 |
| Mini-batch | 256; 12.000 ảnh → **47 lần cập nhật/epoch**, batch cuối 224 |
| Ngân sách | 50 epoch cho mỗi seed 42,43,44 |
| Quy tắc chọn | CE validation thấp nhất; hòa chính xác lấy epoch sớm nhất |
| Seed chính | 42 ấn định trước; không chọn seed tốt nhất để báo test |

`partial_fit` giữ trạng thái Adam giữa các epoch. Không gọi `fit` từ đầu ở từng epoch. Chương trình tính lại CE train và validation ở cuối epoch với cùng trọng số, **không cộng L2 vào hai đường CE hiển thị**; optimizer vẫn dùng L2. 50 epoch là ngân sách, không phải chứng minh đã hội tụ.

`protocol_before_fit.json` được ghi trước huấn luyện; `frozen_before_test.json` ghi quyết định trước tính metric test. Các seed bổ sung dùng để mô tả biến động. Ba seed không tạo thành một khoảng tin cậy cho hiệu năng tổng quát.

## 8. Đọc kết quả và phản biện

Với cấu hình mặc định, các mốc tham chiếu từ slide:

| Mô hình/seed | Epoch chọn | Đúng validation |
|---|---:|---:|
| Logistic 784 pixel | Không áp dụng | 2.500/3.000 |
| MLP seed 42 | 40 | 2.581/3.000 |
| MLP seed 43 | 27 | 2.590/3.000 |
| MLP seed 44 | 40 | 2.597/3.000 |

Ở seed 42, epoch 40 có validation CE≈0,408158; epoch 50 có CE≈0,421123 dù train CE tiếp tục thấp hơn. Đây là lý do giữ checkpoint theo validation. Hai cấu hình đã chốt cho test: logistic **8.277/10.000**, MLP chính **8.544/10.000**, chênh **267 ảnh hoặc 2,67 điểm phần trăm**.

Test này công khai và đã từng được xem ở pilot của bộ bài giảng; không gọi là test mới niêm phong. Kết quả chỉ so hai cấu hình đã định, không chứng minh MLP luôn hơn mọi mô hình tuyến tính. Xem confusion theo hàng và cả ba nhóm ảnh: MLP sửa lỗi baseline, cả hai cùng sai, MLP làm sai ảnh baseline đúng. Một ảnh khó nhìn không tự chứng minh nguyên nhân mạng nhầm.

## 9. Tự kiểm tra và thay đổi có kiểm soát

| Câu hỏi | Đáp án và giải thích |
|---|---|
| Thêm ba lớp affine mà không activation có giải XOR? | Không; hợp affine vẫn affine. |
| Gradient một trọng số bằng 0 nghĩa là bỏ trọng số đó? | Không; đó là đạo hàm tại một vị trí cụ thể. |
| Cập nhật v trước rồi dùng v mới để tính gradient W có đúng bước backprop? | Không; gradient của một bước phải cùng bộ tham số cũ. |
| Accuracy 100% có làm CE bằng 0? | Không; xác suất nhãn đúng có thể nhỏ hơn 1. |
| Nên chọn seed theo accuracy test cao nhất? | Không; đó là dùng test để lựa chọn. |
| 47 batch có nghĩa mỗi batch đều có 256 ảnh? | Không; batch cuối có 224 ảnh. |

Thử 5 epoch và giải thích vì sao chưa thể kết luận kiến trúc kém. Thử seed khác nhưng giữ split và ngân sách, báo mọi lần chạy đã định trước. Tự đổi một tham số mạng nhỏ rồi kiểm lại gradient, tránh ReLU=0. Với nhãn XOR không cân bằng, gradient lúc p=0,5 không còn đơn thuần bằng −Cov(H,y): có thêm `(0,5−mean(y))*mean(H)`; kiểm thử kèm phản ví dụ cụ thể.

## 10. Dùng mô hình đã học và đọc đầu ra

```bash
python -m examples.bai10.predict --model outputs/bai10/mlp_model.npz --image outputs/bai10/one_image_uint8.npy
```

Lệnh này chỉ suy luận, không fit lại. Đầu vào là NPY uint8 28×28; lấy ảnh mẫu mà bài đã xuất để so với `one_image_source.json` và `one_image_probabilities.csv`. NPZ chỉ chứa mảng số; loader dùng `allow_pickle=False`. Bộ mô hình lưu đủ trọng số để suy luận; không lưu trạng thái optimizer để tiếp tục Adam chính xác từ checkpoint.

| Tệp trong `outputs/bai10/` | Nội dung |
|---|---|
| `toy_xor.csv`, `toy_backprop.csv`, `toy_details.json` | Các phép tính tay kiểm được |
| `split_membership.csv` | ID và nhãn, vai trò từng ảnh |
| `history_seed_*.csv` | Đủ mọi epoch của từng seed |
| `protocol_before_fit.json`, `frozen_before_test.json` | Quy trình và lựa chọn đã chốt |
| `mlp_model.npz` | Trọng số MLP và baseline |
| `validation_predictions.csv`, `test_predictions.csv` | Dự đoán từng ảnh và mã gốc |
| `error_examples.csv` | Quy tắc và ID chọn ảnh lỗi |
| `one_image_*` | Ảnh gốc, 64 kích hoạt, 10 logits/xác suất, nhãn nguồn |
| 9 PNG, `real_details.json`, `results.json` | Hình và kết quả đầy đủ |

Bài 10 khép lại chuỗi: biểu diễn → láng giềng → độ đo → tối ưu → xác suất → cây → kiểm chứng → phân cụm → giảm chiều → học biểu diễn phi tuyến. Năng lực biểu diễn, khả năng tối ưu và chất lượng ngoài mẫu là ba câu hỏi liên quan nhưng phải được kiểm riêng.

## Đối chiếu tên biến mạng nhỏ

Slide dùng $W_1,b_1$ cho tầng ẩn, $v,b$ cho tầng ra và $s$ cho score. Hàm `tiny_forward` giữ tên nội bộ `W,b,v,c,z` để bảo toàn giao diện; lần lượt tương ứng $W_1,b_1,v,b,s$. `PARAM_NAMES` trong CSV được giữ và có thêm cột `slide_parameter`. Mạng ảnh dùng mỗi hàng là một quan sát (`X @ W1`), nên shape ma trận khác cách viết vector cột trên slide; phép tính tương đương.
