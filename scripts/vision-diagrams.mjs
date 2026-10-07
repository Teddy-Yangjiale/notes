import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(import.meta.dirname, '../src/content/notes');
const esc = s => String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
const palette = { bg:'#f7f5ef', ink:'#26372f', muted:'#5b6b62', green:'#d9e8de', blue:'#dce8f4', orange:'#f3dfc4', red:'#a34435', white:'#ffffff' };
const txt = (x,y,s,size=25,fill=palette.ink,anchor='start') => '<text x="'+x+'" y="'+y+'" font-size="'+size+'" fill="'+fill+'" text-anchor="'+anchor+'">'+esc(s)+'</text>';
const lines = (x,y,arr,size=25,gap=36,fill=palette.ink) => arr.map((s,i)=>txt(x,y+i*gap,s,size,fill)).join('');
const rect = (x,y,w,h,fill=palette.white,stroke='#95a99b',radius=13) => '<rect x="'+x+'" y="'+y+'" width="'+w+'" height="'+h+'" rx="'+radius+'" fill="'+fill+'" stroke="'+stroke+'" stroke-width="2"/>';
const line = (x1,y1,x2,y2,color=palette.ink,dashed=false) => '<line x1="'+x1+'" y1="'+y1+'" x2="'+x2+'" y2="'+y2+'" stroke="'+color+'" stroke-width="3"'+(dashed?' stroke-dasharray="9 7"':'')+'/>';
const arrow = (x1,y1,x2,y2,color=palette.ink) => line(x1,y1,x2,y2,color)+'<path d="M '+(x2-11)+' '+(y2-7)+' L '+x2+' '+y2+' L '+(x2-11)+' '+(y2+7)+'" fill="none" stroke="'+color+'" stroke-width="3"/>';
const card=(x,y,w,h,title,desc=[],fill=palette.green)=>rect(x,y,w,h,fill)+txt(x+20,y+40,title,28)+lines(x+20,y+82,desc,22,32);
const grid=(x,y,values,size=58,colors=[])=>values.map((row,i)=>row.map((v,j)=>rect(x+j*size,y+i*size,size-3,size-3,colors[i]?.[j]??palette.white,'#89998f',4)+txt(x+j*size+size/2-2,y+i*size+size/2+8,v,23,palette.ink,'middle')).join('')).join('');
function save(slug,name,title,description,drawing,h=640){
 const svg='<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="'+h+'" viewBox="0 0 1200 '+h+'" role="img" aria-labelledby="title desc"><title id="title">'+esc(title)+'</title><desc id="desc">'+esc(description)+'</desc><rect width="1200" height="'+h+'" fill="'+palette.bg+'"/><g font-family="Microsoft YaHei, PingFang SC, Noto Sans CJK SC, sans-serif">'+txt(45,58,title,34)+txt(45,100,description,22,palette.muted)+drawing+'</g></svg>\n';
 const target=path.join(root,slug,'images',name+'.svg');fs.mkdirSync(path.dirname(target),{recursive:true});fs.writeFileSync(target,svg);return target;
}
const outputs=[];
outputs.push(save('vision-01-map','pixels','像素位置、RGB通道与数值','2×2图有4个位置，每位置3个通道，共12个标量。',
 grid(70,170,[['红','绿'],['蓝','白']],120,[['#f4b8ae','#b9dcb5'],['#b8cbed','#fff']])+
 arrow(330,270,420,270)+
 card(460,150,205,250,'R 红通道',['255       0','  0     255'], '#f4d4cb')+
 card(700,150,205,250,'G 绿通道',['  0     255','  0     255'], '#d9ebd6')+
 card(940,150,205,250,'B 蓝通道',['  0       0','255     255'], '#d9e5f3')+
 txt(70,490,'空间轴：H=2、W=2',27)+txt(460,490,'通道轴：C=3；RGB顺序必须与模型协议一致',26)+
 txt(70,550,'增加batch轴只是组织多张图，不把它们的空间内容混成一张图。',24)));
outputs.push(save('vision-01-map','patches','图像切块 → 展平 → 可学习投影 → token序列','图中仅示意4块；224×224图配16×16 patch实际有196块。',
 grid(70,180,[['块1','块2'],['块3','块4']],105,[['#d9e8de','#dce8f4'],['#f3dfc4','#e8d8ed']])+
 arrow(310,280,395,280)+card(420,180,230,220,'每块展平',['16×16×3','768个输入值'])+
 arrow(660,280,725,280)+card(750,180,380,220,'共享权重W：768×D',['每块输出D维向量','输出shape：196×D'],palette.blue)+
 txt(70,500,'块1   →   块2   →   块3   →   块4   →   …',27)+
 txt(70,555,'序列次序与空间位置表示需要明确；连续视觉token不必先变成文字。',24)));
outputs.push(save('vision-01-map','interfaces','双塔对齐与生成式VLM的不同输出接口','示意常见路线，具体连接器、冻结策略与注意力结构需要逐模型核对。',
 card(60,150,215,140,'图像编码器',['图片 → 向量u'])+card(60,330,215,140,'文本编码器',['候选 → 向量v'])+
 arrow(290,230,390,230)+arrow(290,400,390,400)+card(420,205,260,220,'向量比较',['u与v相似度','输出候选排序'],palette.orange)+
 line(740,130,740,520,'#96a69b',true)+card(790,150,330,100,'图像 → 视觉表示',[],palette.blue)+
 card(790,285,330,100,'连接器 + 问题',[],palette.orange)+card(790,420,330,100,'LLM → 文本答案',[],palette.green)+
 txt(60,565,'检索 / 零样本分类',27)+txt(790,565,'逐token条件生成',27)));
outputs.push(save('vision-01-map','evidence','把感知、证据与推理分开诊断','原图、替图、人工描述和工具结果是不同对照，不可忽略任务简化或答案泄露。',
 card(60,180,275,210,'输入对照',['原图 / 反事实替图','正确事实描述','工具产生的证据'])+
 arrow(355,280,425,280)+card(450,180,275,210,'中间过程',['是否看清？','是否对应正确区域？','是否使用相关证据？'],palette.blue)+
 arrow(745,280,815,280)+card(840,180,290,210,'输出评价',['事实正确性','推理正确性','成本与不确定性'],palette.orange)+
 txt(60,480,'描述答对、原图答错：提示视觉路径可能有问题，但尚不能唯一归因于encoder。',23)+
 txt(60,540,'控制问题、样本、预算、描述信息量；报告失败类型与统计波动。',25)));
outputs.push(save('vision-02-math','matmul','矩阵乘法：每项输出是一行与一列的点积','A:2×3，B:3×2，C=AB:2×2；公共轴3被求和。',
 grid(75,175,[[1,2,3],[4,5,6]],65,[['#f3dfc4','#f3dfc4','#f3dfc4']])+
 txt(130,370,'A',30)+txt(305,270,'×',40)+grid(405,145,[[1,0],[0,1],[1,1]],65,[['#d9e8de'],['#d9e8de'],['#d9e8de']])+
 txt(450,385,'B',30)+txt(610,270,'=',40)+grid(730,175,[[4,5],[10,11]],75,[['#f3dfc4']])+
 txt(780,370,'C',30)+lines(75,470,['C₁₁ = 1×1 + 2×0 + 3×1 = 4','C₁₂ = 1×0 + 2×1 + 3×1 = 5'],27,45)+
 txt(730,505,'不是逐元素相乘',27)));
outputs.push(save('vision-02-math','projection','投影：保留沿u方向的信息','x=(3,4)，u=(1,0)；投影=(3,0)，残差=(0,4)。',
 line(110,460,730,460)+line(160,510,160,140)+line(160,460,530,160,palette.ink)+
 line(160,460,530,460,'#3b7e57')+line(530,460,530,160,palette.red,true)+
 txt(550,155,'x=(3,4)',28)+txt(330,500,'投影=(3,0)',27,'#3b7e57')+txt(550,320,'残差',25,palette.red)+
 rect(510,440,20,20,'none')+card(795,190,340,250,'正交条件',['uᵀ(x−au)=0','a=(uᵀx)/(uᵀu)','本例a=3'],palette.blue)+
 txt(100,570,'残差与u点积为0；投影是保留指定方向，不是无损压缩。',25)));
outputs.push(save('vision-02-math','backprop','一次完整反向传播：前向值与梯度必须区分','x=(1,2)，w=(1,−1)，b=3，v=2，c=0，目标y=1。',
 card(45,190,215,165,'线性汇总',['a = 1−2+3 = 2'])+arrow(275,270,320,270)+
 card(335,190,215,165,'ReLU',['h = 2'],palette.blue)+arrow(565,270,610,270)+
 card(625,190,215,165,'输出层',['预测 = 2×2 = 4'])+arrow(855,270,900,270)+
 card(915,190,240,165,'平方损失',['L = (4−1)²/2','L = 4.5'],palette.orange)+
 lines(55,430,['到预测的梯度：3','到h的梯度：3×v=6','到a的梯度：6×1=6'],25,42,palette.red)+
 lines(590,430,['∂L/∂v = 3×h = 6','∂L/∂w₁ = 6×1 = 6','∂L/∂w₂ = 6×2 = 12'],25,42,palette.red)+
 txt(50,600,'全部梯度在旧参数下计算；统一更新后重新做完整前向。',23)));
outputs.push(save('vision-02-math','broadcast','广播陷阱：逐样本误差变成两两配对','示意B=3；target:(B,1)，prediction:(B,)会广播到(B,B)。',
 card(65,160,480,130,'期望：同一个样本配对',['样本1↔1，样本2↔2，样本3↔3'],palette.green)+
 grid(100,350,[['1↔1'],['2↔2'],['3↔3']],70)+txt(235,410,'只应有3个误差项',26)+
 card(630,160,490,130,'错误：所有样本两两配对',['shape=(3,3)，出现9个误差项'],palette.orange)+
 grid(660,335,[['1↔1','1↔2','1↔3'],['2↔1','2↔2','2↔3'],['3↔1','3↔2','3↔3']],95)+
 txt(70,600,'先统一预测和标签shape，再核对轴语义；程序不报错不等于任务正确。',23)));
outputs.push(save('vision-03-probability','bayes','罕见事件：高命中率不等于高阳性真实性','1000个工件、1%缺陷、命中90%、正常误报5%；分支数是期望数量。',
 card(55,180,240,150,'1000个工件',['缺陷10 / 正常990'])+
 arrow(310,250,395,250)+card(425,145,300,170,'缺陷分支',['报阳性：10×0.9=9','报阴性：1'],palette.green)+
 card(425,350,300,170,'正常分支',['误报：990×0.05=49.5','正确阴性：940.5'],palette.orange)+
 card(820,235,310,240,'只看阳性',['真缺陷：9','总阳性：58.5','9/58.5 ≈ 15.38%'],palette.blue)+
 txt(50,600,'后验比例取决于条件性能与先验发生率；不能把命中率当作后验概率。',23)));
outputs.push(save('vision-03-probability','softmax','三类别手算：logits → 概率 → loss → 梯度','目标第二类，q=(0,1,0)；自然对数和归一化分母不可省略。',
 card(50,170,260,220,'分数z',['(2,1,0)','先减max=2','变为(0,−1,−2)'])+
 arrow(325,275,390,275)+card(415,170,340,220,'softmax概率p',['0.66524','0.24473','0.09003'],palette.blue)+
 arrow(770,275,835,275)+card(860,170,290,220,'目标类loss',['−ln(0.24473)','≈1.40761'],palette.orange)+
 txt(55,475,'对logits梯度：p−q = (0.66524, −0.75527, 0.09003)',27)+
 txt(55,535,'下降更新降低错误类分数、提高目标类分数；它还需链式传到网络参数。',24)));
outputs.push(save('vision-04-images','aliasing','降采样混叠：高频变化可能消失','同一条交替信号，以不同采样相位得到全0或全1。',
 txt(55,190,'原信号',27)+grid(250,145,[[0,1,0,1,0,1,0,1]],90,[['#fff','#c8d9ce','#fff','#c8d9ce','#fff','#c8d9ce','#fff','#c8d9ce']])+
 txt(55,335,'偶数位置',27)+grid(250,290,[[0,0,0,0]],90)+
 txt(55,480,'奇数位置',27)+grid(250,435,[[1,1,1,1]],90,[['#c8d9ce','#c8d9ce','#c8d9ce','#c8d9ce']])+
 txt(55,585,'抗混叠先抑制不能表示的高频，再降采样；它也会削弱细节。',25)));
outputs.push(save('vision-04-images','convolution','局部相关手算：滑动窗口与核逐项相乘求和','不补边，stride=1；3×3输入与2×2核得到2×2输出。',
 grid(70,155,[[1,2,3],[4,5,6],[7,8,9]],70,[['#f3dfc4','#f3dfc4'],['#f3dfc4','#f3dfc4']])+
 txt(325,260,'核',28)+grid(405,185,[[1,0],[0,'−1']],80)+arrow(590,265,690,265)+
 grid(750,185,[['−4','−4'],['−4','−4']],85)+
 lines(65,470,['左上输出：1×1 + 2×0 + 4×0 + 5×(−1) = −4','严格卷积翻转核，本例输出变为+4。'],27,48)));
outputs.push(save('vision-04-images','coordinates','crop与resize：模型坐标必须映回原图','原图1000×800，crop原点(200,100)，尺寸400×300，缩放s=2。',
 rect(65,150,475,345,'#e6ece6')+rect(160,210,230,190,palette.green)+
 txt(180,245,'crop区域',26)+txt(90,530,'原点(200,100)',26)+txt(90,570,'原图点(350,220)',26)+
 '<circle cx="245" cy="300" r="8" fill="#a34435"/>'+arrow(570,310,660,310)+
 rect(705,180,405,305,palette.blue)+txt(730,225,'resize后800×600',27)+
 '<circle cx="857" cy="302" r="8" fill="#a34435"/>'+txt(760,355,'新坐标(300,240)',27)+
 lines(715,530,['x′=2(x−200)','逆变换x=x′/2+200'],24,38)));
outputs.push(save('vision-05-training','training','训练更新与验证选模必须分开','train参与梯度更新；validation用于选模；test应保留独立评估角色。',
 card(50,165,260,170,'训练数据',['前处理 → forward','loss → backward'])+arrow(325,250,390,250)+
 card(415,165,315,170,'optimizer更新',['梯度 + 历史状态','参数变为下一步'],palette.blue)+
 arrow(745,250,810,250)+card(835,165,310,170,'保存checkpoint',['权重 / 状态 / step','可恢复训练轨迹'],palette.green)+
 card(95,405,470,150,'验证：eval + 不追踪梯度',['按固定协议计算指标、选择配置'],palette.orange)+
 card(630,405,475,150,'测试：独立最终评估',['反复据test修改会造成选择偏差'],palette.blue)));
outputs.push(save('vision-05-training','normalization','BN与LN：归约轴不同，结果语义也不同','示意B×D矩阵；CNN的BN通常还在空间轴上统计。',
 txt(80,170,'BN：每特征跨样本',28)+grid(90,215,[[1,3],[2,6],[3,9]],85,[['#d9e8de','#dce8f4'],['#d9e8de','#dce8f4'],['#d9e8de','#dce8f4']])+
 txt(630,170,'LN：每样本跨特征',28)+grid(640,215,[[1,3],[2,6],[3,9]],85,[['#d9e8de','#d9e8de'],['#dce8f4','#dce8f4'],['#f3dfc4','#f3dfc4']])+
 txt(80,535,'训练batch影响BN统计；eval常用running统计。',24)+
 txt(630,535,'[1,3] → 均值2、方差1 → [−1,1]',24)+
 txt(80,600,'γ和β可学习；ε控制数值稳定；轴定义必须对应实际模块接口。',24)));
outputs.push(save('vision-06-classical-cnn','sift-scale','SIFT：高斯层 → DoG → 三维邻域极值','s=3时构造6张高斯图、5张DoG图；内部候选比较26个邻居。',
 [0,1,2,3,4,5].map(i=>rect(60,145+i*65,235,48,palette.green)+txt(78,178+i*65,'L：σ × k'+['⁰','¹','²','³','⁴','⁵'][i],23)).join('')+
 [0,1,2,3,4].map(i=>arrow(305,170+i*65,375,200+i*65)+line(305,235+i*65,375,200+i*65)+rect(400,177+i*65,175,45,palette.blue)+txt(415,208+i*65,'相邻层相减',22)).join('')+
 txt(650,180,'下尺度：9个',25)+txt(840,180,'同尺度：8个',25)+txt(650,375,'上尺度：9个',25)+
 grid(650,205,[['•','•','•'],['•','•','•'],['•','•','•']],49)+grid(850,205,[['•','•','•'],['•','点','•'],['•','•','•']],49,[[],[palette.white,palette.orange,palette.white]])+
 grid(650,400,[['•','•','•'],['•','•','•'],['•','•','•']],49)+lines(845,425,['比较极大或极小','再做定位与剔除','k = 2^(1/3)'],23,38)+
 txt(60,600,'左侧每个框是一张图；右侧每个小格是尺度图中的一个像素位置。',24)));
outputs.push(save('vision-06-classical-cnn','hog-blocks','HOG：局部方向统计 → 重叠块归一化 → 窗口向量','示意4×4个cell；经典64×128窗口实际有8×16个cell。',
 grid(70,165,[['↑','↗','→','↘'],['↗','↑','↘','→'],['→','↘','↑','↗'],['↘','→','↗','↑']],77)+
 '<rect x="66" y="161" width="155" height="155" fill="none" stroke="#28734c" stroke-width="6"/>'+
 '<rect x="145" y="240" width="155" height="155" fill="none" stroke="#386fa5" stroke-width="6"/>'+
 txt(70,520,'绿框、蓝框重叠1个cell',25)+txt(70,565,'箭头仅示意梯度方向',24)+
 arrow(410,315,480,315)+card(510,170,290,180,'每个cell',['9个unsigned方向bin','幅值与插值决定票重'],palette.green)+
 card(850,170,285,180,'每个block',['2×2个cell','拼接并归一化：36维'],palette.blue)+
 card(510,390,625,175,'全部block按固定次序拼接',['7列 × 15行 × 36维 = 3780维','一个cell可参与多个block的归一化'],palette.orange)));
outputs.push(save('vision-06-classical-cnn','conv-backward','反传：共享权重累计梯度，最大池化按选中位置路由','对应算例M与N：左侧卷积无ReLU；右侧四个窗口都选择中心9。',
 txt(70,155,'输入X',27)+grid(70,180,[[1,2,3],[4,5,6],[7,8,9]],58)+txt(305,155,'共享核W',27)+grid(305,180,[[1,0],[0,-1]],58)+
 arrow(440,240,490,240)+grid(515,180,[[-4,-4],[-4,-4]],58)+
 lines(70,435,['四个输出都参与核梯度：','∂L/∂W₀₀ = −4 × (1+2+4+5) = −48','同一输入被多处使用，也累计全部路径。'],24,42)+
 line(710,140,710,570,'#95a99b',true)+txt(780,155,'重叠最大池化',27)+grid(800,180,[[1,2,3],[4,9,6],[7,8,5]],67,[[],[palette.white,palette.orange,palette.white]])+
 lines(780,440,['上游梯度为1、2、3、4','中心9接收总梯度10','其他位置接收0'],24,42)));
outputs.push(save('vision-06-classical-cnn','cnn-architectures','LeNet-5与AlexNet：尺寸变化、通道与分类头','上：原LeNet通道连接；下：227输入、首层无padding的AlexNet教学尺寸。',
 txt(60,148,'LeNet输入：1×32×32',27)+
 [['C1','6×28×28'],['S2','6×14×14'],['C3 稀疏','16×10×10'],['S4','16×5×5'],['C5','120×1×1'],['F6','84维']].map((a,i)=>card(60+i*180,180,160,115,a[0],[a[1]],i%2?palette.blue:palette.green)+(i<5?arrow(222+i*180,238,237+i*180,238):'')).join('')+
 txt(60,345,'距离输出：84维表示与类别模板比较；较小距离更匹配。',25)+line(60,380,1135,380,'#95a99b',true)+
 txt(60,430,'AlexNet输入：3×227×227（论文标注224，正文单独说明）',26)+
 [['Conv1','96×55×55'],['Pool1','96×27×27'],['Conv2，g=2','256×27×27'],['Pool2','256×13×13']].map((a,i)=>card(60+i*275,470,250,110,a[0],[a[1]],i%2?palette.blue:palette.green)).join('')+
 [['Conv3','384×13×13'],['Conv4，g=2','384×13×13'],['Conv5，g=2','256×13×13'],['Pool5','256×6×6']].map((a,i)=>card(60+i*275,620,250,110,a[0],[a[1]],i%2?palette.blue:palette.green)).join('')+
 txt(60,795,'空间路线：Conv1 → Pool1 → Conv2 → Pool2 → Conv3 → Conv4 → Conv5 → Pool5',24)+txt(60,845,'展开9216维 → FC4096 → FC4096 → FC1000 → softmax',26),900));
outputs.push(save('vision-07-vgg-inception','vgg-stages','VGG16：五组卷积、五次池化与大分类头','卷积使用3×3、stride1、padding1；每个stage最后池化使空间边长减半。',
 [
  ['Stage1',['64通道','224 → 112','卷积 × 2']],['Stage2',['128通道','112 → 56','卷积 × 2']],
  ['Stage3',['256通道','56 → 28','卷积 × 3']],['Stage4',['512通道','28 → 14','卷积 × 3']],['Stage5',['512通道','14 → 7','卷积 × 3']],
 ].map((a,i)=>card(50+i*220,165,200,200,a[0],a[1],i%2?palette.blue:palette.green)).join('')+
 txt(50,430,'13个卷积 + 3个全连接 = 16个带权重层',28)+
 card(50,470,1090,160,'最后表示512×7×7 → 展平25088维',['FC4096 → FC4096 → FC1000 → softmax','大分类头占约89.36%的参数；卷积占绝大多数MAC。'],palette.orange),700));
outputs.push(save('vision-07-vgg-inception','inception-branches','Inception 3a：降维再做大核，四个输出沿通道拼接','输入192×28×28；四分支输出64、128、32、32通道，合计256。',
 card(45,310,220,130,'输入192通道',['空间28×28'],palette.orange)+
 line(280,200,280,560)+line(265,375,280,375)+
 [200,320,440,560].map(y=>arrow(280,y,335,y)).join('')+
 rect(350,160,510,80,palette.green)+txt(375,210,'1×1：192 → 64',27)+
 rect(350,280,210,80,palette.green)+txt(367,330,'1×1：192→96',24)+arrow(575,320,635,320)+rect(650,280,210,80,palette.blue)+txt(667,330,'3×3：96→128',24)+
 rect(350,400,210,80,palette.green)+txt(367,450,'1×1：192→16',24)+arrow(575,440,635,440)+rect(650,400,210,80,palette.blue)+txt(667,450,'5×5：16→32',24)+
 rect(350,520,210,80,palette.blue)+txt(367,570,'3×3最大池化',25)+arrow(575,560,635,560)+rect(650,520,210,80,palette.green)+txt(667,570,'1×1：192→32',24)+
 [200,320,440,560].map(y=>line(860,y,915,y)).join('')+line(915,200,915,560)+arrow(915,375,945,375)+
 card(960,300,200,160,'concat',['256通道','空间28×28'],palette.orange)+
 txt(45,680,'96与16是分支中间通道；它们不重复加入最终256通道。',26),750));
outputs.push(save('vision-07-vgg-inception','factorization','顺序分解、平行分支与reduction的区别','核名称相同也不代表计算图相同；concat必须对齐空间尺寸。',
 card(55,160,260,140,'顺序',['输入 → 1×3 → 3×1','单输出可看3×3'],palette.green)+
 card(390,160,360,140,'平行',['同一输入各做1×3和3×1','输出拼接；分支各看一条线'],palette.blue)+
 card(825,160,310,140,'结构约束',['单中间通道、线性时','非对称分解为外积核'],palette.orange)+
 txt(55,365,'下采样两条路径：输入空间35×35',28)+
 card(55,405,455,160,'3×3卷积，stride2，padding0',['输出17×17；通道可改变'])+
 card(620,405,515,160,'3×3池化，stride2，padding0',['输出17×17；原通道保留'],palette.blue)+
 txt(55,635,'两条路径可沿通道concat；若一条padding1变18×18，就不能直接拼接。',25),700));
outputs.push(save('vision-08-resnet-densenet','residual-paths','残差路径：更新分支与直达参照','同shape才能直接相加；投影会改变shortcut；加法后激活会门控梯度。',
 card(55,205,200,125,'输入x',['C×H×W'],palette.orange)+
 line(270,170,270,420)+line(255,265,270,265)+arrow(270,210,330,210)+
 card(350,160,350,110,'残差分支F(x)',['卷积、归一化、激活'])+
 line(270,420,825,420)+line(825,420,825,270)+txt(400,400,'恒等shortcut：x',26)+
 arrow(710,210,775,210)+card(790,165,155,105,'相加',['x+F(x)'],palette.blue)+
 arrow(955,210,995,210)+card(1010,165,150,105,'输出',['同shape'],palette.orange)+
 card(55,490,500,145,'后激活：先相加，再ReLU',['直达路径仍经过加法后的ReLU','负坐标可截断上游梯度'],palette.blue)+
 card(625,490,535,145,'预激活：BN/ReLU放在分支内',['加法后不再加ReLU','同shape路径可以严格保留x']),700));
outputs.push(save('vision-08-resnet-densenet','resnet-stages','ResNet18与50：空间层级相同，块宽度不同','输入224×224；stem和池化后56×56；表中每项为输出通道与block数量。',
 txt(55,165,'Stage',26)+[1,2,3,4].map((s,i)=>txt(300+i*220,165,String(s),28)).join('')+
 txt(55,235,'空间边长',26)+[56,28,14,7].map((s,i)=>txt(300+i*220,235,String(s),28)).join('')+
 txt(55,325,'ResNet18',27)+[64,128,256,512].map((s,i)=>card(265+i*220,275,195,140,s+'通道',['Basic × 2'],palette.green)).join('')+
 txt(55,505,'ResNet50',27)+[256,512,1024,2048].map((s,i)=>card(265+i*220,455,195,140,s+'通道',['Bottleneck × '+[3,4,6,3][i]],palette.blue)).join('')+
 txt(55,665,'瓶颈内部：64、128、256、512 → 末1×1分别扩展为4倍输出通道',25),730));
outputs.push(save('vision-08-resnet-densenet','dense-connections','DenseNet：读取旧特征列表，再追加新特征','示意C₀=16、k=8；一个dense block内空间不变，transition再压缩和下采样。',
 card(55,165,210,130,'初始x₀',['16通道'],palette.orange)+
 [1,2,3,4].map((s,i)=>card(310+i*215,165,195,130,'新特征x'+s,['8通道'],palette.green)).join('')+
 txt(55,360,'第1层读16',25)+txt(310,360,'第2层读24',25)+txt(550,360,'第3层读32',25)+txt(790,360,'第4层读40',25)+
 line(55,405,1135,405,'#95a99b',true)+
 card(55,455,455,160,'block输出：16+4×8=48通道',['concat保留旧通道与新增通道','梯度按切片分开，再累加复用路径'],palette.blue)+
 arrow(525,535,610,535)+card(635,455,500,160,'transition',['1×1压缩：48 → 24通道','2×2平均池化：空间边长减半'],palette.orange),690));
outputs.push(save('vision-09-efficient-cnn','depthwise-pointwise','空间混合与通道混合：普通卷积 vs DW+PW','DW每通道独立过滤，PW在每位置混合通道；两者合起来才能同时完成两类混合。',
 card(55,170,300,170,'普通3×3卷积',['每输出读全部输入通道','权重9×Cᵢ×Cₒ'],palette.blue)+
 card(470,170,310,170,'Depthwise 3×3',['每输入通道一张核','权重9×Cᵢ'])+
 arrow(795,255,845,255)+card(860,170,285,170,'Pointwise 1×1',['通道Cᵢ → Cₒ','权重Cᵢ×Cₒ'],palette.orange)+
 line(55,400,1145,400,'#95a99b',true)+
 txt(55,455,'32输入、64输出：普通18432权重；DW288 + PW2048 = 2336',26)+
 txt(55,515,'输出56×56：普通57.80M MAC；可分离7.33M MAC',27)+
 txt(55,575,'减少计算也限制核的结构；实际速度还取决于访存、布局和算子实现。',25),650));
outputs.push(save('vision-09-efficient-cnn','inverted-blocks','三种瓶颈：比较宽度与空间卷积的位置','宽度数字为示例；MobileNet在展开空间做DW，ConvNeXt先做DW再扩展。',
 txt(55,165,'ResNet瓶颈：256 → 64 → 64 → 256',27)+
 card(55,195,310,120,'1×1降维',['256 → 64'])+card(445,195,310,120,'3×3普通卷积',['64 → 64'],palette.blue)+card(835,195,310,120,'1×1升维',['64 → 256'],palette.orange)+
 txt(55,370,'MobileNetV2：24 → 144 → 144 → 24',27)+
 card(55,400,310,120,'1×1扩展',['24 → 144'])+card(445,400,310,120,'3×3 depthwise',['144通道各自处理'],palette.blue)+card(835,400,310,120,'线性投影',['144 → 24'],palette.orange)+
 txt(55,575,'ConvNeXt：96 → DW96 → LN → MLP384 → 96',27)+
 card(55,605,310,120,'7×7 depthwise',['96通道各自处理'],palette.blue)+card(445,605,310,120,'LN与线性扩展',['96 → 384，GELU'])+card(835,605,310,120,'线性投影',['384 → 96'],palette.orange)+
 txt(55,785,'shortcut对齐各块的长期状态；同尺寸/通道条件满足时才可恒等相加。',25),850));
outputs.push(save('vision-09-efficient-cnn','se-gate','SE：压缩空间统计 → 预测通道门 → 缩放原特征','通道门依赖当前输入；空间位置共享同通道gate，并不等于token self-attention。',
 card(55,180,230,170,'特征U',['C×H×W','保留原空间特征'],palette.orange)+
 arrow(300,260,345,260)+card(360,180,230,170,'GAP',['每通道平均','得到C维z'])+
 arrow(605,260,650,260)+card(665,180,230,170,'小MLP',['C → hidden → C','sigmoid门a'],palette.blue)+
 arrow(910,260,955,260)+card(970,180,175,170,'缩放',['V = a⊙U','空间不变'],palette.orange)+
 line(175,365,175,425)+line(175,425,1060,425)+line(1060,425,1060,365)+txt(470,410,'原特征直接送到缩放处',25)+
 txt(55,505,'反传有两条路径：直接缩放 + 输入改变gate后的间接影响',27)+
 txt(55,565,'若把gate当常数，只乘a，会漏掉门预测网络返回的梯度。',25),650));
outputs.push(save('vision-09-efficient-cnn','compound-scaling','复合缩放：同一资源预算怎样分配三条轴','近似成本 d×w²×r²；DW、SE、首尾层和整数取整使真实计算偏离近似。',
 card(55,180,310,210,'深度d = α^φ',['增加block重复数','计算近似一次方','参数也随深度增加'])+
 card(445,180,310,210,'宽度w = β^φ',['增加通道数','PW计算近似平方','DW计算只按一次方'],palette.blue)+
 card(835,180,310,210,'边长r = γ^φ',['提高图像分辨率','计算、激活近似平方','卷积权重数量不变'],palette.orange)+
 txt(55,470,'α=1.2，β=1.1，γ=1.15：一档近似成本 ×1.92027',28)+
 txt(55,530,'各轴连续公式 → 通道/层数/分辨率取整 → 真实逐层账本',27)+
 txt(55,590,'最佳比例依赖模型、任务、数据与设备；近似成本不是精确全网计数。',25),680));
outputs.push(save('vision-10-structured-tasks','task-outputs','同一张图，不同问题需要不同输出空间','分类向量、对象集合、像素网格与时间身份不能直接互换；标签与指标也不同。',
 card(55,170,495,160,'全局：分类 / 检索',['整图K类分数，或D维embedding','标签对应图或查询与库的相关关系'])+
 card(645,170,495,160,'对象：检测 / 实例',['可变数量的框、类别与mask','匹配对象，处理重复与漏检'],palette.blue)+
 card(55,410,495,160,'稠密：分割 / 光流 / 深度',['每位置类别、二维位移或距离','坐标、单位与有效mask要一致'],palette.orange)+
 card(645,410,495,160,'具名与时间：姿态 / 跟踪',['关键点部位顺序，跨帧track ID','位置正确仍可能身份关联错误']),650));
outputs.push(save('vision-10-structured-tasks','hrnet-fusion','HRNet：保留高路，逐步加入低路并反复交换','水平为网络深度，垂直为分辨率；融合先对齐通道与网格，再求和。',
 [0,1,2,3].map(i=>{
   const y=180+i*115;
   const start=180+i*240;
   return txt(50,y+30,['1/4','1/8','1/16','1/32'][i],27)+line(start,y+20,1130,y+20,i%2?'#386fa5':'#28734c')+
    [0,1,2,3].filter(j=>j>=i).map(j=>rect(180+j*240,y-15,180,70,i%2?palette.blue:palette.green)+txt(270+j*240,y+30,[32,64,128,256][i]+'通道',23,palette.ink,'middle')).join('');
 }).join('')+
 [1,2,3].map(j=>line(390+j*240,205,390+j*240,205+j*115,'#a98554',true)).join('')+
 txt(50,700,'低→高：1×1对齐通道再上采样；高→低：多次3×3 stride2',26)+
 txt(50,755,'示意W32后续宽度；stem/stage1的具体通道与块数由配置决定。',24),810));
outputs.push(save('vision-10-structured-tasks','raft-iteration','RAFT：全对相关可复用，流状态循环更新','流保持在1/8网格；相关金字塔提供多尺度查找，最后上采样并转换向量单位。',
 card(55,170,270,140,'两帧特征',['共享编码器','每帧D×h×w'])+arrow(340,240,390,240)+
 card(405,170,330,140,'全对相关 / 金字塔',['N×N相关，N=h×w','仅池化目标位置轴'],palette.blue)+
 card(825,170,320,140,'context与隐藏态',['来自第一帧','为迭代提供空间信息'],palette.orange)+
 line(580,325,580,375)+line(980,325,980,375)+
 card(55,420,270,170,'当前流fₜ',['目标中心p+fₜ','初始通常零流'],palette.orange)+
 arrow(340,500,390,500)+card(405,420,330,170,'查找 + ConvGRU',['按当前流读取相关证据','更新隐藏状态hₜ'],palette.blue)+
 arrow(750,500,800,500)+card(825,420,320,170,'增量与新流',['预测Δfₜ','fₜ₊₁ = fₜ + Δfₜ'])+
 line(980,605,980,650)+line(980,650,190,650)+line(190,650,190,605)+txt(400,690,'多轮共享权重；detach规则决定实际梯度图',24)+
 txt(55,755,'全图输出：9邻居凸组合，8×8子位置；粗网格流向量先乘8。',26),820));
console.log(JSON.stringify({generated:outputs.length,files:outputs.map(p=>path.relative(root,p))},null,2));
