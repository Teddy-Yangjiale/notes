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
 const target=path.join(root,slug,'images',name+'.svg');fs.mkdirSync(path.dirname(target),{recursive:true});if(!fs.existsSync(target)||fs.readFileSync(target,'utf8').replaceAll('\r\n','\n')!==svg)fs.writeFileSync(target,svg);return target;
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
outputs.push(save('vision-11-attention-transformer','qkv-read','Attention：先匹配，再读取；两个求和轴不同','行是位置，列是通道。查询数决定输出位置数；key与value的候选位置必须对应。',
 card(55,160,320,160,'查询输入 Xq',['Nq×Dq → Q：Nq×dk','用WQ生成查询条件'])+
 card(440,160,320,160,'记忆输入 Xm',['Nk×Dm → K：Nk×dk','用WK生成匹配特征'],palette.blue)+
 card(825,160,320,160,'同一记忆 Xm',['Nk×Dm → V：Nk×dv','用WV生成读取内容'],palette.orange)+
 card(55,415,320,180,'QKᵀ / √dk',['沿dk通道做点积','输出Nq×Nk位置对'],palette.blue)+
 arrow(390,500,425,500)+card(440,415,320,180,'mask + 行softmax',['沿Nk候选轴归一化','每query分配读取权重'])+
 arrow(775,500,810,500)+card(825,415,320,180,'A V',['沿Nk候选轴求和','输出Nq×dv'],palette.orange)+
 line(215,335,215,400)+line(600,335,600,365)+line(215,365,600,365)+line(985,335,985,400)+
 txt(55,690,'Q/K决定从哪里读；V决定读出什么；A不是最终任务类别概率。',26)+
 txt(55,748,'缩放、mask、softmax、value汇聚和输出投影各有独立计算角色。',25),810));
outputs.push(save('vision-11-attention-transformer','attention-masks','mask定义允许信息：看清query行与key列','绿格允许、灰格屏蔽。因果关系按真实时间定义，不能仅靠局部矩阵行号。',
 txt(55,160,'双向有效位置',28)+txt(450,160,'方形因果（含对角）',28)+txt(845,160,'padding key',28)+
 grid(55,210,[['✓','✓','✓','✓'],['✓','✓','✓','✓'],['✓','✓','✓','✓'],['✓','✓','✓','✓']],65,Array.from({length:4},()=>Array(4).fill(palette.green)))+
 grid(450,210,[['✓','×','×','×'],['✓','✓','×','×'],['✓','✓','✓','×'],['✓','✓','✓','✓']],65,Array.from({length:4},(_,i)=>Array.from({length:4},(_,j)=>j<=i?palette.green:'#e4e4e0')))+
 grid(845,210,[['✓','✓','×','×'],['✓','✓','×','×'],['✓','✓','×','×'],['✓','✓','×','×']],65,Array.from({length:4},()=>[palette.green,palette.green,'#e4e4e0','#e4e4e0']))+
 txt(55,530,'行：谁读取；列：从谁读取。禁止位置在softmax前排除。',26)+
 card(55,590,1090,130,'缓存例：4个旧key + 1个新key，只有1条新query',['query全局时间4，key时间0—4 → 五列都允许。1×5不能机械左上三角。'],palette.orange),780));
outputs.push(save('vision-11-attention-transformer','transformer-paths','残差与来源：Pre/Post-LN、编码器与解码器','F代表MHA或FFN；归一化位置改变梯度路径，cross的输出属于目标query位置。',
 card(55,160,510,170,'Post-LN：LN(x + F(x))',['分支输出相加后，直达路径仍经过LN','F=0时输出LN(x)'],palette.blue)+
 card(635,160,510,170,'Pre-LN：x + F(LN(x))',['分支读归一化输入；直达x路径保留','F=0时输出x'])+
 card(55,415,310,240,'编码器',['源输入 → 源状态','双向self-attention','逐位置FFN'],palette.green)+
 card(445,415,310,240,'解码器self',['右移目标 → 目标状态','因果self-attention','只读取允许的前缀'],palette.orange)+
 card(835,415,310,240,'解码器cross',['Q：目标状态','K/V：编码器记忆','输出仍是目标位置'],palette.blue)+
 arrow(770,530,820,530)+line(210,675,210,720)+line(210,720,990,720)+line(990,720,990,675)+
 txt(330,758,'编码器输出作为cross的记忆，不与目标行直接相加',25)+
 txt(55,815,'完整decoder常有self → cross → FFN；decoder-only可以没有独立cross。',24),875));
outputs.push(save('vision-11-attention-transformer','attention-costs','三种账本：模型参数、位置对、历史K/V','标准编码器M=4D的矩阵MAC：12ND² + 2N²D；参数与输入长度N无关。',
 card(55,175,310,220,'共享权重',['Q/K/V/输出投影','FFN与归一化参数','同权重用于各token','总数不随N变'])+
 card(445,175,310,220,'显式位置对A',['B×H×Nq×Nk','self时随N平方','一张A ≠ 全部显存','内核可避免长期保存'],palette.blue)+
 card(835,175,310,220,'KV cache',['每层旧K与旧V','按缓存token数增长','只在适用的信息图成立','不是整张历史attention'],palette.orange)+
 txt(55,480,'N → 2N：线性投影/FFN约×2；位置对核心约×4。',27)+
 txt(55,540,'图片边长×2、patch边长不变：token约×4，位置对约×16。',26)+
 txt(55,600,'单token增量读取n个key：核心约2nD MAC；仍需逐步生成。',25)+
 txt(55,670,'更少MAC、更多并行、更少外存读写与实测更快，是不同结论。',25),750));
outputs.push(save('vision-12-vit','patch-tokenize','ViT输入：保留块内顺序，再使用共享线性投影','4×4灰度图、P=2；第一块是1、2、5、6，不能把整图第一行当作一个块。',
 grid(55,180,[['1','2','3','4'],['5','6','7','8'],['9','10','11','12'],['13','14','15','16']],68,
 [['#d9e8de','#d9e8de','#dce8f4','#dce8f4'],['#d9e8de','#d9e8de','#dce8f4','#dce8f4'],['#f3dfc4','#f3dfc4','#e6deee','#e6deee'],['#f3dfc4','#f3dfc4','#e6deee','#e6deee']])+
 arrow(340,300,415,300)+grid(445,180,[['1','2','5','6'],['3','4','7','8'],['9','10','13','14'],['11','12','15','16']],68)+
 arrow(745,300,795,300)+card(825,180,320,270,'共享投影 E',['每行4个输入槽位','4×D权重 + D维bias','四行各输出D维token'],palette.blue)+
 txt(55,530,'切块展平是索引重排；投影是否丢失信息取决于维度与rank。',27)+
 txt(55,590,'相同E用于每块；kernel=P、stride=P卷积可实现同一投影。',26),670));
outputs.push(save('vision-12-vit','cls-context','CLS与patch一起更新：全局槽位不是输入标签','输入CLS是共享参数；读取图像之后，其输出状态才成为当前图像的全局表示。',
 card(55,175,300,145,'共享CLS c',['D个参数','每张图用同一起点'],palette.orange)+
 card(55,405,300,180,'N个patch token',['来自当前图像','每行D维局部表示'])+
 arrow(370,250,425,250)+arrow(370,485,425,485)+
 card(445,235,310,320,'共同编码',['CLS与patch都产生Q/K/V','位置表示加入各槽位','L层attention + MLP','各行获得上下文'],palette.blue)+
 arrow(770,310,815,310)+card(835,180,310,145,'全局接口',['取最终LN后的CLS','分类 / 检索头'],palette.orange)+
 arrow(770,490,815,490)+card(835,405,310,180,'空间接口',['保留N个patch状态','恢复原网格','稠密头 / VLM连接器'])+
 txt(55,685,'CLS不是目标类别one-hot；patch序列也不自动成为像素预测。',26),760));
outputs.push(save('vision-12-vit','position-resize','位置表迁移：特殊token单独保留，patch恢复二维','仅展示一个embedding通道；真实D个通道各自做空间插值，不混合通道。',
 card(55,165,285,120,'CLS位置值 99',['单独保留'],palette.orange)+
 grid(55,340,[['0','2'],['4','6']],105)+
 arrow(365,415,430,415)+card(450,320,260,205,'二维插值',['2×2 → 3×3','明确坐标/边界','这里用双线性'],palette.blue)+
 arrow(735,415,800,415)+grid(825,310,[['0','1','2'],['2','3','4'],['4','5','6']],100)+
 line(350,220,1125,220,palette.orange)+txt(825,185,'新CLS位置仍为99',25)+
 txt(55,655,'恢复网格需要源Gh/Gw与顺序；不能把含CLS的长度直接开平方。',26)+
 txt(55,715,'位置插值 ≠ 图像resize ≠ patch投影核resize。',27),785));
outputs.push(save('vision-12-vit','vit-ledger','ViT账本：更多token与更多参数不是同一件事','标准B/16：D768、L12、M3072、一个CLS；矩阵MAC不等于实测延迟。',
 card(55,170,495,220,'R224：14×14 patch + CLS',['T=197；参数86,567,656','整网约17.564G MAC','单张B1/H12/FP16 A：0.888MiB'])+
 card(645,170,495,220,'R384：24×24 patch + CLS',['T=577；学习位置表需处理','整网约55.484G MAC','单张B1/H12/FP16 A：7.620MiB'],palette.blue)+
 card(55,465,1085,160,'同R224改P32：token少，patch投影核更大',['T=50；参数88,224,232，略多于B/16；整网约4.409G MAC，明显更少。'],palette.orange)+
 txt(55,700,'训练峰值还包含FFN激活、参数、梯度、优化器与工作区。',26),770));
outputs.push(save('vision-12-vit','vit-transfer','迁移分清骨干、接口与训练范围','预训练目标与目标任务可能不同；新head的类别和初始化要单独核对。',
 card(55,160,300,180,'预训练骨干',['图像 → token编码','保存权重与输入协议','全局/patch接口明确'])+
 arrow(370,245,420,245)+card(440,160,315,180,'替换任务头',['旧类别头移除或调整','D → 新K类','零初始化是可选协议'],palette.orange)+
 arrow(770,245,820,245)+card(840,160,300,180,'目标数据与loss',['训练/验证/测试区分','类别顺序与mask','目标协议决定指标'],palette.blue)+
 card(55,430,495,170,'Linear probe',['冻结骨干，只训练新头','固定feature接口与提取模式'])+
 card(645,430,495,170,'全量微调',['骨干也参与梯度更新','分辨率、位置与预算一起记录'],palette.blue)+
 txt(55,680,'零头第一步：头梯度可非零，骨干的该loss梯度为零；以后可回传。',24),760));

outputs.push(save('vision-13-deit','dual-token','CLS与DIST：共享骨干，分别接收直接监督','特殊token是输入参数，教师类别通过loss进入；教师无需成为学生推理输入。',
 card(55,160,310,145,'图像 → patch投影',['N个patch，宽D'],palette.green)+
 card(55,350,310,145,'输入特殊位置',['CLS c / DIST d','拼接后T=N+2'],palette.blue)+
 arrow(385,255,455,255)+arrow(385,425,455,425)+
 card(480,240,270,245,'共享Transformer',['所有token交换信息','最终LN','取位置0、位置1'],palette.orange)+
 arrow(765,285,820,285)+arrow(765,430,820,430)+
 card(845,180,305,135,'CLS分类头',['真实标签/混合软目标'],palette.green)+
 card(845,380,305,135,'DIST分类头',['固定教师hard/soft目标'],palette.blue)+
 txt(55,610,'部署：只执行学生骨干和两头，按指定政策融合输出。',26),700));
outputs.push(save('vision-13-deit','head-fusion','融合顺序改变概率，甚至改变top-1','p=(0.8,0.1,0.1)，q=(0.01,0.495,0.495)；所有数字为教学构造。',
 card(60,160,500,215,'先softmax，再平均概率',['算术平均： (p+q)/2','(0.405, 0.2975, 0.2975)','第1类最大'],palette.green)+
 card(640,160,500,215,'先平均logits，再softmax',['归一化几何平均：sqrt(p×q)','(0.1674, 0.4163, 0.4163)','第2/3类并列最大'],palette.blue)+
 rect(60,425,1080,190,palette.orange)+
 lines(85,465,['softmax是非线性，两个操作一般不交换。','论文文字和实际代码路径分别核对；评价记录采用哪一种融合。','两头单独质量接近，也不保证融合必定改善。'],25,48),700));
outputs.push(save('vision-13-deit','shared-gradients','两个监督最终在共享参数处相加','局部方向可以同向、冲突或抵消；额外头不代表额外独立骨干。',
 card(60,155,420,165,'标签分支',['g_c=(1−α)(p_c−r)','特征梯度：g_c W_cᵀ'],palette.green)+
 card(720,155,420,165,'教师分支',['hard：g_d=α(p_d−e_teacher)','特征梯度：g_d W_dᵀ'],palette.blue)+
 line(270,330,270,385)+line(930,330,930,385)+line(270,385,930,385)+
 card(300,425,600,145,'attention / FFN / patch投影',['共同参数梯度 = 两条反传贡献之和'],palette.orange)+
 txt(60,635,'输出头只取两行，不表示patch没有梯度：attention会把依赖传回图像。',24),715));
outputs.push(save('vision-13-deit','augmentation-targets','混合输入与两个目标不是同一对象','Mixup/CutMix作用于输入和真实目标；在线教师在当前增强输入上重新预测。',
 card(55,155,290,180,'两张原图',['x_i，x_j','标签 r_i，r_j'],palette.green)+
 arrow(365,240,425,240)+card(450,155,330,180,'产生增强输入',['Mixup像素线性混合','CutMix复制实际区域'],palette.orange)+
 arrow(800,240,860,240)+card(885,155,265,180,'当前图 x̃',['学生、教师均读取','类别顺序要对应'],palette.blue)+
 card(55,405,500,185,'真实标签分支',['目标：λ r_i + (1−λ)r_j','CutMix λ使用裁剪后的实际面积'],palette.green)+
 card(640,405,510,185,'教师分支',['目标来自g_teacher(x̃)','一般不等于两原图教师输出的线性混合'],palette.blue)+
 txt(55,655,'缓存原图logits再混合，是不同监督协议，需独立验证。',26),725));
outputs.push(save('vision-13-deit','distillation-cost','学生参数增量、教师训练与部署分账','固定教师省去其反向更新，仍有前向计算；学生推理通常不需要教师。',
 card(55,155,500,205,'学生新增参数',['DIST向量：D','一行位置：D','第二头：(D+1)K'],palette.green)+
 card(640,155,510,205,'Base / 1000类增量',['768 + 768 + 769,000','总新增：770,536','蒸馏学生：87,338,192'],palette.blue)+
 card(55,410,500,205,'蒸馏训练每批',['学生前向 + 学生反向','教师前向；另记录教师来源/训练成本'],palette.orange)+
 card(640,410,510,205,'部署学生',['学生骨干 + 两分类头','指定CLS/DIST/融合政策','MAC不直接等于实测延迟'],palette.green),700));

outputs.push(save('vision-14-swin-pvt','window-shift','移位窗口：规则容器与真实允许连接','4×4网格，M2、s1；编号图无需跟特征再次roll。图中数值是教学位置身份。',
 txt(55,155,'原始网格',27)+grid(55,185,[[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]],57,
 [['#d9e8de','#d9e8de','#dce8f4','#dce8f4'],['#d9e8de','#d9e8de','#dce8f4','#dce8f4'],['#f3dfc4','#f3dfc4','#e7dbea','#e7dbea'],['#f3dfc4','#f3dfc4','#e7dbea','#e7dbea']])+
 txt(375,155,'特征roll(−1,−1)',27)+grid(375,185,[[6,7,8,5],[10,11,12,9],[14,15,16,13],[2,3,4,1]],57)+
 txt(725,155,'计算坐标的区域编号',27)+grid(725,185,[[0,0,1,2],[0,0,1,2],[3,3,4,5],[6,6,7,8]],57)+
 card(55,475,510,160,'中心新窗：6 / 7 / 10 / 11',['四项互见，跨过上一层旧窗边界','不能用旧窗身份再次禁止它们。'],palette.green)+
 card(635,475,510,160,'右上容器：8 / 5 / 12 / 9',['标签1 / 2 / 1 / 2','只允许8↔12、5↔9；排除边缘绕回。'],palette.blue)+
 txt(55,705,'mask在softmax前排除禁止项；最后reverse并roll(+1,+1)放回原坐标。',24),780));
outputs.push(save('vision-14-swin-pvt','relative-bias','相对bias：少量参数，多次引用，反传累加','M2窗口：query−key；对角索引4，向右读索引3，向左读索引5。',
 txt(55,170,'窗内坐标与序列次序',27)+grid(55,215,[['(0,0)','(0,1)'],['(1,0)','(1,1)']],135)+
 txt(445,170,'4×4位置对索引',27)+grid(445,215,[[4,3,1,0],[5,4,2,1],[7,6,4,3],[8,7,5,4]],60)+
 card(815,215,325,235,'可学习表：9×heads',['同位移共享表项','索引矩阵是整数buffer','每个block单独计表'],palette.blue)+
 card(55,545,1085,145,'梯度不是reshape',['按索引scatter-add：对同一表项的全部位置对、全部图像与窗口求和。'],palette.orange)+
 txt(55,765,'禁止位置对在精确mask下贡献0；所有分数同加常数不改变softmax。',24),840));
outputs.push(save('vision-14-swin-pvt','pyramid-merge','四stage与patch merging：空间减四倍、通道翻倍','224输入、Swin-T宽96；取stage特征时说明merge前还是merge后。',
 [0,1,2,3].map((i)=>card(55+i*280,165,245,155,'stage '+(i+1),
 [['56×56×96','stride4 / 2 blocks'],['28×28×192','stride8 / 2 blocks'],['14×14×384','stride16 / 6 blocks'],['7×7×768','stride32 / 2 blocks']][i],
 i%2?palette.blue:palette.green)).join('')+
 grid(55,430,[['00','01'],['10','11']],95)+
 arrow(285,520,375,520)+card(400,430,305,190,'拼接顺序',['[00; 10; 01; 11]','每组4C，先LN4C'],palette.orange)+
 arrow(725,520,795,520)+card(820,430,325,190,'无bias线性4C→2C',['输出网格H/2 × W/2','总标量降到原来1/2'],palette.blue)+
 txt(55,705,'拼接可逆，完整merge不保证无损；Swin V2改为reduce以后LN2C。',25),780));
outputs.push(save('vision-14-swin-pvt','sra-comparison','三种attention：可见范围与证据粒度','都可保持N个输出；不同的是每个query本层允许读取的key集合。',
 card(55,170,335,245,'全局attention',['Q：N×d，K/V：N×d','每个位置读全部原key','分数：N×N','交互MAC：2N²C'],palette.green)+
 card(435,170,335,245,'窗口attention',['每窗M²个Q/K/V','逐位置读取本窗证据','分数总项：NM²','交互MAC：2NM²C'],palette.blue)+
 card(815,170,330,245,'普通SRA',['Q：N×d','K/V：N/r²×d','读取全图学习摘要','交互MAC：2N²C/r²'],palette.orange)+
 card(55,495,1090,155,'固定P×P摘要的LSRA',['K/V数量P²固定，交互MAC为2NP²C；softmax函数仍非线性。','图像变大后一个摘要混合更多原位置，远处细节粒度需单独评价。'],palette.blue)+
 txt(55,735,'上面只列交互项；完整预算还包括投影、reduction、FFN与数据组织。',24),810));
outputs.push(save('vision-14-swin-pvt','v2-mechanisms','Swin V2：分支归一化、方向分数与连续bias','版本变化作用在不同位置；不能仅凭同shape直接混装checkpoint。',
 card(55,170,500,195,'V1：Pre-LN',['Z = X + Attn(LN(X))','Y = Z + FFN(LN(Z))','merge：LN4C → reduce'],palette.green)+
 card(645,170,500,195,'V2：residual-post-norm',['Z = X + LN(Attn(X))','Y = Z + LN(FFN(Z))','merge：reduce → LN2C'],palette.blue)+
 card(55,450,500,185,'cosine attention',['归一化Q/K方向，再乘每头尺度','正幅度缩放不改变cosine','epsilon与尺度clamp须核对'],palette.orange)+
 card(645,450,500,185,'连续位置bias',['二维位移 → 有符号log坐标','小MLP → 每头bias','可求新位移值，不保证外推质量'],palette.blue)+
 txt(55,720,'这里省略DropPath，实际训练需包含它；普通Post-LN是另一条公式。',24),800));
outputs.push(save('vision-15-position-tokens','coordinate-contracts','同一个位置：像素中心、边界与patch坐标','位置数值必须连同原点、单位和映射保存；图中采用整数像素中心。',
 card(55,165,325,200,'第一块16个像素',['像素中心：0 … 15','patch中心：7.5','边界坐标的中心：8'],palette.green)+
 card(435,165,325,200,'矩形网格：14×20',['第19号：(311.5, 7.5)','第20号：(7.5, 23.5)','序列邻近不等于空间邻近'],palette.blue)+
 card(815,165,330,200,'crop + resize',['原中心350，crop左端200','放大2倍：新中心300.5','半像素逆变换回到350'],palette.orange)+
 line(80,465,1080,465)+[0,1,2,3,4].map((i)=>line(100+i*220,447,100+i*220,483)+txt(100+i*220,525,['像素','patch','crop局部','tile来源','原图'][i],25,palette.ink,'middle')).join('')+
 txt(55,615,'网格(x,y)、图像像素、归一化坐标、帧与秒是不同单位；回投必须沿原映射。',24),690));
outputs.push(save('vision-15-position-tokens','position-insertion','位置信息加在哪里：三条不同计算路径','相同位置名称不代表相同函数；内容交叉项、V路径与mask需分别核对。',
 card(55,170,340,270,'输入加法位置',['输入：X + P','再生成Q、K、V','QK含内容与位置交叉项','位置可进入FFN与残差'],palette.green)+
 card(430,170,340,270,'相对logit bias',['输入先投影Q、K、V','logit：QKᵀ/√d + B','B按query / key位移查表','不能吸收任意内容交叉项'],palette.blue)+
 card(805,170,340,270,'旋转Q与K',['Qᵢ → R(pᵢ)Qᵢ','Kⱼ → R(pⱼ)Kⱼ','点积含相对相位','本章V不做同样旋转'],palette.orange)+
 card(55,520,1090,130,'允许关系另有职责',['mask决定能否读取；位置bias或旋转决定合法位置之间的分数。'],palette.blue)+
 txt(55,735,'特殊token、投影前后次序、配对布局与频率都是checkpoint协议的一部分。',24),810));
outputs.push(save('vision-15-position-tokens','rotary-axes','旋转通道对：轴向、混合与三轴教学例','每两项是一对旋转通道；角度由坐标与对应频率决定，不由序列长度自动确定。',
 card(55,175,335,250,'二维axial',['一部分对只用x','另一部分对只用y','角度分别为ωx / ωy','配置需定义通道分配'],palette.green)+
 card(435,175,335,250,'二维mixed',['每对读取x与y','φ = fₓx + fᵧy','不同对可有不同方向','频率可连续学习'],palette.blue)+
 card(815,175,330,250,'三轴教学d6',['第1对读取时间t','第2对读取纵向y','第3对读取横向x','帧/秒改变须同步频率'],palette.orange)+
 card(55,505,1090,150,'相对点积恒等式',['[R(p)q]ᵀ[R(p′)k] = qᵀR(p′−p)k（线性相位、同一频率政策）','共同坐标平移可抵消相位；它不证明完整网络尺度或旋转等变。'],palette.blue)+
 txt(55,745,'范数保持；分数随相位周期变化，不保证随每一对位置距离单调下降。',24),820));
outputs.push(save('vision-15-position-tokens','packed-identities','打包：共享容器，保留每张图的身份','A有2项，B有3项，pad有2项；绿色表示真实允许对，pad只允许自读。',
 txt(60,155,'key →',25)+txt(500,155,'每图独立pool与head',27)+
 grid(60,180,Array.from({length:7},(_,i)=>Array.from({length:7},(_,j)=>i<2&&j<2?'A':i>=2&&i<5&&j>=2&&j<5?'B':i===j&&i>=5?'P':'×')),55,
 Array.from({length:7},(_,i)=>Array.from({length:7},(_,j)=>i<2&&j<2?palette.green:i>=2&&i<5&&j>=2&&j<5?palette.blue:i===j&&i>=5?palette.orange:'#fff')))+
 card(500,185,640,150,'pool A：只读取第0 / 1项',['输出A的分类loss；不按容器把A与B混成一图。'],palette.green)+
 card(500,375,640,150,'pool B：只读取第2 / 3 / 4项',['输出B的分类loss；pad不作为图或对比负例。'],palette.blue)+
 card(60,625,1080,135,'数学隔离 ≠ 自动节省稠密乘法',['真实对数：2²+3²=13；加入pad自读共15；稠密L7仍存49个分数。'],palette.orange)+
 txt(60,835,'编码器隔离不消除对比loss的跨样本负例耦合；需核对完整计算图。',24),910));
outputs.push(save('vision-15-position-tokens','merging-provenance','多对一合并：保存质量、来源与近似边界','示意固定匹配，不求选择操作的导数；保护CLS与DIST，两个source共用一个destination。',
 grid(55,165,[['CLS','DIST','2','3','4','5','6','7']],132,
 [[palette.orange,palette.orange,palette.green,palette.blue,palette.green,palette.white,palette.green,palette.blue]])+
 txt(55,360,'选择边：2→3，4→3，6→7；8个输入成为5个代表。',26)+
 card(55,425,335,210,'合并组 {2,3,4}',['质量：1 + 3 + 2 = 6','特征：(2,10),(8,−2),(4,6)','加权均值：(17/3, 8/3)'],palette.green)+
 card(435,425,335,210,'保留协议',['来源索引与质量继续传递','代表坐标可取加权质心','下次合并不能忽略旧质量'],palette.blue)+
 card(815,425,330,210,'不能保证的恢复',['unmerge复制代表到来源','shape恢复不等于细节恢复','logsize仅在限定条件精确'],palette.orange)+
 txt(55,735,'先旋转再平均与在质心旋转一般不同；保存质心不能保留全部相位分布。',24),810));

outputs.push(save('vision-16-contrastive','contrastive-pipeline','同源视图 → 共享编码 → 投影 → 候选分类','源图ID产生配对监督；loss空间z与迁移表示h是两个明确接口。',
 card(55,175,245,180,'原图A / B',['每图两次随机增强','生成A₁/A₂/B₁/B₂'],palette.green)+
 arrow(315,265,370,265)+card(385,175,300,180,'共享f与g',['h = encoder(view)','z = projector(h)','u = z / norm(z)'],palette.blue)+
 arrow(705,265,765,265)+card(785,175,360,180,'每anchor选配对项',['排除self，保留positive','分母含全部合法候选','softmax + 交叉熵'],palette.orange)+
 card(55,450,1090,150,'不要混淆三个数量',['B张原图，M=2B个视图；每行M−1候选，其中1正、M−2负。','预训练通过g回传到f；linear probe常删除g，只训练新的标签head。'],palette.blue)+
 txt(55,690,'无人工类别标签仍有明确监督关系；增强与候选采样共同定义任务。',25),770));
outputs.push(save('vision-16-contrastive','density-ratio','抽样实验决定posterior：条件项与边缘负项','公平二进制C，X以0.8概率等于C；图示C=0，候选值[0,1]。',
 card(55,170,330,210,'条件分布',['p(X=0|C=0) = 0.8','p(X=1|C=0) = 0.2','一个正项来自此分布'],palette.green)+
 card(435,170,330,210,'边缘分布',['p(X=0) = 0.5','p(X=1) = 0.5','其他项独立来自边缘'],palette.blue)+
 card(815,170,330,210,'密度比与posterior',['比值：(1.6, 0.4)','归一化：(0.8, 0.2)','不直接只用条件概率'],palette.orange)+
 card(55,480,1090,150,'下界有抽样与期望条件',['log(M) − E[loss] ≤ I(C;X)；M包含positive。','改变负proposal后比值变成p(x|c)/ν(x)，不能直接沿用边缘下界解释。'],palette.blue)+
 txt(55,725,'二进制真MI约0.192745 nat；M4枚举下界约0.145801 nat。',26),800));
outputs.push(save('vision-16-contrastive','cpc-causal','CPC：上下文不读取未来，未来仍参加训练','教学三步递归；未来正项与两个负项使用同一可导encoder。',
 ['历史x₀','历史x₁','历史x₂','未来正x₃','负x₄/x₅'].map((s,i)=>card(55+i*225,165,200,135,s,['共享encoder → z'],i<3?palette.green:i===3?palette.blue:palette.orange)).join('')+
 card(55,410,570,170,'causal context',['c₂只汇总z₀ / z₁ / z₂','未来改变：c₂不变，target与loss可变'],palette.green)+
 arrow(645,490,725,490)+card(755,410,390,170,'预测与候选比较',['q = 预测头(context)','q读取正/负z，分类正项','梯度回到context与所有候选'],palette.blue)+
 txt(55,690,'因果前向边界与stop-gradient是不同机制；原CPC目标支路可以回传。',25),770));
outputs.push(save('vision-16-contrastive','moco-state','MoCo：本步query梯度、EMA key与旧字典快照','图示本章核对的历史builder顺序；每步只做约定的一次EMA。',
 card(55,170,335,190,'query encoder θq',['增强1 → query q','本步loss梯度更新','使用optimizer与scheduler'],palette.green)+
 card(435,170,335,190,'key encoder θk',['θk ← mθk + (1−m)θq','增强2 → positive key','本步key支路停止梯度'],palette.blue)+
 card(815,170,330,190,'旧queue快照',['K个历史负key','q·k+ 与 q·queue','标签positive列0'],palette.orange)+
 card(55,460,520,180,'先固定本步字典再入队',['loss与query梯度使用相同旧值','当前keys入队、覆盖最旧项','保存queue / pointer / 全部状态'],palette.blue)+
 card(625,460,520,180,'不要交换职责',['EMA不是SGD momentum','detach不复制旧queue数值','大K同时增候选与历史年龄'],palette.orange)+
 txt(55,735,'本文K5/B2演示一般环写；作者历史helper另要求K可被global batch整除。',24),810));
outputs.push(save('vision-16-contrastive','simclr-dual-path','SimCLR：一个embedding参与自己的行与别人的列','两图双视图、交错次序；对角×排除self，+为positive，其余−为negative。',
 grid(55,190,[['×','+','−','−'],['+','×','−','−'],['−','−','×','+'],['−','−','+','×']],95,
 [['#fff',palette.green,palette.blue,palette.blue],[palette.green,'#fff',palette.blue,palette.blue],[palette.blue,palette.blue,'#fff',palette.green],[palette.blue,palette.blue,palette.green,'#fff']])+
 card(525,190,620,150,'anchor路径：第i行',['uᵢ与候选uⱼ点积，收到Eᵢⱼ贡献。'],palette.green)+
 card(525,395,620,150,'candidate路径：第i列',['其他anchor读取uᵢ，收到Eⱼᵢ贡献；不能漏掉。'],palette.blue)+
 card(55,650,1090,135,'完整梯度回到同一个共享encoder',['G(uᵢ) = Σⱼ(Eᵢⱼ + Eⱼᵢ)uⱼ / τ，随后通过L2 norm与投影头。'],palette.orange)+
 txt(55,870,'microbatch分开loss缺少跨批候选；普通no-grad gather也不自动恢复远端梯度。',24),950));

outputs.push(save('vision-17-noncontrastive','prediction-branches','共享网络，两方向各有一条停止目标边','图示SimSiam接口；BYOL还为目标encoder/projector保存独立EMA参数。',
 card(55,175,310,180,'视图1 → f / g',['z₁可导 → predictor → p₁','z₁另作为方向2停止目标'],palette.green)+
 card(435,175,330,180,'两方向loss平均',['p₁ 对 sg(z₂)','p₂ 对 sg(z₁)','两条prediction路径均回传'],palette.blue)+
 card(835,175,310,180,'视图2 → f / g',['z₂可导 → predictor → p₂','z₂另作为方向1停止目标'],palette.green)+
 card(55,450,520,170,'停止的是目标图边',['sg前向值不变，反向为0','共享参数仍收到两侧预测梯度','不是冻结某张视图整条网络'],palette.orange)+
 card(625,450,520,170,'核查半梯度的差分',['本次forward生成目标快照','改变输入/参数时保持快照','重新生成目标测的是另一函数'],palette.blue)+
 txt(55,725,'predictor、BN与loss归约是算法接口；同样的输出形状不代表同样的求导。',24),805));
outputs.push(save('vision-17-noncontrastive','normalization-axes','每行单位长度，与每列跨样本变化是两件事','矩阵行是样本、列是feature维；图中两边都从raw矩阵开始。',
 grid(55,190,[['样本1','维1','维2','维3'],['样本2','维1','维2','维3'],['样本3','维1','维2','维3']],100)+
 card(525,190,620,160,'行L2：单样本各维平方和',['uₙ = zₙ / norm(zₙ)','所有单位行仍可以完全同向、跨样本方差0'],palette.green)+
 card(525,405,620,160,'列标准化：多个样本的同一维',['μ / var按样本轴统计，再中心化并缩放','均值与std也是可导函数，反向不能冻结'],palette.blue)+
 card(55,660,1090,140,'VICReg直接读取raw embedding',['方差hinge要求每列足够变化；任意先做单位行L2会改变尺度可行性。'],palette.orange)+
 txt(55,885,'BN、LN、L2的轴与状态不同；先明确接口，再讨论防坍塌。',24),965));
outputs.push(save('vision-17-noncontrastive','barlow-matrix','Barlow Twins：交叉矩阵保留两个feature轴','C = UᵀV / N；每个元素把配对样本求和，矩阵不是样本候选表。',
 grid(55,205,[['C₁₁','C₁₂','C₁₃'],['C₂₁','C₂₂','C₂₃'],['C₃₁','C₃₂','C₃₃']],125,
 [[palette.green,palette.orange,palette.orange],[palette.orange,palette.green,palette.orange],[palette.orange,palette.orange,palette.green]])+
 card(525,205,620,155,'对角：同维跨视图贴近1',['Σᵢ(Cᵢᵢ−1)²；D个元素，采用sum。'],palette.green)+
 card(525,415,620,155,'非对角：减少维度间相关',['λ Σᵢ≠ⱼ Cᵢⱼ²；上下三角全部D(D−1)项','两视图不同时，C一般不对称。'],palette.orange)+
 card(55,690,1090,140,'完整反向还需经过列标准化',['E = ∂L/∂C；Gᵤ = VEᵀ/N，Gᵥ = UE/N；均值、尺度也回传。'],palette.blue)+
 txt(55,910,'中心化rank至多N−1；D>N−1时，单batch的C不能精确成为Iᴅ。',24),990));
outputs.push(save('vision-17-noncontrastive','vicreg-terms','VICReg：一致、变化量、线性冗余分别约束','两视图raw embedding都求导；本章采用作者固定代码的sum / mean。',
 card(55,180,335,270,'invariance',['配对行：Aₙ 对 Bₙ','逐元素平方差 / (ND)','两侧梯度符号相反','单独此项允许常数解'],palette.green)+
 card(435,180,335,270,'variance',['每侧样本std，分母N−1','各维hinge：max(0,1−std)','两侧mean再平均','超过阈值不继续罚'],palette.blue)+
 card(815,180,330,270,'covariance',['各侧Cov，排除对角','全部off平方 / D','两侧loss求和','不单独保证跨视图对齐'],palette.orange)+
 card(55,540,1090,150,'组合：25 × inv + 25 × var + 1 × cov',['常数两侧相同、epsilon1e−4：总loss24.75，却可有精确零梯度。','惩罚常数值、消除驻点、改变稳定性，是需要分别核查的命题。'],palette.blue)+
 txt(55,785,'raw尺度、hinge拐点、epsilon和完整归约必须连同权重一起保存。',24),865));
outputs.push(save('vision-17-noncontrastive','global-statistics','全局统计：不能遗漏分片之间的均值差异','第一维在两片各为常数，但全局有变化；其他维和外积也需正确合并。',
 card(55,175,335,220,'shard1：两行',['第一维：[+1, +1]','局部均值 +1','局部样本方差 0','保存n、列和S、外积和Q'],palette.green)+
 card(435,175,335,220,'shard2：两行',['第一维：[−1, −1]','局部均值 −1','局部样本方差 0','保存n、列和S、外积和Q'],palette.blue)+
 card(815,175,330,220,'合并：四行',['第一维均值 0','全局平方偏差和 4','样本方差 4 / 3','局部方差平均仍错误地为0'],palette.orange)+
 card(55,505,1090,160,'合并统计，再构造目标',['N = Σn；S = ΣS；Q = ΣQ；Cov = [Q − SSᵀ/N] / (N−1)','实际大均值/小方差宜用稳定中心化合并；保留可导路径与归约。'],palette.blue)+
 txt(55,760,'SyncBN、embedding gather、DDP与梯度累积处理不同量，不能互相替代。',24),840));
outputs.push(save('vision-18-masked-modeling','beit-two-paths','BEiT：同一训练图的输入patch与离散目标','主干读取像素patch；固定tokenizer从未遮原图生成同坐标的类别ID。',
 card(55,170,300,190,'训练图 x',['224×224×3','共同crop / flip / color流程'],palette.green)+
 arrow(370,220,450,220)+card(475,150,300,210,'主干输入路径',['14×14个16×16 patch','部分embedding换成[MASK]','完整长度送入Transformer'],palette.blue)+
 arrow(370,350,450,350)+card(475,385,300,210,'固定tokenizer路径',['原内容 → 14×14 token ID','K = 8192；MIM不更新tokenizer','只选择masked坐标作为标签'],palette.orange)+
 card(835,245,310,250,'位置i必须对齐',['hidden hᵢ → K类logit','target zᵢ来自同一网格','CE只对i∈M取平均','下游丢弃token分类head'],palette.green)+
 txt(55,700,'两个路径shape对齐仍可能转置或crop错位；人工坐标图应成为单元测试。',24),780));
outputs.push(save('vision-18-masked-modeling','mask-policies','同样的遮挡比例，可以来自不同采样分布','绿色可见、橙色masked；示意8×8网格，不代表论文某一随机seed。',
 grid(55,175,Array.from({length:8},(_,i)=>Array.from({length:8},(_,j)=>(i*3+j*5)%4===0?'M':'V')),48,
 Array.from({length:8},(_,i)=>Array.from({length:8},(_,j)=>(i*3+j*5)%4===0?palette.orange:palette.green)))+
 txt(245,595,'散点 / 无放回随机',27,palette.ink,'middle')+
 grid(465,175,Array.from({length:8},(_,i)=>Array.from({length:8},(_,j)=>(i>=1&&i<=4&&j>=2&&j<=5)||(i>=5&&j>=5)?'M':'V')),48,
 Array.from({length:8},(_,i)=>Array.from({length:8},(_,j)=>(i>=1&&i<=4&&j>=2&&j<=5)||(i>=5&&j>=5)?palette.orange:palette.green)))+
 txt(655,595,'矩形块反复覆盖',27,palette.ink,'middle')+
 card(870,175,275,250,'分布要记录',['每位置纳入概率','连通块/最近可见距离','实际masked整数','重叠与失败重试'],palette.blue)+
 card(870,475,275,145,'难度不是质量',['更难的mask不保证','迁移表示一定更强'],palette.orange)+
 txt(55,700,'BEiT原始路线约40%块状；MAE默认75%均匀无放回随机。',24),780));
outputs.push(save('vision-18-masked-modeling','mae-index-restore','MAE：随机排列选可见项，再用逆排列回原网格','例中8项仅保留原位置6和3；restore满足restore[shuffle[j]]=j。',
 grid(55,165,[['A','B','C','D','E','F','G','H']],95)+
 txt(55,305,'原位置：0  1  2  3  4  5  6  7',23)+arrow(405,335,405,390)+
 grid(55,420,[['G','D','B','A','F','H','E','C']],95,
 [[palette.green,palette.green,palette.orange,palette.orange,palette.orange,palette.orange,palette.orange,palette.orange]])+
 card(845,165,300,155,'shuffle',['[6,3,1,0,5,7,4,2]','前2项送入encoder'],palette.blue)+
 card(845,370,300,175,'restore',['[3,2,7,1,6,4,0,5]','补6个MASK后gather','恢复到A…H原坐标'],palette.orange)+
 txt(55,610,'decoder原顺序：MASK  MASK  MASK  D  MASK  MASK  G  MASK',25)+
 txt(55,705,'encoder位置编码随可见token同行；inverse不包含CLS。',24),780));
outputs.push(save('vision-18-masked-modeling','mae-asymmetry','MAE非对称计算：重型encoder稀疏，轻decoder全长','224/P16、mask75%示意；patch长度不含CLS，实际两侧各再加一个CLS。',
 card(55,175,285,210,'196个patch',['随机保留49，删除147','先添加原坐标位置编码'],palette.green)+
 arrow(355,275,415,275)+card(435,155,300,250,'重型ViT encoder',['只处理49个可见patch','无mask token','Dₑ大、迁移时保留'],palette.blue)+
 arrow(750,275,810,275)+card(835,155,310,250,'轻量decoder',['投影到D_d，补147 MASK','inverse恢复196位置','全序列预测每patch Q值'],palette.orange)+
 card(55,500,1090,155,'attention矩阵项与整block成本要分开',['49² / 196² = 1/16；但QKV/MLP的D²项约按49/196=1/4缩放。','decoder、反向与硬件kernel另计；理论项数不是实测吞吐。'],palette.blue)+
 txt(55,745,'预训练后丢decoder，但decoder的Jacobian已决定encoder收到的重建梯度。',24),825));
outputs.push(save('vision-18-masked-modeling','target-spaces','三类重建目标：单位、信息与损失不可直接比较','相同masked坐标可接不同监督头；数值更小不表示表征更好。',
 card(55,175,335,250,'离散视觉token',['目标：整数ID，K类','loss：交叉熵','依赖tokenizer与码本','可过滤/继承其偏差'],palette.green)+
 card(435,175,335,250,'raw patch像素',['目标：Q个当前tensor值','loss：逐元素MSE','保留亮度/对比度尺度','无需额外教师'],palette.blue)+
 card(815,175,330,250,'patch-normalized像素',['每patch减均值/除std','loss仍为Q维MSE','常数patch目标为0','variance政策要固定'],palette.orange)+
 card(55,520,1090,150,'公平证据来自对齐下游与预算',['CE随K/entropy，MSE随像素scale/Q；预训练loss绝对值不能横向排名。','同时报告额外tokenizer数据与计算、mask政策、decoder和迁移协议。'],palette.blue)+
 txt(55,760,'目标空间、encoder可见内容、预测模块与loss位置共同定义方法。',24),840));


outputs.push(save('vision-19-dino','dino-multicrop','DINO：两类视图、两条参数路径、一个跨视图目标','teacher只读两个全局视图；student读全部视图；同索引全局pair排除。',
 card(45,165,240,190,'同一原图',['g₀ / g₁：224全局','l₀…l₇：96局部','随机外观增强'],palette.green)+
 arrow(300,220,365,220)+card(390,135,300,225,'student θs',['读取10个视图','梯度下降更新','产生p₀…p₉'],palette.blue)+
 arrow(300,420,365,420)+card(390,390,300,185,'teacher θt',['只读取g₀ / g₁','target停止梯度','产生q₀ / q₁'],palette.orange)+
 card(760,155,385,205,'18个合法交叉熵项',['q₀→p₁,p₂…p₉','q₁→p₀,p₂…p₉','排除q₀→p₀、q₁→p₁'],palette.green)+
 card(760,430,385,150,'状态更新',['optimizer先更新θs','再做θt ← mθt+(1−m)θs'],palette.orange)+
 txt(45,690,'多裁剪沿batch分别前向，不把十个crop拼成一个attention序列。',24),770));

outputs.push(save('vision-19-dino','dino-collapse-balance','Centering与sharpening：相反倾向共同约束teacher目标','三种分布都是K=4示意；箭头表示动力学倾向，不是一步后的精确数值。',
 card(55,165,310,210,'单坐标占优',['q≈[1,0,0,0]','所有输入同一输出','样本entropy≈0'],palette.orange)+
 arrow(375,270,455,270,'#3b7e57')+card(470,165,310,210,'centering',['减历史逐坐标均值','压低长期占优槽位','单独使用倾向均匀'],palette.green)+
 arrow(790,270,870,270,palette.red)+card(885,165,260,210,'均匀坍塌',['q≈[¼,¼,¼,¼]','所有输入无区别','entropy=log4'],palette.blue)+
 card(260,480,680,150,'低温sharpening从均匀方向拉回尖锐目标',['q = softmax((z−c)/τt)；低τt放大已有logit差。','配合momentum teacher与多裁剪；不构成任意设置下的收敛证明。'],palette.orange)+
 txt(55,735,'诊断需同时看单样本entropy、batch边缘分布与样本间差异。',24),815));

outputs.push(save('vision-19-dino','dino-pair-matrix','默认配对矩阵：2个teacher目标 × 10个student视图','绿色为合法CE项，×为同一全局视图排除；每个local列收到两个目标。',
 grid(55,180,[['×','✓','✓','✓','✓','✓','✓','✓','✓','✓'],['✓','×','✓','✓','✓','✓','✓','✓','✓','✓']],86,
 [[palette.white,...Array(9).fill(palette.green)],[palette.green,palette.white,...Array(8).fill(palette.green)]])+
 txt(55,390,'列：   g₀      g₁      l₀      l₁      l₂      l₃      l₄      l₅      l₆      l₇',23)+
 card(55,475,510,155,'teacher q₀',['对9个student视图计分','只跳过student g₀'],palette.orange)+
 card(635,475,510,155,'teacher q₁',['对9个student视图计分','只跳过student g₁'],palette.blue)+
 txt(55,725,'pair总数2×(10−1)=18；不是20，也不是10×9。',25),805));

outputs.push(save('vision-19-dino','dino-attention-evidence','同一DINO模型的两种空间证据接口','可视化attention与DAVIS标签传播读取不同tensor、使用不同监督信息。',
 card(55,160,300,190,'CLS attention',['最后层：CLS query→patch keys','按累计质量阈值成mask','无需像素真值即可画图'],palette.green)+
 arrow(370,255,445,255)+card(470,160,300,190,'定性 / mask评价',['可观察前景样结构','插值不增加patch分辨率','attention不等同因果贡献'],palette.orange)+
 card(55,445,300,190,'patch features',['每个patch的D维表示','跨帧相似度与局部邻域','不是CLS attention数值'],palette.blue)+
 arrow(370,540,445,540)+card(470,445,300,190,'DAVIS标签传播',['使用首帧ground-truth mask','最近邻传播到后续帧','报告J / F等定量指标'],palette.orange)+
 card(835,250,310,270,'结论边界',['“像分割”是现象','DAVIS分数属于传播协议','预训练无标签','不等于下游评价无标签'],palette.green)+
 txt(55,735,'先标出tensor与外部信息，再决定证据支持哪一个命题。',24),815));

outputs.push(save('vision-19-dino','dino-state-eval','DINO训练状态与冻结评价：对象不能串线','上半是每步可变状态；下半是训练完成后冻结特征的独立协议。',
 card(45,155,245,190,'student',['10视图forward','loss反传','optimizer / lr / wd'],palette.green)+
 arrow(305,250,365,250)+card(385,155,245,190,'teacher',['2全局forward','停止梯度','参数EMA m(t)'],palette.blue)+
 arrow(645,250,705,250)+card(725,155,420,190,'target状态',['center EMA：raw teacher logits','teacher softmax：center + τt','18项跨视图CE'],palette.orange)+
 line(45,410,1145,410,'#96a69b',true)+
 card(45,485,330,170,'冻结CLS feature',['L2 normalize','weighted k-NN / linear probe','评价使用类别标签'],palette.green)+
 card(435,485,330,170,'冻结patch feature',['视频标签传播 / 稠密匹配','DAVIS使用首帧mask'],palette.blue)+
 card(825,485,320,170,'最后层attention',['固定head与阈值规则','定性图 + mask指标','展示随机样本与失败例'],palette.orange)+
 txt(45,750,'checkpoint续训需保存student、teacher、optimizer、scheduler位置、scaler与center。',24),830));

outputs.push(save('vision-20-dinov2-dinov3','ibot-dual-objective','iBOT：全局CLS与局部patch的两种蒸馏关系','CLS跨随机视图；patch在同一视图、同一网格位置只对masked项计分。',
 card(45,160,255,180,'视图u',['student看masked û','teacher看原始u','patch坐标一一对应'],palette.green)+card(45,410,255,180,'视图v',['student看masked v̂','teacher看原始v','各自生成mask'],palette.blue)+
 arrow(315,245,390,245)+card(415,145,325,205,'Patch MIM',['qᵤ,i → p_û,i','qᵥ,i → p_v̂,i','只计mᵢ=1；同视图同位置'],palette.orange)+
 arrow(315,500,390,500)+card(415,405,325,205,'CLS跨视图',['qᵥ,CLS → p_û,CLS','qᵤ,CLS → p_v̂,CLS','获得全局语义'],palette.green)+
 card(805,245,340,260,'两套状态',['CLS / patch可有不同center','teacher温度可不同','总loss = CLS + MIM','teacher均停止梯度并EMA'],palette.blue)+txt(45,710,'在线tokenizer = teacher backbone + patch head；不是固定离散ID表。',24),790));
outputs.push(save('vision-20-dinov2-dinov3','dinov2-three-axes','DINOv2扩展的三条轴：目标、数据与系统','“更大模型”只有三分之一；公平复现需同时锁定三条轴。',
 card(55,165,330,260,'训练目标',['DINO：跨视图CLS','iBOT：masked patch','Sinkhorn teacher分配','KoLeo展开CLS feature'],palette.green)+
 card(435,165,330,260,'数据策展',['1.2B池过滤 / 去重','seed检索 + cluster采样','LVD-142M','移除评价集近重复'],palette.blue)+
 card(815,165,330,260,'规模化系统',['packing + block mask','跳过式stochastic depth','FSDP混合精度','短高分辨率适配'],palette.orange)+
 card(55,520,1090,145,'输出接口分别评价',['CLS：分类/检索；patch：分割/深度/对应；数据与probe协议决定结论边界。'],palette.blue)+txt(55,755,'DINO与iBOT head在DINOv2中分离；与原iBOT默认共享不同。',24),835));
outputs.push(save('vision-20-dinov2-dinov3','register-token-contract','Registers：给内部全局计算专用槽，保持patch空间接口','R=4示意；下游patch从索引1+R开始，register输出默认丢弃。',
 grid(55,170,[['CLS','R₁','R₂','R₃','R₄','P₀','P₁','…','P₁₉₅']],105,
 [[palette.orange,palette.blue,palette.blue,palette.blue,palette.blue,palette.green,palette.green,palette.green,palette.green]])+
 card(55,350,330,190,'CLS',['图像级输出','承受global目标','下游可读取'],palette.orange)+card(435,350,330,190,'Registers',['无像素/二维坐标','供模型存取中间全局量','输出通常丢弃'],palette.blue)+card(815,350,330,190,'Patch tokens',['严格对应空间网格','避免被挪作scratch','dense下游读取'],palette.green)+
 txt(55,650,'总长度1+4+196=201；错误切片1:197会混入4个register并漏4个patch。',25),730));
outputs.push(save('vision-20-dinov2-dinov3','register-vs-gram','两种dense故障，两种修复层级','无高范数outlier不代表patch关系长期稳定。',
 card(55,160,480,190,'故障A：patch范数outlier',['低信息背景patch被挪作全局scratch','局部probe差、全局probe强','Registers提供专用工作槽'],palette.orange)+
 card(665,160,480,190,'故障B：patch关系退化',['norm稳定但无关位置cosine升高','global指标升、dense指标降','Gram锚定两两相似结构'],palette.blue)+
 arrow(295,370,295,440)+arrow(905,370,905,440)+
 card(55,465,480,165,'输出：干净patch接口',['special token与空间token分离','仍需dense任务验证'],palette.green)+card(665,465,480,165,'输出：稳定局部关系',['XsXsᵀ匹配早期teacher','允许共同正交旋转'],palette.green)+
 txt(55,730,'Registers与Gram Anchoring互补，不是前后版本对同一bug的重复命名。',24),810));
outputs.push(save('vision-20-dinov2-dinov3','dinov3-stages','DINOv3：长预训练、Gram refinement与三类后训练','主teacher、Gram teacher和固定蒸馏teacher是三个不同状态对象。',
 card(45,150,330,210,'阶段1：长程SSL',['DINO + iBOT + 0.1 DKoLeo','EMA teacher；常数schedule','global升，dense可能后期降'],palette.green)+arrow(390,255,455,255)+
 card(475,150,330,210,'阶段2：Gram refinement',['早期dense优质teacher快照','global crop关系矩阵匹配','可用2×分辨率teacher下采样'],palette.blue)+arrow(820,255,880,255)+
 card(900,150,255,210,'旗舰7B',['patch关系修复','保留global质量','形成冻结视觉encoder'],palette.orange)+
 card(45,480,330,165,'高分辨率适配',['混合global/local尺寸','继续Gram；额外10k步'],palette.blue)+card(435,480,330,165,'小模型蒸馏',['固定7B teacher','不使用EMA teacher更新','论文未用Gram'],palette.green)+card(825,480,330,165,'dino.txt文本对齐',['冻结视觉backbone','训练文本侧与顶层适配','获得开放词汇接口'],palette.orange)+txt(45,745,'checkpoint名称必须标注阶段；基础视觉权重不自动具备文本零样本分类。',24),825));
outputs.push(save('vision-21-rcnn-fpn-yolo','detection-box-iou','检测框的共同语言：坐标、交并集与责任分配','所有检测器都要先把几何约定说清；IoU只量重叠，不量类别与置信度。',
 card(45,155,300,210,'框A = (10,20,50,60)',['宽40，高40，面积1600','连续坐标：右下边界不加1','中心(30,40)'],palette.green)+
 card(450,155,300,210,'框B = (30,40,70,80)',['交集20×20=400','并集1600+1600−400','IoU=400/2800=1/7'],palette.blue)+
 card(855,155,290,210,'IoU阈值的三种用途',['训练：分正/负/忽略','NMS：删除重复预测','评价：判定TP/FP'],palette.orange)+
 card(45,470,1100,155,'同一个0.5不代表同一个操作',['匹配阈值决定监督标签；NMS阈值比较预测与预测；AP阈值比较预测与真值。','坐标闭区间、半开区间或连续边界必须全链路一致。'],palette.blue)+txt(45,725,'先定义框与坐标，再讨论anchor、proposal、回归和后处理。',24),805));
outputs.push(save('vision-21-rcnn-fpn-yolo','rcnn-evolution','R-CNN家族：昂贵计算逐步从区域移到共享特征图','“两阶段”指proposal后再分类回归，不等于整条训练流程只有两个脚本。',
 card(45,155,315,210,'R-CNN',['Selective Search约2000框','逐框warp并跑CNN','SVM与回归器分开训练'],palette.orange)+arrow(375,260,435,260)+
 card(455,155,315,210,'Fast R-CNN',['整图CNN只跑一次','RoI Pooling抽固定尺寸','仍依赖外部proposal'],palette.blue)+arrow(785,260,845,260)+
 card(865,155,290,210,'Faster R-CNN',['共享特征上的RPN','anchor→proposal','检测head二次判别'],palette.green)+
 card(45,470,1100,155,'不变的核心任务',['候选位置覆盖真值 → 每个候选分类 → 正样本回归 → 抑制重复框。','变化的是候选如何产生、特征是否共享、几何是否量化以及损失如何归约。'],palette.blue)+txt(45,725,'RoIAlign后来替换RoI Pooling的坐标量化，但不改变两阶段定义。',24),805));
outputs.push(save('vision-21-rcnn-fpn-yolo','rpn-anchor-contract','RPN的张量契约：每个位置k个anchor，两类输出头','以H×W特征图、k=9为例；回归只对正anchor生效。',
 card(45,155,280,205,'共享特征 H×W×D',['3×3滑动卷积','每个位置同一套参数','anchor只是参考框'],palette.green)+arrow(340,255,410,255)+
 card(435,115,315,175,'objectness头',['H×W×2k logits','前景/背景','训练含正负anchor'],palette.blue)+
 card(435,350,315,175,'box头',['H×W×4k offsets','tx,ty,tw,th','只监督正anchor'],palette.orange)+
 arrow(765,255,830,255)+card(850,155,295,265,'proposal生成',['decode到图像坐标','clip并删极小框','按score排序','NMS后取top-N'],palette.green)+
 txt(45,655,'原论文k=3尺度×3宽高比=9；约60×40位置产生约21600个原始anchor。',24)+txt(45,710,'anchor是固定回归参考；proposal是网络解码后的候选框。',24),790));
outputs.push(save('vision-21-rcnn-fpn-yolo','fpn-roialign','FPN与RoIAlign：先补语义，再保留连续几何','FPN解决尺度上的语义强度；RoIAlign解决每个RoI内部的采样对齐。',
 card(45,130,280,260,'Bottom-up C2…C5',['分辨率逐层降低','语义逐层增强','stride约4,8,16,32'],palette.green)+arrow(340,260,405,260)+
 card(430,130,320,260,'Top-down + lateral',['高层上采样2×','同尺度1×1 lateral相加','3×3平滑得P2…P5'],palette.blue)+arrow(765,260,830,260)+
 card(855,130,290,260,'按RoI尺度选层',['k=k0+floor(log2(s/224))','小框去高分辨率层','各层head共享参数'],palette.orange)+
 card(45,485,1100,150,'RoIAlign在选定层内工作',['边界、bin和采样点均不取整；用邻近四点双线性插值，再按bin聚合。','FPN层选择仍是离散决策；它与RoIAlign的连续采样是两个步骤。'],palette.green)+txt(45,730,'多尺度不等于把每个RoI送遍所有层；原FPN Fast R-CNN为每个RoI选择一层。',24),810));
outputs.push(save('vision-21-rcnn-fpn-yolo','yolo-nms-pipeline','单阶段检测：密集预测之后仍需解码、排序与去重','YOLO把候选分类回归放进一次整图前向；经典版本仍使用NMS。',
 card(45,145,280,225,'密集输出',['网格/金字塔位置','每位置多个框或anchor','objectness、类别、offset'],palette.green)+arrow(340,255,410,255)+
 card(435,145,280,225,'解码与打分',['offset→图像框','score组合规则固定','阈值过滤低分框'],palette.blue)+arrow(730,255,800,255)+
 card(825,145,320,225,'class-aware NMS',['每类按分数降序','保留最高分','删IoU超过阈值的同类框'],palette.orange)+
 card(45,480,520,160,'训练侧不平衡',['密集位置多数是容易背景','采样、objectness或focal loss处理','责任分配决定谁回归'],palette.blue)+
 card(625,480,520,160,'评价侧排序',['按最终score全数据集排序','一对一匹配GT','PR曲线积分得到AP'],palette.green)+txt(45,735,'one-stage描述网络预测路径；它不意味着零后处理或只输出一个框。',24),815));
outputs.push(save('vision-22-detr','set-matching','DETR集合匹配：先一对一指派，再逐槽计算损失','N=5示意；3个真值补2个∅，匈牙利算法在整张代价矩阵上选最小和。',
 card(45,150,270,250,'真值集合',['猫 g₁','人 g₂','车 g₃','∅','∅'],palette.green)+arrow(330,275,400,275)+
 card(425,115,350,320,'5×5匹配代价',['类别代价 + 框L1 + GIoU','∅行只含类别代价','每行每列恰选一次','全局最优，不逐行贪心'],palette.blue)+arrow(790,275,855,275)+
 card(875,150,270,250,'预测槽',['q₄→猫','q₁→人','q₅→车','q₂→∅','q₃→∅'],palette.orange)+
 card(45,505,1100,140,'唯一匹配使重复预测付出代价',['同一物体附近的两个query不能都匹配同一GT；一个成为正槽，另一个通常被监督为∅。','去重压力来自全局集合损失，因此标准DETR推理不依赖NMS。'],palette.green)+txt(45,735,'匹配是离散选择；网络梯度通过选中后的分类与框损失传播。',24),815));
outputs.push(save('vision-22-detr','detr-tensors','原始DETR张量流：空间token与对象槽是两条轴','以C5特征h×w、d=256、N=100为例；decoder并行输出固定100个槽。',
 card(45,145,270,220,'CNN feature',['B×2048×h×w','1×1投影到d','flatten为B×hw×d'],palette.green)+arrow(330,255,395,255)+
 card(420,145,290,220,'Encoder memory',['加2D位置编码','全局self-attention','shape B×hw×d'],palette.blue)+arrow(725,255,790,255)+
 card(815,145,330,220,'Decoder slots',['N个learned object queries','self-attn + cross-attn','shape B×N×d'],palette.orange)+
 card(45,480,520,160,'每槽分类',['线性层→C+1 logits','额外∅类','softmax概率'],palette.blue)+card(625,480,520,160,'每槽框',['MLP→4数 + sigmoid','归一化(cx,cy,w,h)','训练用L1+GIoU'],palette.green)+txt(45,735,'object query不是裁剪图像，也不是一开始就绑定某个类别或固定物体。',24),815));
outputs.push(save('vision-22-detr','deformable-sampling','Deformable attention：围绕reference稀疏采样多尺度特征','每个query、head、level只预测K个offset与权重；采样点用双线性插值。',
 card(45,155,275,220,'query + reference',['encoder：像素自身','decoder：预测参考点/框','归一化到[0,1]'],palette.green)+arrow(335,265,405,265)+
 card(430,115,330,300,'L层×M头×K点',['offset Δp可学习','attention权重和为1','默认M=8，K≤4','不扫描全部HW keys'],palette.blue)+arrow(775,265,845,265)+
 card(870,155,275,220,'聚合输出',['各层坐标按尺寸映射','双线性读feature','加权、投影、跨层融合'],palette.orange)+
 card(45,500,1100,140,'归纳偏置与代价',['稀疏reference邻域让优化更像“从位置附近找证据”，并允许高分辨率多尺度输入。','offset可把采样移到远处；“deformable”不等于固定局部窗口。'],palette.green)+txt(45,735,'复杂度近似随query数×层数×头数×采样点数线性增长。',24),815));
outputs.push(save('vision-22-detr','dn-attention-mask','DN-DETR：训练时增加有答案的噪声query，并用mask防泄漏','每个denoising group含整套GT的一个噪声版本；推理时整个DN部分移除。',
 card(45,145,330,205,'Denoising queries',['GT label/box加噪','直接重建原GT','绕过匈牙利匹配'],palette.green)+card(45,435,330,205,'Matching queries',['普通learned/anchor queries','仍做一对一匹配','构成真实推理路径'],palette.blue)+
 card(450,120,695,520,'Decoder self-attention mask',['DN group 1：可看本组，屏蔽其他DN组','DN group 2：可看本组，屏蔽其他DN组','…','matching部分不能看DN答案','是否允许DN看matching依具体掩码方向'],palette.orange)+
 txt(45,730,'没有mask，matching query可抄noisy GT；多个DN组也可互相泄露同一真值。',24),810));
outputs.push(save('vision-22-detr','dino-components','检测版DINO：三项改动放在训练与query初始化的不同位置','它是DETR检测器，不是第19—20讲的自监督DINO视觉表征。',
 card(45,145,330,220,'Contrastive DN',['近GT小噪声→重建GT','更远噪声→∅','训练query选择与拒绝'],palette.green)+
 card(435,145,330,220,'Mixed query selection',['encoder top-k初始化4D anchor','content query仍可学习','只增强位置部分'],palette.blue)+
 card(825,145,320,220,'Look forward twice',['当前层box供下层refine','后一层loss的框梯度','也回流前一层box参数'],palette.orange)+
 card(45,485,1100,145,'共同基座',['multi-scale deformable attention + dynamic anchor box + iterative refinement + Hungarian matching。','CDN只在训练存在；matching queries仍决定推理输出，标准路线仍无需NMS。'],palette.green)+txt(45,730,'DINO论文常用900 matching queries；query数是输出容量和decoder成本的显式上限。',24),810));
outputs.push(save('vision-23-segmentation','tasks','语义、实例与全景分割：同一图像的三种输出合同','先确定像素是否要实例身份、是否要求完整且不重叠，再选择标签、损失与指标。',
 card(45,145,330,245,'语义分割',['每像素一个类别','两辆车共享car标签','常用mIoU'],palette.green)+
 card(435,145,330,245,'实例分割',['每个thing独立mask','同类实例ID不同','常用mask AP'],palette.blue)+
 card(825,145,320,245,'全景分割',['thing实例 + stuff区域','全图唯一、不重叠','常用PQ=SQ×RQ'],palette.orange)+
 card(45,500,1100,145,'输出不是可互换的文件格式',['语义标签无法可靠恢复接触实例；实例输出不一定覆盖road/sky；全景需解决原始mask重叠。','Ignore区域、thing/stuff表和空类别规则都属于数据合同。'],palette.blue)+txt(45,735,'先写任务合同，才能判断模型“做对了什么”。',24),810));
outputs.push(save('vision-23-segmentation','fcn','FCN：粗语义score与浅层位置score逐级融合','FCN-32s只上采样最深层；16s/8s加入pool4/pool3的同类score。',
 card(45,155,260,210,'深层score stride 32',['语义强、边界粗','1×1 conv → C类'],palette.orange)+arrow(320,260,390,260)+
 card(415,115,310,160,'上采样2× + pool4',['先把pool4投影到C类','坐标对齐后逐元素相加'],palette.blue)+
 card(415,355,310,160,'再上采样2× + pool3',['得到stride 8 score','仍为C个通道'],palette.green)+arrow(740,300,815,300)+
 card(840,185,305,230,'上采样8×到原图',['每像素C logits','softmax/argmax','输出H×W标签'],palette.orange)+
 txt(45,650,'“相加”要求通道、尺寸和像素中心三者都对齐；拼接会改变通道数。',24)+txt(45,705,'插值恢复网格尺寸，浅层证据帮助恢复位置。',24),790));
outputs.push(save('vision-23-segmentation','unet','U-Net：高分辨率encoder feature与decoder按通道拼接','skip保存定位线索；decoder结合底部上下文决定哪些细节有用。',
 card(45,145,230,160,'Encoder 128×128',['conv → feature E1','pool ↓'],palette.green)+card(45,400,230,160,'Encoder 64×64',['conv → feature E2','pool ↓'],palette.green)+
 card(475,275,245,180,'Bottleneck 32×32',['大感受野','语义上下文'],palette.orange)+
 card(900,400,250,160,'Decoder 64×64',['up + concat(E2)','conv融合'],palette.blue)+card(900,145,250,160,'Decoder 128×128',['up + concat(E1)','输出mask'],palette.blue)+
 arrow(290,480,455,380)+arrow(735,380,880,480)+arrow(1020,390,1020,325)+line(275,470,895,470,'#3b7e57',true)+line(275,220,895,220,'#3b7e57',true)+
 txt(45,660,'valid卷积版本需裁剪encoder feature；same padding版本仍要检查奇偶尺寸。',24)+txt(45,715,'skip不能复活输入中本就没有的证据，也可能传入噪声。',24),800));
outputs.push(save('vision-23-segmentation','deeplab','DeepLab：空洞卷积保分辨率，ASPP聚合多尺度上下文','rate只有结合feature尺寸与output stride才有输入图像尺度意义。',
 card(45,140,275,230,'Backbone OS=16',['后段stride改为1','dilation补偿感受野','feature更密'],palette.green)+arrow(335,255,400,255)+
 card(425,105,335,315,'ASPP并行分支',['1×1','3×3 rates 6/12/18','image pooling','对齐后concat + projection'],palette.blue)+arrow(775,255,840,255)+
 card(865,140,280,230,'v3+ decoder',['上采样4×','concat压缩后的低层feature','卷积 + 最终上采样'],palette.orange)+
 card(45,510,1100,140,'三个容易混淆的作用',['dilation扩大采样跨度；ASPP并行多个尺度；decoder补浅层边界。','CRF属于早期DeepLab后处理，不是DeepLabv3/v3+的定义条件。'],palette.green)+txt(45,735,'降低output stride会让高宽变大，精度收益必须连同显存与计算报告。',24),810));
outputs.push(save('vision-23-segmentation','mask2former','Mask2Former：query先预测mask，再用它限制下一层cross-attention','pixel decoder提供多尺度空间feature；Transformer decoder产生区域集合。',
 card(45,135,285,245,'Pixel decoder',['高/中/低分辨率feature','per-pixel embedding','多尺度轮流送入'],palette.green)+arrow(345,255,410,255)+
 card(435,105,330,305,'Decoder layer l',['N个query cross-attend','分类头 → C+1','mask embedding · pixel embedding','输出N张soft mask'],palette.blue)+arrow(780,255,845,255)+
 card(870,135,275,245,'Layer l+1',['上一层mask阈值化','区域外加−∞','区域内读取新feature'],palette.orange)+
 card(45,500,1100,150,'训练与推理',['Hungarian matching：类别 + sampled BCE/Dice；各层aux loss。','语义聚合、实例保留、全景竞争使用同一张量但不同解码规则。'],palette.green)+txt(45,735,'若某query屏蔽全部位置，必须解除整行屏蔽，避免softmax NaN。',24),810));
console.log(JSON.stringify({generated:outputs.length,files:outputs.map(p=>path.relative(root,p))},null,2));
