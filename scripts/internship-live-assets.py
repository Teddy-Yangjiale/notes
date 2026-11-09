from pathlib import Path
import urllib.request,json,re,concurrent.futures,hashlib,paramiko,io
from PIL import Image
ROOT=Path(r'D:\notes\public\internship');OUT=ROOT/'media'
op=urllib.request.build_opener(urllib.request.ProxyHandler({}))
def get(url):
 with op.open(url,timeout=45) as r:return r.read(),r.status
def page(port):
 try:
  b,s=get(f'http://100.105.132.36:{port}/');t=re.search(r'<title>(.*?)</title>',b.decode('utf-8',errors='replace'),re.S)
  return dict(port=port,status=s,title=t.group(1) if t else '',sha256=hashlib.sha256(b).hexdigest())
 except Exception as e:return dict(port=port,error=str(e))
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:pages=list(ex.map(page,range(8821,8834)))
(ROOT/'live-services.json').write_text(json.dumps(dict(checked='2026-11-09',services=pages),ensure_ascii=False,indent=2),encoding='utf-8')
print('homepage inventory',len(pages),flush=True)
sources=[]
def save(b,name,source,kind):
 with Image.open(io.BytesIO(b)) as im:
  im=im.convert('RGB');im.thumbnail((1600,1600));im.save(OUT/name,quality=90)
 sources.append(dict(file=name,source=source,source_sha256=hashlib.sha256(b).hexdigest(),sha256=hashlib.sha256((OUT/name).read_bytes()).hexdigest(),kind=kind))
d=json.loads(get('http://100.105.132.36:8830/api/list')[0]);name=d['items'][0]['name']
b,_=get(f'http://100.105.132.36:8830/img/{name}.jpg');save(b,'8830-observation.jpg',f'/home/yjl/data/0907/eval_disease_v1/images/{name}.jpg','raw_observation')
state=json.loads(get(f'http://100.105.132.36:8830/api/item/{name}')[0]);(ROOT/'annotation-example.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
c=paramiko.SSHClient();c.load_host_keys(str(Path.home()/'.ssh/known_hosts'))
for kind,key in c.get_host_keys().lookup('192.168.203.143').items():c.get_host_keys().add('100.105.132.36',kind,key)
c.set_missing_host_key_policy(paramiko.RejectPolicy());c.connect('100.105.132.36',username='yjl',key_filename=str(Path.home()/'.ssh/id_ed25519'),look_for_keys=False,allow_agent=False,timeout=25)
s=c.open_sftp();s.get_channel().settimeout(45)
for path,name in [('/home/yjl/data/1012/front_all/000052.jpg','8828-front-000052.jpg'),('/home/yjl/data/1012/front_all/003540.jpg','8828-front-003540.jpg')]:
 with s.open(path,'rb') as f:save(f.read(),name,path,'raw_observation')
for path,prefix in [('/home/yjl/crack/snap1012/site_raw/ground/L0','8831-ground'),('/home/yjl/crack/viewer1012/site2/ground/L0','8828-ground')]:
 items=sorted(p for p in s.listdir(path) if p.endswith('.webp'))
 # Use a substantial existing tile, not an empty border fragment.
 ranked=sorted(items,key=lambda n:s.stat(path+'/'+n).st_size,reverse=True)[:2] if len(items)<50 else [items[len(items)//2]]
 for j,n in enumerate(ranked):
  with s.open(path+'/'+n,'rb') as f:save(f.read(),prefix+f'-{j}.jpg',path+'/'+n,'saved_orthophoto')
s.close();c.close()
(ROOT/'live-media-provenance.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')
print('live images',len(sources),flush=True)
