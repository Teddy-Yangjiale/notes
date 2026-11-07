"""Native PowerPoint geometry specs; captions stay outside the figure."""
import math
import random

TEAL='0F766E'; ORANGE='B45309'; PURPLE='5B21B6'; GRAY='5B6B7C'; RED='B91C1C'

class Canvas:
    def __init__(self): self.ops=[]
    def name(self): return f'fig.o{len(self.ops):03d}'
    def text(self,text,x,y,w=2,h=.38,color=GRAY,size=12):
        self.ops.append(dict(op='add_text',name=self.name(),text=text,x=x,y=max(.14,y),w=w,h=h,font_size=size,text_color=color,align='center',anchor='middle'))
    def box(self,x,y,w,h,text='',color=TEAL,fill='FFFFFF',shape='rect',size=12):
        name=self.name(); self.ops.append(dict(op='add_shape',name=name,shape=shape,x=x,y=y,w=w,h=h,text=text,fill=fill,line=color,text_color=color,font_size=size,align='center',anchor='middle'));return name
    def line(self,a,b,color=TEAL,arrow='none',width=1.5,dash='solid'):
        self.ops.append(dict(op='add_connector',name=self.name(),**{'from':a,'to':b},color=color,arrow=arrow,line_width=width,dash=dash))
    def dot(self,x,y,color=ORANGE,r=.035): self.box(x-r,y-r,2*r,2*r,color=color,fill=color,shape='ellipse')
    def path(self,points,color=TEAL,width=1.5):
        for a,b in zip(points,points[1:]): self.line(a,b,color,width=width)
    def doc(self,caption):
        return dict(slide=1,profile='paper-sans',ops=self.ops+[dict(op='set_caption',text=caption)])

def chain(labels, caption):
    c=Canvas()
    for i,label in enumerate(labels):
        x=.28+i*2.25
        # A short relation, not a fake depiction of an image tensor.
        c.text(str(i+1),x,.40,1.95,.36,color=[TEAL,ORANGE,PURPLE][i],size=14)
        name=c.box(x,1.02,1.95,1.05,label,color=[TEAL,ORANGE,PURPLE][i],size=13)
        if i: c.line(last,name,color=GRAY,arrow='end')
        last=name
    return c.doc(caption)

def geom(kind, labels, args, caption):
    c=Canvas(); rng=random.Random(184)
    if kind=='bars':
        vals=args; maximum=max(vals)
        for i,v in enumerate(vals):
            x=.55+i*2.1
            height=max(.006,1.5*v/maximum)
            c.box(x,2.15-height,1.1,height,color=[TEAL,ORANGE,PURPLE][i%3],fill=[TEAL,ORANGE,PURPLE][i%3])
            c.text(str(v),x-.1,2.20,1.3,.3,size=12)
            c.text(labels[i],x-.35,.15,1.8,.4,size=11)
    elif kind=='curve':
        name=args[0]; c.line([.7,2.2],[6.5,2.2],GRAY);c.line([.7,2.2],[.7,.4],GRAY)
        fun={'gamma':lambda x:x**2.2,'fresnel':lambda x:.04+.96*(1-x)**5,
             'sqrt':lambda x:math.sqrt(x),'tone':lambda x:5*x/(1+5*x),
             'square':lambda x:x*x,'inverse':lambda x:1/(1+4*x)**2,
             'exp':lambda x:math.exp(-3*x),'ease':lambda x:x*x*(3-2*x)}[name]
        c.path([[.7+5.7*i/50,2.2-1.65*fun(i/50)] for i in range(51)])
        c.text(labels[0],4.8,2.36,1.9,.3,size=11);c.text(labels[1],.15,.03,2.5,.3,size=11)
        c.text(labels[2],2.2,.35,3.5,.4,color=ORANGE,size=12)
    elif kind in ('samples','disk'):
        for panel in range(2):
            cx=1.8+panel*3.5;cy=1.35
            if kind=='samples':
                c.box(cx-1,cy-.8,2,1.6,color=GRAY)
                for j in range(5):
                    for i in range(6):
                        if panel==0: x=(i+.5)/6;y=(j+.5)/5
                        else: x=(i+rng.random())/6;y=(j+rng.random())/5
                        c.dot(cx-1+2*x,cy-.8+1.6*y,TEAL if panel==0 else ORANGE)
            else:
                c.box(cx-.8,cy-.8,1.6,1.6,color=GRAY,shape='ellipse')
                for j in range(80):
                    u=rng.random();r=(u if panel==0 else math.sqrt(u))*.77;phi=2*math.pi*rng.random()
                    c.dot(cx+r*math.cos(phi),cy+r*math.sin(phi),TEAL if panel==0 else ORANGE,r=.018)
            c.text(labels[panel],cx-1.4,2.35,2.8,.4,size=12)
    elif kind in ('triangle','gamut'):
        pts=[[1,2.1],[5.8,2.1],[2.3,.45]]
        c.path(pts+[pts[0]],TEAL,2)
        for p,label in zip(pts,labels[:3]): c.dot(*p);c.text(label,p[0]-.45,p[1]+.08 if p[1]>1 else .05,.9,.32,size=11)
        if kind=='triangle':
            c.line([2.3,.45],[2.3,2.1],GRAY,dash='dash');c.text('h',2.4,1.1,.5,.3)
            c.dot(2.3,1,ORANGE);c.line([2.3,.58],[2.3,.9],ORANGE,arrow='end')
        else:
            c.dot(2.8,1.4,ORANGE,r=.065);c.text(labels[3],3.0,1.2,2,.35,color=ORANGE)
            c.dot(5.7,.6,RED,r=.065);c.text(labels[4],5,.85,1.7,.4,color=RED)
    elif kind=='pixels':
        for j in range(4):
            for i in range(6):
                col=f'{int(255*i/5):02X}{int(255*j/3):02X}00'
                c.box(.7+i*.55,.3+j*.48,.55,.48,color='FFFFFF',fill=col)
        c.text(labels[0],4.1,.45,2.6,.5);c.text(labels[1],4.1,1.5,2.6,.5,color=ORANGE)
    elif kind=='coverage':
        for panel in range(2):
            x=.7+panel*3.3;c.box(x,.4,1.8,1.8,color=GRAY)
            c.line([x,.7],[x+1.8,1.7],TEAL,width=2)
            coords=[(.9,.9)] if panel==0 else[(.45,.45),(1.35,.45),(.45,1.35),(1.35,1.35)]
            for a,b in coords:c.dot(x+a,.4+b,ORANGE,r=.055)
            c.text(labels[panel],x-.35,2.35,2.5,.35,size=12)
    elif kind in ('rays','reflection','refraction','solidangle'):
        p=[3.5,2.05];c.line([.7,2.05],[6.4,2.05],GRAY,width=2)
        c.line(p,[3.5,.35],GRAY,dash='dash');c.text('n',3.6,.35,.3,.3)
        if kind=='solidangle':
            c.line(p,[1.2,.55]);c.line(p,[2.8,.55]);c.line([1.2,.55],[2.8,.55],ORANGE,width=4)
            c.text(labels[0],.6,.02,2.8,.4);c.text(labels[1],4.1,1,2.5,.45)
        else:
            if kind=='reflection' and not args:c.line(p,[1.2,.55],TEAL,arrow='end')
            else:c.line([1.2,.55],p,TEAL,arrow='end')
            if kind!='rays':c.line(p,[5.8,.55],ORANGE,arrow='end')
            c.text(labels[0],.45,.06,2.5,.4);c.text(labels[1],4.3,.06,2.5,.4,color=ORANGE)
            if kind=='refraction':
                c.line(p,[4.3,2.57],PURPLE,arrow='end');c.text(labels[2],4.6,2.3,2,.35,color=PURPLE)
            elif len(labels)>2:c.text(labels[2],2.0,2.28,3,.38,size=11)
    elif kind=='path':
        pts=[[.6,1.9],[2.2,.7],[3.8,2.0],[6,.65]]
        for i,p in enumerate(pts):
            c.dot(*p,color=TEAL if i<3 else ORANGE,r=.07)
            c.text(labels[i],p[0]-.5,p[1]+.18 if p[1]>1 else p[1]-.5,1.2,.4,size=11)
        for a,b in zip(pts,pts[1:]):c.line(a,b,TEAL,arrow='end')
        if args and args[0]=='direct':c.line(pts[1],pts[3],ORANGE,arrow='end',dash='dash')
    elif kind=='tree':
        root=c.box(.4,1,1.4,.65,labels[0],size=12)
        a=c.box(3,.35,1.7,.65,labels[1],color=TEAL,size=12);b=c.box(3,1.75,1.7,.65,labels[2],color=GRAY,size=12)
        c.line(root,a,TEAL,arrow='end');c.line(root,b,GRAY,arrow='end')
        c.text(labels[3],5,.4,1.8,.55,color=TEAL);c.text(labels[4],5,1.8,1.8,.55)
    elif kind=='normals':
        c.line([.5,1.8],[6.5,1.8],GRAY)
        for i in range(8):
            x=.8+i*.75;ang=(-.6 if i%2==0 else .6)
            c.line([x,1.8],[x+ang*.5,.7],TEAL,arrow='end')
        c.text(labels[0],.8,2.1,2.7,.45);c.text(labels[1],3.8,2.1,2.7,.45,color=ORANGE)
        c.line([3.4,1.8],[3.4,.3],ORANGE,arrow='end',width=2)
    elif kind=='ellipse':
        c.box(1,.55,1.6,1.6,color=TEAL,shape='ellipse');c.box(4,.95,2.1,.8,color=ORANGE,shape='ellipse')
        c.text(labels[0],.6,2.2,2.5,.4);c.text(labels[1],3.7,2.2,2.7,.4)
    elif kind=='spectrum':
        for panel in range(2):
            x=.6+panel*3.5
            for i,v in enumerate(args[panel]):
                c.box(x+i*.37,2.1-1.4*v,.22,1.4*v,color=TEAL if panel==0 else ORANGE,fill=TEAL if panel==0 else ORANGE)
            c.text(labels[panel],x-.15,2.2,2.8,.4,size=12)
        c.text(labels[2],2,.05,3.2,.4,color=PURPLE)
    elif kind=='contrast':
        for x,bg in [(0.5,'333333'),(3.9,'EEEEEE')]:
            c.box(x,.35,2.7,1.8,color=bg,fill=bg);c.box(x+.9,.9,.9,.7,color='888888',fill='888888')
        c.text(labels[0],.5,2.25,2.7,.4);c.text(labels[1],3.9,2.25,2.7,.4)
    elif kind=='skeleton':
        for panel,sign in enumerate([1,-1]):
            p=[.6+panel*3.5,1.9];t=[2.5+panel*3.5,1.35]
            dx,dy=t[0]-p[0],t[1]-p[1];dist=math.hypot(dx,dy)
            height=math.sqrt(1.3**2-(dist/2)**2)
            e=[(p[0]+t[0])/2+sign*dy/dist*height,(p[1]+t[1])/2-sign*dx/dist*height]
            c.path([p,e,t],TEAL,3)
            for pt in [p,e,t]:c.dot(*pt,ORANGE,r=.06)
            c.text(labels[panel],.5+panel*3.5,.25,2.7,.4)
    elif kind=='collapse':
        for x,color in [(1.4,TEAL),(5.3,ORANGE)]:
            c.line([x,1.5],[x+(.8 if x<3 else -.8),1.5],color,arrow='end',width=3)
            c.dot(x,1.5,GRAY)
        c.dot(3.5,1.5,RED,r=.1);c.text(labels[0],.4,.35,2.6,.45);c.text(labels[1],4.1,.35,2.6,.45)
        c.text(labels[2],2.1,2.1,2.8,.4,color=RED)
    elif kind=='spring':
        c.dot(.7,1.3,TEAL,r=.12);c.dot(6.3,1.3,ORANGE,r=.12)
        points=[[.9,1.3],[1.4,1.3]]+[[1.4+i*.35,1.05 if i%2 else 1.55] for i in range(1,13)]+[[5.9,1.3],[6.1,1.3]]
        c.path(points,GRAY)
        c.line([.8,.65],[2,.65],TEAL,arrow='end');c.line([6.2,.65],[5,.65],ORANGE,arrow='end')
        c.text(labels[0],.4,2.1,2.3,.4);c.text(labels[1],4.3,2.1,2.3,.4);c.text(labels[2],2.2,.06,2.6,.4)
    elif kind=='phase':
        for idx,method in enumerate(['explicit','semi','implicit']):
            x,v=1.,0.;pts=[]
            for i in range(160):
                scale=.45;pts.append([1.2+idx*2.3+scale*x,1.35-scale*v])
                h=.1
                if method=='explicit':x,v=x+h*v,v-h*x
                elif method=='semi':v-=h*x;x+=h*v
                else:xnew=(x+h*v)/(1+h*h);v-=h*xnew;x=xnew
            c.path(pts,[RED,TEAL,PURPLE][idx],.9);c.text(labels[idx],.25+idx*2.3,2.35,1.9,.3,size=10)
    elif kind=='field':
        mode=args[0]
        for panel in range(2):
            cx=1.65+panel*3.5;cy=1.25
            for j in [-1,0,1]:
                for i in [-1,0,1]:
                    if i==j==0:continue
                    x=cx+.48*i;y=cy+.48*j
                    if (mode=='divcurl' and panel==1) or mode=='curl':dx,dy=-j*.22,i*.22
                    elif mode=='uniform' and panel==1:dx,dy=.25,0
                    else:dx,dy=.22*i,.22*j
                    c.line([x,y],[x+dx,y+dy],TEAL if panel==0 else ORANGE,arrow='end')
            c.text(labels[panel],cx-1.45,2.25,2.9,.45,size=11)
    elif kind=='stencil':
        for i,j,val in [(1,1,labels[0]),(0,1,labels[1]),(2,1,labels[2]),(1,0,labels[3]),(1,2,labels[4])]:
            c.box(2+i*.72,.25+j*.72,.68,.68,val,color=ORANGE if i==j==1 else TEAL,size=12)
        if len(labels)>5:c.text(labels[5],4.5,1,2.1,.7)
    elif kind=='mac':
        for j in range(2):
            for i in range(3):
                x=1.2+i*1.2;y=.35+j*.9;c.box(x,y,1.2,.9,color='CBD5E1')
                c.dot(x+.6,y+.45,PURPLE,r=.06);c.line([x+.1,y+.45],[x+.35,y+.45],TEAL,arrow='end');c.line([x+.6,y+.05],[x+.6,y+.25],ORANGE,arrow='end')
        c.text(labels[0],.4,2.35,2,.3,color=PURPLE);c.text(labels[1],2.6,2.35,2,.3,color=TEAL);c.text(labels[2],4.8,2.35,2,.3,color=ORANGE)
    elif kind=='backtrace':
        c.line([.8,1.5],[6.2,1.5],GRAY)
        for x,label in [(1.3,labels[0]),(3.1,labels[1]),(5.3,labels[2])]:
            c.dot(x,1.5,r=.07);c.text(label,x-.9,1.8,1.8,.5)
        start,end=([5.3,1.1],[3.1,1.1]) if args and args[0]=='reverse' else ([3.1,1.1],[5.3,1.1])
        c.line(start,end,ORANGE,arrow='end');c.text(labels[3],2.8,.45,3,.4,color=ORANGE)
    elif kind=='stereo':
        left=[2,2.05];right=[5,2.05];target=[3.5,.5]
        for p in [left,right]:c.box(p[0]-.25,p[1]-.15,.5,.3,color=TEAL,shape='ellipse');c.line(p,target,TEAL)
        c.dot(*target,ORANGE,r=.06);c.line([2,2.4],[5,2.4],GRAY,arrow='both');c.text(labels[0],2.5,2.05,2,.3)
        c.text(labels[1],2.2,.03,2.6,.35);c.text(labels[2],.3,1,1.4,.45)
    elif kind=='fovea':
        for x,y,w,h,col in [(1,.35,5,1.9,GRAY),(2,.65,3,1.3,TEAL),(2.95,.95,1.1,.7,ORANGE)]:c.box(x,y,w,h,color=col,shape='ellipse')
        c.text(labels[0],.25,2.35,2.2,.3);c.text(labels[1],2.4,2.35,2.2,.3);c.text(labels[2],4.65,2.35,2.2,.3)
    elif kind=='occlusion':
        c.line([5.5,.4],[5.5,2.3],GRAY,width=4);c.line([3.1,.8],[3.1,1.8],ORANGE,width=5)
        for p in [[.6,1.7],[1.4,2.25]]:c.dot(*p,r=.07);c.line(p,[5.5,.5],TEAL);c.line(p,[5.5,2.15],TEAL)
        c.text(labels[0],.15,.25,2.0,.4);c.text(labels[1],2.65,.2,1.3,.4,color=ORANGE);c.text(labels[2],5.8,.7,1.1,1)
    elif kind in ('lens','coc','fov'):
        c.line([.45,1.4],[6.6,1.4],GRAY,dash='dash')
        c.box(3.2,.35,.15,2.0,color=TEAL,shape='ellipse')
        if kind=='fov':
            c.line([1,.5],[1,2.3],PURPLE,width=3);c.line([1,.5],[3.3,1.4],TEAL);c.line([1,2.3],[3.3,1.4],TEAL)
            c.line([3.3,1.4],[6.2,.35],ORANGE);c.line([3.3,1.4],[6.2,2.4],ORANGE)
        else:
            c.line([.7,.5],[3.25,.5],TEAL);c.line([3.25,.5],[5.9,2.3353],TEAL)
            c.line([.7,.5],[3.25,1.4],ORANGE);c.line([3.25,1.4],[5.9,2.3353],ORANGE)
            if kind=='coc':c.line([5,.3],[5,2.4],PURPLE,width=2)
        for i,label in enumerate(labels[:3]):c.text(label,.3+i*2.3,2.4,2.1,.3,size=11)
    elif kind=='aperture':
        for idx,d in enumerate([1.6,.8,.4]):
            x=1.25+idx*2.2;c.box(x-d/2,1.3-d/2,d,d,color=[TEAL,ORANGE,PURPLE][idx],shape='ellipse')
            c.text(labels[idx],x-.9,2.3,1.8,.3,size=11)
    elif kind=='motion':
        for i in range(6):c.box(.8+i*.85,.65,.4,1.1,color=TEAL,fill='E0F2F1')
        c.line([.85,2.0],[5.5,2.0],ORANGE,arrow='end');c.text(labels[0],1,.1,4.8,.4);c.text(labels[1],1.2,2.28,4.5,.4)
    elif kind=='kernel':
        nums=args
        for j in range(3):
            for i in range(3):c.box(2+i*.63,.3+j*.63,.6,.6,str(nums[j*3+i]),color=ORANGE if i==j==1 else TEAL,size=12)
        c.text(labels[0],.15,.95,1.6,.7);c.text(labels[1],4.3,.8,2.5,.9,color=ORANGE)
    elif kind=='blocks':
        for j in range(4):
            for i in range(4):c.box(.7+i*.45,.35+j*.45,.43,.43,color=TEAL,fill='E0F2F1')
        for j in range(2):
            for i in range(2):c.box(3.4+i*.8,.4+j*.8,.75,.75,color=ORANGE,fill='FFF7ED')
        c.text(labels[0],.4,2.3,2.4,.35);c.text(labels[1],3,2.3,2.6,.35);c.text(labels[2],5.4,.8,1.5,1)
    else: raise ValueError(kind)
    return c.doc(caption)

# kind, labels, numeric arguments, caption; all numerical graphics are teaching examples.
EXTRAS={
'01':[
('pixels',['左上 (0,0,0)','右下 (1,1,0)'],[], '屏幕 y 向下，颜色定义为 (u,v,0) 时，左上为黑、右下为黄。'),
('triangle',['A','B','C'],[], 'C 向底边移动使高减小；超过底边后需重新判断高度。'),
('coverage',['每像素 1 个样本','每像素 4 个样本'],[], '相同边界下增加子样本，能估计部分覆盖而非只有二元判断。'),
('bars',['2D：8²','3D：8³','4D：8⁴'],[64,512,4096], '规则网格每维八点，积分维数增加使总样本数指数增长。'),
('path',['相机','表面 A','表面 B','灯'],[], '像素可以接收经过多个表面散射后到达相机的光。'),
('skeleton',['父关节带动子关节','不同姿态同样有末端'],[], '骨架由层级控制，表面运动需要另外的蒙皮阶段。'),
('lens',['物体','镜头','传感器'],[], '有限镜头汇聚光线，传感器并非直接等同投影矩阵。'),
('stereo',['眼间距','空间目标','两个视点'],[], '左右眼分别从自己的视点成像，产生双目视差。')],
'14':[
('solidangle',['远方面元','方向锥张角'],[], '立体角描述光源从接收点张开的方向范围。'),
('rays',['入射方向','倾斜接收关系','余弦来自投影面积'],[], '入射方向与表面法线决定投影余弦，不能用光线与平面的夹角替代。'),
('bars',['r = 1','r = 2','r = 4'],[1,.25,.0625], '点光源保持强度与朝向，辐照度按距离平方反比变化。'),
('curve',['归一化距离','相对辐照度','E ∝ 1/r²'],['inverse'], '曲线使用 r=1+4x 的教学参数，显示近处到远处的平方衰减。'),
('aperture',['较大方向锥','中等方向锥','较小方向锥'],[], '有限角域大小不同，不能只比较域内相同的辐亮度数值；圆形仅示意角域。'),
('lens',['场景光线','孔径','像素'],[], '相机像素需要考虑有限孔径与面积积分，针孔只是简化。'),
('spectrum',['光谱 A','光谱 B','能量分布随波长变化'],[[.2,.4,.9,.6,.3],[.7,.5,.2,.4,.8]], '两条示意光谱有不同波段分布，光度量必须再乘视觉敏感度。'),
('backtrace',['Q = 24 J','t = 4 s','Φ = 6 W','功率等于能量除时间'],[], '同一教学例的三个量分别是 24 J、4 s 与 6 W，以关系而非柱高比较不同单位。')],
'15':[
('samples',['规则分层中心','层内随机位置'],[], '两组样本都覆盖同一方形，右侧加入层内随机性以打散规律。'),
('bars',['N=16','N=64','N=256'],[.2,.1,.05], '独立有限方差样本增加四倍，标准差约减半。'),
('curve',['x / 归一化位置','密度形状','p(x) ∝ x²'],['square'], '重要性采样让大贡献区域更常出现，但贡献必须除以实际 PDF。'),
('curve',['均匀随机数 ξ','采样半径 r','r = √ξ'],['sqrt'], '平方根半径映射使圆盘采样按面积均匀。'),
('disk',['错误：r 均匀','正确：r = √ξ'],[], '相同数量的圆盘样本，半径均匀会让圆心附近过密。'),
('solidangle',['光源面元 dA','dω = cosθL dA/r²'],[], '面积样本与立体角样本由几何 Jacobian 连接。'),
('tree',['贡献 C=2','存活 q=0.25','终止 0.75','返回 8','返回 0'],[], '概率变小需要补偿权重，期望仍为 2；这是后续轮盘的基础。'),
('backtrace',['密度 p=4','区间长 0.25','概率=1','密度 × 区间长度'],[], '概率密度可以大于一，密度乘区间长度才是概率。')],
'16':[
('path',['相机','表面 A','表面 B','灯'],['direct'], '橙色虚线是从 A 直接连灯，折线路径则经 B，二者属于不同反弹次数。'),
('bars',['0 次','1 次','2 次'],[1,.5,.25], '标量传输 K=0.5 时，各阶贡献构成收敛级数。'),
('tree',['后续 C=2','q=0.25 存活','0.75 终止','补偿为 8','贡献为 0'],[], '轮盘用少量较大贡献代替每次都计算后续路径，保持期望。'),
('reflection',['镜面入射','唯一反射方向','delta 事件需要专用采样'],[], '理想镜面不能靠普通连续随机方向恰好命中。'),
('backtrace',['表面起点','遮挡 t=1','灯 t=2','只检查到灯之前'],[], '阴影光线有有限有效区间，灯背后的几何不应产生遮挡。'),
('bars',['ρ₁=0.8','再乘 ρ₂=0.5','乘 Le=10'],[.8,.4,4], '路径权重由 0.8 到 0.4，最后乘灯的辐亮度得到贡献 4。'),
('spectrum',['少数大贡献','较均匀贡献','示意样本贡献，非渲染测量'],[[.05,.05,.9,.05,.05],[.2,.2,.3,.2,.2]], '稀少重要光路造成更大的样本贡献波动，采样策略力求降低这种波动。'),
('bars',['显式 Le','反射贡献','合计 Lo'],[2,3,5], '发光项和反射项分别累积，不能在不同递归分支重复加入同一项。')],
'18':[
('reflection',['wi 指向来源','wo 指向去向','两侧与法线夹角相等'],[], '理想镜面保持法线分量、翻转切向分量。'),
('refraction',['入射光','反射分支','折射分支'],[], '界面将能量分配给反射与透射；折射线只作方向示意。'),
('curve',['cosθ','反射比例 F','F₀=0.04'],['fresnel'], 'Schlick 近似在法向为 0.04，掠射趋于 1；横轴是余弦而非角度。'),
('normals',['实际微面法线分布','平均法线'],[], '用平均法线替换分布会丢失能够把光反射到指定方向的微面统计。'),
('ellipse',['各向同性示意','各向异性示意'],[], '方向性结构可拉长高光；图形只表达形状差异，不是 BRDF 测量。'),
('path',['入射','表面','内部','出射'],[], '毛发和次表面材料包含内部传播，不能只看一次表面反射。'),
('curve',['距离 d','透过率 T','T = exp(-σt d)'],['exp'], '均匀介质示例用 σt d=3x，传播距离增加使未消光比例指数下降。'),
('backtrace',['入射 xi','内部散射','出射 xo','两个表面位置不同'],[], 'BSSRDF 连接两个位置，BRDF 只在同一位置描述散射。')],
'19':[
('spectrum',['光谱 A','光谱 B','真实同色需传感器积分相等'],[[.2,.8,.3,.6,.2],[.6,.2,.7,.2,.4]], '光谱形状不同不自动意味着感知不同；图中未声称两条任意曲线是实测同色异谱。'),
('gamut',['基色 1','基色 2','基色 3','域内','域外'],[], '非负三基色混合覆盖凸三角形，域外目标需要映射。'),
('curve',['编码值 a','线性强度 I','I = a^2.2（近似）'],['gamma'], '幂律演示编码值与线性光量的区别，不是完整 sRGB 标准曲线。'),
('bars',['直接编码均值','正确线性均值','线性均值再编码'],[.5,.5,.72974], '前两列数值相同但语义不同，正确线性均值 0.5 编码后约 0.72974。'),
('contrast',['中心块 RGB = 136','中心块 RGB = 136'],[], '相同中心灰块处在不同背景中；数值相同与感知相同是不同问题。'),
('curve',['线性值 L / 5','压缩值 T','T = L/(1+L)'],['tone'], '教学色调映射保留高亮值差异，而硬裁剪会把它们全部压成 1。'),
('bars',['X','Y','Z'],[2,3,5], 'XYZ=(2,3,5) 的色度为 (0.2,0.3)，归一化会丢掉亮度尺度。'),
('bars',['滤镜一 T₁','滤镜二 T₂','串联 T₁T₂'],[.5,.2,.1], '简单滤镜的光谱透过率相乘，与发光源光谱相加不同。')],
'21':[
('skeleton',['肘向上分支','肘向下分支'],[], '两条骨链的两段长度均为 1.3，相对根节点的末端目标相同，存在肘向上与向下两个解。'),
('collapse',['旋转 0°','旋转 180°','线性平均可压成零'],[], '合法旋转的逐元素平均可能不是旋转，LBS 扭曲与这个约束有关。'),
('curve',['归一化时间','插值位置','缓入缓出示意'],['ease'], '平滑时间参数改变起止速度，位置终点并不是动画的全部。'),
('bars',['骨骼 A 权重','骨骼 B 权重','权重和'],[.75,.25,1], '蒙皮权重和为 1 是保持共同平移与绑定姿态的重要条件。'),
('backtrace',['中性值 1','位移 0.2','结果 1.1','系数 a = 0.5'],[], 'Blend shape 将位移乘权重再加回中性形状，绝对目标位置不能直接当位移。'),
('tree',['目标位置','可达且多解','不可达','加入姿态偏好','求最近可行点'],[], 'IK 首先面对可达性与多解，再选择解析或数值求解。'),
('motion',['曝光中物体持续运动','图像积分整段轨迹'],[], '运动模糊与单帧姿态插值不同，曝光覆盖一段时间。'),
('bars',['位置误差平方','速度误差平方','总连接代价'],[.04,.09,.13], '动作片段拼接需要同时考虑位置与速度，数值为教学示例。')],
'24':[
('spring',['a 端向右拉','b 端向左拉','伸长状态'],[], '弹簧内力成对反向；压缩时两端受力反转。'),
('phase',['显式 Euler','半隐式 Euler','隐式 Euler'],[], '同一无阻尼振子、h=0.1、160 步，轨迹展示增能、近似有界与数值耗散；横纵是位置与速度相图。'),
('bars',['显式 E₁','半隐式 E₁','初始 E₀'],[.505,.49505,.5], '相同初值 x=1,v=0,h=0.1 下的一步能量，不能用单步结果替代长期稳定分析。'),
('backtrace',['位置 0','修为 0.2','修为 1.2','等质量长度投影'],[], '两端各移动 0.2，将距离 1.4 修回 1，同时保持质心。'),
('tree',['两端运动','共同平移','相对伸缩','内部阻尼为零','阻尼耗散能量'],[], '内部阻尼只惩罚相对伸缩，不应阻止刚体平移。'),
('bars',['一个 k=10','两段各 k=20','错误：各 k=10'],[10,10,5], '一维串联模型中，细分时需调整弹簧常数以保持整体刚度。'),
('backtrace',['旧状态','两半步终点','一步终点','比较同一终止时间'],[], '自适应步长比较同起点同终点的两种离散近似，而不是比较不同时间的位置。'),
('reflection',['入射速度','反弹方向','法向与切向分量分开处理'],['velocity'], '碰撞响应需分解法向和切向，不能简单翻转整个速度向量。')],
'25':[
('mac',['中心：压力 p','竖面：u','横面：v'],[], '交错网格把压力放中心，两个速度分量放对应单元面。'),
('field',['向外流：散度非零','旋转流：散度为零'],['divcurl'], '旋转与膨胀是不同导数性质，旋涡可以满足不可压缩约束。'),
('backtrace',['旧 q(1)=2','旧 q(1.5)=3','新网格 x=2','沿速度反向回溯'],['reverse'], '目标位置回溯到旧时刻的来源，再插值旧字段。'),
('stencil',['-4','1','1','1','1','除以网格间距平方'],[], '二维压力拉普拉斯的五点模板，中心与邻居共同构成耦合方程。'),
('field',['临时速度有净流出','均匀流可无散度'],['uniform'], '压力投影消除散度，不是把整个速度场清零；左右仅示意两类场。'),
('bars',['临时散度','压力修正散度','投影后散度'],[3,3,0], '正文数值例为 3-3=0，最后一列在基线上标记精确零。'),
('spring',['弹性储存形变','卸载可以回弹','黏弹性还需流动状态'],[], '弹性需要可恢复形变状态，单纯黏性系数不能产生同样回弹机制。'),
('bars',['原质量','错误后质量','损失质量'],[4,3.5,.5], '质量账本比截图更能发现数值损失，此例损失 12.5%。')],
'26':[
('stereo',['基线 B','目标深度 Z','左右眼'],[], '两个观察位置产生深度相关视差，渲染时两眼必须使用一致的世界状态。'),
('bars',['光学焦面 / D','近处目标 / D','需求差 / D'],[.5,2,1.5], '2 米光学焦面与 0.5 米目标对应 0.5 D 和 2 D，仅说明几何需求差。'),
('bars',['延迟 11 ms','延迟 22 ms','延迟 33 ms'],[19.8,39.6,59.4], '角速度 90°/s、20 PPD 时，像素误差与延迟近似成正比。'),
('fovea',['周边较低密度','过渡区域','注视点较高密度'],[], '计算预算随注视区域分配，过渡、过滤和追踪时效都要处理。'),
('curve',['归一化半径','形变程度示意','边缘更容易被拉伸'],['square'], '径向畸变在边缘更显著，校正后的采样密度需重新检查；曲线只示意增长趋势。'),
('occlusion',['相机位置改变','遮挡物','新暴露背景'],[], '平移会露出旧图没有记录的区域，仅重投影旧颜色无法精确补齐。'),
('bars',['1 米深度','2 米深度','10 米深度'],[10,5,1], 'f=1000px、横移 0.01m 时，平移像移近似 fΔx/Z，不能由单一旋转替代。'),
('bars',['转向 0°','转向 60°','转向 90°'],[6,3,0], '固定双全景的简化有效基线是 Bcosθ；90° 时为零，基线单位为厘米。')],
'90':[
('fov',['传感器宽度','焦距与光心','视场角'],[], '视场由传感器尺寸与焦距共同决定，必须明确水平或对角方向。'),
('aperture',['f/2','f/4','f/8'],[], '同焦距下孔径直径依次减半，面积依次减为四分之一。'),
('lens',['物点','薄透镜','清晰像点'],[], '理想薄透镜把同一物点的光线汇聚到像点，图形是几何示意。'),
('coc',['物点','孔径','传感器截到光锥'],[], '紫色传感器面偏离清晰像点，光束截面产生有限离焦光斑。'),
('disk',['错误孔径半径采样','按面积均匀采样'],[], '薄透镜相机的圆孔径采样需使用平方根半径映射。'),
('motion',['匀速物体在曝光中移动','模糊长度 ≈ 速度 × 曝光'],[], '曝光时长影响运动轨迹积分，与行间扫描时差不是同一参数。'),
('bars',['100 光子','400 光子','900 光子'],[10,20,30], '仅考虑散粒噪声时，信噪比近似为光子计数平方根。'),
('backtrace',['C=0.01 mm','像素 0.005 mm','对应 2 像素','光斑直径除以像素间距'],[], '弥散圆、像素间距和最终像素数通过除法联系，不以柱高比较不同单位。')],
'91':[
('kernel',['Gaussian 示例','总权重除以 16'],[1,2,1,2,4,2,1,2,1], '可分离的 3×3 Gaussian 型平滑核是两个 [1,2,1]/4 的外积。'),
('kernel',['锐化核','常数保持，边缘可过冲'],[0,-1,0,-1,5,-1,0,-1,0], '中心 5、四邻 -1 的锐化核权重和为 1，但负权重能使输出超出输入范围。'),
('kernel',['Sobel 横向相关核','差分 × 垂直平滑'],[-1,0,1,-2,0,2,-1,0,1], '按相关运算解释的 Sobel 横向核；数学卷积翻核会改变导数符号。'),
('bars',['直接 15×15','横向 1D','纵向 1D'],[225,15,15], '每像素累加数由 225 降至 15+15=30，操作数比为 7.5，非实测加速比。'),
('bars',['脉冲邻域均值','同邻域中值','正常水平'],[59,10,10], '邻域 [10,11,255,10,9] 的均值被脉冲拉高，中值为 10。'),
('blocks',['较密亮度采样','较稀色度采样','4:2:0'],[], '色度降采样与亮度保留不同空间分辨率，图中方块表示采样区域。'),
('bars',['原系数 c','量化重建','绝对误差'],[23,20,3], '量化步长 10 将系数 23 还原成 20，误差为 3；变换本身并非这个损失来源。'),
('tree',['已知邻域','候选 A 距离 1','候选 B 距离 5','更相似','较不相似'],[], '纹理合成通过已知邻域比较候选，不应将未知区域当作零参与距离。')]
}
