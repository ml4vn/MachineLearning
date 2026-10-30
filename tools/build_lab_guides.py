"""Tạo hướng dẫn thực hành  từ nguồn teaching.json của từng bài."""
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def render(config):
    n=config['lesson']; name=f'bai{n:02d}'
    parts=[f'# Bài {n} · Lộ trình thực hành',
        f'[Hướng dẫn chi tiết](README.md) · [Đọc trước](../../readings/{name}/README.md) · [Kiểm tra học liệu](../../docs/MAINTAINING.md)',
        f"**{config['recap_title']}.** Lộ trình ví dụ nhỏ dự kiến 35–50 phút. Không cần dữ liệu thật để hoàn thành ví dụ nhỏ.",
        '## 1. Dự đoán trước khi chạy', config['question'],
        'Ghi câu trả lời bằng số và một câu giải thích. Chưa mở đáp án bên dưới; mục tiêu là kiểm cách hiểu, không chỉ chép đầu ra.',
        '## 2. Chạy ví dụ nhỏ',
        f'Chạy từ thư mục gốc repository, sau khi cài thư viện theo README chung:\n\n```bash\npython -m examples.{name}.main --mode toy --output-dir outputs/toy/{name}\n```',
        'PNG mặc định 3840×2160. Công thức trong hình dùng Matplotlib mathtext; nguồn Markdown dùng LaTeX. `--dpi 80` dùng xem thử nhanh, không phải bản 4K.',
        '## 3. Đọc theo ba chặng']
    for k,stage in enumerate(config['stages'],1):
        parts += [f"### {k}. {stage['title']}",stage['explain'],f"```math\n{stage['formula'].strip('$')}\n```"]
    parts += [f'![Tổng kết thực hành Bài {n}](../../docs/figures/illustrations/{name}_summary.png)']
    details={4:['toy_wb_update','toy_loss_surface'],6:['toy_gini_trace'],8:['toy_silhouette'],9:['toy_covariance'],10:['toy_backprop_path']}
    for image in details.get(n,[]):
        parts += [f'![Minh họa tính từng bước Bài {n}](../../docs/figures/illustrations/{name}_{image}.png)']
    parts += ['## 4. Mở đúng đầu ra',
        'Các tệp nằm trong thư mục `--output-dir` của lần chạy. Tên bắt đầu `toy_` thuộc ví dụ nhỏ; `real_` thuộc thí nghiệm thật. `results.json` lưu số liệu và cấu hình phiên bản.',
        '\n'.join(f'- `{file}`' for file in config['outputs']),
        '- `summary.png`: tổng kết ví dụ chuẩn và giới hạn diễn giải.',
        '## 5. Đối chiếu và giải thích',
        '<details>\n<summary>Mở sau khi đã tự tính</summary>\n\n'+config['answer']+'\n\n</details>',
        '**Điều cần mang theo:** '+config['takeaway'],
        'Bài nộp ngắn: ghi cấu hình đã chạy, một kết quả tính tay khớp mã, một hình kèm lời giải thích và một điều kết quả chưa chứng minh. Khi số khác, kiểm dữ liệu, seed, tham số, mẫu số và quy tắc làm tròn trước khi kết luận mã sai.',
        '## 6. Nối với slide và tài liệu đọc trước',
        '| Slide | Điểm bắt đầu | Điểm kết thúc |\n|---|---|---|\n'+'\n'.join(f"| {x['start']}–{x['end']} | {x['first_title']} | {x['last_title']} |" for x in config['slide_sections']),
        'Bảng đối chiếu giúp giảng viên nối ví dụ với nội dung giảng dạy; repository không phân phối PowerPoint.',
        '## 7. Mở rộng sang dữ liệu thật',
        f'Chuẩn bị đúng dữ liệu theo [README của bài](README.md), rồi chạy:\n\n```bash\npython -m examples.{name}.main --mode all --output-dir outputs/{name}\n```',
        'Đọc ví dụ trước, chạy cấu hình chuẩn sau; cuối cùng mới thay một yếu tố và lưu sang thư mục khác. Giữ nguyên tập chấm khi so mô hình; chọn cấu hình trên validation, không chọn lại bằng test. Với phân tích mô tả ở Bài 1 và 8, giới hạn kết luận ở snapshot và cách biểu diễn đã dùng.',
        'Phần tính tay và giải thích hình là yêu cầu cơ bản. Vét cạn, chứng minh, nhiều seed, nested CV và các kiểm tra thư viện sâu là phần mở rộng phù hợp từng bài. Bài 10 mặc định chạy 3 seed × 50 epoch trên CPU; không coi cấu hình chạy nhanh là phép tái lập đầy đủ.']
    return '\n\n'.join(parts)+'\n'


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    for n in range(1,11):
        folder=ROOT/f'examples/bai{n:02d}'; c=json.loads((folder/'teaching.json').read_text(encoding='utf-8')); target=folder/'HUONG_DAN.md'; expected=render(c)
        if args.check:
            assert target.read_text(encoding='utf-8')==expected, target
        else: target.write_text(expected,encoding='utf-8',newline='\n')
    print('10 lab guides match teaching.json')


if __name__=='__main__':main()
