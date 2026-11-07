"""Verify the newly completed CS184 course sources and built HTML."""
from pathlib import Path
from html.parser import HTMLParser
import argparse,json,re,runpy
from urllib.parse import unquote

ROOT=Path(__file__).resolve().parents[1]

class HTMLCount(HTMLParser):
    def __init__(self):
        super().__init__();self.count=dict(h2=0,img=0,katex=0,katex_error=0);self.images=[];self.links=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag in ('h2','img'):self.count[tag]+=1
        if tag=='img':self.images.append(a.get('src',''))
        if tag=='a':self.links.append(a.get('href',''))
        classes=a.get('class','').split()
        if 'katex' in classes:self.count['katex']+=1
        if 'katex-error' in classes:self.count['katex_error']+=1

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-only',action='store_true');args=ap.parse_args()
    ns=runpy.run_path(str(ROOT/'scripts/cs184-complete-course.py'));rows=[]
    for c in ns['load']():
        p=ROOT/'src/content/notes'/c['slug']/'index.md';md=p.read_text(encoding='utf8')
        refs=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',md)
        actual={str(x.relative_to(p.parent)).replace('\\','/') for folder in ['images','diagrams'] for x in (p.parent/folder).glob('*.png')}
        assert set(refs)==actual,(c['key'],'missing or unused image',set(refs)^actual)
        assert all((p.parent/r).is_file() for r in refs),c['key']
        assert len(re.findall(r'^### 自测 \d+\.',md,re.M))==26
        assert len(re.findall(r'^### 🔧 手算 \d+',md,re.M))==12
        assert all(line.strip()=='$$' for line in md.splitlines() if '$$' in line)
        assert (ROOT/'public/cs184/figures'/f'{c["key"]}-editable.zip').is_file()
        row=dict(key=c['key'],slug=c['slug'],lines=len(md.splitlines()),unique_images=len(actual),image_references=len(refs),h2=len(re.findall(r'^## ',md,re.M)))
        if not args.source_only:
            hp=ROOT/'dist'/c['slug']/'index.html';h=HTMLCount();h.feed(hp.read_text(encoding='utf8'))
            assert h.count['h2']==row['h2'],(c['key'],h.count,row)
            assert h.count['img']==len(refs),(c['key'],h.count,row)
            assert h.count['katex_error']==0 and h.count['katex']>=12,(c['key'],h.count)
            for src in h.images:
                if src.startswith('/notes/'):assert (ROOT/'dist'/src[len('/notes/'):]).is_file(),src
            for link in h.links:
                if not link.startswith('/notes/'):continue
                target=unquote(link[len('/notes/'):].split('#')[0].split('?')[0])
                path=ROOT/'dist'/target
                assert path.is_file() or (path/'index.html').is_file(),(c['key'],link)
            row.update(h.count)
        rows.append(row)
    report=dict(status='PASS',scope='12 new CS184 notes only',articles=len(rows),unique_images=sum(r['unique_images'] for r in rows),results=rows)
    out=ROOT/'.work/cs184/verification.json';out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
