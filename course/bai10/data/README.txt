Fashion-MNIST — Zalando Research — giấy phép MIT
Nguồn: https://github.com/zalandoresearch/fashion-mnist
Kaggle: https://www.kaggle.com/datasets/zalando-research/fashionmnist
Bốn tệp gzip/IDX gốc nằm trong raw/. Hash trong source_manifest.json.
train:<row> là hàng nguồn chính thức, chỉ số từ 0; vai trò train/validation thuộc cách chia thí nghiệm.
fashion_subset.npz giữ đúng bytes của Bài 9 . bai09_reference.npz/json giữ baseline/PCA đã chốt.
lab_arrays.npz chứa checkpoint seed 42, tham số và dự đoán. epoch_orders.npz chứa 3×50 thứ tự xáo trộn.
Test công khai đã từng được báo cáo ở Bài 10 . MLP  được chạy lại với RNG tiến liên tục.
