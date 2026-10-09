---
title: "23 · FCN、U-Net、DeepLab与Mask2Former：从逐像素分类到统一分割"
date: 2026-10-09
summary: "从语义、实例与全景分割的输出定义开始，手算混淆矩阵、IoU、Dice和PQ；逐层推导FCN转置卷积、U-Net跳跃连接、DeepLab空洞卷积与ASPP，再完整解释Mask R-CNN、MaskFormer和Mask2Former的mask分类、二分图匹配与masked attention。"
tags: ["视觉大模型", "图像分割", "FCN", "U-Net", "DeepLab", "Mask2Former"]
series: "vision-foundations"
order: 23
shortTitle: "FCN到Mask2Former"
---

> 检测回答“有什么、在哪里”，分割还要回答“每一个像素属于谁”。这句话看似只把框换成mask，却会引出三种不同任务、两类输出范式、边界与类别不平衡问题，以及高分辨率计算。本文先把标签与评价口径钉牢，再沿着FCN、U-Net、DeepLab、Mask R-CNN、MaskFormer、Mask2Former的历史主线解释：模型怎样从逐像素分类，走到预测一组带类别的mask。

设输入图像为$x\in\mathbb R^{H\times W\times 3}$，语义类别数为$C$。逐像素分类器输出logits $Z\in\mathbb R^{H\times W\times C}$；mask分类器输出$N$个类别分布$p_i\in\mathbb R^{C+1}$与$N$张软mask $m_i\in[0,1]^{H\times W}$。额外一类$\varnothing$表示“该query没有对象/区域”。

![三种分割任务与输出契约](./images/tasks.svg)

## 一、先分清语义、实例与全景分割

### 1. 语义分割给每个像素一个类别

语义分割输出$Y_{h,w}\in\{1,\dots,C\}$。同类别的两个独立物体共享标签：街上两辆车都写“car”，模型无需区分哪一辆是哪一辆。输出通常是$H\times W\times C$ logits，对类别轴softmax后逐像素argmax。

### 2. 实例分割同时给类别和实例身份

实例分割对每个可数物体输出$(c_i,m_i,s_i)$：类别、二值mask、置信度。两辆车必须是两个实例。背景或道路、天空这类不可数“stuff”通常不要求实例ID；输出数量随图像变化，常需排序、匹配与去重。

### 算例A：同一张街景的三种答案

图中有两个人、一辆车和道路。语义答案只含`person/car/road`三类像素；实例答案含person#1、person#2、car#1三个前景mask；全景答案覆盖全部像素，既含三个thing实例，也含road这个stuff区域。

### 3. 全景分割要求完整且不重叠的场景划分

全景输出为每像素二元组$(class,instance\_id)$。thing类别的不同实例ID不同；stuff类别通常同类合并。有效结果要求每个像素最多属于一个segment，且应尽量覆盖整幅图。因此原始重叠mask必须通过打分、阈值、归属竞争或融合规则变成不重叠结果。

### 4. Thing与stuff是数据集语义，不是物理定律

person、car常被定义为thing，sky、road常为stuff；但类别表由数据集规定。某个类别可数并不自动意味着标注提供实例ID。训练和评价必须读取数据集metadata，不能靠英文名猜测。

### 5. Ignore label不应当作一个普通类别

边界不确定、未标注区域或数据集外类别常写成255等ignore值。交叉熵应令这些像素权重为0；混淆矩阵也应排除它们。若把255截断为最后一类，指标和梯度都会被污染。

### 算例B：ignore像素如何改变准确率

四个有效像素中预测对3个，另有6个ignore像素。正确pixel accuracy是$3/4=75\%$；若错误把ignore都当背景且碰巧预测背景，会得到$9/10=90\%$，产生虚假提升。

### 6. Pixel accuracy会被大背景支配

若99%像素是背景，一个永远输出背景的模型已有99%像素准确率，却完全找不到目标。分割更常报告每类IoU、mean IoU、Dice，实例任务则报告mask AP，全景任务报告PQ。

### 7. 每类IoU来自全数据集混淆矩阵

对类别$c$：

$$IoU_c=\frac{TP_c}{TP_c+FP_c+FN_c}. $$

标准dataset-level mIoU通常先在整个评估集累加每类$TP,FP,FN$，再对有效类别求均值。它不等同于先算每张图mIoU再平均，尤其在目标尺寸差异大时。

### 算例C：手算二类IoU

真值为`[0,0,1,1,1]`，预测为`[0,1,1,1,0]`。类0有$TP=1,FP=1,FN=1$，$IoU_0=1/3$；类1有$TP=2,FP=1,FN=1$，$IoU_1=1/2$；$mIoU=5/12\approx0.4167$。

### 8. Dice与IoU可互相换算但权重不同

$$Dice=\frac{2TP}{2TP+FP+FN},\qquad Dice=\frac{2IoU}{1+IoU}. $$

Dice对小前景常比像素准确率敏感。作为loss时通常对soft概率计算；作为指标时往往先阈值化。两者同名但数值定义不同，必须报告平滑项、类别平均方式和空mask规则。

### 9. Boundary质量不能被区域指标完全描述

大物体边界错一圈，区域IoU可能只降很少；细长结构断裂却影响功能。可补充Boundary IoU、trimap内准确率、Hausdorff distance等，但它们各自依赖边界宽度或距离约定，不能用一个数字替代任务判断。

### 10. Panoptic Quality把识别和分割相乘

预测segment与GT同类且$IoU>0.5$才匹配。该阈值下不可能一个预测同时与两个不重叠GT都超过0.5，因此匹配唯一。定义：

$$PQ=\frac{\sum_{(p,g)\in TP}IoU(p,g)}{|TP|+\frac12|FP|+\frac12|FN|}=SQ\times RQ,$$

其中$SQ$是匹配对平均IoU，$RQ=|TP|/(|TP|+0.5|FP|+0.5|FN|)$。

### 算例D：手算PQ

有2个匹配对，IoU为0.8、0.6，另有1个假阳性和1个漏检。$SQ=0.7$，$RQ=2/(2+0.5+0.5)=2/3$，所以$PQ=1.4/3\approx0.4667$。

## 二、FCN：把分类网络改造成稠密预测器

### 11. 滑窗分类重复计算大量重叠区域

早期做法对每个像素附近裁patch并分类。相邻patch高度重叠，同一卷积被反复计算。全卷积网络一次共享整图特征，把空间位置保留到输出，计算从“每个patch一遍”变成“整图一遍”。

### 12. 全连接层可等价改写成卷积

输入feature为$h\times w\times C_{in}$，连接到$C_{out}$个神经元的全连接层等价于核大小$h\times w$、输出通道$C_{out}$的卷积；后续全连接等价于$1\times1$卷积。这样网络可接受更大输入，并输出更大的空间score map。

### 算例E：为何FC转卷积支持更大图

若分类器最后feature是$7\times7\times512$，FC有1000个输出，它等价于$7\times7$卷积。输入变大使feature变成$10\times10$时，同一个核可滑出$4\times4\times1000$类别分数，而普通固定长度FC无法直接接收。

### 13. 下采样换来语义和感受野，也丢失定位

五次stride 2使output stride为$32$：原图相邻32像素才对应score map相邻位置。深层单元感受野大、类别语义强，但边缘和小物体只剩粗略位置。分割decoder的核心任务是把粗语义恢复到像素网格。

### 14. 双线性上采样没有可学习参数

输出点按连续坐标从四个邻点加权：

$$v(x,y)=\sum_{i\in\{\lfloor x\rfloor,\lceil x\rceil\}}\sum_j F_{ij}(1-|x-i|)(1-|y-j|).$$

它平滑、稳定，但无法凭空恢复下采样前已经丢失的边界，只能插值已有值。

### 15. 转置卷积是线性算子的转置而非“逆卷积”

普通卷积可写$y=Kx$；转置卷积计算$K^\top y$。它不保证恢复$x$，因为stride卷积通常不可逆。1D输出长度为：

$$L_{out}=(L_{in}-1)s-2p+d(k-1)+output\_padding+1.$$

### 算例F：转置卷积输出尺寸

$L_{in}=3,k=4,s=2,p=1,d=1,output\_padding=0$，则$L_{out}=(3-1)2-2+3+1=6$。`output_padding`只消除stride导致的shape歧义，不是在输出四周补实际零值。

![FCN的粗分数、跳跃融合与上采样](./images/fcn.svg)

### 16. 转置卷积重叠不均会产生棋盘格

当kernel尺寸不能被stride整除，不同输出位置接收的覆盖次数不同。即使权重相近，也可能出现周期纹理。常见缓解是“插值后普通卷积”、选择可整除组合，或谨慎初始化为双线性核。

### 17. FCN-32s直接把最深层上采样32倍

它最简单，却只依赖stride 32的深层预测，轮廓粗糙。FCN论文随后把深层score与较浅层pool4、pool3的score对齐相加，得到FCN-16s与FCN-8s；浅层补位置，深层补语义。

### 18. Skip fusion前必须统一通道、尺度与坐标原点

浅层feature先用$1\times1$卷积变成$C$类score，再与上采样后的深层score逐元素相加。两者不仅shape要相同，像素中心还要对齐。早期网络的padding/cropping会造成偏移，源码中的crop不是装饰。

### 算例G：相加与拼接的通道差别

两个$64\times64\times C$ score map相加仍是$64\times64\times C$；若拼接则为$64\times64\times2C$，需要后续卷积学习融合。FCN skip用和，U-Net经典skip用通道拼接。

### 19. 逐像素交叉熵把分割看成共享分类器

$$L_{CE}=-\frac{1}{|\Omega|}\sum_{u\in\Omega}\log\frac{e^{Z_{u,y_u}}}{\sum_c e^{Z_{u,c}}},$$

$\Omega$排除ignore像素。所有位置共享卷积权重，但每个像素各有一个监督项。类别频率不平衡可用class weight、采样或区域型loss处理。

### 20. FCN确立“任意尺寸输入→对应尺寸输出”范式

“全卷积”不表示没有非线性、归一化或池化；它表示网络不依赖固定长度全连接接口。现代ViT分割器虽未必只用卷积，仍继承其稠密特征与端到端像素预测思想。

## 三、U-Net：对称解码器与高分辨率跳跃连接

### 21. U-Net由收缩路径和扩张路径组成

encoder逐层下采样、通道增加以聚合上下文；decoder逐层上采样、通道减少以恢复定位。每个decoder尺度接收同尺度encoder feature，形状像字母U。最底部是语义瓶颈，而不是最终输出。

### 22. U-Net skip保留的是feature而非最终类别分数

FCN skip常融合$C$通道score；经典U-Net把encoder的多通道feature裁剪后与decoder feature拼接，再做卷积。这样decoder能学习选择纹理、边缘和上下文，但显存开销也更大。

### 算例H：一次U-Net拼接

上采样分支为$64\times64\times256$，同尺度encoder为$64\times64\times256$；按通道拼接成$64\times64\times512$。若接$3\times3$卷积输出256通道，参数为$3\cdot3\cdot512\cdot256+256=1,179,904$。

### 23. 原版valid卷积导致skip需要裁剪

原U-Net的$3\times3$卷积不padding，每次空间尺寸缩小2。decoder上采样后的feature比早期encoder crop小，因此先中心裁剪encoder feature再拼接。今天常用same padding使尺寸更直观，但边界上下文和输出区域随之改变。

### 24. 上采样不能自动恢复消失的小目标

若一个2像素病灶在多次pooling后完全消失，decoder只能从skip feature找回证据。若最浅skip也被噪声或预处理抹掉，再精巧的上采样也无法恢复真实信息。

### 25. 数据增强是原U-Net小样本方案的一部分

原论文针对生物医学图像强调弹性形变等增强，让少量标注覆盖更多形态变化。增强必须同步作用于图像和mask；mask的几何插值应用最近邻，避免把离散类别插成小数。

### 算例I：图像与mask为何用不同插值

旋转后RGB图可双线性插值产生平滑颜色；类别mask若在0和2之间双线性，可能出现1并被误当成真实类别。对硬标签用最近邻；对soft target才保留连续值。

### 26. Patch训练会改变可见上下文和类别分布

裁patch增大batch并聚焦小目标，但靠近patch边界的对象缺上下文；只采前景patch又会改变真实先验。训练应记录采样策略，验证时用整图或明确的滑窗重叠与融合规则。

### 27. Overlap-tile缓解大图显存限制与边界效应

把大图分成重叠tile，模型只保留每块中央可信区域，再拼接输出。这样边缘像素也能在某个tile中获得完整上下文。重叠宽度至少覆盖模型受padding影响的边界范围。

### 28. Dice loss直接优化区域重叠

二类soft Dice常写：

$$L_{Dice}=1-\frac{2\sum_u p_u y_u+\epsilon}{\sum_u p_u+\sum_u y_u+\epsilon}.$$

它在batch、类别与空间轴上的归约方式会改变梯度。空前景时分子分母主要由$\epsilon$决定，必须明确是否跳过空类、按图平均或全batch合并。

### 算例J：小前景对CE与Dice的不同影响

100像素中仅4个前景。漏掉2个前景只占全像素CE的2%，但若无FP，前景Dice为$2\cdot2/(2\cdot2+0+2)=2/3$。Dice放大区域级漏检信号，却不能替代概率校准。

### 29. BCE、CE与Dice组合要避免重复或错误激活

互斥多类通常用softmax+CE；多标签可用每通道sigmoid+BCE。Dice可与两者相加。若对互斥类别用独立sigmoid，多个类别可同时高分，推理argmax虽给唯一类，训练却没有强制竞争。

### 30. U-Net是可复用拓扑而非单一固定网络

ResUNet、UNet++、Attention U-Net、3D U-Net等改变block、skip或维度，但共同问题仍是：下采样多大、skip传什么、decoder如何对齐、loss怎样处理类别和空mask。名称不能替代逐层shape表。

![U-Net的编码、拼接与解码契约](./images/unet.svg)

## 四、DeepLab：空洞卷积与多尺度上下文

### 31. 空洞卷积在权重之间插入采样间隔

1D形式为：

$$y[i]=\sum_{k=0}^{K-1}w[k]x[i+r k],$$

$r$是dilation rate。有效核宽$K_{eff}=K+(K-1)(r-1)$；$3\times3,r=2$覆盖$5\times5$范围，但仍只有9组参数和9次采样。

### 算例K：三种rate的有效感受范围

$3\times3$核在$r=1,2,3$时有效尺寸依次为$3,5,7$。它们不是等价的$5\times5/7\times7$密集卷积，因为中间位置没有采样。

### 32. 空洞卷积可以降低output stride而不再池化

分类backbone后段原本stride 2；把stride改为1，并给后续卷积增加dilation，可保持近似感受野同时让feature更密。例如OS=16相对OS=32把高宽各翻倍，feature元素约4倍，计算与显存也明显增加。

### 33. Dilation修改必须累计补偿后续层

若移除一次stride 2，之后所有核在输入坐标上的采样步长减半。为维持原感受野，后续dilation通常乘2；再移除一次stride则乘4。只改某一层rate而不检查整段stride，会得到错误空间尺度。

### 34. DeepLab早期版本结合双线性上采样与DenseCRF

DeepLab v1在深层CNN上使用atrous卷积得到更密score map，再双线性放大，并用全连接CRF按颜色和位置细化边界。后续DeepLabv3通过更强多尺度上下文可不依赖CRF；不能把CRF说成所有DeepLab版本的必需组件。

### 35. ASPP并行观察多个有效尺度

Atrous Spatial Pyramid Pooling对同一feature并行施加$1\times1$卷积、多个不同rate的$3\times3$空洞卷积，并在DeepLabv3加入image-level pooling分支；拼接后用$1\times1$投影融合。

### 算例L：ASPP张量shape

输入$64\times64\times256$，5个分支各输出256通道；每个分支空间对齐后拼成$64\times64\times1280$，再$1\times1$卷积投影到256通道。拼接不会自动混合分支，投影层才学习组合。

### 36. Rate数值必须结合output stride解释

同一个rate=6在OS=16和OS=8特征上对应输入图像的间隔不同。DeepLab配置常按output stride调整rates；照抄`[6,12,18]`而改变backbone stride，会改变有效视野。

### 37. Gridding来自周期采样的盲点

连续多层使用相同大rate时，信息可能只来自规则子网格，邻近像素之间缺少交互。混合不同rate、加入普通卷积或多网格策略可减轻，但要用真实感受路径分析，不能只看理论包围框。

### 38. Image pooling分支提供全局场景先验

对整个feature做全局平均，经过$1\times1$卷积，再上采样回每个位置。所有位置获得同一全局向量，有助于区分局部外观相似但场景语义不同的区域；它不保留对象位置。

### 39. DeepLabv3+把ASPP语义与浅层边界结合

encoder输出先经ASPP；decoder将其上采样4倍，与低层feature拼接。低层通道先用$1\times1$压缩，避免纹理信号和计算量压倒高层语义；再做卷积和最终上采样。

### 算例M：为何先压缩低层通道

ASPP上采样后256通道，低层有256通道。直接拼接为512通道；若低层先压到48通道，则只拼成304通道，同时迫使网络提炼边缘/位置线索。48是论文配置选择，不是数学定理。

### 40. 深度可分离空洞卷积分开空间与通道混合

先对每个输入通道独立做$k\times k$空洞卷积，再用$1\times1$混合通道。普通卷积参数$k^2C_{in}C_{out}$；深度可分离为$k^2C_{in}+C_{in}C_{out}$，但实际速度还取决于硬件、布局和实现。

![DeepLab的output stride、ASPP与decoder](./images/deeplab.svg)

## 五、实例与全景：从RoI mask到集合mask

### 41. Mask R-CNN为每个正RoI增加并行mask分支

Faster R-CNN先给proposal分类并回归框；Mask R-CNN从RoIAlign feature预测$K$张$m\times m$ mask logits，训练时只监督GT类别对应通道。mask分支与分类/框分支并行，不把mask像素先压成一个全连接向量。

### 42. RoIAlign对mask边界尤其重要

RoIPool取整会让RoI与feature采样错位，框分类可能容忍一格偏差，逐像素mask更敏感。RoIAlign保留浮点边界并双线性采样，使输入区域与输出mask坐标更一致。

### 算例N：class-specific mask选择

RoI的GT类是`person`，mask head输出80张$28\times28$ logits；只对person通道计算逐像素BCE。其他79通道本次没有mask梯度。推理按分类头预测类选择对应mask，再缩放回检测框。

### 43. Mask AP先按mask IoU匹配再积分PR

COCO mask AP在多个IoU阈值上评价实例mask，和box AP不是同一数字。正确框加粗糙mask可能box AP高而mask AP低；类别分数、重复实例和漏检仍共同影响PR曲线。

### 44. 传统panoptic系统需融合thing实例与stuff语义

一种基线分别运行实例分割和语义分割：先按分数放置thing mask、解决重叠，再用stuff预测填未占像素、删除太小区域。融合规则本身会影响PQ，并可能产生语义/实例分支冲突。

### 45. Mask classification把输出单位改成“区域+类别”

模型预测一组$(p_i,m_i)$，每个query给一张二值软mask和一个全局类别。语义、实例、全景任务可复用同一训练接口；差别主要在GT集合构造和推理如何组合这些区域。

### 算例O：像素分类与mask分类的参数化

像素分类直接预测每像素$C$个logit。mask分类若有N=100、mask embedding维D=256，则类别头给$100\times(C+1)$，每个mask通过query向量与$H'\times W'\times D$像素embedding点积得到。类别数不直接乘进每个高分辨率像素特征头。

### 46. MaskFormer由pixel decoder和Transformer decoder组成

backbone多尺度feature进入pixel decoder，产生高分辨率per-pixel embedding；Transformer decoder产生N个query embedding。每个query经分类头得类别，经mask embedding MLP后与pixel embedding点积得到mask logits。

### 47. MaskFormer仍需二分图匹配

GT segment集合无序且数量变化，matcher综合类别代价与mask代价，为每个GT选择唯一query。mask代价常用采样点上的BCE/focal与Dice，避免在所有高分辨率像素上构造巨大$N\times M\times H\times W$张量。

### 算例P：两个query与一个GT

q1类别概率高但mask Dice差，q2类别稍低但mask几乎吻合。若总代价权重为类别1、Dice5，q2可能匹配GT；q1成为$\varnothing$。匹配权重决定“像类别”和“像区域”谁更重要。

### 48. 语义推理由类别概率与mask概率相乘聚合

一种常用形式：

$$S_c(u)=\sum_{i=1}^{N}p_i(c)\,\sigma(m_i(u)).$$

再对$c$取argmax。多个同类query可以共同贡献同一像素；这不是先把每个query硬阈值化。实际实现可能过滤低置信query，需核对推理代码。

### 49. 实例与全景推理需要不同的区域竞争

实例输出可保留多个thing query并按类分数与mask质量排序；全景输出通常为每像素选最大$p_i(c)\sigma(m_i(u))$的query，再合并同类stuff、过滤小区域。相同网络不意味着三任务后处理完全相同。

## 六、Mask2Former：masked attention与多尺度query解码

### 50. 标准cross-attention一开始让每个query看全图

若Q有N个query、像素feature有HW个位置，cross-attention权重为$N\times HW$。早期query尚未局部化，容易被大量无关区域干扰；高分辨率时计算也昂贵。

### 51. Masked attention只在上一层预测区域内读特征

Mask2Former把上一decoder层的mask预测二值化为attention mask：预测为前景的位置可参与下一层cross-attention，其余位置加$-\infty$。第$l$层可写：

$$X_l=softmax(M_{l-1}+Q_lK_l^\top)V_l+X_{l-1}.$$

这里$M_{l-1}$是空间门控，不是训练GT mask。

### 算例Q：masked attention减少多少key

特征层有4096个位置，某query上一层mask含640个前景位置，则该query本层只允许640个key，保留15.625%。不同query有不同门控，因此不能简单裁成一个全局矩形。

![Mask2Former的多尺度masked attention](./images/mask2former.svg)

### 52. 全部被屏蔽时必须防止softmax NaN

若某query预测mask为空，整行attention logits都是$-\infty$，softmax未定义。实现通常把“全True屏蔽行”重置为可看全部位置，或采用等价兜底。这个细节决定训练是否稳定。

### 53. 多尺度feature轮流送入decoder层

Mask2Former的pixel decoder产生多尺度feature，Transformer decoder各层循环使用不同分辨率。低分辨率先提供语义和较低成本，高分辨率后细化边界；每层还预测mask供下一层attention门控。

### 54. Query feature与query position承担不同角色

可学习query feature携带内容状态，query positional embedding提供槽身份/位置偏置；cross-attention后内容不断更新。不能把query position直接理解成固定二维点，Mask2Former的空间支持主要来自预测mask。

### 55. 点采样训练把算力集中在不确定边界

对每个匹配mask，不必在所有像素计算loss。先过采样候选点，按$|logit|$小选不确定点，再混入随机点，计算sigmoid CE与Dice。边界附近logit接近0，因此被更多抽中。

### 算例R：不确定度排序

四点logits为`[-4,-0.2,0.1,3]`，不确定度定义$-|z|$，排序为0.1、-0.2、3、-4。前两点最接近决策边界；只选它们会偏置区域内部，所以还需随机点覆盖。

### 56. 匹配和最终mask loss可以共享形式但采样不同

matcher为每个GT-query对估算代价，需比较大量组合，常在一组共享随机点上高效计算；匹配确定后，criterion再对选中对采样并反传。二者权重、点集和归约可能不同。

### 57. Auxiliary loss让每层都学会产生可用mask

因为下一层attention依赖上一层mask，若只监督最后一层，早期门控很难学。各decoder层都输出类别和mask并参与matching/loss，给中间层直接信号。训练成本也随层数增加。

### 58. Universal architecture不等于一个权重零配置通吃

Mask2Former用同一架构处理语义、实例、全景，但数据类别、thing/stuff metadata、采样、损失权重和推理器仍按任务配置。论文中的“universal”强调接口与架构统一，不代表任意数据集无需微调。

### 算例S：同一组三个query的不同解码

两个car query与一个road query。语义输出可将两car mask对car类共同聚合；实例输出保留两辆car；全景输出让三个区域逐像素竞争，并把所有road预测合并为一个stuff类别。模型张量相同，结果结构不同。

### 59. Mask2Former的优势来自一组相互依赖的改动

masked attention、多尺度高分辨率feature、顺序调整、点采样与训练配方共同作用。只把全局attention加一张mask，不能自动复现论文结果。消融时要锁定backbone、像素decoder、训练schedule和增强。

### 60. 分割主线从像素独立决策走向区域集合建模

FCN/DeepLab主要问“这个像素是哪类”；U-Net强调多尺度定位恢复；Mask R-CNN在检测RoI内预测实例；MaskFormer/Mask2Former问“这个query代表哪个区域、是什么类”。后者仍需像素feature，只是监督与输出单位从像素变成集合中的mask。

### 算例T：选择模型前先写输出合同

医学器官只有互斥类别且每类可视为一个区域，可从U-Net/DeepLab语义分割起步；拥挤细胞需要分开同类个体，应做实例分割；自动驾驶场景既要车辆实例又要道路天空全覆盖，应做全景分割。先定任务，才有正确标签、loss与指标。

## 七、四段标准库程序：指标、上采样、空洞卷积与mask分类

### 程序一：混淆矩阵、mIoU、Dice与PQ手算

~~~python
truth = [0, 0, 1, 1, 1]
pred  = [0, 1, 1, 1, 0]

def counts(c):
    tp = sum(t == c and p == c for t, p in zip(truth, pred))
    fp = sum(t != c and p == c for t, p in zip(truth, pred))
    fn = sum(t == c and p != c for t, p in zip(truth, pred))
    return tp, fp, fn

ious, dices = [], []
for c in [0, 1]:
    tp, fp, fn = counts(c)
    iou = tp / (tp + fp + fn)
    dice = 2 * tp / (2 * tp + fp + fn)
    assert abs(dice - 2 * iou / (1 + iou)) < 1e-12
    ious.append(iou); dices.append(dice)

matched_ious, fp, fn = [0.8, 0.6], 1, 1
sq = sum(matched_ious) / len(matched_ious)
rq = len(matched_ious) / (len(matched_ious) + 0.5 * fp + 0.5 * fn)
pq = sum(matched_ious) / (len(matched_ious) + 0.5 * fp + 0.5 * fn)
assert abs(pq - sq * rq) < 1e-12
print("IoU=", [round(x, 6) for x in ious], "mIoU=", round(sum(ious)/2, 6))
print("Dice=", [round(x, 6) for x in dices])
print("SQ/RQ/PQ=", round(sq, 6), round(rq, 6), round(pq, 6))
~~~

### 程序二：1D线性插值与转置卷积覆盖次数

~~~python
def linear_upsample(values, scale):
    # align_corners=True的教学版本：端点对齐，便于手算
    out_n = (len(values) - 1) * scale + 1
    out = []
    for j in range(out_n):
        x = j / scale
        left = int(x)
        right = min(left + 1, len(values) - 1)
        a = x - left
        out.append((1-a) * values[left] + a * values[right])
    return out

def transpose_coverage(n, kernel, stride):
    out = [0] * ((n - 1) * stride + kernel)
    for i in range(n):
        for k in range(kernel):
            out[i * stride + k] += 1
    return out

interp = linear_upsample([0.0, 2.0, 4.0], 2)
even = transpose_coverage(4, 4, 2)
uneven = transpose_coverage(4, 3, 2)
assert interp == [0.0, 1.0, 2.0, 3.0, 4.0]
assert max(even[2:-2]) == min(even[2:-2]) == 2
assert len(set(uneven[2:-2])) > 1
print("linear=", interp)
print("kernel4/stride2=", even)
print("kernel3/stride2=", uneven)
~~~

### 程序三：空洞卷积有效核与采样盲点

~~~python
def dilated_conv1d(x, w, rate):
    effective = len(w) + (len(w)-1) * (rate-1)
    return [sum(w[k] * x[i + rate*k] for k in range(len(w)))
            for i in range(len(x) - effective + 1)]

x = list(range(10))
w = [1, 10, 100]
for r in [1, 2, 3]:
    effective = 3 + 2 * (r-1)
    y = dilated_conv1d(x, w, r)
    print("rate/effective/samples/output=", r, effective,
          [0, r, 2*r], y[:2])
    assert effective == 2*r + 1
assert dilated_conv1d(x, w, 2)[0] == 0 + 20 + 400
~~~

### 程序四：query类别与mask概率聚合成语义图

~~~python
import math

def sigmoid(x): return 1 / (1 + math.exp(-x))

# 3 queries × 2 semantic classes；最后的no-object概率未写入聚合
class_probs = [[0.8, 0.1], [0.6, 0.2], [0.1, 0.85]]
mask_logits = [[3, 2, -3, -3], [-2, 2, 2, -2], [-3, -2, 2, 3]]
scores = [[0.0] * 4 for _ in range(2)]
for q in range(3):
    for c in range(2):
        for u in range(4):
            scores[c][u] += class_probs[q][c] * sigmoid(mask_logits[q][u])
semantic = [max(range(2), key=lambda c: scores[c][u]) for u in range(4)]
assert semantic == [0, 0, 1, 1]

# Mask2Former空mask兜底：若所有位置都被屏蔽，恢复为全可见
blocked = [True, True, True, True]
if all(blocked): blocked = [False] * len(blocked)
assert not any(blocked)
print("class_scores=", [[round(v, 4) for v in row] for row in scores])
print("semantic=", semantic, "fallback_mask=", blocked)
~~~

## 八、练习与详解

### 练习1：语义分割能否直接数出两辆相连的车？
**解析：** 不能保证。两车像素同属car，接触时可能成为一个连通域；连通域启发式不等于实例身份。需要实例标注与实例分割，或额外中心/边界建模。

### 练习2：为什么全景输出不允许重叠segment？
**解析：** 它是完整场景划分，每个像素需要唯一的类别和实例ID。原始模型mask可重叠，但必须用竞争/融合转成唯一归属后评价PQ。

### 练习3：mIoU为何不能由总体TP、FP、FN一次计算？
**解析：** mIoU先为每类算IoU再等权平均，让小类与大类同等贡献。把所有类计数合并会被大类支配，语义也变成micro IoU。

### 练习4：预测和GT都没有某类时IoU是多少？
**解析：** 分母为0，数学上未定义。评估器可能跳过该类、记NaN或按特定规则处理；不可擅自记1并混入平均。

### 练习5：Dice loss加入很大$\epsilon$有什么风险？
**解析：** 可稳定空mask，却会主导小区域分子分母，使差预测看起来也接近高Dice。$\epsilon$、按图/按batch归约都应固定并报告。

### 练习6：全连接转卷积后为何能接受任意尺寸？
**解析：** 权重变成可在空间滑动的卷积核，不再要求固定展平长度。输入仍需满足最小尺寸和stride等约束，“任意”不代表任何小尺寸都有效。

### 练习7：转置卷积是卷积的逆吗？
**解析：** 不是。它是线性矩阵的转置；下采样已丢的信息一般不可逆，且$K^\top K$通常不等于单位矩阵。

### 练习8：双线性上采样为何不能重建真实边界？
**解析：** 它只在已知粗值间插值，不含下采样前的高频证据。真实边界需skip feature、较低output stride或额外图像证据。

### 练习9：FCN-8s为何比FCN-32s更细？
**解析：** 它融合stride 16和stride 8浅层score，补充高分辨率位置线索；“更细”仍取决于坐标对齐和浅层feature质量。

### 练习10：U-Net skip为什么可能传播噪声？
**解析：** 浅层feature保留纹理与局部高频，也会保留成像噪声和伪边缘。decoder必须学习筛选；门控、归一化和增强有时有帮助。

### 练习11：same padding后还能称U-Net吗？
**解析：** 可以。U-Net通常指多尺度encoder-decoder与对应skip拓扑，不要求复刻原论文valid卷积；但输出尺寸、边界上下文和crop规则已不同。

### 练习12：类别mask几何变换为什么通常用最近邻？
**解析：** 硬类别是离散ID，线性插值会制造不存在的中间ID。若标签本来是连续概率或距离图，才可用连续插值并保持其语义。

### 练习13：空洞卷积扩大的是参数量还是采样跨度？
**解析：** 对固定$3\times3$核，参数和采样点仍是9个，扩大的是采样间距与有效包围范围；它不是密集大核。

### 练习14：OS=8一定比OS=16好吗？
**解析：** 不一定。OS=8保留更密feature，边界和小目标可能更好，但显存与计算显著增加；训练batch、归一化和推理预算也可能改变结果。

### 练习15：ASPP多个rate为何不是简单重复？
**解析：** 不同rate从不同间隔取样，提供多尺度上下文。若feature太小，大rate大量落到padding区，分支可能退化，因此rate要结合尺寸。

### 练习16：全局池化分支能定位物体吗？
**解析：** 不能单独定位。池化抹去空间位置，广播后为各像素提供同一场景上下文；定位仍来自其他空间分支。

### 练习17：DeepLabv3+为何还需要decoder？
**解析：** ASPP增强高层多尺度语义，但高层分辨率有限。decoder融合低层feature以细化边界，实现上下文与定位的互补。

### 练习18：Mask R-CNN的80张mask是否都参与一次RoI训练？
**解析：** 经典class-specific head只取GT类别通道计算mask loss，避免类别间竞争；分类损失由独立分类头负责。

### 练习19：box AP与mask AP可直接比较高低吗？
**解析：** 不可作为同一质量量尺。两者匹配几何不同，一个用框IoU，一个用mask IoU；同一模型数值差异混合了任务难度与预测质量。

### 练习20：MaskFormer为何也需要$\varnothing$类？
**解析：** 固定N个query多于GT segment数，未匹配query需要被监督为无区域，否则会产生大量重复或伪segment。

### 练习21：mask分类是否不再需要逐像素特征？
**解析：** 仍需要。query的mask embedding与pixel embedding点积，空间细节来自像素decoder；改变的是输出组织和集合监督。

### 练习22：语义聚合为何不用每张query mask先阈值化？
**解析：** 软类别概率与软mask乘积保留不确定性，多个同类query可共同贡献。过早阈值会丢信息并引入敏感超参数。

### 练习23：masked attention会不会把早期错误锁死？
**解析：** 有风险，因此每层aux loss、跨尺度feature和空mask兜底很重要；mask也会逐层更新，不是永久固定。训练配方需让早期mask有可用召回。

### 练习24：attention mask为何通常detach？
**解析：** 二值阈值本身不可微，常把它作为下一层离散门控；mask预测仍通过本层显式mask loss获得梯度。具体实现应查源码，不能由公式猜测。

### 练习25：只采不确定点会遗漏什么？
**解析：** 会过度集中边界，忽略区域内部的系统性错分。Mask2Former混入随机点，在难点和全局覆盖间折中。

### 练习26：“统一分割”是否意味着评价指标也统一？
**解析：** 不。语义常用mIoU，实例用mask AP，全景用PQ；相同网络输出要按任务协议解码并分别评价。

### 练习27：复现Mask2Former需要锁定哪些关键项？
**解析：** 数据类别/thing-stuff映射、backbone和pixel decoder、多尺度层序、query数、点采样、matching/loss权重、训练schedule、增强与推理后处理。

### 练习28：四段程序通过后仍未证明什么？
**解析：** 未训练真实分割器、复现mIoU/AP/PQ、验证CUDA算子、测试高分辨率显存，也未证明教学聚合等同某一仓库全部细节。程序只核对定义、shape与小型数值。

## 九、来源、版本与下一讲

本文程序已运行核对混淆矩阵、mIoU/Dice/PQ关系、插值与转置卷积覆盖、空洞采样和query-mask语义聚合。它们是可审计的教学例子，不构成论文精度复现或训练性能结论。

下一讲第24讲进入SAM、SAM 2与SAM 3，讨论提示编码、歧义mask、数据引擎、视频记忆和概念提示。返回[课程总览](../vision-00-overview/)；[第21讲](../vision-21-rcnn-fpn-yolo/)补FPN、RoIAlign与Mask R-CNN的检测基座；[第22讲](../vision-22-detr/)补集合匹配和query基础。

### 原论文与作者资料

- [Long等：Fully Convolutional Networks for Semantic Segmentation](https://arxiv.org/abs/1411.4038)，CVPR 2015；用于核对FC转卷积、FCN-32s/16s/8s与skip融合。
- [Ronneberger等：U-Net](https://arxiv.org/abs/1505.04597)，MICCAI 2015；用于核对valid卷积、crop-and-concatenate、overlap-tile与增强。
- [Chen等：DeepLab v1](https://arxiv.org/abs/1412.7062)，ICLR 2015；[DeepLabv3](https://arxiv.org/abs/1706.05587)用于核对ASPP与image pooling；[DeepLabv3+](https://arxiv.org/abs/1802.02611)用于核对decoder和atrous separable convolution。
- [He等：Mask R-CNN](https://arxiv.org/abs/1703.06870)，ICCV 2017；用于核对RoIAlign和class-specific mask branch。
- [Kirillov等：Panoptic Segmentation](https://arxiv.org/abs/1801.00868)，CVPR 2019；用于核对thing/stuff定义与PQ、SQ、RQ。
- [Cheng等：MaskFormer](https://arxiv.org/abs/2107.06278)，NeurIPS 2021；用于核对mask classification统一语义/全景接口。
- [Cheng等：Mask2Former](https://arxiv.org/abs/2112.01527)，CVPR 2022；[作者实现](https://github.com/facebookresearch/Mask2Former)用于核对masked attention、多尺度decoder、点采样与三任务推理。

资料核对日期：2026-10-09。论文中的mIoU、AP、PQ和速度只属于各自数据、backbone、训练计划与硬件；本文不借用这些数字声称本站实现达到相同性能。
