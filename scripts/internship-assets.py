"""Package traceable existing images and code; does not run a reconstruction."""
from pathlib import Path
import json,hashlib,shutil,html,urllib.request,re
from PIL import Image
ROOT=Path(r'D:\notes'); WORK=Path(r'D:\Downloads\8820起'); SNAP=WORK/'.codex-work/internship-notes-20261109/source/home/yjl'
OUT=ROOT/'public/internship'; MEDIA=OUT/'media'; CODE=OUT/'code'
for p in [MEDIA,CODE]:p.mkdir(parents=True,exist_ok=True)
manifest=[]
def copy_image(src,name,caption,kind='historical_result'):
 src=Path(src);dst=MEDIA/name
 with Image.open(src) as im:
  im=im.convert('RGB');im.thumbnail((1600,1600));im.save(dst,quality=90)
 manifest.append(dict(file=name,source=str(src),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),kind=kind,description=caption))
docs=WORK/'8820起/01-桌面资料/路面病害查看器文档/images'
for p in docs.glob('*.jpg'):copy_image(p,p.name,'2026-10-05 导出的历史说明配图；不是本次重新运行结果')
shots=WORK/'8820起/02-报告/viewer-decks/assets/shots'
for p in shots.glob('*.jpg'):copy_image(p,p.name,'既有项目报告中的真实查看器截图；观察日期以原报告为准')
for n in ['sheet_hold.jpg','sheet_novel.jpg']:
 copy_image(WORK/'.codex-work/gaussian-audit/g1_00'/n,'g1_00-'+n,'历史 g1_00 诊断拼图；训练母版缺失且位姿版本改变，不是真值精度评测')
release=WORK/'analysis_time/deploy_8829'
for n in ['best_resolved_source.png','equal_weight_blend.png','heldout_intersections.jpg','correspondence_review.jpg','center_patch_review.jpg','coverage_comparison.jpg','raw_grid_rows.jpg']:
 found=sorted(release.rglob(n))
 if found:copy_image(found[-1],'8829-'+Path(n).stem+'.jpg','8829 已有局部实验产物；不是全路线几何验收')
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
for n in ['3540-rgb.jpg','3540-labels.jpg','3540-depth.jpg']:
 dst=MEDIA/n
 if not dst.exists():
  with opener.open('http://100.105.132.36:8833/media/'+n,timeout=45) as r:dst.write_bytes(r.read())
 manifest.append(dict(file=n,source='/vdata/yjl/recon8833/site/media/'+n,sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),kind='saved_observation' if n.endswith('rgb.jpg') else 'saved_model_output',description='2026-11-09 读取现有服务器产物；未运行模型'))
FILES={
 '8820':['crack/viewer3d/build/s03_ortho.py','crack/viewer3d/build/s04_register.py','crack/viewer3d/build/s05_site.py'],
 '8821':['crack/viewer3d/build/t03d_hmm24.py','crack/viewer3d/build/t03f_pose24.py','crack/viewer3d/build/run_v2.sh'],
 '8822':['crack/viewer3d/build/u01_run24.py','crack/viewer3d/build/u02_site.py','crack/viewer3d/build/u09_pairs.py'],
 '8823':['crack/viewer3d/build/k01_kitti.py','crack/viewer3d/build/k02_rot.py','crack/viewer3d/build/k03_site.py'],
 '8824':['asset8824/a/geom.py','asset8824/run/a1_locate.py','asset8824/run/a2_verify.py','asset8824/README.md'],
 '8825':['crack/show8821/serve.py','crack/show8821/index.html'],
 '8826':['crack/viewer8826/build/t01a_vo.py','crack/viewer8826/build/t01f_track.py','crack/viewer8826/build/t04_cloud.py'],
 '8827':['crack/city8827/build/e00_frames.py','crack/city8827/build/e01_masks.py','crack/city8827/build/e02_poses.py','crack/city8827/build/e03_depth.py','crack/city8827/build/e04_train.py','crack/city8827/build/e05_export.py','crack/city8827/build/p01_nodes.py'],
 '8828':['crack/viewer1012/README.md','crack/viewer1012/build/t01e_1012.py','crack/viewer1012/build/t01f_track.py'],
 '8829':['crack/snap1012/build/p13_joint.py','crack/snap1012/build/p14_render.py','crack/snap1012/build/prepare_clean_inputs.py','crack/snap1012/build/run_clean_pipeline.py'],
 '8830':['crack/annot_tool/server.py','crack/annot_tool/build_verify_queue.py'],
 '8831':['crack/snap1012/build/sn_raw.py','crack/snap1012/build/p22_rawortho.py','crack/snap1012/build/p11_raw.py'],
 '8832':['crack/radix8832/site/radix-compare/viewer.js','crack/radix8832/site/radix-compare/compare.js','crack/radix8832/site/radix-compare/config.json'],
}
sources={}
for port,paths in FILES.items():
 sources[port]=[]
 for rel in paths:
  p=SNAP/rel
  if not p.exists():
   # Some deployed frontends live in site/; resolve only exact basename in that directory.
   q=p.parent/'site'/p.name
   if q.exists():p=q
   else:print('missing',rel);continue
  data=p.read_text(encoding='utf-8',errors='replace');slug=port+'-'+p.name+'.html'
  rows='\n'.join(f'<span class="line" id="L{i}"><a href="#L{i}">{i:4}</a> {html.escape(line)}</span>' for i,line in enumerate(data.splitlines(),1))
  digest=hashlib.sha256(p.read_bytes()).hexdigest()
  (CODE/slug).write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>'+html.escape(p.name)+'</title><style>body{margin:24px;font:15px system-ui;background:#faf8f3;color:#243342}pre{overflow:auto;line-height:1.6;background:white;padding:16px}.line{display:block}.line:target{background:#fff1a8}a{color:#58728a}header{overflow-wrap:anywhere}</style><header><a href="/notes/series/internship/">返回实习专栏</a><h1>'+html.escape(p.name)+'</h1><p>只读快照：2026-11-09 · /home/yjl/'+html.escape(str(p.relative_to(SNAP)).replace('\\','/'))+'</p><p>SHA-256: '+digest+'</p></header><pre>'+rows+'</pre></html>',encoding='utf-8')
  sources[port].append(dict(name=p.name,path='/home/yjl/'+str(p.relative_to(SNAP)).replace('\\','/'),url='/notes/internship/code/'+slug,sha256=digest,lines=len(data.splitlines())))
(OUT/'media-provenance.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'source-index.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'images':len(manifest),'source_files':sum(map(len,sources.values()))}))
