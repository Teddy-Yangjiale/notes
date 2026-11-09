"""Recompute teaching diagnostics from saved frame 3484. CPU only; no model execution."""
from pathlib import Path
import argparse, json, hashlib, shutil
import numpy as np
import cv2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, LogNorm

p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--out',required=True)
a=p.parse_args();src=Path(a.input);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
cam=json.loads((src/'cam.json').read_text(encoding='utf-8'));z=np.load(src/'depth/003484.npz');poses=np.load(src/'poses.npz')
rgb=cv2.imread(str(src/'frames/003484.jpg'))[...,::-1];lab=cv2.imread(str(src/'masks/003484.png'),0)
H,W=lab.shape;K=np.array([[cam['fx'],0,cam['cx']],[0,cam['fy'],cam['cy']],[0,0,1.]])
fidx=np.flatnonzero(poses['frames']==3484)[0];c2w=poses['c2w'][fidx]
sel=(poses['frames']>=3484)&(poses['frames']<=3582);frames=poses['frames'][sel]
origin=poses['c2w'][sel,:3,3].mean(0);origin[2]=0
local=c2w.copy();local[:3,3]-=origin
dep=cv2.resize(z['depth'].astype(np.float32),(W,H),interpolation=cv2.INTER_LINEAR)
conf=cv2.resize(z['conf'].astype(np.float32),(W,H),interpolation=cv2.INTER_LINEAR)
yy,xx=np.mgrid[:H,:W];rays=np.stack([(xx+.5-K[0,2])/K[0,0],(yy+.5-K[1,2])/K[1,1],np.ones_like(xx)],-1)
dw=rays@local[:3,:3].T;tz=dw[...,2]
plane=np.where(tz<-.001,-local[2,3]/np.minimum(tz,-.001),0.)
use=(lab==1)&(tz<-.001)&(plane<80)
target=np.where(use,plane,dep).astype(np.float32)
dyn=cv2.dilate((lab==2).astype(np.uint8),np.ones((19,19),np.uint8))>0
valid=(~dyn)&(yy<1032);sky=lab==3
weight=np.where(use,1.,np.clip(conf,0,1));weight=np.where(valid&~sky&(target>.5),weight,0.).astype(np.float32)
gy,gx=np.mgrid[:H:6,:W:6];keep=(target[::6,::6]>60)&(~sky[::6,::6])&valid[::6,::6]
depths=np.minimum(target[::6,::6][keep],400)
points=rays[::6,::6][keep]*depths[:,None]@local[:3,:3].T+local[:3,3]
cammean=poses['c2w'][sel,:3,3].mean(0)
samples=[]
for name,u,v in [('A',960,900),('B',978,546),('C',1500,600),('D',840,180)]:
    d=float(target[v,u]);xc=rays[v,u]*d;delta=xc@local[:3,:3].T;mu=delta+local[:3,3]
    distance=float(np.linalg.norm(mu-cammean+origin));scale=float(np.clip(.006*distance,.3,3))
    samples.append(dict(name=name,u=u,v=v,label=int(lab[v,u]),rgb=rgb[v,u].tolist(),model_depth=float(dep[v,u]),
        target_depth=d,confidence=float(conf[v,u]),plane_used=bool(use[v,u]),valid=bool(valid[v,u]),weight=float(weight[v,u]),
        far_candidate=bool(keep[v//6,u//6]),ray=rays[v,u].tolist(),camera_point=xc.tolist(),world_delta=delta.tolist(),
        local_mean=mu.tolist(),global_mean=(mu+origin).tolist(),distance_to_mean_camera=distance,
        far_init_scale=scale,far_log_scale=float(np.log(scale)),sh0=((rgb[v,u]/255.-.5)/.28209479177387814).tolist()))
report=dict(frame=3484,range=[3484,3582],image_shape=list(rgb.shape),depth_shape=list(z['depth'].shape),
    label_counts=np.bincount(lab.ravel(),minlength=4).tolist(),camera_K=K.tolist(),depth_K=z['K'].tolist(),
    c2w=c2w.tolist(),pose_source=int(poses['src'][fidx]),origin=origin.tolist(),local_c2w=local.tolist(),
    valid_rgb_pixels=int(valid.sum()),road_replaced_pixels=int(use.sum()),positive_depth_weights=int((weight>0).sum()),
    far_candidates=int(keep.sum()),confidence_quantiles=np.percentile(conf,[0,10,50,90,100]).tolist(),
    clipped_conf_unique=np.unique(np.clip(conf,0,1)).tolist(),samples=samples,
    evidence='Recomputed from current saved inputs; not a replay of historical g1_00 initialization or training.')
(out/'measurements.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
shutil.copyfile(src/'frames/003484.jpg',out/'3484-rgb.jpg')
np.savez_compressed(out/'case-3484.npz',depth=z['depth'],conf=z['conf'],K_depth=z['K'],labels=lab,K=K,c2w=c2w,origin=origin)
plt.rcParams.update({'font.size':10,'figure.facecolor':'white','axes.spines.top':False,'axes.spines.right':False})
def markers(ax):
    for s in samples:
        ax.plot(s['u'],s['v'],'o',mfc='none',mec='#e34a33',ms=9,mew=1.6)
        ax.annotate(s['name'],(s['u'],s['v']),xytext=(7,-12),textcoords='offset points',color='#b2182b',weight='bold',bbox=dict(fc='white',ec='none',alpha=.85,pad=1))
fig,axes=plt.subplots(1,2,figsize=(13,4.2))
for ax,data,title in zip(axes,[lab,weight],['Saved semantic labels (nearest-neighbor classes)','Depth weights after road replacement and masking']):
    if data is lab:
        im=ax.imshow(data,cmap=ListedColormap(['#bdbdbd','#55a868','#c44e52','#4c72b0']),vmin=-.5,vmax=3.5);fig.colorbar(im,ax=ax,ticks=[0,1,2,3],fraction=.03,pad=.02)
    else:im=ax.imshow(data,cmap='gray',vmin=0,vmax=1);fig.colorbar(im,ax=ax,ticks=[0,1],fraction=.03,pad=.02)
    ax.set_title(title);markers(ax);ax.set_xlabel('u / pixel');ax.set_ylabel('v / pixel')
fig.tight_layout();fig.savefig(out/'labels-weights.png',dpi=170);plt.close(fig)
fig,axes=plt.subplots(1,2,figsize=(13,4.2))
for ax,data,title in zip(axes,[dep,target],['Saved DA3 depth resized to 1920 x 1080','Depth target consumed by e04 (road replaced)']):
    im=ax.imshow(data,cmap='turbo',norm=LogNorm(1,100));markers(ax);ax.set_title(title);ax.set_xlabel('u / pixel');ax.set_ylabel('v / pixel');fig.colorbar(im,ax=ax,label='camera z / m',fraction=.03,pad=.02)
fig.tight_layout();fig.savefig(out/'depth-target.png',dpi=170);plt.close(fig)
fig,axes=plt.subplots(1,2,figsize=(11,4.3));ys=gy[keep];xs=gx[keep]
axes[0].scatter(xs,ys,s=3,c=depths,cmap='viridis');axes[0].set(xlim=(0,W),ylim=(H,0),xlabel='u / pixel',ylabel='v / pixel',title=f'3484: {len(points)} far candidates on 6-pixel grid')
camera_points=rays[::6,::6][keep]*depths[:,None]
sc=axes[1].scatter(camera_points[:,0],camera_points[:,2],c=ys,s=4,cmap='viridis');axes[1].set(xlabel='camera x / m',ylabel='camera z / m',title='Back-projection of the SAME saved depth');fig.colorbar(sc,ax=axes[1],label='v / pixel')
fig.tight_layout();fig.savefig(out/'far-candidates.png',dpi=180);plt.close(fig)
manifest=[]
for f in [src/'frames/003484.jpg',src/'masks/003484.png',src/'depth/003484.npz',src/'poses.npz',src/'cam.json']:
    manifest.append(dict(source='/home/yjl/crack/city8827/work/'+f.relative_to(src).as_posix(),sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
(out/'provenance.json').write_text(json.dumps(dict(kind='saved inputs and CPU diagnostics',files=manifest),ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
