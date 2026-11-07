"""Editable geometric explanations for targeted L02-L13 revision (pptdraw)."""
from pathlib import Path
import json,math,os,runpy,subprocess,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]
Canvas=runpy.run_path(str(ROOT/'scripts/cs184-course/figures.py'))['Canvas']
course=runpy.run_path(str(ROOT/'scripts/cs184-foundations-v2.py'))
T='0F766E';O='B45309';P='5B21B6';G='5B6B7C';R='B91C1C'

def label(c,s,x,y,w=2,col=G):c.text(s,x,min(y,2.35),w,.34,color=col,size=11)
def arrow(c,a,b,col=T):c.line(a,b,col,arrow='end',width=1.2)
def poly(c,pts,col=T):c.path(pts+[pts[0]],col,width=1.2)
def curve(c,pts,col=T):c.path(pts,col,width=1.2)
def bar(c,x,value,scale=1,base=2.05,col=T,w=.5):
    height=abs(value)*scale
    if height:c.box(x,base-height if value>=0 else base,w,height,color=col,fill=col)

def draw(key,j):
    c=Canvas()
    if key=='02':
        if j==1:
            ox,oy,s=.5,.4,.45
            for i in range(5):
                c.line([ox+i*s,oy],[ox+i*s,oy+4*s],G,width=.5)
                c.line([ox,oy+i*s],[ox+4*s,oy+i*s],G,width=.5)
            c.line([ox+4*s,oy],[ox,oy+4*s],O,width=2)
            for y in range(4):
                for x in range(4):c.dot(ox+(x+.5)*s,oy+(y+.5)*s,T if x+y<3 else P,.045)
            label(c,'A：6 点',3,.55,2,T);label(c,'B：10 点',3,1.15,2,P)
            label(c,'共享边上的 4 点归 B',3,1.9,3.5)
            label(c,'y 向下；中心采样',.4,2.35,2.5)
        elif j==2:
            for x0,vals,col in ((.6,[12,8,8,4],T),(4.1,[-4,-8,-8,-12],R)):
                c.box(x0,.6,1.5,1.2,color=col)
                for k,value in enumerate(vals):
                    x=x0+(k%2)*1.5;y=.6+(k//2)*1.2
                    c.dot(x,y,col,.04)
                    label(c,str(value),x-.4,y-.36 if k<2 else y+.1,.8,col)
                label(c,'整块为正' if vals[0]>0 else '整块为负',x0-.15,2.35,1.8,col)
            label(c,'E = 16 − 4x − 4y',2.15,1.05,2.5)
        else:
            ox,oy,size=.55,.35,1.9
            c.box(ox,oy,size,size,color=G)
            poly(c,[[ox,oy+size],[ox+.99*size,oy+size],[ox,oy+.01*size]],T)
            for y in (.25,.75):
                for x in (.25,.75):c.dot(ox+x*size,oy+(1-y)*size,O if x+y<.99 else G,.05)
            for x,val,txt,col in ((3.15,.49005,'面积',T),(4.45,.25,'四点采样',O),(5.75,.5,'最近档位',P)):
                bar(c,x,val,2.7,col=col);label(c,str(val),x-.3,.25,1.1,col);label(c,txt,x-.4,2.3,1.3)
    elif key=='03':
        if j==1:
            for freq,col in ((7,O),(1,T)):
                curve(c,[[.4+6*i/160,1.45-.8*math.cos(2*math.pi*freq*i/160)] for i in range(161)],col)
            for i in range(8):c.dot(.4+6*i/8,1.45-.8*math.cos(2*math.pi*i/8),P,.05)
            label(c,'1 Hz',.8,.15,1,T);label(c,'7 Hz',3,.15,1,O);label(c,'fs = 8',5,.15,1.5,P)
            label(c,'相同样本点，不同连续波形',1.8,2.4,3.5)
        elif j==2:
            for start,f in ((.6,.5),(4.,1.5)):
                sinc=math.sin(math.pi*f)/(math.pi*f)
                vals=[sinc,sinc*sinc,math.exp(-.5*math.pi**2*f*f)]
                c.line([start-.1,1.7],[start+2.5,1.7],G,width=.6)
                for k,(v,col,name) in enumerate(zip(vals,(T,O,P),('box','tent','Gauss'))):
                    x=start+.85*k;bar(c,x,v,1.3,1.7,col,.43)
                    label(c,f'{v:.3g}',x-.18,.5,.85,col);label(c,name,x-.18,2.35,.9)
                label(c,f'f = {f}',start+.3,.15,1.7)
        else:
            for i,n in enumerate((4,16,64)):
                x=.65+1.8*i
                bar(c,x,.24/n,6,col=T,w=.5);bar(c,x+.55,.24,6,col=O,w=.5)
                label(c,f'N={n}',x-.1,2.3,1.3)
            label(c,'独立：0.24 / N',.5,.15,2.7,T);label(c,'复用：0.24',3.8,.15,2.3,O)
    elif key=='04':
        if j==1:
            origin=[.7,2.3];camera=[2.05,1.4];point=[2.5,.5]
            arrow(c,origin,[1.5,2.3],G);arrow(c,origin,[.7,1.5],G)
            arrow(c,camera,[2.05,.7],T);arrow(c,camera,[1.35,1.4],O)
            c.dot(*camera,P);c.dot(*point,R);c.line(camera,point,P,dash='dash')
            label(c,'世界原点',.15,2.4,1.7);label(c,'c=(3,2)',1.4,1.8,1.7,P)
            label(c,'p=(4,4)',4.5,.5,1.8,R);label(c,'p−c=(1,2)',4.5,1.25,2)
            label(c,'Rᵀ(p−c)=(2,−1)',4.15,2.15,2.8,T)
        elif j==2:
            for y,end,mid,txt in ((.8,6.4,2.,'原线段 t=0.25'),(1.9,6.4,2.88,'屏幕线段 s=0.4')):
                c.line([.6,y],[end,y],G);c.dot(.6,y,G);c.dot(end,y,G);c.dot(mid,y,O,.055)
                label(c,txt,2.5,y-.5,3.1)
            label(c,'u = 0.25',.9,2.35,2,T);label(c,'不能直接用 s 插值 u',3.5,2.35,3)
        else:
            for x,s,v,col in ((1.2,50,.001489967,T),(4.9,500,.1489967,O)):
                bar(c,x,v,10,col=col,w=.8)
                label(c,f'{s} m',x-.45,2.35,1.7,col)
                label(c,f'{v*1000:.2f} mm / 档',x-.8,.25,2.4,col)
            label(c,'距离 ×10 → 局部间隔约 ×100',1.6,.8,4)
    elif key=='06':
        if j==1:
            cx,cy=3.4,1.4;scale=.38
            pts=[]
            for i in range(65):
                t=2*math.pi*i/64;x,y=4*math.cos(t)+3*math.sin(t),math.sin(t)
                pts.append([cx+scale*x,cy-scale*y])
            curve(c,pts,T);arrow(c,[cx,cy],[cx+4*scale,cy],O);arrow(c,[cx,cy],[cx+3*scale,cy-scale],P)
            label(c,'Jx=(4,0)',4.45,1.7,2,O);label(c,'Jy=(3,1)',4.45,.5,2,P)
            label(c,'σmax≈5.0368；σmin≈0.7942',1.3,2.35,4.5,T)
            label(c,'texel / pixel',.35,.25,2)
        elif j==2:
            curve(c,[[.65+5.7*i/70,2.1-1.5*(i/70)/(4-3*i/70)] for i in range(71)],T)
            for s,val in ((0,2.56),(.5,6.5536),(1,40.96)):
                c.dot(.65+5.7*s,2.1-1.5*s/(4-3*s),O,.045)
                label(c,str(val),.15+5.4*s,.22,1.5,O)
            label(c,'局部梯度：texel / pixel',1.7,2.4,3.7)
        else:
            for i,col in enumerate((R,R,P,P)):
                c.box(.7+i*1.35,.85,1.35,.9,color=col,fill='FDE8E8' if i<2 else 'EDE9FE')
                c.dot(.7+(i+.5)*1.35,1.3,col,.045)
                label(c,str((i+.5)/4),.7+i*1.35,1.95,1.35,col)
            c.line([3.4,.45],[3.4,2.15],O,width=2)
            label(c,'子图边界 u=0.5',2,.15,2.8,O)
            label(c,'红色中心 0.375',.55,2.45,2.4,R);label(c,'边界处 50% 红 + 50% 蓝',3.6,2.45,3.3,P)
    elif key=='08':
        if j==1:
            left=c.box(.35,.65,1.6,.85,'端点 clip\nz / w',color=G)
            top=c.box(2.7,.2,1.9,.8,'恢复齐次位置\n再除 w',color=T)
            bottom=c.box(2.7,1.5,1.9,.8,'端点 NDC\n屏幕线性插值',color=O)
            dest=c.box(5.35,.8,1.45,.8,'z_ndc = 0',color=P)
            c.line(left,top,G,arrow='end');c.line(left,bottom,G,arrow='end');c.line(top,dest,T,arrow='end');c.line(bottom,dest,O,arrow='end')
            label(c,'再次透视校正会错误得到 −0.3',1.4,2.45,4.5,R)
        elif j==2:
            origin=[3.5,2.15]
            arrow(c,origin,[3.5-1.9*math.sqrt(3)/2,1.2],T);arrow(c,origin,[3.5+1.9*math.sqrt(3)/2,1.2],T)
            arrow(c,origin,[3.5,1.2],O);arrow(c,origin,[3.5,.25],P)
            label(c,'n0',1.1,.8,1,T);label(c,'n1',5.25,.8,1,T)
            label(c,'平均长度 0.5',4,1.65,2.1,O);label(c,'归一化后长度 1',.25,.2,2.8,P)
            label(c,'端点高光 1/65536 → 中点高光 1',1,2.45,5)
        else:
            for i,d in enumerate((.3,.4,.6,.9)):
                x=.45+1.18*i
                c.box(x,.75,1,.7,str(d),color=G)
                c.box(x,1.7,1,.55,'0' if d<.5 else '1',color=R if d<.5 else T)
            label(c,'接收深度 0.5',.55,.2,2.5)
            label(c,'先比较',5.25,.75,1.5);label(c,'再平均 = 0.5',4.9,1.7,2,T)
            label(c,'比较平均深度 0.55 → 1（不同结果）',.7,2.45,5.9,R)
    elif key=='10':
        if j==1:
            for x,name,col in ((.7,'A2',T),(3.3,'接缝',G),(4.6,'B1',O),(6.22,'B2',P)):
                c.dot(x,1.35,col,.055);label(c,name,x-.45,1.65,.9,col)
            c.line([.7,1.35],[6.22,1.35],G,width=.7)
            label(c,'2 秒：柄长 2',.4,.5,2.6,T);label(c,'1 秒：柄长 1',3.65,.5,2.6,O)
            label(c,'速度均为 3；加速度均为 1.5',1.25,2.35,4.8)
        elif j==2:
            c.line([.6,1.5],[6.4,1.5],G,width=.7)
            c.line([.6,1.5],[1.18,1.5],T,width=5)
            for x,txt,col in ((.6,'0',T),(1.18,'1',T),(3.645,'5.25',O),(6.4,'10',P)):
                c.dot(x,1.5,col,.05);label(c,txt,x-.22,1.8,.44,col)
            label(c,'短弦 [0,1]',.3,.7,1.8,T);label(c,'曲线中点',2.65,.7,2,O);label(c,'控制点',5.1,.7,1.8,P)
            label(c,'到直线为 0；到线段为 4.25',1.3,2.4,4.7)
        else:
            scale=1.65;ox=2.5;oy=2.2
            poly(c,[[ox+scale,oy],[ox+scale,oy-scale],[ox,oy-scale]],G)
            for rational,col in ((True,T),(False,O)):
                pts=[]
                for i in range(51):
                    t=i/50;b=[(1-t)**2,2*t*(1-t),t*t];w=[1,math.sqrt(.5) if rational else 1,1];den=sum(a*v for a,v in zip(b,w))
                    x=(b[0]+b[1]*w[1])/den;y=(b[1]*w[1]+b[2])/den
                    pts.append([ox+scale*x,oy-scale*y])
                curve(c,pts,col)
            label(c,'有理：圆上',.25,.4,2.1,T);label(c,'等权：向外鼓',4.8,.4,2.1,O)
            label(c,'中间权重 √2/2',2.05,2.45,3)
    elif key=='11':
        if j==1:
            for k in range(3):
                x=.4+2.3*k;y=.6;s=1.4
                poly(c,[[x,y],[x+s,y],[x+s,y+s],[x,y+s]],G)
                if k==0:c.line([x+s,y],[x,y+s],T,width=2)
                else:
                    c.line([x,y],[x+s,y+s],O if k==1 else R,width=2)
                    arrow(c,[x+.25,y+.15],[x+.95,y+.85],T)
                    arrow(c,[x+1.15,y+1.25],[x+.45,y+.55],P) if k==1 else arrow(c,[x+.2,y+.4],[x+.9,y+1.1],R)
                label(c,('原对角线','反向配对','同向：错误')[k],x-.15,2.35,1.9)
            label(c,'三者 χ 均为 1',2.1,.15,3)
        elif j==2:
            # x-y section; z is unconstrained, explicitly noted.
            ox,oy=1.2,2.15;scale=.75
            for radius in (.5,1,1.5,2):
                curve(c,[[ox+scale*radius*math.cos(i*math.pi/40),oy-scale*radius*math.sin(i*math.pi/40)] for i in range(21)],G)
            c.line([ox+scale,oy],[ox,oy-2*scale],T,width=2)
            for xx,yy,name,col in ((.8,.4,'最优 t=0.2',O),(.5,1,'中点 t=0.5',P)):
                c.dot(ox+scale*xx,oy-scale*yy,col,.05)
                label(c,name,3.3,.6 if col==O else 1.35,2.8,col)
            label(c,'x-y 截面；z 方向没有约束',1.2,2.45,4.7)
        else:
            for x,txt,col in ((.5,'旧数组',G),(2.8,'同时计算',T),(5.1,'新数组',P)):
                name=c.box(x,.5,1.55,.8,txt,color=col)
                if x>.5:c.line(last,name,G,arrow='end')
                last=name
            label(c,'每个旧顶点 → 原位置的 1/4',1.3,1.6,4.8,T)
            label(c,'原地写回：结果依赖遍历顺序',1.2,2.35,4.8,R)
    elif key=='13':
        if j==1:
            ox,oy,s=.6,2.15,1.65
            poly(c,[[ox,oy],[ox+s,oy],[ox,oy-s]],T)
            c.dot(ox+.2*s,oy-.3*s,O,.05)
            label(c,'u=0.2，v=0.3',2.6,.45,3,O)
            label(c,'d=(0,0,2)，t=1',2.6,1.15,3)
            label(c,'距离=2；两种回代交点相同',2.4,1.9,4)
            label(c,'A',.3,2.3,.6);label(c,'B',2.25,2.3,.6);label(c,'C',.3,.15,.6)
        elif j==2:
            for y,lo,hi,name,col in ((.55,1,2,'x',T),(1.25,0,1,'y',O),(2.05,1,1,'交集',P)):
                c.line([1.2,y],[5.6,y],G,width=.5)
                c.line([1.2+2.2*lo,y],[1.2+2.2*hi,y],col,width=3)
                c.dot(1.2+2.2*lo,y,col,.05);c.dot(1.2+2.2*hi,y,col,.05)
                label(c,name,.2,y-.15,.8,col)
            label(c,'0',.8,2.45,.8);label(c,'1：相切仍保留',2.8,2.45,2.2,P);label(c,'2',5.25,2.45,.8)
        else:
            for x,val,name,col in ((.7,800,'叶子',G),(2.5,481,'A',O),(4.3,377,'B',T)):
                bar(c,x,val,1.4/800,base=2.2,col=col,w=.8)
                label(c,str(val),x-.1,.15,1,col);label(c,name,x-.2,2.35,1.2)
            label(c,'Ct = 1',5.55,.75,1.3);label(c,'Ci = 8',5.55,1.3,1.3)
            label(c,'同一代价单位',4.9,1.9,2.1)
    return c

def package():
    out=ROOT/'public/cs184/figures';out.mkdir(parents=True,exist_ok=True)
    for key in course['COURSES']:
        folder=ROOT/'.work/cs184-foundations/editable'/key
        slides=sorted(folder.glob('*.pptx'));assert len(slides)==3,(key,len(slides))
        with zipfile.ZipFile(out/f'foundations-{key}-editable.zip','w',zipfile.ZIP_DEFLATED) as z:
            for p in slides:
                z.write(p,p.name);z.write(p.with_suffix('.json'),p.with_suffix('.json').name)
            z.writestr('README.txt','Three original teaching figures added in the foundations v2 revision.\nPPTX contains editable native shapes; JSON contains pptdraw operations.\nThis package does not include the older matplotlib diagrams or Berkeley slides.\n')
    print('8 archives packaged: 3 PPTX + 3 JSON each')

def main():
    if '--package' in sys.argv:
        package();return
    draw_root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(r'D:\Draw')
    out=ROOT/'.work/cs184-foundations';tasks=[]
    env=dict(os.environ,PYTHONIOENCODING='utf-8')
    for key,items in course['DATA'].items():
        folder=out/'editable'/key;folder.mkdir(parents=True,exist_ok=True)
        for j,item in enumerate(items,1):
            name=f'd{22+j}-v2';ppt=folder/(name+'.pptx');spec=folder/(name+'.json')
            spec.write_text(json.dumps(draw(key,j).doc(item['caption']),ensure_ascii=False,indent=2),encoding='utf8')
            if not ppt.exists():
                for args in (['new',str(ppt),'--size','7.16x2.85'],['apply',str(ppt),str(spec)]):
                    r=subprocess.run([sys.executable,'-m','pptdraw',*args],cwd=draw_root,env=env,capture_output=True)
                    assert r.returncode==0,r.stderr
            tasks.append(dict(pptx=str(ppt),png=str(ROOT/'src/content/notes'/course['COURSES'][key][0]/'diagrams'/(name+'.png'))))
        print(key,'3 editable figures ready',flush=True)
    (out/'render-tasks.json').write_text(json.dumps(tasks),encoding='utf8')

if __name__=='__main__':main()
