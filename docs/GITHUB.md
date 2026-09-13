# Đăng khóa học lên ml4vn MachineLearning

Repository đích: [ml4vn/MachineLearning](https://github.com/ml4vn/MachineLearning). Lúc chuẩn bị, repository công khai, nhánh mặc định main, chưa có commit. Bộ học liệu local đã đủ 10 tài liệu đọc trước và 10 bài Python. Các bước dưới đây dùng cho lần đăng đầu và các lần cập nhật tiếp theo. Git cần một tài khoản có quyền ghi và danh tính tác giả commit do chủ repository lựa chọn.

## Cách thuận tiện trên Windows

Trong thư mục bộ học liệu đã chuẩn bị hoặc thư mục MachineLearning sau khi giải nén ZIP, mở PowerShell và chạy:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\publish_course.ps1
```

Tham số Bypass chỉ áp dụng cho tiến trình đang chạy lệnh này, không đổi chính sách PowerShell toàn máy. Script tìm Git đã cài; nếu cần, truyền đường dẫn chương trình qua -GitPath. Trên máy biên soạn, Git có sẵn trong runtime Codex. Nếu máy khác chưa cài Git, dùng [Git for Windows](https://gitforwindows.org/) rồi mở lại terminal.

Script kiểm repository đích, hỏi **tên và email dùng cho commit** nếu chưa được cấu hình, ghi cấu hình riêng cho repository này, tạo commit và push nhánh main. Email có thể là địa chỉ noreply do GitHub cung cấp trong **Settings → Emails** của tài khoản. Không tự đoán địa chỉ hoặc dùng email ví dụ.

Khi Git yêu cầu đăng nhập, chọn **Sign in with your browser**, đăng nhập tài khoản có quyền ghi vào ml4vn/MachineLearning, hoàn tất xác thực của GitHub rồi quay về terminal. Git Credential Manager xử lý đăng nhập; không cần gửi mật khẩu hoặc token vào cuộc trò chuyện. Nếu tài khoản thuộc tổ chức, tài khoản đó phải có quyền ghi vào repository đích.

Script chỉ công bố vào ml4vn/MachineLearning, không force-push. Nếu remote có commit mới khác lịch sử local, script dừng để đồng bộ. Nếu đăng nhập chưa hoàn tất hoặc push thất bại, commit local vẫn còn và có thể chạy lại script sau khi xử lý nguyên nhân. Dùng tùy chọn -CheckOnly để chỉ kiểm đích và cấu hình, không commit/push.

## Nếu muốn tự chạy từng lệnh

Mở terminal tại thư mục có README và requirements. Nếu vừa giải nén ZIP và chưa có .git, chạy git init -b main. Với bộ mã trên máy biên soạn, Git đã được khởi tạo và remote đã được gắn.

```bash
git status --short
git remote -v
git ls-remote origin
```

Nếu chưa có remote, thêm bằng lệnh sau:

```bash
git remote add origin https://github.com/ml4vn/MachineLearning.git
```

Sau khi cấu hình tên/email thật theo lựa chọn của chủ repository:

```bash
git add .
git diff --cached --check
git diff --cached --stat
git commit -m "Add ten pre-reading guides and Python machine learning labs"
git push -u origin main
```

Các lệnh này phù hợp với repository hiện còn trống hoặc có cùng lịch sử local. Khi repository đã có nội dung khác, cần clone/fetch và đưa thay đổi vào nhánh phù hợp; không dùng force-push để vượt qua lỗi lịch sử.

## Đặt mô tả khóa học trên trang GitHub

Mở repository → tại **About** chọn biểu tượng bánh răng → dán nội dung dưới đây vào **Description** → **Save changes**:

> Khoá học: Học máy của PGS.TS. Nguyễn Văn Hậu, Khoa Công nghệ Thông tin, Trường Đại học Công nghệ Kỹ thuật Hưng Yên.

Mô tả cũng được lưu trong [MO_TA_DU_AN.txt](MO_TA_DU_AN.txt) và thể hiện ở README. Trường About là metadata trên GitHub, không tự đổi khi push README.

## Kiểm tra sau khi push

1. Mở trang chính: đúng tên khóa học, giảng viên, đơn vị và đủ 10 hàng bài học.
2. Mở từng bài: đọc Markdown, mở PDF/Word và chuyển sang Python bằng liên kết tương ứng.
3. Mở **Actions** để xem workflow kiểm tài liệu, 60 kiểm thử toán học và 10 ví dụ nhỏ trên Windows/Ubuntu. Chỉ kết luận CI thành công sau khi cả hai lượt hoàn tất.
4. Chọn **Code → Download ZIP** hoặc clone repository trên một thư mục khác; làm theo README để kiểm trải nghiệm sinh viên.

Các archive trong data/raw, output chương trình và venv không được theo dõi. CSV/JSON trong readings là dữ liệu và kết quả tham chiếu đi kèm tài liệu; [điều kiện nguồn](DU_LIEU_VA_NGUON.md) được giữ. ZIP cần giải nén trước khi đưa nội dung lên; nếu chỉ upload nguyên ZIP, GitHub sẽ không có mục lục học liệu để đọc trực tiếp.

Tham khảo chính thức: [Đăng tệp bằng Git](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository), [đăng nhập qua Git Credential Manager](https://docs.github.com/en/get-started/git-basics/caching-your-github-credentials-in-git).
