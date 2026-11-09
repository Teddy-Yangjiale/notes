"""Validate the internship deliverable against rendered HTML, without running models."""
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json, re
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
errors, rows, images, local_links = [], [], set(), set()
for md in sorted((ROOT / 'src/content/notes').glob('internship-*/index.md')):
    target = ROOT / 'dist' / md.parent.name / 'index.html'
    if not target.exists():
        errors.append(f'Missing page: {target}')
        continue
    soup = BeautifulSoup(target.read_text(encoding='utf-8'), 'html.parser')
    text = md.read_text(encoding='utf-8')
    bad = soup.select('.katex-error')
    errors.extend(f'{md.parent.name}: formula error {x.get_text()}' for x in bad)
    for el in soup.select('[href], img[src]'):
        url = el.get('href') or el.get('src')
        parts = urlsplit(url)
        if not parts.path.startswith('/notes/'):
            continue
        local_links.add(url)
        path = ROOT / 'dist' / unquote(parts.path.removeprefix('/notes/'))
        if path.is_dir():
            path /= 'index.html'
        if not path.exists():
            errors.append(f'{md.parent.name}: broken {url}')
        elif parts.fragment and path.suffix == '.html':
            linked = BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')
            if not linked.find(id=unquote(parts.fragment)):
                errors.append(f'{md.parent.name}: missing anchor {url}')
        if el.name == 'img':
            images.add(url)
    rows.append(dict(id=md.parent.name, chinese_characters=len(re.findall(r'[\u4e00-\u9fff]', text)),
                     formulas=len(soup.select('.katex')), images=len(soup.select('article img')),
                     sections=len(soup.select('article h2'))))
column = ROOT / 'dist/series/internship/index.html'
if not column.exists():
    errors.append('Missing column')
else:
    column_html = BeautifulSoup(column.read_text(encoding='utf-8'), 'html.parser')
    if len(column_html.select('ol.toc > li')) != 18:
        errors.append('Column must list 18 notes')
report = dict(pages=len(rows), chinese_characters=sum(x['chinese_characters'] for x in rows),
              formulas=sum(x['formulas'] for x in rows), unique_images=len(images),
              checked_local_links=len(local_links), errors=errors, articles=rows)
out = ROOT / '.work/internship/validation.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='articles'},ensure_ascii=False,indent=2))
raise SystemExit(bool(errors))
