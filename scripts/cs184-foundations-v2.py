"""Targeted additions to the eight existing L02-L13 notes; existing prose stays editable."""
from pathlib import Path
import argparse, ast, contextlib, io, json, re

ROOT=Path(__file__).resolve().parents[1]
DATA={}
COURSES={
 '02':('cs184-02-drawing-triangles','L02-drawing-triangles.pdf',12,26),
 '03':('cs184-03-sampling-aliasing','L03-sampling-aliasing.pdf',12,26),
 '04':('cs184-04-05-transforms','L04-05-transforms.pdf',12,26),
 '06':('cs184-06-07-texture-mapping','L06-07-texture-mapping.pdf',12,26),
 '08':('cs184-08-09-rasterization-shading','L08-09-rasterization-pipeline-shading.pdf',12,27),
 '10':('cs184-10-bezier-curves-surfaces','L10-bezier-curves-surfaces.pdf',14,28),
 '11':('cs184-11-12-meshes-geometry','L11-12-meshes-geometry-processing.pdf',14,26),
 '13':('cs184-13-ray-tracing-acceleration','L13-ray-tracing-acceleration.pdf',13,30),
}

def topic(title,pages,why,assume,derive,example,code,checks,failure,question,answer,caption):
    return locals()

for source in sorted((ROOT/'scripts/cs184-foundations-v2').glob('*.py')):
    exec(compile(source.read_text(encoding='utf8'),str(source),'exec'))

def execute(item):
    buf=io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(item['code'],item['title'],'exec'),{})
    return buf.getvalue().strip()

def render(key):
    slug,pdf,worked,tests=COURSES[key]
    text='<!-- foundations-v2:start -->\n\n'
    for j,item in enumerate(DATA[key],1):
        text+=f'## 深入 {j}. {item["title"]}\n\n'
        text+='本节为补充推导与可复现教学实验。回查本讲 PDF：'+ '、'.join(f'p{p}' for p in item['pages'])+'；下列数值由明确的模型计算，不是课件测量。\n\n'
        text+=item['why']+'\n\n### 约定与输入\n\n'
        text+='| 量或条件 | 本节约定 |\n| --- | --- |\n'
        for a,b in item['assume']:text+=f'| {a} | {b} |\n'
        text+='\n### 推导：把省略的步骤补出来\n\n'
        for i,(prose,formula) in enumerate(item['derive'],1):
            text+=f'**第 {i} 步。** {prose}\n\n'
            if formula:text+='$$\n'+formula+'\n$$\n\n'
        text+=f'![{item["title"]}](diagrams/d{22+j}-v2.png)\n\n*{item["caption"]}*\n\n'
        text+=f'### 🔧 手算 {worked+j}：{item["title"]}\n\n'
        for i,line in enumerate(item['example'],1):text+=f'{i}. {line}\n\n'
        text+='### 独立回查与适用边界\n\n'+'\n\n'.join(item['checks'])+'\n\n'
        text+='### 运行验证\n\n下列 Python 程序只依赖标准库。它验证本节的小模型及反例，不代表完整渲染器或网格系统已经通过测试。\n\n```python\n'+item['code'].strip()+'\n```\n\n实际运行输出：\n\n```text\n'+execute(item)+'\n```\n\n'
        text+='### 实现坑：症状与定位\n\n'+item['failure']+'\n\n'
        text+=f'### 自测 {tests+j}. {item["question"]}\n\n<details>\n<summary>展开推理与答案</summary>\n\n'+item['answer']+'\n\n</details>\n\n'
    text+=f'[下载本轮 3 张可编辑图解（PPTX 与操作 JSON）](/notes/cs184/figures/foundations-{key}-editable.zip)\n\n'
    text+='<!-- foundations-v2:end -->\n\n'
    return text

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    results=[]
    for key,items in DATA.items():
        assert len(items)==3
        for j,item in enumerate(items,1):
            results.append(dict(key=key,workshop=j,title=item['title'],output=execute(item),assertion_sites=sum(isinstance(x,ast.Assert) for x in ast.walk(ast.parse(item['code'])))))
        if args.write:
            p=ROOT/'src/content/notes'/COURSES[key][0]/'index.md';s=p.read_text(encoding='utf8')
            s=re.sub(r'<!-- foundations-v2:start -->.*?<!-- foundations-v2:end -->\n*','',s,flags=re.S)
            pos=s.index('## 附录 A')
            s=s[:pos]+render(key)+s[pos:]
            # Standalone display delimiters prevent remark-math from consuming headings.
            s=re.sub(r'(?m)^(.*?)\$\$(.*?)\$\$(.*?)$',lambda m: '\n'.join(x for x in [m[1].rstrip(),'$$',m[2].strip(),'$$',m[3].lstrip()] if x),s)
            s=s.replace('\n$$\n$$\n','\n$$\n\n$$\n')
            p.write_text(s.rstrip()+'\n',encoding='utf8')
    out=ROOT/'.work/cs184-foundations';out.mkdir(parents=True,exist_ok=True)
    report=dict(status='PASS',programs=len(results),assertion_sites=sum(r['assertion_sites'] for r in results),results=results)
    (out/'numerical-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({k:v for k,v in report.items() if k!='results'}))

if __name__=='__main__':main()
