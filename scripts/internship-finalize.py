from pathlib import Path
import json,re,html,hashlib,zipfile,shutil
R=Path(r'D:\notes');P=R/'public/internship';W=Path(r'D:\Downloads\8820起\.codex-work');S=W/'internship-notes-20261109/source/home/yjl'
index=json.loads((P/'source-index.json').read_text(encoding='utf-8'))
extra={'8833':[(W/'recon8833/app.js','app.js','2026-11-08 local deployment source'),(W/'recon8833/serve.py','serve.py','2026-11-08 local deployment source')],
'models':[(W/'pipeline-code-audit-20261107'/n,n,'2026-11-07 model audit snapshot') for n in ['abot_pi3.py','abot_config.json','abot_preprocessing.py','da3_model.py','da3_nested_config.yaml','sam3_processor.py']],
'8826':[(W/'gaussian-audit/upstream/g11_ba.py','g11_ba.py','2026-11-07 existing audit snapshot')]}
for port,files in extra.items():
 for f,name,date in files:
  assert f.exists(),f
  raw=f.read_text(encoding='utf-8',errors='replace');url=f'/notes/internship/code/{port}-{name}.html';digest=hashlib.sha256(f.read_bytes()).hexdigest()
  lines='\n'.join(f'<span id="L{i}"><a href="#L{i}">{i:4}</a> {html.escape(x)}</span>' for i,x in enumerate(raw.splitlines(),1))
  (P/'code'/f'{port}-{name}.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>'+name+'</title><style>body{font:15px system-ui;margin:24px;background:#faf8f3}pre{overflow:auto;line-height:1.6}pre span{display:block}span:target{background:#fff1a8}header{overflow-wrap:anywhere}</style><header><a href="/notes/series/internship/">实习专栏</a><h1>'+name+'</h1><p>'+date+'</p><p>SHA-256 '+digest+'</p></header><pre>'+lines+'</pre></html>',encoding='utf-8')
  index.setdefault(port,[])
  index[port]=[x for x in index[port] if x['name']!=name]+[dict(name=name,path=str(f),url=url,sha256=digest,lines=len(raw.splitlines()),snapshot=date)]
(P/'source-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf-8')
snippets={
'8820':('s04_register.py','RES = 0.04',8,'先看采样分辨率与搜索常量。它们将米制位置变成离散搜索格。这里纵向常量与文件头旧说明不同，因此本篇采用实际代码值。'),
'8821':('t03d_hmm24.py','def maxconv',21,'V 是上一层状态得分，pen 是移动若干状态格的惩罚。每次移位后逐格比较，保留更高得分并记录来源；这就是正文Viterbi递推的局部实现。'),
'8822':('u02_site.py','def make_fmask',12,'这一段把车辆语义标签变成前摄遮挡掩膜。它不会估计车辆三维运动，而是为页面决定哪些位置不应被地面贴图覆盖。'),
'8823':('k01_kitti.py','def rel_gt',6,'先把两个3×4真值补成齐次矩阵，再用前一帧逆变换乘后一帧。取出的横向、前向和朝向是相对运动，不是两台相机的世界坐标直接相减。'),
'8824':('geom.py','def triangulate',24,'P 去掉沿射线的分量；A、b 累加每条射线的约束；cond 检查系统是否退化；solve 求三维点。逐句对应正文的正规方程。'),
'8825':('serve.py','    def send_head',17,'Range 是浏览器请求的字节范围。程序先验证文件与区间，再返回206和内容长度。此处只传已有文件，没有任何模型推理调用。'),
'8826':('t04_cloud.py','def frame_scale',18,'先挑有效道路像素，再计算几何道路距离与模型距离之比。中位比例给尺度，远近两组的比例差用于发现尺度之外的非线性问题；不是把点云随意乘一个经验数。'),
'8827':('e04_train.py','def load_frame',14,'这里依次读取RGB与标签、膨胀动态区域、缩放深度、计算道路射线交点，再构造颜色与深度有效区域。注意平面替换和conf裁剪发生在训练循环之前。'),
'8828':('t01e_1012.py','tb = tb + LAG12',8,'定位时刻先加本分支的时延，再按照片时刻插值经纬度，最后保存逐帧位置信息。若重复在空间坐标上扣同一时延，会修正两次。'),
'8829':('p13_joint.py','def update_T',28,'固定当前几何与外观参数后，这一函数重新估计路面纹理。读代码时追踪每个格子的颜色和权重累加，再看分母；它与随后对几何执行Adam是交替步骤。'),
'8830':('server.py','def render_seg',21,'先复制预测，删除指定连通块，再改类别，最后画人的折线。顺序决定最终标签；保存的是类别编码而非叠加展示颜色。'),
'8831':('p22_rawortho.py','rows = np.where',7,'这里只挑可读照片，然后从各行表格直接取经纬度、航向与时间。clock条件分支不是原始基线默认路径；读实验时必须确认命令行选择。'),
'8832':('viewer.js','function apply()',1,'同一个父页面状态同步相机位置、四元数与当前方法。若两边相机不一致，就无法把画面差异归因于渲染路径。'),
'8833':('serve.py','class ',12,'这个服务文件负责HTTP资源交付。算法阶段已经离线生成文件，读取页面不会回调SAM、DA3或高斯训练。'),
'models':('sam3_processor.py','        out_probs = out_logits.sigmoid()',9,'先把logit变成候选分数，再乘presence分数，最后按阈值筛选。这个实例级筛选与随后像素掩膜阈值是两层不同判断。'),
}
for port,entries in index.items():
 note=R/'src/content/notes'/('internship-models' if port=='models' else 'internship-'+port)/'index.md'
 if not note.exists():continue
 body=note.read_text(encoding='utf-8');marker='\n## 源码课：从公式回到真实文件\n';body=body.split(marker)[0].rstrip()
 appendix=marker+'\n下面是可离线阅读的带行号代码快照。项目调用代码采集于2026-11-09；模型与历史补充文件单独标注日期。源码注释也可能包含旧判断，应与本文核验和实际语句一起读。\n\n| 文件 | 原路径 / 快照 | 长度 |\n|---|---|---|\n'
 for e in entries:appendix+=f"| [{e['name']}]({e['url']}) | `{e.get('snapshot',e['path'])}` | {e['lines']} 行 |\n"
 if port in snippets:
  name,needle,count,explain=snippets[port];entry=next(x for x in entries if x['name']==name)
  f=Path(entry['path']) if entry.get('snapshot') else S/entry['path'].removeprefix('/home/yjl/')
  lines=f.read_text(encoding='utf-8',errors='replace').splitlines();start=next(i for i,l in enumerate(lines) if needle in l)
  lang='javascript' if f.suffix=='.js' else 'python'
  appendix+=f"\n### 关键片段逐句读\n\n{explain}\n\n原文件定位：[{name} 第 {start+1} 行]({entry['url']}#L{start+1})。以下为真实节选，依赖所在文件上下文，不是独立可运行程序。\n\n```{lang}\n"+'\n'.join(lines[start:start+count])+"\n```\n"
 appendix+='\n[返回专栏总览](/notes/internship-00-overview/) · [下载可编辑图解](/notes/internship/editable-diagrams.zip)\n'
 note.write_text(body+'\n'+appendix,encoding='utf-8')
with zipfile.ZipFile(P/'editable-diagrams.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in Path(r'D:\Draw\out\internship_notes_20261109').glob('*.pptx'):z.write(p,'pptx/'+p.name)
 for p in Path(r'D:\Draw\.pptdraw\internship_notes_20261109').glob('*.json'):
  if not p.name.endswith('-inspect.json'):z.write(p,'ops/'+p.name)
 for p in (P/'figures').glob('*.png'):z.write(p,'png/'+p.name)
print('finalized sources',sum(map(len,index.values())),'notes',len(list((R/'src/content/notes').glob('internship-*/index.md'))))
