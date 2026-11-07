"""Reproduce notes, selected PDF pages, and editable pptdraw figure sources.

Run with Python 3, PyMuPDF, Pillow, and the user's pptdraw checkout.
No server configuration or global package installation is performed.
"""
from pathlib import Path
import argparse, hashlib, json, runpy, subprocess, sys, zipfile
import fitz
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=ROOT/'scripts'

def load():
    ns=runpy.run_path(str(SCRIPTS/'cs184-completion-content.py'))
    for p in sorted((SCRIPTS/'cs184-course').glob('*.py')):
        if p.name!='figures.py': exec(compile(p.read_text(encoding='utf8'),str(p),'exec'),ns)
    return sorted(ns['COURSES'],key=lambda c:int(c['key']))

EXISTING=[
('cs184-02-drawing-triangles','L02 · 三角形与覆盖','像素由哪些图元覆盖？','半平面判定与插值'),
('cs184-03-sampling-aliasing','L03 · 采样与抗锯齿','离散图像为何锯齿？','区域积分、过滤与采样'),
('cs184-04-05-transforms','L04–05 · 变换','怎样放置物体和相机？','坐标系、矩阵与投影'),
('cs184-06-07-texture-mapping','L06–07 · 纹理','表面参数如何随位置变化？','UV、过滤与像素足迹'),
('cs184-08-09-rasterization-shading','L08–09 · 着色','看见哪个表面、怎样着色？','深度、管线与局部照明'),
('cs184-10-bezier-curves-surfaces','L10 · 曲线曲面','怎样控制连续形状？','插值、逼近与连续性'),
('cs184-11-12-meshes-geometry','L11–12 · 几何','复杂表面如何表示和操作？','网格、拓扑与几何处理'),
('cs184-13-ray-tracing-acceleration','L13 · 光线追踪','光线怎样快速找到最近表面？','求交与 BVH')]

def url(slug): return f'/notes/{slug}/'
def table(headers,rows):
    return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+''.join('| '+' | '.join(str(x).replace('|','\\|').replace('\n',' ') for x in r)+' |\n' for r in rows)

def page_title(text):
    lines=[s.strip() for s in text.splitlines() if s.strip()]
    bad=('CS184','CS 184','Ren Ng','Presented by','F26','S26','O’Brien','O\'Brien')
    for s in lines:
        if not s.startswith(bad) and not s.isdigit() and len(s)>2 and 'http' not in s and 'target=' not in s:
            return s.replace('|','/').replace('<','&lt;').replace('>','&gt;')[:130]
    return '图像或演示页（请以原页视觉内容为准）'

def notes(c,allcourses,pages,figs,meta):
    out=ROOT/'src/content/notes'/c['slug'];out.mkdir(parents=True,exist_ok=True)
    key=c['key']; term={'fa26':'Fall 2026','sp26':'Spring 2026','su26':'Summer 2026'}[c['term']]
    figure_sections={
        '01':[2,3,7,6,6,9,10,10], '14':[2,4,4,4,8,10,11,1],
        '15':[1,5,6,10,10,8,4,2], '16':[1,4,7,9,11,6,10,1],
        '18':[2,3,5,6,7,9,10,11], '19':[1,6,9,9,11,10,5,7],
        '21':[10,3,2,7,8,10,12,6], '24':[2,6,7,10,3,4,8,11],
        '25':[2,3,5,8,6,6,11,12], '26':[4,5,7,8,9,10,10,12],
        '90':[2,4,7,8,10,6,5,9], '91':[3,4,5,6,7,9,10,12]}
    count=len(pages); pad=3 if count>99 else 2
    used=sorted({p for s in c['sections'] for p in s['pages']})
    source=f'https://github.com/Teddy-Yangjiale/CS184/blob/main/CS184_2026/{c["term"]}/lectures/{c["filename"]}'
    short=c['title'].split('：')[0]
    summary=c['chain']+'。以原课件为依据，配 20 张可编辑图解、12 个数值例子、26 道带答案自测与 PDF 全页索引。'
    text=f'''---
title: "CS184 {c['title']}"
date: 2026-11-07
updated: 2026-11-07
summary: "{summary}"
tags: ["计算机图形学", "CS184", "课程笔记"]
series: "cs184"
order: {int(key)+1 if int(key)>=90 else int(key)}
shortTitle: "{short}"
---

> UC Berkeley · CS184/284A · {term} · 文件标识 `{c['filename']}`。
> 本文的 **pN 一律是 PDF 的第 N 页**，不是封面讲次或页脚旧编号。文件名与封面可能不同，以下均按文件和页码回查。

## 0. 先抓住这一条推理链

```text
{c['chain'].replace(' → ',chr(10)+'    ↓'+chr(10))}
```

这篇笔记的阅读顺序是：先理解输入和输出，再确认公式的条件，最后用小数值检查。
正文将课件概念、补充推导和教学例子分开；示意图中的理想几何与数字不冒充真实实验测量。

| 内容 | 本文提供什么 |
|---|---|
| 来源 | {term}，PDF 共 {count} 页；正文选择 {len(used)} 张关键页 |
| 图解 | 12 张概念关系图 + 8 张几何或数值图，均有原生可编辑 PPTX |
| 手算 | 12 个带输入、结果和回代检查的教学例子 |
| 复习 | 26 道自测及答案，末尾保留全页索引 |
| 运行证据 | 数值核对脚本覆盖解析小模型，不代表完整渲染器或模拟器已经实现 |

[下载本篇 20 张可编辑图解（PPTX 与操作 JSON）](/notes/cs184/figures/{key}-editable.zip)

### 课件与推导的使用边界

课件截图用于对照原始定义与几何；正文用中文解释关系，并提供必要的修正与推导。
后续专题按本地文件的学期和编号组织，不假定它们与秋季一一对应。
若只做第一遍学习，先读每节前两段和数值例子，再展开原页核对。

'''
    if key=='01':
        text+='### 从已经做过的小练习出发\n\n渐变图检查坐标与 RGB；第一个三角形检查覆盖；超采样检查像素面积平均。后面所有大算法都可以拆回这种“固定输入、改变一个因素、预测结果、再运行”的小实验。\n\n'
    else:
        link={'14':'cs184-13-ray-tracing-acceleration','15':'cs184-14-radiometry','16':'cs184-15-monte-carlo-integration','18':'cs184-16-17-global-illumination','19':'cs184-18-material-modeling','21':'cs184-04-05-transforms','24':'cs184-21-23-animation','25':'cs184-24-physical-simulation','26':'cs184-19-20-color-science','90':'cs184-14-radiometry','91':'cs184-03-sampling-aliasing'}[key]
        text+=f'### 与前面哪一讲接上\n\n先回顾[相关前置讲义]({url(link)})。本篇在已有表示与数学工具上增加新变量或新约束，而不是另起一套互不相关的公式。\n\n'
    for i,s in enumerate(c['sections'],1):
        text+=f'## {i}. {s["h"]}\n\n'
        text+=s['body'].replace('¶','\n\n')+'\n\n'
        text+=f'![概念关系：{s["h"]}](diagrams/d{i:02d}-relation.png)\n\n'
        text+='*读图：'+' → '.join(s['flow'])+'。箭头表示本节的推理或处理顺序，具体条件见正文。*\n\n'
        text+='### 先读符号与条件\n\n'
        symbols=[]
        for chunk in s['symbols'].split(';'):
            pair=chunk.split('：',1);symbols.append(pair if len(pair)==2 else ['条件或约定',chunk])
        text+=table(['符号 / 条件','含义'],symbols)+'\n'
        text+='### 核心关系与推导入口\n\n'
        text+='以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。\n\n$$\n'+s['formula']+'\n$$\n\n'
        text+=f'### 🔧 手算 {i}：把关系落到数字上\n\n{s["example"]}\n\n'
        text+=table(['检查步骤','操作'],[
            ['输入','先从例子中抄下给定量及单位，不引入未给定的数值。'],
            ['计算','按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。'],
            ['回查',s['example'].split('。')[-2]+'。' if len(s['example'].split('。'))>1 else s['example']],
            ['适用边界',s['pitfall']]])+'\n'
        for fi,target in enumerate(figure_sections[key]):
            if target!=i:continue
            ex=figs[fi]
            text+=f'![几何或数值解释 {fi+1}](diagrams/d{fi+13:02d}-{ex[0]}.png)\n\n*{ex[3]}*\n\n'
        text+='### ⚠️ 易错点：先识别症状与假设\n\n'+s['pitfall']+'\n\n'
        text+=f'### 停下来解释一次\n\n**问题：{s["question"]}**\n\n<details>\n<summary>展开参考回答</summary>\n\n{s["answer"]}\n\n</details>\n\n'
        text+='<details>\n<summary>展开原课件关键页，对照术语与图形</summary>\n\n'
        for p in s['pages']:
            title=page_title(pages[p-1]['text'])
            text+=f'#### {title}\n\n*PDF p{p} · 对应本节：{s["h"]}*\n\n![PDF p{p}：{title}](images/p{p:0{pad}d}.png)\n\n'
        text+='</details>\n\n'
    text+='## 13. 把十二个数值例子连成检查顺序\n\n'
    text+='先手算再运行。随仓库提供的 `scripts/cs184-numerical-checks.py` 是小模型验证，不依赖 GPU，也不修改服务器配置。它不能替代完整渲染场景或模拟系统的验证。\n\n'
    text+=table(['顺序','本节关系','最容易漏掉的约定'],[(i,s['h'],s['symbols'].split(';')[-1]) for i,s in enumerate(c['sections'],1)])+'\n'
    text+='### 复现实验的最小记录\n\n'
    text+=table(['记录项','用途'],[('固定输入','相同几何、材质、网格或信号，避免一次改变多个因素。'),('参数与单位','包括采样数、步长、分辨率、角度单位、颜色空间。'),('输出量','保留线性值、误差或状态，再生成展示图。'),('参考','解析解、手算或高精度结果必须说明来源。'),('失败样例','边界和极端条件是检查假设的入口。')])+'\n'
    text+='## 14. 实现排查：把公式错误与系统错误分开\n\n'
    text+='本节列出由模型和手算能够判断的排查方向；没有把尚未写出的完整应用测试说成已完成。最小数值检查的真实执行结果见本次发布核对报告。\n\n'
    for j in range(0,12,4):
        text+=f'### 阶段 {j//4+1}：第 {j+1}–{j+4} 节\n\n'
        text+=table(['涉及关系','错误机制 / 修正方向'],[(s['h'],s['pitfall']) for s in c['sections'][j:j+4]])+'\n'
    text+='## 15. 跨讲连接：同一工具在哪些尺度重复出现？\n\n'
    text+=table(['前置工具','在整门课里的用途','回查'],[
        ('采样与积分','像素、光源、孔径、时间、方向都需要有限样本估计连续量。',f'[L03]({url(EXISTING[1][0])}) / [L15]({url("cs184-15-monte-carlo-integration")})'),
        ('坐标与线性代数','相机、法线、骨架与局部速度都需要一致的参考系。',f'[L04–05]({url(EXISTING[2][0])})'),
        ('几何表示','可见性、接触、遮挡与网格邻域依赖可靠的几何关系。',f'[L11–12]({url(EXISTING[6][0])})'),
        ('物理量与单位','把颜色值、概率密度、力和能量区别开，防止错误补偿。',f'[L14]({url("cs184-14-radiometry")})'),
        ('颜色与显示','展示图不等于线性数据；显示变换会改变视觉比较。',f'[L19–20]({url("cs184-19-20-color-science")})')])+'\n'
    text+='回头看，许多错误并非来自复杂公式，而是来自“同一个词指了不同的量”：方向密度与概率、位置与方向、线性颜色与编码颜色、稳定与准确。先说清对象，再选择算法。\n\n'
    text+='## 16. 自测：能否不看公式说清楚？\n\n'
    for i,s in enumerate(c['sections'],1):
        text+=f'### 自测 {i}. {s["question"]}\n\n<details>\n<summary>参考答案</summary>\n\n{s["answer"]}\n\n</details>\n\n'
    for i,s in enumerate(c['sections'],13):
        text+=f'### 自测 {i}. 第 {i-12} 节的数值例子，哪一项假设不能悄悄删掉？\n\n<details>\n<summary>参考答案与反例入口</summary>\n\n{s["pitfall"]}\n\n再复算本节的例子：{s["example"]}\n\n</details>\n\n'
    text+='### 自测 25. 本讲的输入、输出和中间表示各是什么？\n\n<details>\n<summary>参考答案</summary>\n\n'+c['chain']+'。请沿箭头逐项解释，尤其说清中间表示的单位、坐标或概率测度；只复述名词不算掌握。\n\n</details>\n\n'
    text+='### 自测 26. 能否只用一张“看起来正确”的图片证明实现正确？\n\n<details>\n<summary>参考答案</summary>\n\n不能。需要将关键关系拆成可预测的小输入，检查数值、边界与对照；随机方法还要区分一次结果与统计期望，显示图还需区分编码与原始数据。\n\n</details>\n\n'
    text+='## 17. 带走的结论与仍需练习的内容\n\n'
    for s in c['sections']:text+='- '+s['answer']+'\n'
    text+='\n'+table(['层次','已经说明','还需动手验证'],[('概念','本篇十二个问题、公式与原页对应。','用自己的话重新解释，并给出一个反例。'),('数值','正文手算与解析小模型。','改变一个输入，预测再运行。'),('系统','指出实现条件和典型错误。','完整应用需另外检查场景、性能和边界。')])+'\n'
    text+='## 18. 整门课闭环与继续阅读\n\n'
    mapping=[('cs184-01-introduction','L01 · 导论','这门课在求什么？','从场景到像素与感知')]+EXISTING
    for other in allcourses:
        if other['key']=='01':continue
        mapping.append((other['slug'],other['title'].split('：')[0],other['chain'].split(' → ')[0],other['chain'].split(' → ')[-1]))
    text+=table(['讲义','起点问题','得到的工具或终点'],[(f'[{label}]({url(slug)})',q,a) for slug,label,q,a in mapping])+'\n'
    text+='春季 L18–27 与夏季补充专题保留本地文件标识，**不冒充不存在的秋季同编号讲次**。可以按上表顺序学习，也可在相机、颜色、采样之间按依赖往返。\n\n'
    text+='## 19. 原课件全页索引与来源\n\n'
    text+=f'[原课件文件与版本记录]({source}) · [课程官网]({"https://cs184.eecs.berkeley.edu/"+c["term"]+"/"})\n\n'
    text+=f'文件：`{c["filename"]}`；PDF 页数：{count}；SHA-256：`{meta["sha256"]}`。\n\n'
    text+='“正文核对”表示本篇实际引用该页截图；“索引保留”包括演示、行政信息、补充、致谢与重复构建页，不表示逐页都有独立讲解。原视频的运动过程不能由静态 PDF 截图完整复现。\n\n'
    text+=table(['PDF 页','原页可提取标题','本篇使用'],[(p['page'],page_title(p['text']),'正文核对' if p['page'] in used else '索引保留') for p in pages])+'\n'
    if key=='18':text+='外部核对：[PBRT 4e：镜面反射与透射](https://pbr-book.org/4ed/Reflection_Models/Specular_Reflection_and_Transmission)。用于核对反射/透射方向和界面散射的区分；正文其余内容主要依据所列课件。\n\n'
    if key=='16':text+='外部核对：[PBRT 4e：Path Tracing](https://pbr-book.org/4ed/Light_Transport_I_Surface_Reflection/Path_Tracing)。用于核对随机终止与路径采样的解释；本文标量例子为自行推导。\n\n'
    text=text.rstrip()+'\n'
    (out/'index.md').write_text(text,encoding='utf8')
    return dict(key=key,slug=c['slug'],pages=count,screenshots=len(used),diagrams=20,worked_examples=12,self_tests=26,
                lines=len(text.splitlines()),tables=text.count('| ---'),h2=text.count('\n## '))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--pdf-root',type=Path,required=True);ap.add_argument('--draw-root',type=Path)
    ap.add_argument('--figures',action='store_true');ap.add_argument('--pages',action='store_true');ap.add_argument('--notes',action='store_true');args=ap.parse_args()
    courses=load();figmod=runpy.run_path(str(SCRIPTS/'cs184-course/figures.py'));meta=[];stats=[]
    work=ROOT/'.work/cs184';work.mkdir(parents=True,exist_ok=True)
    tasks=[]
    for c in courses:
        pdf=args.pdf_root/c['term']/'lectures'/c['filename'];doc=fitz.open(pdf)
        pages=[dict(page=i+1,text=p.get_text()) for i,p in enumerate(doc)]
        m=dict(key=c['key'],term=c['term'],filename=c['filename'],pages=len(doc),sha256=hashlib.sha256(pdf.read_bytes()).hexdigest());meta.append(m)
        dest=ROOT/'src/content/notes'/c['slug'];(dest/'diagrams').mkdir(parents=True,exist_ok=True)
        if args.notes:stats.append(notes(c,courses,pages,figmod['EXTRAS'][c['key']],m))
        if args.pages:
            (dest/'images').mkdir(exist_ok=True);pad=3 if len(doc)>99 else 2
            for p in sorted({p for s in c['sections'] for p in s['pages']}):
                pg=doc[p-1]; pix=pg.get_pixmap(matrix=fitz.Matrix(1200/pg.rect.width,1200/pg.rect.width),alpha=False)
                im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples).quantize(colors=256)
                im.save(dest/'images'/f'p{p:0{pad}d}.png',optimize=True)
        if args.figures:
            if not args.draw_root:ap.error('--figures needs --draw-root')
            specs=[]
            for i,s in enumerate(c['sections'],1):specs.append((f'd{i:02d}-relation',figmod['chain'](s['flow'],s['body'].replace('¶','\n'))))
            for i,(kind,labels,params,caption) in enumerate(figmod['EXTRAS'][c['key']],13):specs.append((f'd{i:02d}-{kind}',figmod['geom'](kind,labels,params,caption)))
            for name,spec in specs:
                folder=work/'editable'/c['key'];folder.mkdir(parents=True,exist_ok=True)
                ops=folder/(name+'.json');pptx=folder/(name+'.pptx')
                ops.write_text(json.dumps(spec,ensure_ascii=False,indent=2),encoding='utf8')
                if not pptx.exists():
                    subprocess.run([sys.executable,'-m','pptdraw','new',str(pptx),'--size','7.16x2.85'],cwd=args.draw_root,check=True,capture_output=True)
                    result=subprocess.run([sys.executable,'-m','pptdraw','apply',str(pptx),str(ops)],cwd=args.draw_root,capture_output=True)
                    if result.returncode:raise RuntimeError(result.stderr.decode('utf8',errors='replace')+result.stdout.decode('utf8',errors='replace'))
                tasks.append(dict(pptx=str(pptx),png=str(dest/'diagrams'/(name+'.png'))))
        print(c['key'],len(doc),'done',flush=True)
    if tasks:(work/'render-tasks.json').write_text(json.dumps(tasks,ensure_ascii=False),encoding='utf8')
    (SCRIPTS/'cs184-course-sources.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    if stats:(work/'content-stats.json').write_text(json.dumps(stats,indent=2),encoding='utf8')

if __name__=='__main__':main()
