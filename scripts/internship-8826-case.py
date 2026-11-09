"""Recompute one saved-frame diagnostic on CPU; never runs ABot or bundle adjustment."""
from pathlib import Path
import argparse, json, shutil, ast
import numpy as np, cv2
from scipy.ndimage import maximum_filter, minimum_filter
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, ListedColormap

p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
I=a.input; O=a.out;O.mkdir(parents=True,exist_ok=True); code=I.parent/'code'
cfg=json.loads((I/'effective_camera.json').read_text());K=np.array([[cfg['fx'],0,cfg['cx']],[0,cfg['fy'],cfg['cy']],[0,0,1.]])
r,pit,y=cfg['roll'],cfg['pitch'],cfg['yaw']
Rz=np.array([[np.cos(y),-np.sin(y),0],[np.sin(y),np.cos(y),0],[0,0,1.]])
Rx=np.array([[1,0,0],[0,np.cos(pit),-np.sin(pit)],[0,np.sin(pit),np.cos(pit)]])
Ry=np.array([[np.cos(r),0,np.sin(r)],[0,1,0],[-np.sin(r),0,np.cos(r)]])
B=np.array([[1,0,0],[0,0,1],[0,-1,0.]])
RCV=Rz@Rx@Ry@B
jj,ii=np.meshgrid(np.arange(756),np.arange(420));u=(jj+.5)*1920/756-.5;v=(ii+2+.5)*1080/425-.5
nrm=cv2.undistortPoints(np.stack([u,v],-1).reshape(-1,1,2),K,np.array(cfg['dist'])).reshape(420,756,2)
rc=np.concatenate([nrm,np.ones((420,756,1))],-1);rc/=np.linalg.norm(rc,axis=-1,keepdims=True)
rv=(rc@RCV.T).astype(np.float32)
li=np.clip(np.round((v+.5)/2-.5).astype(int),0,539);lj=np.clip(np.round((u+.5)/2-.5).astype(int),0,959)
lab0=np.load(I/'labels-3540.npz')['labels'];lab=lab0[li,lj]
zz=np.load(I/'abot-3540.npz');P=zz['local_points'];rm=np.linalg.norm(P,axis=-1);cf=zz['confidence'];Z=P[...,2]
rt=np.where(-rv[...,2]>.02,1.475/np.maximum(-rv[...,2],1e-6),np.inf)
scale_mask=(lab==1)&(cf>.1)&(rt>5)&(rt<25)&(rm>1e-4)
scale=float(np.median(rt[scale_mask]/rm[scale_mask]));sc=np.load(I/'cloud2_scale.npy');sr=sc[sc[:,0]==3540][0];smoothed=float(sr[2]);distance=rm*smoothed
veh0=(lab0==2).astype(np.uint8);veh=cv2.dilate(veh0,np.ones((7,7),np.uint8));veh|=cv2.dilate(veh0,np.ones((7,5),np.uint8),anchor=(2,6));veh=veh[li,lj]>0
edge=(maximum_filter(Z,size=3)-minimum_filter(Z,size=3))<.06*np.maximum(Z,1e-6)
m0=(cf>.1)&edge&~veh&(distance>1.5)&(distance<42)&(Z>1e-4)
X=rv*distance[...,None];X[...,2]+=1.475
m1=m0&(X[...,2]>-.35)&(X[...,2]<30)
tr=np.load(I/'track0903.npz');ti=int(np.flatnonzero(tr['idx']==3540)[0]);psi=float(tr['psi'][ti]);c,s=np.cos(psi),np.sin(psi)
V=np.array([[c,s,0],[-s,c,0],[0,0,1.]])
world=X@V.T+np.array([tr['E'][ti],tr['N'][ti],0]);E,N=world[...,0],world[...,1]
trees=[]
for pas in [0,1]:
 ids=np.flatnonzero((tr['seg']>=0)&(tr['pas']==pas));parts=[]
 for ia,ib in zip(ids[:-1],ids[1:]):
  d=np.hypot(tr['E'][ib]-tr['E'][ia],tr['N'][ib]-tr['N'][ia])
  if ib-ia==1 and d<8:
   q=np.arange(max(1,int(d/.5)))/max(1,int(d/.5));parts.append(np.c_[tr['E'][ia]+q*(tr['E'][ib]-tr['E'][ia]),tr['N'][ia]+q*(tr['N'][ib]-tr['N'][ia])])
  else:parts.append(np.array([[tr['E'][ia],tr['N'][ia]]]))
 trees.append(cKDTree(np.vstack(parts)))
own=trees[int(tr['pas'][ti])].query(world[...,:2].reshape(-1,2))[0].reshape(420,756);other=trees[1-int(tr['pas'][ti])].query(world[...,:2].reshape(-1,2))[0].reshape(420,756)
m2=m1&(own<=other+.3);cov=np.load(I/'coverage.npz');covered=np.zeros((420,756),bool)
gx=np.floor(E/20).astype(int);gn=np.floor(N/20).astype(int);col=np.clip(((E-gx*20)/.2).astype(int),0,99);row=np.clip((((gn+1)*20-N)/.2).astype(int),0,99)
for key in cov.files:
 ex,ny=map(int,key.split('_'));sel=(gx==ex)&(gn==ny);covered[sel]=cov[key][row[sel],col[sel]]
m3=m2&~(((lab==1)|(X[...,2]<.08))&covered)
samples=[]
for name,j,i in [('A',378,352),('B',163,236),('C',416,256),('D',378,76)]:
 samples.append(dict(name=name,model_pixel=[j,i],raw_half_pixel=[float((u[i,j]+.5)/2-.5),float((v[i,j]+.5)/2-.5)],label=int(lab[i,j]),model_point=P[i,j].tolist(),model_z=float(Z[i,j]),model_range=float(rm[i,j]),confidence=float(cf[i,j]),unit_ray_camera=rc[i,j].tolist(),unit_ray_vehicle=rv[i,j].tolist(),scaled_range=float(distance[i,j]),vehicle_point=X[i,j].tolist(),enu=world[i,j].tolist(),scale_support=bool(scale_mask[i,j]),edge_ok=bool(edge[i,j]),vehicle=bool(veh[i,j]),stage_keep=[bool(mm[i,j]) for mm in [m0,m1,m2,m3]],road_covered=bool(covered[i,j])))
ba=np.load(I/'gs/ba/s1_00.npz');bi=int(np.flatnonzero(ba['frames']==3540)[0]);C0=ba['c2w0'][bi];C1=ba['c2w'][bi]
report=dict(frame=3540,model_index=708,track_index=ti,ba_chunk='s1_00',ba_frame_index=bi,camera=cfg,R_camera_vehicle=RCV.tolist(),vehicle_to_enu=V.tolist(),scale_raw=scale,scale_saved=sr.tolist(),scale_support=int(scale_mask.sum()),filter_counts=[int(mm.sum()) for mm in [m0,m1,m2,m3]],conf_quantiles=np.percentile(cf,[0,25,50,75,100]).tolist(),samples=samples,
 track={k:float(tr[k][ti]) for k in ['E','N','psi','GE','GN','gh','t','s']},gnss_ok=bool(tr['gnss_ok'][ti]),ba_before=C0.tolist(),ba_after=C1.tolist(),ba_corr=ba['corr'][bi].tolist(),ba_obs=int(ba['n_obs'][bi]),ba_point_count=len(ba['pts']),ba_observations=int(ba['n_obs'].sum()),ba_weak_frames=int((ba['n_obs']<80).sum()),ba_reproj_before=ba['reproj_before'].tolist(),ba_reproj_after=ba['reproj_after'].tolist(),ba_shapes={k:list(ba[k].shape) for k in ba.files})
# Run only the pure CPU image-matching function on saved strips, preserving its input gate and seed.
source=ast.parse((code/'t01a_vo.py').read_text(encoding='utf-8'));wanted={'bandpass','to_u8','px2g','rigid_fit','vo_images'}
ns={'np':np,'cv2':cv2,'RES':.02,'XR':(-9.,9.),'YR':(4.8,13.4)}
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name in wanted],type_ignores=[]),str(code/'t01a_vo.py'),'exec'),ns)
st=np.load(I/'strips-case.npz');meta=np.load(I/'strips2_meta.npz');vo=np.load(I/'vo0903.npz');ka=int(np.flatnonzero(meta['idx']==3539)[0]);kb=int(np.flatnonzero(meta['idx']==3540)[0]);vr=vo['R'][(vo['R'][:,0]==ka)&(vo['R'][:,1]==kb)][0];d=float(vr[2]);ia=int(np.flatnonzero(st['frames']==3539)[0]);ib=int(np.flatnonzero(st['frames']==3540)[0])
match=ns['vo_images'](cv2.cvtColor(st['images'][ia],cv2.COLOR_BGR2GRAY),cv2.cvtColor(st['images'][ib],cv2.COLOR_BGR2GRAY),st['valid'],d,ka*7919+kb,True,st['road'][ia]>0,st['road'][ib]>0,(min(.72*d,d-.25),max(1.5*d,d+.25)))
report['strip_pair']={'frames':[3539,3540],'stored':dict(zip(vo['keys'].tolist(),[float(v) if np.isfinite(v) else None for v in vr])),'recomputed':{k:v for k,v in match.items() if k not in ['PA','PB']}}
edge_idx=np.flatnonzero((tr['edges'][:,0]==ti-1)&(tr['edges'][:,1]==ti));report['track_edge_residual']=tr['edge_res'][edge_idx].tolist()
# Deterministic diagnostic plots; all points and images come from saved data.
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'white'})
def save(fig,name):fig.tight_layout();fig.savefig(O/name,dpi=170);plt.close(fig)
def marks(ax):
 for x in samples: j,i=x['model_pixel'];ax.plot(j,i,'o',mec='red',mfc='none',ms=8);ax.annotate(x['name'],(j,i),xytext=(7,-10),textcoords='offset points',color='red',bbox=dict(fc='white',alpha=.8,ec='none',pad=1))
fig,axs=plt.subplots(1,3,figsize=(14,3.5))
axs[0].imshow(zz['colors']);axs[0].set_title('Saved ABot colors: 420 x 756')
im=axs[1].imshow(rm,cmap='turbo',norm=LogNorm(1,150));axs[1].set_title('Model range ||P|| (not camera z)');fig.colorbar(im,ax=axs[1],fraction=.03)
im=axs[2].imshow(cf,cmap='viridis',vmin=0,vmax=1);axs[2].set_title('Saved confidence');fig.colorbar(im,ax=axs[2],fraction=.03)
for ax in axs:marks(ax);ax.set_xlabel('model column j');ax.set_ylabel('model row i')
save(fig,'pointmap.png')
fig,axs=plt.subplots(1,2,figsize=(11,4));axs[0].hist((rt/rm)[scale_mask],bins=80,range=(6,13),color='#477a99');axs[0].axvline(scale,color='#d95f02');axs[0].set(xlabel='road range / model range',ylabel='pixels',title=f'3540: {scale_mask.sum()} road supports')
near=(sc[:,0]>=3450)&(sc[:,0]<=3640);axs[1].plot(sc[near,0],sc[near,1],'.-',label='raw road median');axs[1].plot(sc[near,0],sc[near,2],label='saved smoothed scale');axs[1].axvline(3540,color='#d95f02');axs[1].legend();axs[1].set(xlabel='business frame',ylabel='meters / model unit',title='Saved scale sequence (not a new training run)');save(fig,'scale.png')
fig,axs=plt.subplots(1,2,figsize=(11,4));axs[0].imshow(np.where(m3,2,np.where(m0,1,0)),cmap=ListedColormap(['#eeeeee','#ddbd7b','#276c87']),vmin=0,vmax=2);marks(axs[0]);axs[0].set(title='0 rejected / 1 later removed / 2 frame candidates',xlabel='j',ylabel='i')
ids=np.flatnonzero(m3.ravel())[::5];ww=world.reshape(-1,3)[ids];axs[1].scatter(ww[:,0]-tr['E'][ti],ww[:,1]-tr['N'][ti],c=ww[:,2],s=1,cmap='viridis');axs[1].plot(0,0,'r^');axs[1].set(xlabel='E - camera E / m',ylabel='N - camera N / m',title='Same frame: ENU candidates, colored by height');axs[1].axis('equal');save(fig,'fusion-filter.png')
fig,axs=plt.subplots(1,2,figsize=(12,3.5))
for ax,ix in zip(axs,[ia,ib]):ax.imshow(st['images'][ix][...,::-1]);ax.set_title(f'Saved road strip {st["frames"][ix]}: 430 x 900');ax.set_xlabel('column');ax.set_ylabel('row')
if 'PA' in match:
 for ax,pts in zip(axs,[match['PA'],match['PB']]):ax.scatter((pts[:,0]+9)/.02-.5,(13.4-pts[:,1])/.02-.5,s=6,c='#00ffff')
else:
 fig.suptitle('CPU replay: matching rejected; no accepted motion edge',color='#a52a2a')
save(fig,'strips.png')
fig,axs=plt.subplots(1,2,figsize=(11,4));sel=(tr['idx']>=3484)&(tr['idx']<=3650);e0,n0=tr['E'][ti],tr['N'][ti]
axs[0].plot(tr['GE'][sel]-e0,tr['GN'][sel]-n0,label='GNSS prior');axs[0].plot(tr['E'][sel]-e0,tr['N'][sel]-n0,label='t01f track');axs[0].plot(0,0,'ro',label='3540');axs[0].axis('equal');axs[0].legend();axs[0].set(xlabel='local E / m',ylabel='local N / m',title='Position prior vs optimized planar track')
axs[1].plot(ba['frames'],np.degrees(ba['corr'][:,:3]));axs[1].axvline(3540,color='k',ls=':');axs[1].legend(['camera x','camera y','camera z']);axs[1].set(xlabel='frame',ylabel='rotation-vector correction / degree',title='Saved BA correction, chunk s1_00');save(fig,'poses.png')
shutil.copyfile(I/'raw-3540.jpg',O/'3540-raw.jpg')
for n in ['tensor-info.json','effective_camera.json']:shutil.copyfile(I/n,O/n)
np.savez_compressed(O/'case-3540.npz',model_points=P,colors=zz['colors'],confidence=cf,labels=lab0,K=K,dist=np.array(cfg['dist']),Rcv=RCV,V=V,scale=smoothed,ba_before=C0,ba_after=C1)
(O/'measurements.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
