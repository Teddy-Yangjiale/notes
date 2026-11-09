"""Package already-fetched evidence and source snapshots for the 8826 lesson."""
from pathlib import Path
import argparse, json, hashlib, html, shutil, zipfile
p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];O=root/'public/internship/8826-lesson';(O/'code').mkdir(exist_ok=True)
manifest=json.loads((a.evidence/'manifest.json').read_text());sources=[]
for item in manifest:
 if not item['archive'].startswith('code/'):continue
 src=a.evidence/item['archive'];data=src.read_bytes();assert hashlib.sha256(data).hexdigest()==item['sha256'];name=src.name
 header=f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>{name}</title><style>body{{font:15px system-ui;margin:24px;background:#faf8f3}}pre{{overflow:auto;line-height:1.6}}pre span{{display:block}}span:target{{background:#fff1a8}}header{{overflow-wrap:anywhere}}</style><header><a href="/notes/internship-8826/">返回8826课堂笔记</a><h1>{name}</h1><p>2026-11-10 服务器只读快照：{html.escape(item["path"])}<br>SHA-256 {item["sha256"]}</p></header><pre>'
 lines=data.decode('utf-8').splitlines();body='\n'.join(f'<span id="L{i}"><a href="#L{i}">{i:4d}</a> {html.escape(line)}</span>' for i,line in enumerate(lines,1));(O/'code'/(name+'.html')).write_text(header+body+'</pre></html>',encoding='utf-8');sources.append({**item,'url':'/notes/internship/8826-lesson/code/'+name+'.html','lines':len(lines)})
(O/'code-manifest.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')
for f in ['internship-8826-case.py','internship-8826-ba-diagnostic.py']:
 shutil.copyfile(root/'scripts'/f,O/f)
for name in ['s1_00','s1_01']:shutil.copyfile(a.evidence/'input/gs/ba'/(name+'.npz'),O/(name+'-ba.npz'))
provenance={'date':'2026-11-10','mode':'read-only server snapshots; CPU diagnostics only; no inference, training, BA rerun, or server writes','saved_inputs':manifest,'tensor_slices':json.loads((a.evidence/'input/tensor-info.json').read_text()),'caveats':['Current source is not proof of the exact historical checkpoint or invocation.','CPU feature matches are newly extracted, not original BA observation arrays.','Deployed tile is existing output; CPU single-frame candidates are before cross-frame voxel filtering.'],'assets':[]}
for f in sorted(O.iterdir()):
 if f.is_file() and f.name not in ['provenance.json','editable-diagrams.zip']:
  data=f.read_bytes();normalization='none'
  if f.suffix in ['.json','.py','.txt']:
   data=data.replace(b'\r\n',b'\n');normalization='CRLF to LF, matching Git publication'
  provenance['assets'].append({'file':f.name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'normalization':normalization})
(O/'provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2),encoding='utf-8')
draw=Path(r'D:\Draw');work=draw/'.pptdraw/internship_8826_deep_20261110';decks=draw/'out/internship_8826_deep_20261110'
with zipfile.ZipFile(O/'editable-diagrams.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(decks.glob('*.pptx')):z.write(f,'pptx/'+f.name)
 for f in sorted(work.glob('*.json')):
  if '-inspect' not in f.name and '-before' not in f.name and f.name!='render-tasks.json':z.write(f,'ops/'+f.name)
 z.write(work/'build.py','build.py');z.write(O/'3540-raw.jpg','assets/3540-raw.jpg')
 z.writestr('README.txt','Four native editable PPTX figures made with D:\\Draw. Text, boxes, and arrows are editable. Photos are saved real inputs. See the article and provenance.json for source and evidence limits. build.py uses local paths; adapt them before rebuilding. Inspect existing decks and preserve edits.\n')
print('Packaged',len(sources),'source snapshots and four editable diagrams')
