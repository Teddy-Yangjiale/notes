DATA['11']=[
topic('翻边后的 Euler 数正确，为什么半边仍可能坏掉',[24,26,28,29,30,32,33],
'Euler 示性数只看元素数量，看不到有向边是否配对、next 是否闭环。用两个三角形组成的方片，可以在翻边前后数出同样的 V/E/F，再故意把一个面的绕序翻转，证明“计数正确”不足以证明连接结构正确。',
[('顶点','0=(0,0)、1=(1,0)、2=(0,1)、3=(1,1)。'),('旧面','(0,1,2)、(2,1,3)，共享无向边 {1,2}。'),('翻边后','(0,1,3)、(0,3,2)，共享无向边 {0,3}。')],
[('翻边只重接两个面，元素总数不变，因此 Euler 数不会改变。',r'(V,E,F)=(4,5,2),\qquad\chi=4-5+2=1'),('三角形面的 next 必须三步返回；内部有向边应有反向 twin。',r'\operatorname{next}^3(h)=h,\qquad\operatorname{twin}(\operatorname{twin}(h))=h'),('如果两个面把同一边都写成 3→0，计数仍不变，但不能构造方向相反的 twin。',r'(3,0)\not\equiv(0,3)')],
['旧内部半边为 1→2 与 2→1。','新内部半边为 3→0 与 0→3，配对后共享新对角线。','四条边界半边仍无普通邻面 twin；若实现用边界虚面，应按自己的统一约定补齐。','将第二个新面误写成 (0,2,3)，内部边也变为 3→0。','V=4、E=5、F=2 仍全部正确，但内部边方向配对失败。'],
'''def audit(faces):
    vertices=set();edges=set();directed=[];nxt={}
    for f,tri in enumerate(faces):
        vertices.update(tri)
        for j in range(3):
            a,b=tri[j],tri[(j+1)%3]
            edges.add(tuple(sorted((a,b))));directed.append((a,b))
            nxt[(f,j)]=(f,(j+1)%3)
    assert all(nxt[nxt[nxt[h]]]==h for h in nxt)
    paired=sum((b,a) in directed for a,b in directed)
    return len(vertices)-len(edges)+len(faces),paired,len(set(directed))==len(directed)
old=[(0,1,2),(2,1,3)];new=[(0,1,3),(0,3,2)];bad=[(0,1,3),(0,2,3)]
assert audit(old)==audit(new)==(1,2,True)
assert audit(bad)==(1,0,False)
print('valid flip:',audit(new),'same Euler but broken:',audit(bad))
''',
['同时检查计数、有向边唯一性、反向 twin 和面环。真实半边结构还需检查 vertex/edge/face 的代表半边和指针所有权。','这里是二维流形内部边翻转。边界边、非流形边以及翻转后退化或自交的情形不能直接套用；几何合法性还要单独检查。'],
'症状：翻边后统计数正确，但遍历一环死循环或法线突然反向。先检查 next 环和 twin 互反，再检查面绕序及几何面积；不要只把 Euler=1 当作全部验收。',
'三角形两个面的朝向都一起反转，是否也会失去共享边配对？',
'不会，原来两条反向共享边仍互为反向。问题是局部不一致地反转一个面；全局朝向和局部一致性需要分别验证。',
'翻边前后对角线改变，合法版本中共享边箭头相反；错误版本箭头同向，虽然元素数量完全相同。'),
topic('QEM 奇异时如何把最优点限制在线段上',[122,123,124,125,126],
'平坦区域的二次型缺少某些方向约束，矩阵奇异往往是几何本身的性质。直接加一个很大的正则项或永远退回中点，会隐藏这种结构。先在线段参数上求一元二次最小值，能给出一个简单、可回代的候选策略。',
[('平面','x=0 与 y=0，单位法线。'),('代价','E(x,y,z)=x²+y²，z 未受约束。'),('边端点','a=(1,0,2)，b=(0,2,4)。')],
[('齐次平面外积相加得到 Q，其空间块 A 的秩只有 2；不唯一不等于无解。',r'A=\operatorname{diag}(1,1,0),\qquad\arg\min E=\{(0,0,z)\}'),('将候选点约束在原边 v(t)=a+t(b−a)，得到一元二次函数。',r'E(t)=(1-t)^2+(2t)^2=1-2t+5t^2'),('导数为零后夹到 [0,1]，再与端点及中点回代比较。',r"E'(t)=-2+10t=0\Rightarrow t^*=0.2,\qquad v^*=(0.8,0.4,2.4)")],
['端点 a 的误差为 1，b 的误差为 4。','中点 (0.5,1,3) 的误差为 1.25。','线段最优点误差 0.8²+0.4²=0.8，比三个简单候选都小。','配方 E(t)=5(t−0.2)²+0.8，证明这是整个线段上的全局最小值。','该点只保证二次型误差较小，不保证收边后拓扑合法或没有翻面。'],
'''from math import isclose
a=(1.,0.,2.);b=(0.,2.,4.)
def point(t):return tuple(x+t*(y-x) for x,y in zip(a,b))
def error(v):return v[0]**2+v[1]**2
t=.2;v=point(t)
assert all(isclose(x,y) for x,y in zip(v,(.8,.4,2.4)))
assert isclose(error(v),.8)
assert error(v)<min(error(point(s)) for s in (0,.5,1))
for i in range(101):assert error(point(i/100))>=error(v)-1e-12
assert error((0,0,123))==0
print('segment optimum:',v,'cost:',round(error(v),6),'midpoint:',error(point(.5)))
''',
['配方法给出解析证明，采样扫描只检查程序。平面法线必须单位化，否则外积会隐式改变权重。','对一般 E=vᵀAv+2bᵀv+c，令方向 e=b_endpoint−a，分母为 eᵀAe；接近零时应比较有限候选并用尺度相关判据。不要用固定 abs(det A)<epsilon 跨单位判断病态。'],
'症状：平坦网格收边时出现巨大坐标或随机跳点。检查秩与条件数、平面归一化和符号，再使用受约束候选；最终仍要做边界、法线翻转与流形检查。',
'本例无约束最小代价是 0，为什么还选择代价 0.8 的线段点？',
'因为候选可行域不同。无约束解可以离开原边，线段约束保持局部位置关系；代价更低不自动意味着更安全的网格操作。',
'误差的零谷沿 z 轴延伸，原边穿过一组等误差轮廓；边上的最优点偏向 a，明显不同于中点。'),
topic('Loop 更新为什么必须读旧位置、写新位置',[51,52,53,54,55,56,57],
'细分权重是同时作用于旧网格的一次线性映射。若遍历到一个顶点就立刻覆盖位置，后续顶点会读到新旧混合的数据，算法便依赖遍历顺序。规则四面体提供了一个可以精确预测整体缩放的回查模型。',
[('拓扑','四面体，四个顶点度数均为 3。'),('权重','Loop 的 n=3 特例 β=3/16，中心权重 1−3β=7/16。'),('位置','(1,1,1)、(1,−1,−1)、(−1,1,−1)、(−1,−1,1)。')],
[('所有权重和为 1，保证常量场及平移不变；这不代表每个网格都会保持体积。',r'p_i^{new}=\frac7{16}p_i+\frac3{16}\sum_{j\ne i}p_j'),('四个旧顶点和为零，所以每个顶点的邻居和等于自身的负值。',r'\sum_{j\ne i}p_j=-p_i'),('同步更新得到精确的 1/4 缩放，而原地更新不再使用同一个旧邻域。',r'p_i^{new}=\left(\frac7{16}-\frac3{16}\right)p_i=\frac14p_i')],
['顶点 (1,1,1) 更新为 (0.25,0.25,0.25)。','其他三点分别缩放相同倍数，重心仍为零。','如果先覆盖第一个点，第二个点的邻居和已经改变，不能再用 −p1。','反转遍历顺序，会得到另一组错误输出。','正确方法先计算所有旧顶点的新位置与新边点，再统一提交位置和拓扑变化。'],
'''from math import isclose
P=[(1.,1.,1.),(1.,-1.,-1.),(-1.,1.,-1.),(-1.,-1.,1.)]
def updated(i,points):
    return tuple(7/16*points[i][k]+3/16*sum(points[j][k] for j in range(4) if j!=i) for k in range(3))
sync=[updated(i,P) for i in range(4)]
assert all(q==tuple(x/4 for x in p) for p,q in zip(P,sync))
def inplace(order):
    q=P.copy()
    for i in order:q[i]=updated(i,q)
    return q
forward=inplace(range(4));reverse=inplace(reversed(range(4)))
assert forward!=sync and forward!=reverse
assert all(isclose(sum(p[k] for p in sync),0) for k in range(3))
print('synchronous first vertex:',sync[0])
print('in-place depends on order:',forward!=reverse)
''',
['预测缩放倍数、检查重心、反转遍历顺序，是三种互补检查。','这个缩放结论只属于所选对称四面体的旧顶点更新；一次完整细分还包含新边点和重连。边界、锐边和不同度数有不同权重，不能照搬 3/16。'],
'症状：网格越细分越偏向遍历起点，换顶点编号后形状改变。分离 old/new 数组，并在拓扑编辑前完成依赖旧邻接关系的计算。',
'权重和为 1，能否推出整个物体体积不变？',
'不能。它保证平移与常量再现，本例旧顶点整体缩小就已经说明形状尺度可能改变。体积涉及全局几何，需要额外约束或修正。',
'上排表示从旧数组统一读取、计算后统一写入新数组；下方给出四面体旧顶点缩小为 1/4 的检验结果，并标出原地更新的顺序依赖。')]

DATA['13']=[
topic('Möller–Trumbore 的符号怎样用回代锁定',[49,50,51,52,54],
'求交代码最危险的情况是推导、记号和程序各自来自不同约定。先从同一条向量等式整理线性系统，再选 u≠v 的测试点，便能同时查出右端项符号、t 符号和顶点属性对应错误。',
[('三角形','A=(0,0,0)、B=(1,0,0)、C=(0,1,0)。'),('光线','o=(0.2,0.3,−2)，d=(0,0,2)，故方向不是单位向量。'),('记号','E1=B−A、E2=C−A、S=o−A；u 对应 B、v 对应 C。')],
[('从光线点等于三角形重心表示出发，将未知项整理到左边。',r'o+td=A+uE_1+vE_2\Rightarrow[-d\ E_1\ E_2](t,u,v)^T=S'),('将法向 N=E1×E2 点乘原式，u、v 项消失。',r't=-\frac{S\cdot N}{d\cdot N}'),('利用标量三重积，可选择一套与常见实现一致的中间变量。',r'h=d\times E_2,\ a=E_1\cdot h,\ q=S\times E_1;\quad u=\frac{S\cdot h}{a},\ v=\frac{d\cdot q}{a},\ t=\frac{E_2\cdot q}{a}')],
['h=(−2,0,0)，a=−2；负号不表示没命中，只与方向和绕序有关。','S·h=−0.4，所以 u=0.2。','q=(0,−2,−0.3)，d·q=−0.6，所以 v=0.3。','E2·q=−2，t=1。回代 o+td=(0.2,0.3,0)。','重心回代 (1−u−v)A+uB+vC 也得相同点；沿光线的物理距离是 |td|=2，不是 t=1。'],
'''from math import isclose,sqrt
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def dot(a,b):return sum(x*y for x,y in zip(a,b))
E1=(1,0,0);E2=(0,1,0);S=(.2,.3,-2);d=(0,0,2)
h=cross(d,E2);a=dot(E1,h);q=cross(S,E1)
u=dot(S,h)/a;v=dot(d,q)/a;t=dot(E2,q)/a
assert all(isclose(x,y) for x,y in zip((t,u,v),(1,.2,.3)))
ray=tuple(o+t*di for o,di in zip(S,d));bary=(u,v,0)
assert all(isclose(x,y) for x,y in zip(ray,bary))
assert -dot(S,cross(E1,E2))/dot(d,cross(E1,E2))==t
assert u+v<=1 and u>=0 and v>=0
print('t,u,v:',t,u,v,'hit:',ray,'distance:',t*sqrt(dot(d,d)))
''',
['必须选 u≠v 的案例才能发现属性槽交换；只用 u=v=0.2 的对称点无法区分。','单纯交换 u、v 不改变对称包含判据，但会错配属性；叉积顺序或分母符号不一致才可能翻转正负。近乎平行、退化三角形与 watertight 求交需要进一步处理。'],
'症状：已知内部点被报为未命中，或方向长度变化后距离错误。先回代向量方程再检查 epsilon；不要把符号错误解释成“不同教材把 u/v 换了”。',
'把 d 改为 (0,0,1)，交点不变时 t 应如何变化？',
't 变为 2，u、v 不变。t 是参数，只有方向单位化时才等于沿线距离；所有 t_min/t_max 必须采用同一参数约定。',
'不等的 u=0.2 与 v=0.3 标出交点相对两个顶点的权重；光线方向长度为 2，因此参数 t=1 对应距离 2。'),
topic('AABB 相切、平行与有限线段要放进同一个区间',[71,75,76,77,78,93],
'把三个 slab 区间相交还不够：必须再与射线允许的参数区间相交。对加速结构，擦边命中宁可保守保留；d=0 时如果原点恰好在面上，盲目乘倒数可能产生 0×∞ 的 NaN。',
[('盒子','每轴范围 [0,1]，视作闭集。'),('射线','允许 t∈[0,tmax]，教学实现显式处理方向分量为零。'),('反例','o=(−1,0,0.5)、d=(1,1,0)，仅在 t=1 触及角边。')],
[('非零方向按两个端面求参数并排序，再收紧当前区间。',r't_{lo}\leftarrow\max(t_{lo},\min(t_0,t_1)),\quad t_{hi}\leftarrow\min(t_{hi},\max(t_0,t_1))'),('平行轴若原点在 slab 外则不可能命中；在内则这一轴不限制参数。',r'd_i=0:\quad o_i\notin[b_i^{min},b_i^{max}]\Rightarrow\varnothing'),('闭包围盒保守测试允许端点相等。',r'\operatorname{hit}\Longleftrightarrow t_{lo}\le t_{hi}')],
['反例 x 轴给 [1,2]，y 轴给 [0,1]，z 轴平行且在内。','交集只有 {1}，点为 (0,1,0.5)，属于盒子。','若用严格小于会拒绝这一接触，对包围盒可能造成错误漏测。','o=(−1,0.5,0.5)、d=(1,0,0) 给区间 [1,2]；若 tmax=0.5，有限线段不能到达盒子。','o=(−1,2,0.5)、d=(1,0,0) 在 y slab 外且平行，应立即拒绝，不做除零。'],
'''def intersect(o,d,tmax=float('inf')):
    lo,hi=0.,tmax
    for origin,direction in zip(o,d):
        if direction==0:
            if not 0<=origin<=1:return None
        else:
            a,b=sorted(((0-origin)/direction,(1-origin)/direction))
            lo=max(lo,a);hi=min(hi,b)
            if lo>hi:return None
    return lo,hi
assert intersect((-1,0,.5),(1,1,0))==(1.,1.)
assert intersect((-1,.5,.5),(1,0,0))==(1.,2.)
assert intersect((-1,.5,.5),(1,0,0),.5) is None
assert intersect((-1,2,.5),(1,0,0)) is None
assert intersect((0,.5,.5),(0,1,0))==(0.,.5)
print('touch:',intersect((-1,0,.5),(1,1,0)),'segment misses:',intersect((-1,.5,.5),(1,0,0),.5))
''',
['对返回区间端点回代坐标，分别检查每一轴在盒内；点接触与有限 shadow ray 应单独列用例。','此显式分支实现用于教学，不声称已覆盖所有浮点舍入情形。高性能倒数实现必须定义 signed zero、NaN 与保守舍入行为；包围盒和表面图元的边界策略也不必相同。'],
'症状：相机恰在盒面或光线平行时模型偶尔消失。先用分支版本建立参照，再检查倒数优化是否制造 NaN 或把相切区间丢掉。',
'只判断 t_exit>0，能判断一条到光源为止的阴影线段是否被盒子挡住吗？',
'不能，还要与 [t_min,t_light] 相交。盒子位于光源之后时，半无限射线会命中，但不应遮挡该光源。',
'x 与 y 的 slab 区间只在 t=1 相交，第三行将交集画成一个点；z 方向平行且原点在 slab 内，因而不再缩小区间。'),
topic('SAH 怎样比较切分与不切分，而不丢单位',[179,180,181,182,183,184,188],
'只比较同一父节点内不同切法时，可以略去公共常数；一旦比较叶子与内部节点，就必须恢复父表面积和求交代价。这里重算原文的两个候选，并解释孩子命中概率之和为什么不一定是 1。',
[('父节点','表面积 SP=2000，N=100。'),('候选','A: SL=SR=1200, NL=NR=50；B: SL=700,NL=40,SR=1100,NR=60。'),('代价','Ct=1，Ci=8，为教学假设，不代表当前 PBRT 默认参数或实测时间。')],
[('孩子期望工作量按条件命中概率加权；两个孩子都可能访问。',r'C_{split}=C_t+C_i\left(\frac{S_L}{S_P}N_L+\frac{S_R}{S_P}N_R\right)'),('同一个父节点的候选排序可只比面积加权数量，但它不是与叶子同单位的代价。',r'Q=S_LN_L+S_RN_R,\qquad C_{leaf}=C_iN'),('代入归一化后的代价，才能判断是否值得切。',r'C_A=1+8\frac{120000}{2000}=481,\quad C_B=1+8\frac{94000}{2000}=377,\quad C_{leaf}=800')],
['A 的 Q=1200×50+1200×50=120000。','B 的 Q=700×40+1100×60=94000。','恢复父面积和 Ci 后得到 481 与 377，二者都低于叶子 800。','B 的模型代价较 A 低 (481−377)/481≈21.62%，这是估计量，不是测得加速比。','A 的两个概率 0.6+0.6=1.2 不矛盾；沿一条光线可能先后穿过两个孩子，事件并非互斥。'],
'''from math import isclose
SP=2000;Ct=1;Ci=8;N=100
def cost(SL,NL,SR,NR):return Ct+Ci*(SL*NL+SR*NR)/SP
A=cost(1200,50,1200,50);B=cost(700,40,1100,60);leaf=Ci*N
assert (A,B,leaf)==(481,377,800)
assert B<A<leaf
assert 1200/SP+1200/SP>1
assert isclose((A-B)/A,104/481)
bad=cost(2000,50,2000,50)
assert bad==801 and bad>leaf
print('A/B/leaf:',A,B,leaf,'full overlap split:',bad)
''',
['增加一个完全重叠候选：两孩子表面积都等于父面积，代价为 801，比不切分更差，能检验停止条件。','表面积比基于理想化射线分布。实际主光线、阴影光线、缓存和遍历顺序不同，最终性能必须在真实负载上测。'],
'症状：树无限倾向切分或极端过深。检查是否拿未归一化的 Q 与 CiN 比较，或丢了 Ct；不要把候选排序中的省略公式直接搬到停止条件。',
'如果把所有空间坐标统一放大 100 倍，SAH 模型应改变吗？',
'表面积都放大 10000 倍，但孩子/父面积比不变，因此在 Ct、Ci 与物体数不变时模型代价不变。未归一化公式会暴露单位错误。',
'三根柱分别为不切分、候选 A、候选 B 的同单位代价；右侧列出固定的遍历代价与图元测试代价。候选 B 最低，但这里只比较模型期望工作量，不把柱高比当成实测加速比。')]
