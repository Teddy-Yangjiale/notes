"""CPU feature/geometry diagnostic on saved inputs. No model inference or BA solve."""
from pathlib import Path
import argparse, ast, json, shutil
import numpy as np
import cv2
from scipy.spatial.transform import Rotation
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();I=a.input;O=a.out
cfg=json.loads((I/'effective_camera.json').read_text());Kh=np.array([[cfg['fx']/2,0,(cfg['cx']+.5)/2-.5],[0,cfg['fy']/2,(cfg['cy']+.5)/2-.5],[0,0,1.]])
MAP1,MAP2=cv2.initUndistortRectifyMap(Kh,np.array(cfg['dist']),None,Kh,(960,540),cv2.CV_32FC1)
ba=np.load(I/'gs/ba/s1_00.npz');frames=[3535,3540,3545];ids=[int(np.flatnonzero(ba['frames']==f)[0]) for f in frames];C=ba['c2w0'][ids];FE=[];ims=[]
for f in frames:
 im=cv2.remap(cv2.imread(str(I/f'raw-{f}.jpg')),MAP1,MAP2,cv2.INTER_LINEAR);ims.append(im[...,::-1]);lab=np.load(I/f'labels-{f}.npz')['labels'];v=(lab==2).astype(np.uint8)
 veh=cv2.dilate(v,np.ones((15,15),np.uint8))|cv2.dilate(v,np.ones((15,5),np.uint8),anchor=(2,14));m=np.ones((540,960),np.uint8);m[512:]=0;m[veh>0]=0;m=cv2.remap(m,MAP1,MAP2,cv2.INTER_NEAREST);m[:2]=0;m[:,:2]=0;m[:,-2:]=0
 kp,des=cv2.SIFT_create(nfeatures=5000,contrastThreshold=.02).detectAndCompute(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY),m*255);des=np.sqrt(des/(np.abs(des).sum(1,keepdims=True)+1e-7)).astype(np.float32);FE.append((np.array([k.pt for k in kp],np.float32),des))
src=ast.parse((I.parent/'code/g11_ba.py').read_text(encoding='utf-8'));ns={'np':np,'cv2':cv2,'R0':C[:,:3,:3],'T0':C[:,:3,3],'Kh':Kh,'FX':Kh[0,0],'FE':FE}
exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in ['rel','match','tri']],type_ignores=[]),'g11_ba.py','exec'),ns)
cv2.setRNGSeed(3540);q01=ns['match']((0,1))[2];q12=ns['match']((1,2))[2];lookup={int(x):int(y) for x,y in q12};triples=np.array([[x,y,lookup[int(y)]] for x,y in q01 if int(y) in lookup],int)
uv=np.stack([FE[k][0][triples[:,k]] for k in range(3)])
Pm=[Kh@np.c_[c[:3,:3].T,-c[:3,:3].T@c[:3,3]] for c in C]
X=ns['tri'](Pm[0],Pm[2],uv[0],uv[2]);projected=[];depths=[]
for c in C:
 xc=(X-c[:3,3])@c[:3,:3];depths.append(xc[:,2]);projected.append((xc@Kh.T)[:,:2]/xc[:,2:3])
pred=np.array(projected);err=np.linalg.norm(pred-uv,axis=-1);valid=(np.array(depths)>.5).all(0)&np.isfinite(err).all(0)&(np.median(err,axis=0)<15)
choice=int(np.flatnonzero(valid)[np.argmin(np.abs(err[1,valid]-np.median(err[1,valid])))])
checks=[]
def check(name,val,limit):
 checks.append({'check':name,'max_error':float(val),'tolerance':limit});assert val<limit,(name,val)
R=C[1,:3,:3];T=C[1,:3,3];xx=X[choice];xc=R.T@(xx-T);fx,fy=Kh[0,0],Kh[1,1];z=xc[2]
Jp=np.array([[fx/z,0,-fx*xc[0]/z**2],[0,fy/z,-fy*xc[1]/z**2]]);sk=np.array([[0,-xc[2],xc[1]],[xc[2],0,-xc[0]],[-xc[1],xc[0],0]])
tr=np.load(I/'track0903.npz');k=int(np.flatnonzero(tr['idx']==3540)[0]);ps=tr['psi'][k];V=np.array([[np.cos(ps),np.sin(ps),0],[-np.sin(ps),np.cos(ps),0],[0,0,1]])
Jc=np.c_[Jp@sk,-Jp@R.T@V];Jx=Jp@R.T
def project(rr,tt,point):
 c=rr.T@(point-tt);return (Kh@c)[:2]/c[2]
eps=1e-6;base=project(R,T,xx)
num=np.column_stack([(project(R@Rotation.from_rotvec(np.eye(3)[i]*eps).as_matrix(),T,xx)-project(R@Rotation.from_rotvec(-np.eye(3)[i]*eps).as_matrix(),T,xx))/(2*eps) for i in range(3)]+[(project(R,T+V[:,i]*eps,xx)-project(R,T-V[:,i]*eps,xx))/(2*eps) for i in range(3)])
check('BA camera Jacobian, central difference',np.max(abs(num-Jc)),1e-4)
numx=np.column_stack([(project(R,T,xx+np.eye(3)[i]*eps)-project(R,T,xx-np.eye(3)[i]*eps))/(2*eps) for i in range(3)]);check('BA point Jacobian',np.max(abs(numx-Jx)),1e-4)
check('c2w inverse roundtrip',np.max(abs(R@xc+T-xx)),1e-8)
rng=np.random.default_rng(3540);AA=rng.normal(size=(15,9));H=AA.T@AA+np.eye(9);g=rng.normal(size=9);U,W,Vp=H[:6,:6],H[:6,6:],H[6:,6:];vi=np.linalg.inv(Vp);dc=np.linalg.solve(U-W@vi@W.T,-g[:6]+W@vi@g[6:]);dx=-vi@(g[6:]+W.T@dc);check('Schur vs full normal solve (synthetic SPD)',np.max(abs(np.r_[dc,dx]+np.linalg.solve(H,g))),1e-10)
meta=json.loads((I/'selected-tile-meta.json').read_text());tile=meta['tile'];N=tile['n'];bb=(I/'selected-tile.bin').read_bytes();assert len(bb)==11*N
q=np.frombuffer(bb,dtype='<u2',count=3*N).reshape(N,3);fr=np.frombuffer(bb,dtype='<u2',count=N,offset=6*N);rgb=np.frombuffer(bb,dtype='u1',count=3*N,offset=8*N).reshape(N,3);xyz=np.array(tile['lo'])+q/65535*np.array(tile['span']);sel=fr==3540;assert sel.sum()==meta['points_from_3540']
fig,axs=plt.subplots(1,3,figsize=(15,3.5))
for i,ax in enumerate(axs):
 ax.imshow(ims[i]);ax.scatter(uv[i,valid,0][::5],uv[i,valid,1][::5],s=5,c='cyan');ax.plot(*uv[i,choice],'ro',ms=9,mfc='none');ax.set(title=f'{frames[i]}: re-extracted common feature tracks',xlabel='undistorted u',ylabel='v')
fig.tight_layout();fig.savefig(O/'ba-features.png',dpi=170);plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(11,4))
for ax,m,title in [(axs[0],np.ones(N,bool),'Saved deployed tile: all source frames'),(axs[1],sel,'Same saved tile: source frame 3540 only')]:
 pts=xyz[m][::3];cc=rgb[m][::3]/255;ax.scatter(pts[:,0]-tr['E'][k],-pts[:,2]-tr['N'][k],c=cc,s=.7);ax.axis('equal');ax.set(xlabel='E - camera E / m',ylabel='N - camera N / m',title=title)
fig.tight_layout();fig.savefig(O/'deployed-cloud.png',dpi=180);plt.close(fig)
report={'kind':'new CPU feature extraction and fixed-pose triangulation; not historical BA observations or a BA rerun','frames':frames,'feature_counts':[len(f[0]) for f in FE],'pair_counts':[len(q01),len(q12)],'common_tracks':len(triples),'positive_depth_low_error_tracks':int(valid.sum()),'sample':{'track_indices':triples[choice].tolist(),'uv':uv[:,choice].tolist(),'projection':pred[:,choice].tolist(),'residual_px':err[:,choice].tolist(),'triangulated_enu':xx.tolist(),'camera_3540':xc.tolist(),'J_projection':Jp.tolist(),'J_camera':Jc.tolist(),'J_point':Jx.tolist()},'numeric_checks':checks,'deployed_tile':meta,'tile_bytes':len(bb),'quantization_step':(np.array(tile['span'])/65535).tolist()}
(O/'ba-diagnostic.json').write_text(json.dumps(report,indent=2),encoding='utf-8');np.savez_compressed(O/'ba-observations-cpu.npz',frames=frames,uv=uv,triangulated=X,valid=valid,c2w0=C)
shutil.copyfile(I/'selected-tile.bin',O/'tile-minus22-minus72.bin');shutil.copyfile(I/'selected-tile-meta.json',O/'tile-meta.json')
print(json.dumps(report,indent=2))
