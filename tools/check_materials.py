"""Check published paths, links, code and the no-PowerPoint policy."""
from pathlib import Path
from urllib.parse import unquote,urlsplit
import subprocess,re,zipfile,io,json
ROOT=Path(__file__).resolve().parents[1]
PRESENTATIONS={'.ppt','.pptx','.pptm','.pps','.ppsx','.ppsm','.pot','.potx','.potm'}
def files():
    names=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT).decode('utf-8').split('\0')
    return sorted({ROOT/n for n in names if n and (ROOT/n).is_file()})
def archive(source,label,depth=0):
    assert depth<5, f'Nested archive too deep: {label}'
    with zipfile.ZipFile(source) as z:
        for info in z.infolist():
            suffix=Path(info.filename).suffix.lower()
            assert suffix not in PRESENTATIONS,f'PowerPoint inside {label}: {info.filename}'
            if suffix=='.zip':
                assert info.file_size<100_000_000,f'Inspect oversized nested archive: {label}'
                archive(io.BytesIO(z.read(info)),label+'/'+info.filename,depth+1)
def main():
    errors=[]; links=0; checked=files()
    for p in checked:
        rel=p.relative_to(ROOT).as_posix()
        if p.suffix.lower() in PRESENTATIONS:errors.append(f'Forbidden presentation: {rel}')
        if re.search(r'(?i)(?:^|[/_-])v\d+(?=[/_.-]|$)',rel):errors.append(f'Version path: {rel}')
        if p.suffix.lower()=='.zip':archive(p,rel)
        if p.suffix=='.py':
            try:compile(p.read_text(encoding='utf-8'),rel,'exec')
            except Exception as e:errors.append(f'{rel}: {e}')
        if p.suffix not in {'.md','.html'} or any(x in p.parts for x in ('katex','third_party','vendor')):continue
        text=p.read_text(encoding='utf-8')
        if p.suffix=='.md':
            text=re.sub(r'```[\s\S]*?```','',text)
            targets=re.findall(r'\]\(([^\s)]+)(?:\s+"[^"]*")?\)',text)
        else:targets=re.findall(r'(?:href|src)=["\']([^"\']+)["\']',text)
        for target in targets:
            parts=urlsplit(target)
            if parts.scheme or target.startswith(('#','//','data:')):continue
            path=unquote(parts.path)
            if not path:continue
            links+=1
            if not (p.parent/path).exists():errors.append(f'Broken link {rel}: {target}')
    if errors:raise SystemExit('\n'.join(errors))
    print(f'PASS: {len(checked)} files; {links} local links; no presentation files/archives; Python syntax valid.')
if __name__=='__main__':main()
