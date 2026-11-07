"""Numerical regression plus source/rendered checks for the eight revised notes."""
from pathlib import Path
import argparse,json,re,runpy,zipfile
from math import isclose
from urllib.parse import unquote
ROOT=Path(__file__).resolve().parents[1]
engine=runpy.run_path(str(ROOT/'scripts/cs184-foundations-v2.py'))
HTML=runpy.run_path(str(ROOT/'scripts/cs184-verify-course.py'))['HTMLCount']

def regressions():
    # Independent regression cases for corrected original prose, separate from new workshops.
    passed=[]
    def check(name,condition):
        assert condition,name
        passed.append(name)
    check('centroid edge value',isclose(16-4*(4/3)-4*(4/3),16/3))
    check('vertical right coverage',sum(x>=10.3 for x in (10.125,10.375,10.625,10.875))/4==.75)
    check('vertical exact coverage',isclose(11-10.3,.7))
    check('subpixel rounding',abs(round(.3*256)/256-.3)<=1/512)
    check('needle triangle centers',sum(x+.5>50 for x in range(100))==50)
    A=((4,1,0),(1,4,1),(0,1,4));v=(2/7,-1/7,2/7)
    check('non-diagonal QEM',all(isclose(sum(a*b for a,b in zip(row,v)),rhs,abs_tol=1e-12) for row,rhs in zip(A,(1,0,1))))
    check('CC vertex count',8+12+6==26)
    check('CC edge count',2*12+4*6==48)
    check('CC Euler',26-48+24==2)
    check('plane Bezier linear reproduction',isclose(sum(w*j for w,j in zip((.421875,.421875,.140625,.015625),range(4))),.75))
    check('perspective ratio threshold',isclose(.5-1/(1+11/9),.05))
    check('shading work ratios',500000/20000==25 and 500000/10000==50)
    return passed

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source-only',action='store_true');args=parser.parse_args()
    rows=[];programs=[]
    for key,(slug,pdf,worked,tests) in engine['COURSES'].items():
        folder=ROOT/'src/content/notes'/slug;s=(folder/'index.md').read_text(encoding='utf8')
        for item in engine['DATA'][key]:programs.append(dict(key=key,title=item['title'],output=engine['execute'](item)))
        refs=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',s)
        local=[x for x in refs if not x.startswith('http')]
        assert all((folder/x).is_file() for x in local),(key,'broken image')
        actual={str(p.relative_to(folder)).replace('\\','/') for sub in ('images','diagrams') for p in (folder/sub).glob('*.png')}
        assert set(local)==actual,(key,'unreferenced assets',actual-set(local))
        # Count actual example headings, not prose mentions of "hand calculation".
        found=re.findall(r'(?m)^(?:#{1,6} |\*\*|> \*\*)🔧 手算 (\d+)',s)
        assert sorted(map(int,found))==list(range(1,worked+4)),(key,found)
        start=s.index('## 附录 C');end=s.find('\n## ',start+3)
        appendix=s[start:end if end!=-1 else len(s)]
        original_questions=re.findall(r'(?m)^\d+\. ',appendix)
        assert len(original_questions)==tests,(key,len(original_questions),tests)
        assert len(re.findall(r'(?m)^### 自测 \d+\.',s))==3
        assert '提示词占位' not in s and '<!-- foundations-v2:start -->' in s
        assert all(line.strip()=='$$' for line in s.splitlines() if '$$' in line),(key,'display delimiters')
        archive=ROOT/f'public/cs184/figures/foundations-{key}-editable.zip'
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None
            assert sum(n.endswith('.pptx') for n in z.namelist())==3
            assert sum(n.endswith('.json') for n in z.namelist())==3
        tables=len(re.findall(r'(?m)^\|\s*:?-{3,}',s))
        row=dict(key=key,slug=slug,lines=len(s.splitlines()),screenshots=len(list((folder/'images').glob('*.png'))),diagrams=len(list((folder/'diagrams').glob('*.png'))),worked=worked+3,selftests=tests+3,tables=tables,h2=len(re.findall(r'(?m)^## ',s)),image_references=len(refs))
        assert row['lines']>=2000 and row['diagrams']>=20 and tables>=30 and row['h2']>=15,row
        if not args.source_only:
            html=ROOT/'dist'/slug/'index.html';parsed=HTML();parsed.feed(html.read_text(encoding='utf8'))
            assert parsed.count['katex_error']==0,(key,'KaTeX errors')
            assert parsed.count['katex_display']==s.count('\n$$\n')//2,(key,parsed.count)
            assert parsed.count['img']==len(refs) and parsed.count['h2']==row['h2'],(key,parsed.count,row)
            for url in parsed.images+parsed.links:
                if url.startswith('/notes/'):
                    target=unquote(url.removeprefix('/notes/').split('#')[0].split('?')[0]);p=ROOT/'dist'/target
                    assert p.is_file() or (p/'index.html').is_file(),(key,url)
            row.update(parsed.count)
        rows.append(row)
    report=dict(status='PASS',scope='eight original CS184 notes',articles=8,programs=len(programs),original_regressions=regressions(),results=rows)
    out=ROOT/'.work/cs184-foundations';out.mkdir(parents=True,exist_ok=True)
    (out/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
