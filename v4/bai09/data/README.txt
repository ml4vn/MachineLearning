Fashion-MNIST — Zalando Research — giấy phép MIT
Nguồn chính thức: https://github.com/zalandoresearch/fashion-mnist
Bản phân phối Kaggle: https://www.kaggle.com/datasets/zalando-research/fashionmnist

Bốn tệp IDX/GZIP gốc có trong raw/. Mã MD5 và SHA-256 được lưu tại source_manifest.json.
train:<row> là ID của ảnh trong tập nguồn 60.000 ảnh train, bắt đầu từ 0. Tiền tố train chỉ tập nguồn, không chỉ vai trò thực nghiệm.
Chia phân tầng với seed 42: 12.000 ảnh train, 3.000 ảnh validation, 45.000 ảnh chưa dùng.
10.000 ảnh test không được dùng để chọn k hoặc báo cáo chỉ số của Bài 9; chúng đã được dùng trong Bài 10 v3.
lab_arrays.npz lưu tham số PCA, Logistic Regression và ảnh tái dựng; fashion_subset.npz lưu pixel, nhãn và ID nguồn.
