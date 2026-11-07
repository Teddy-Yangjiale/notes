"""48 new native PowerPoint diagrams for the v2 derivation workshops."""
from pathlib import Path
import math, json, runpy, subprocess, sys

ROOT=Path(__file__).resolve().parents[1]
ns=runpy.run_path(str(ROOT/'scripts/cs184-course/figures.py'))
Canvas=ns['Canvas']; T=ns['TEAL']; O=ns['ORANGE']; P=ns['PURPLE']; G=ns['GRAY']; R=ns['RED']


def label(c,text,x,y,w=2.8,color=G): c.text(text,x,y,w,.38,color=color,size=12)
def arrow(c,a,b,color=T): c.line(a,b,color,arrow='end',width=1.2)
def circle(c,x,y,r,color=T): c.box(x-r,y-r,2*r,2*r,color=color,shape='ellipse')
def grid(c,x,y,values,cell=.42):
    for j,row in enumerate(values):
        for i,value in enumerate(row):
            c.box(x+i*cell,y+j*cell,cell,cell,str(value),G,size=11)
def curve(c,points,color=T): c.path(points,color,1.25)
def bars(c,values,labels,maximum=None):
    maximum=maximum or max(values)
    for i,(v,name) in enumerate(zip(values,labels)):
        x=.45+i*(6.25/len(values)); width=min(1.1,5/len(values))
        h=1.4*v/maximum
        c.box(x,2.05-h,width,max(.012,h),color=[T,O,P,R][i%4],fill=[T,O,P,R][i%4])
        label(c,str(round(v,4)),x-.12,.15,width+.24)
        label(c,name,x-.35,2.27,width+.7)
def field(c,x,mode):
    for i in (-1,0,1):
        for j in (-1,0,1):
            if i==j==0:continue
            px=x+1.2+i*.65;py=1.35+j*.55
            dx,dy=(i,j) if mode=='radial' else (-j,i)
            arrow(c,[px,py],[px+.23*dx,py+.23*dy],T if mode=='radial' else O)
def spectrum(c,x,values,color):
    for i,v in enumerate(values):
        c.box(x+i*.36,1.9-v*.75,.23,max(.012,v*.75),color=color,fill=color)
def ray_lens(c,x):
    c.line([x, .5],[x,2.3],G)
    c.line([.5,1.4],[6.6,1.4],G,dash='dash')


def draw(key,j):
    c=Canvas()
    if key=='01':
        if j==1:
            grid(c,.5,.6,[['','','',''],['','','','']],.48)
            c.dot(.74,.84,O,.05);label(c,'(i+½, j+½)',.35,1.9,2.4)
            origin=[4.2,1.4];c.dot(*origin,T,.05)
            c.line([6.1,.6],[6.1,2.2],G)
            arrow(c,origin,[6.1,.9],O);arrow(c,origin,[6.1,1.9],T)
            label(c,'相机原点',3.2,2.3,2);label(c,'像平面',5.2,2.3,1.6)
        elif j==2:
            A=[.8,2.1];B=[5.5,2.1];C=[.8,.5];p=[1.975,1.7]
            curve(c,[A,B,C,A]);c.dot(*p,O,.06)
            for v in (A,B,C):c.line(p,v,O)
            label(c,'λA = ½',2.3,.65,2);label(c,'λB = ¼',.35,1.0,1.5);label(c,'λC = ¼',2,1.75,2)
            c.dot(4.7,1.0,R,.05);label(c,'越过 BC',4.5,.35,2,color=R)
        elif j==3:
            for panel,n in enumerate((1,2,4)):
                x=.45+panel*2.2; s=1.5
                c.box(x,.6,s,s,color=G)
                curve(c,[[x,.6+s*.2],[x+s*.8,2.1]],O)
                for a in range(n):
                    for b in range(n):
                        u,v=(a+.5)/n,(b+.5)/n
                        c.dot(x+s*u,2.1-s*v,T if u+v<=.8 else G,.025)
                label(c,('0 / 1','1 / 4','6 / 16')[panel],x-.2,2.3,1.9)
        else:
            for y,work in ((.6,4.5),(1.6,1.5)):
                c.box(.6,y,1.5,.5,'固定 3 s',G,size=12)
                c.box(2.1,y,work,.5,'9 s' if work>2 else '3 s',T,fill='E7F3EF',size=12)
            label(c,'总时间 12 s → 6 s',2,2.35,3.3)
    elif key=='14':
        if j==1:
            x=[.9,1.95];y=[5.9,.8]
            w=[y[0]-x[0],y[1]-x[1]];length=math.hypot(*w);w=[v/length for v in w]
            def rotate(v,a):return [v[0]*math.cos(a)-v[1]*math.sin(a),v[0]*math.sin(a)+v[1]*math.cos(a)]
            nx=rotate(w,-math.acos(.8));ny=rotate([-v for v in w],math.acos(.5))
            for point,n,col in ((x,nx,T),(y,ny,O)):
                tangent=[-n[1],n[0]]
                c.line([point[k]-.45*tangent[k] for k in (0,1)],[point[k]+.45*tangent[k] for k in (0,1)],col)
                arrow(c,point,[point[k]+.55*n[k] for k in (0,1)],col)
            c.line(x,y,G,dash='dash');label(c,'r = 2',2.6,.8,2)
            label(c,'cx = 0.8',.2,2.35,2);label(c,'cy = 0.5',4.9,2.35,2)
            label(c,'dω = cy dAy / r²',2,1.55,3)
        elif j==2:
            for i,angle in enumerate((0,30,45,60,90)):
                a=math.radians(angle);end=[3.6+2*math.sin(a),2.15-1.65*math.cos(a)]
                c.line([3.6,2.15],end,[T,O,P,G,G][i])
                label(c,f'{angle}°',end[0]-.4,max(.14,end[1]-.35),.8)
            label(c,'每带贡献 πL / 4',.3,.85,2.8)
            for i in range(4):c.box(.55+i*.5,1.6,.45,.35,color=[T,O,P,G][i],fill=[T,O,P,G][i])
        elif j==3:
            for x,height,name in ((1.7,.85,'近处：宽锥'),(5.2,.3,'远处：窄锥')):
                origin=[x,2.1];c.line([x-1,.5],[x+1,.5],O)
                curve(c,[[x-height,.5],origin,[x+height,.5]],T)
                label(c,name,x-1.4,2.35)
            label(c,'E ≤ πL',2.2,1.2,2.8)
        else:
            bars(c,[3,1.8,1.8*math.pi],['L₀','ρL₀','漏除 π'])
    elif key=='15':
        if j==1:
            bars(c,[.2,.6,1.2,1.8],['f(0.1)','f(0.3)','f(0.6)','f(0.9)'],2)
            c.line([.4,1.35],[6.6,1.35],G,dash='dash');label(c,'f / p = 1',4,.4,2.5,color=G)
        elif j==2:
            for x,inside,col in ((1.8,'½ 样本',R),(5.2,'¼ 样本',T)):
                circle(c,x,1.3,.9,G);circle(c,x,1.3,.45,col)
                label(c,inside,x-1.2,1.08,2.4,col)
                label(c,'内圆面积 = ¼',x-1.4,2.35)
        elif j==3:
            c.box(.4,.7,2.3,.8,'pA = 0.5',T,size=15)
            c.box(4.4,.7,2.3,.8,'pω = 7.5',O,size=15)
            arrow(c,[2.85,1.1],[4.2,1.1],G)
            label(c,'× r² / cy = 15',2.15,.15,2.9)
            label(c,'两条估计路线：0.213333',1.2,2,4.8)
        else:
            for y in (.8,1.8):
                for i in range(4):c.box(.6+i*1.45,y,1.45,.35,color=G)
            for x in (1.1,1.25,1.55,5.7):c.dot(x,.975,O,.05)
            for i,u in enumerate((.2,.8,.4,.6)):c.dot(.6+(i+u)*1.45,1.975,T,.05)
            label(c,'独立随机',.3,.15,2);label(c,'每层一个',.3,2.35,2)
    elif key=='16':
        if j==1:
            a=c.box(.6,.65,1.5,.7,'B₁',T,size=18);b=c.box(5,.65,1.5,.7,'B₂',O,size=18)
            arrow(c,a,b,T);c.line([5.7,1.5],[1.35,1.5],O,arrow='end')
            label(c,'一次交换 ×¼',2.2,.2,2.8)
            label(c,'往返：1 → 1/16 → 1/256',1.2,2.2,4.8)
        elif j==2:
            origin=c.box(.4,1,.9,.6,'C=4',G,size=13)
            a=c.box(4.6,.5,1.7,.6,'0',R,size=17);b=c.box(4.6,1.7,1.7,.6,'4/q = 10',T,size=14)
            arrow(c,origin,a,R);arrow(c,origin,b,T)
            label(c,'0.6 终止',2,.25,2);label(c,'0.4 存活',2,2.1,2)
        elif j==3:
            for y,wa,name in ((.7,16/21,'区域 1'),(1.6,4/19,'区域 2')):
                c.box(1.5,y,4*wa,.45,color=T,fill=T)
                c.box(1.5+4*wa,y,4*(1-wa),.45,color=O,fill=O)
                label(c,name,.15,y,1.25)
            label(c,'wA + wB = 1',2,2.3,3.2)
        else:
            c.line([.5,1.3],[6.65,1.3],G)
            for x,name,col in ((.6,'自命中',R),(2.2,'遮挡',O),(4.5,'灯',T),(6.2,'灯后',G)):
                c.dot(x,1.3,col,.055);label(c,name,x-.55,1.7,1.1,col)
            c.line([.9,.8],[4.3,.8],T,arrow='end');label(c,'有效查询区间',1.5,.25,3.4)
    elif key=='18':
        if j==1:
            c.line([.5,1.4],[6.6,1.4],G);c.line([3.5,.3],[3.5,2.4],G,dash='dash')
            arrow(c,[2.3,.35],[3.5,1.4],T);arrow(c,[3.5,1.4],[4.3,2.35],O)
            label(c,'sinθi = 0.6',.4,.3,2.5);label(c,'sinθt = 0.4',4.25,1.8,2.4)
            label(c,'ni = 1',4.4,.55,1.8);label(c,'nt = 1.5',.65,1.85,2)
        elif j==2:
            for y,factor,txt,col in ((.55,.04,'反射 4%',O),(1.55,.96,'透射 96%',T)):
                c.box(.6,y,max(.04,5*factor),.45,color=col,fill=col)
                label(c,txt,4.3,y-.4,2.1,col)
            label(c,'抽样权重 = 物理份额 / 分支概率',.6,2.3,6)
        elif j==3:
            for x,ang in ((1.4,0),(3.5,35),(5.6,60)):
                a=math.radians(ang);dx=.7*math.cos(a);dy=.7*math.sin(a)
                c.line([x-dx,1.6+dy],[x+dx,1.6-dy],T,width=2)
                arrow(c,[x,1.6],[x-.5*math.sin(a),1.6-.5*math.cos(a)],O)
                c.line([x-dx,2.2],[x+dx,2.2],P,width=3)
                label(c,f'{ang}°',x-.5,.2,1)
            label(c,'投影面积决定归一化',1.3,2.35,4.6)
        else:
            for x in (.8,3.5):c.box(x,.8,2.1,.8,color=T,fill='E7F3EF')
            arrow(c,[.3,1.2],[6.5,1.2],O)
            label(c,'e⁻⁰·⁵',.7,.25,2.2);label(c,'e⁻⁰·⁵',3.4,.25,2.2)
            label(c,'乘起来 = e⁻¹ = 0.367879',1.1,2.1,4.8)
    elif key=='19':
        if j==1:
            spectrum(c,.6,[1,1,1,0],T);spectrum(c,3.7,[0,0,0,1],O)
            label(c,'(1,1,1,0)',.3,.3,2.7);label(c,'(0,0,0,1)',3.6,.3,2.7)
            label(c,'三通道响应均为 (1,1,1)',1,2.25,5.1)
        elif j==2:
            for x,val,name in ((.7,.735357,'线性平均后编码'),(4.2,.5,'直接平均编码')):
                byte=int(255*val);fill=f'{byte:02X}'*3
                c.box(x,.6,2.1,1.2,color=G,fill=fill)
                label(c,str(round(val,6)),x,.16,2.1);label(c,name,x-.4,2.2,2.9)
        elif j==3:
            c.line([.7,2.1],[3.3,.45],T)
            c.dot(1.7,1.465,T,.055);c.dot(2.7,.83,O,.055)
            label(c,'Y=3',.35,.9,1.4);label(c,'Y=6',2.6,.18,1.3)
            arrow(c,[3.6,1.25],[4.8,1.25],G);c.dot(5.6,1.25,P,.1)
            label(c,'同一 xy',4.4,1.8,2.5)
        else:
            for x,col,name in ((.5,'FF0000','红 α=1'),(2.7,'0000FF','蓝 α=0'),(4.9,'800080','错误紫边')):
                c.box(x,.6,1.55,1,color=G,fill=col);label(c,name,x-.2,1.9,1.95)
            label(c,'透明蓝的预乘贡献为 0',1.1,2.35,4.8)
    elif key=='21':
        if j==1:
            line=[[.6+5.8*u,2.1-1.5*u] for u in [i/40 for i in range(41)]]
            ease=[[.6+5.8*u,2.1-1.5*(3*u*u-2*u**3)] for u in [i/40 for i in range(41)]]
            curve(c,line,G);curve(c,ease,T)
            label(c,'相同端点',.3,.2,2);label(c,'起停速度为零',4.2,2.3,2.6)
        elif j==2:
            circle(c,2.0,1.35,.95,G)
            curve(c,[[2+.95*math.cos(a),1.35-.95*math.sin(a)] for a in [i*math.pi/2/30 for i in range(31)]],T)
            c.line([2.95,1.35],[2,.4],O);c.dot(2.475,.875,O,.055)
            circle(c,5.35,1.35,.95,G);c.line([4.4,1.35],[6.3,1.35],R);c.dot(5.35,1.35,R,.055)
            label(c,'弧与弦',.5,2.35,2.8);label(c,'q 与 −q：平均为 0',3.85,2.35,3)
        elif j==3:
            label(c,'绑定 x=3 → 局部 1 → 当前 4',.3,.2,6.4)
            origin=[3.5,1.55];arrow(c,origin,[3.5,.8],T);arrow(c,origin,[3.5,2.3],O)
            c.dot(*origin,R,.07);label(c,'等权平均',4,1.35,2);label(c,'长度 1 → 0',.5,1.35,2.3)
        else:
            curve(c,[[.6,2.1],[1.8,2.1],[1.8,.9]],T,)
            c.dot(1.8,.9,O,.05);arrow(c,[1.8,.9],[1.35,.9],O)
            curve(c,[[4,2.1],[5.1,2.1],[6.2,2.1]],T)
            arrow(c,[6.2,2.1],[6.2,1],O);label(c,'弯曲：两方向',.3,.2,2.8);label(c,'伸直：一阶共线',3.7,.2,3)
    elif key=='24':
        if j in (1,2):
            for panel,(factor,name,col) in enumerate(((1.015,'显式增能',R),(1.,'半隐式',T),(.985,'隐式耗散',P)) if j==2 else ((1.,'精确能量圆',T),(1.02,'显式向外',R))):
                x=1.25+panel*(2.3 if j==2 else 3.7);scale=.62 if j==2 else .72
                pts=[]
                for k in range(70):
                    a=k*.14;r=scale*factor**k
                    pts.append([x+r*math.cos(a),1.35-r*math.sin(a)])
                if j==1 and panel==1:
                    pts=[[x+.4*(1.008**k)*math.cos(k*.14),1.35-.4*(1.008**k)*math.sin(k*.14)] for k in range(70)]
                if j==2:
                    state_x,state_v=1.,0.;h=.15;pts=[]
                    for _ in range(51):
                        pts.append([x+.5*state_x,1.35-.5*state_v])
                        if panel==0:state_x,state_v=state_x+h*state_v,state_v-h*state_x
                        elif panel==1:
                            state_v-=h*state_x
                            state_x+=h*state_v
                        else:state_x,state_v=(state_x+h*state_v)/(1+h*h),(state_v-h*state_x)/(1+h*h)
                curve(c,pts,col);label(c,name,x-1,2.35,2,col)
        elif j==3:
            for y,points,name in ((.75,(.6,6.0),'原长 3'),(1.65,(3.3,5.1),'目标长 1')):
                c.line([points[0],y],[points[1],y],G)
                circle(c,points[0],y,.1,T);circle(c,points[1],y,.18,O)
                label(c,name,.3,y+.2,1.6)
            label(c,'轻端移 1.5；重端移 0.5',1.5,2.35,4.5)
        else:
            bars(c,[.8,.81,.82,math.exp(-.2)],['整步','两半步','外推','精确'],1)
    elif key=='25':
        if j==1:
            grid(c,1.7,.7,[['p₀=0','p₁=2']],1.35)
            arrow(c,[2.65,.48],[3.45,.48],O)
            label(c,'u* = 2 → u = 0',2,2.25,3.6)
            label(c,'墙 u=0',.2,.2,1.7);label(c,'墙 u=0',5.1,.2,1.7)
        elif j==2:
            for y,vals in ((.55,[.5,0,.5]),(1.45,[.5,.5,.5])):grid(c,1.7,y,[vals],.85)
            label(c,'迭代 1',.2,.72,1.3);label(c,'迭代 2',.2,1.62,1.3)
            label(c,'残差决定剩余散度',2,2.35,4)
        elif j==3:
            for y,vals in ((.45,[0,1,0,0]),(1.15,[0,.5,.5,0]),(1.85,[0,.25,.5,.25])):grid(c,2,y,[vals],.55)
            for y,name in ((.45,'初值'),(1.15,'半格'),(1.85,'再半格')):label(c,name,.5,y,1.3)
        else:
            field(c,.3,'radial');field(c,3.7,'rotational')
            label(c,'散度非零',.4,2.35,2.8);label(c,'旋度非零，散度零',3.6,2.35,3)
    elif key=='26':
        if j==1:
            eye1=[1,2.1];eye2=[2.1,2.1]
            for p,col in (([1.55,1.3],O),([1.55,.4],T)):
                c.line(eye1,p,col);c.line(eye2,p,col)
            label(c,'固定基线 B',.3,2.35,2.8)
            bars_x=[4.3,5.6]
            for x,v,name in zip(bars_x,[30,6],['近 d=30','远 d=6']):
                c.box(x,2.1-v/20,.65,v/20,color=T,fill=T);label(c,name,x-.55,2.35,1.75)
        elif j==2:
            c.line([.8,1.3],[6.3,1.3],G)
            for x,name,col in ((1.3,'−100 px',O),(4.9,'−10 px',T),(5.3,'旧中心',G)):
                c.dot(x,1.3,col,.055)
                label(c,name,x-.8,.55 if name!='旧中心' else 1.9,1.6,col)
            arrow(c,[5.3,1.3],[1.3,1.3],O)
            label(c,'同一旧方向，不同深度',1.1,2.35,4.8)
        elif j==3:
            for y,extra in ((.65,False),(1.65,True)):
                x=.5
                for duration,name,col in ((2,'追踪',T),(6,'渲染',O),(4,'等待',G),(5,'扫描',P)):
                    w=duration*.17;c.box(x,y,w,.45,color=col,fill=col);x+=w
                if extra:c.box(x,y,1.89,.45,color=R,fill=R)
            label(c,'追踪 2 / 渲染 6 / 等待 4 / 扫描 5 ms',.3,.15,6.4)
            label(c,'额外排队一帧',3.35,2.25,3)
        else:
            c.box(.7,.75,1,1,color=T);c.box(4.2,.45,1.6,1.2,color=O)
            arrow(c,[2,1.2],[3.8,1.2],G)
            label(c,'源小格',.3,2.1,2);label(c,'径向 ×1.6',3.9,1.85,2.4);label(c,'切向 ×1.2',3.9,2.3,2.4)
    elif key=='90':
        if j==1:
            for i,ratio in enumerate((.5,.5,2/3)):
                x=.6+2.2*i;height=1.4 if i==1 else .7
                c.box(x,1.95-height,.35,height,color=T,fill=T)
                c.box(x+.65,1.95-height*ratio,.35,height*ratio,color=O,fill=O)
                label(c,('50 mm','100 mm','后退 + 100 mm')[i],x-.35,2.3,2)
        elif j==2:
            c.line([2,.5],[2,2.3],G);c.line([5.4,.5],[5.4,2.3],P)
            curve(c,[[2,.55],[6,1.4],[2,2.25]],T)
            curve(c,[[2,.55],[5.4,1.4],[2,2.25]],O)
            c.line([5.4,1.2725],[5.4,1.5275],R,width=3)
            label(c,'孔径 D',.8,2.35,2);label(c,'传感器',4.3,2.35,2);label(c,'近物像点',5.7,.2,1.3)
        elif j==3:
            c.line([.7,1.4],[6.5,1.4],G)
            for x,txt,col in ((1.1,'近 1.829 m',T),(3.45,'焦点 2 m',G),(6.1,'远 2.207 m',O)):
                c.dot(x,1.4,col,.06);label(c,txt,x-1,1.85,2,col)
            label(c,'两个边界：c = 0.03 mm',1.3,.4,4.6)
        else:
            for x,sigma,name,col in ((1.9,.3,'更多光：σ=20',T),(5.2,.6,'增益：σ=40',O)):
                pts=[[x+t,2.1-1.5*math.exp(-t*t/(2*sigma*sigma))] for t in [(-1.2+i*.04) for i in range(61)]]
                curve(c,pts,col);label(c,name,x-1.5,2.35,3,col)
            label(c,'相同输出均值 400',2,.15,3.3)
    elif key=='91':
        if j==1:
            for y,vals,name in ((.5,[0,10,10],'补零'),(1.4,[10,10,10],'复制')):
                grid(c,1.7,y,[vals],.65);label(c,name,.35,y+.1,1.1)
                label(c,'→ 7.5' if vals[0]==0 else '→ 10',4.2,y+.1,2)
        elif j==2:
            grid(c,.4,.65,[[-1,0,1],[-2,0,2],[-1,0,1]],.48)
            label(c,'=',2.1,1, .5)
            grid(c,3,.65,[[1],[2],[1]],.48);grid(c,4.7,1.13,[[-1,0,1]],.48)
            label(c,'外积',3.6,1.03,.9);label(c,'平滑 × 差分',2.9,2.35,3.4)
        elif j==3:
            for x,v,txt in ((.8,.303265,'0.3033'),(2.9,1.,'1'),(5,.303265,'0.3033')):
                c.box(x,2-v,1,v,color=T,fill=T);label(c,txt,x-.3,.2,1.6)
            label(c,'除以总和 1.606531',1.7,2.35,3.8)
        else:
            grid(c,.5,.7,[[50,50],[50,70]],.62)
            grid(c,3,.7,[[110,-10],[-10,10]],.62)
            grid(c,5.4,.7,[[48,48],[48,80]],.62)
            arrow(c,[1.9,1.3],[2.8,1.3],T);arrow(c,[4.4,1.3],[5.2,1.3],O)
            label(c,'DCT',1.7,.2,1.3);label(c,'量化后逆变换',4.3,2.2,2.6)
    return c


def main():
    draw_root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(r'D:\Draw')
    courses=runpy.run_path(str(ROOT/'scripts/cs184-complete-course.py'))['load']()
    data=runpy.run_path(str(ROOT/'scripts/cs184-v2-content.py'))['DATA']
    tasks=[]
    for course in courses:
        key=course['key']
        for j,lab in enumerate(data[key],1):
            folder=ROOT/'.work/cs184/editable'/key; folder.mkdir(parents=True,exist_ok=True)
            name=f'd{20+j:02d}-workshop'; pptx=folder/(name+'.pptx');ops=folder/(name+'.json')
            spec=draw(key,j).doc(lab['caption'])
            ops.write_text(json.dumps(spec,ensure_ascii=False,indent=2),encoding='utf8')
            if not pptx.exists():
                for args in (['new',str(pptx),'--size','7.16x2.85'],['apply',str(pptx),str(ops)]):
                    result=subprocess.run([sys.executable,'-m','pptdraw',*args],cwd=draw_root,capture_output=True)
                    if result.returncode:raise RuntimeError(result.stdout.decode('utf8','replace')+result.stderr.decode('utf8','replace'))
            tasks.append({'pptx':str(pptx),'png':str(ROOT/'src/content/notes'/course['slug']/'diagrams'/(name+'.png'))})
        print(key,'4 new diagrams ready',flush=True)
    (ROOT/'.work/cs184/v2-render-tasks.json').write_text(json.dumps(tasks,ensure_ascii=False),encoding='utf8')


if __name__=='__main__':main()
