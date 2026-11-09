"""Read-only remote source snapshot for the internship notes. No inference."""
from pathlib import Path
import paramiko, json, sys, zipfile, io
ROOT=Path(r'D:\Downloads\8820起\.codex-work\internship-notes-20261109')
ROOT.mkdir(parents=True,exist_ok=True)
c=paramiko.SSHClient();c.load_host_keys(str(Path.home()/'.ssh/known_hosts'))
for kind,key in c.get_host_keys().lookup('192.168.203.143').items():c.get_host_keys().add('100.105.132.36',kind,key)
c.set_missing_host_key_policy(paramiko.RejectPolicy())
c.connect('100.105.132.36',username='yjl',key_filename=str(Path.home()/'.ssh/id_ed25519'),look_for_keys=False,allow_agent=False,timeout=25)
c.get_transport().set_keepalive(10)
remote=r'''
import os,io,zipfile,json,hashlib
from pathlib import Path
roots=['/home/yjl/crack/viewer3d','/home/yjl/crack/viewer8826','/home/yjl/crack/viewer1012','/home/yjl/crack/snap1012','/home/yjl/crack/annot_tool','/home/yjl/asset8824','/home/yjl/crack/show8821','/home/yjl/crack/city8827','/home/yjl/crack/radix8832']
buf=io.BytesIO(); inventory=[]
with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:
 for root in roots:
  for base,ds,fs in os.walk(root):
   depth=len(Path(base).relative_to(root).parts)
   ds[:]=[d for d in ds if d not in ['.git','node_modules','vendor','__pycache__','venv','.venv','models','checkpoints','work','data','outputs','output','logs','deploy_backups','deploy_staging','releases','tile','tiles','front','crack','ground','frames','media','images','textures','assets','sources','reference'] and depth<2]
   for f in fs:
    p=Path(base)/f
    if p.suffix.lower() in ['.py','.js','.html','.md','.sh','.json']:
     try:
      size=p.stat().st_size
      if size>350000:continue
      data=p.read_bytes(); name=str(p).lstrip('/')
      z.writestr(name,data);inventory.append({'path':str(p),'size':size,'sha256':hashlib.sha256(data).hexdigest()})
     except OSError:pass
 z.writestr('inventory.json',json.dumps(inventory,ensure_ascii=False,indent=2))
import sys
sys.stdout.buffer.write(buf.getvalue())
'''
i,o,e=c.exec_command('python3 -',timeout=120);i.write(remote);i.channel.shutdown_write()
chunks=[]
while True:
 b=o.read(65536)
 if not b:break
 chunks.append(b)
 if len(chunks)%16==0:print('downloaded',len(chunks)*65536,flush=True)
data=b''.join(chunks);err=e.read().decode();assert o.channel.recv_exit_status()==0,err
(ROOT/'source-snapshot.zip').write_bytes(data)
with zipfile.ZipFile(io.BytesIO(data)) as z:z.extractall(ROOT/'source')
print(json.dumps({'bytes':len(data),'files':len(json.loads((ROOT/'source/inventory.json').read_text()))}))
c.close()
