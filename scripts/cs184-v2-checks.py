"""Run all 48 authored workshop programs and save their actual outputs."""
from pathlib import Path
import ast, contextlib, io, json, runpy

ROOT=Path(__file__).resolve().parents[1]


def main():
    data=runpy.run_path(str(ROOT/'scripts/cs184-v2-content.py'))['DATA']
    rows=[]
    for key,labs in data.items():
        assert len(labs)==4
        for j,lab in enumerate(labs,1):
            tree=ast.parse(lab['code'])
            count=sum(isinstance(n,ast.Assert) for n in ast.walk(tree))
            assert count>=1,(key,j)
            out=io.StringIO()
            with contextlib.redirect_stdout(out):
                exec(compile(tree,f'cs184-{key}-workshop-{j}','exec'),{})
            rows.append(dict(key=key,workshop=j,title=lab['title'],assertion_sites=count,output=out.getvalue().strip(),status='PASS'))
    assert len(rows)==48
    report=dict(status='PASS',programs=len(rows),assertion_sites=sum(r['assertion_sites'] for r in rows),
                scope='independent small teaching models, not a complete renderer or simulator',results=rows)
    dest=ROOT/'.work/cs184/v2-numerical-results.json'
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({k:v for k,v in report.items() if k!='results'},ensure_ascii=False))


if __name__=='__main__':main()
