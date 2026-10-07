---
title: "00 · 视觉大模型总览：零基础阅读路线与完整知识覆盖"
date: 2026-10-06
summary: "80章主线、10个前沿专题、8个实验与6个附录的完整覆盖地图。01—10讲已经写入，包含基础、经典视觉/CNN与结构化任务；目录逐项区分已写与待写，说明先修、学习标准和阅读方法。"
tags: ["视觉大模型", "课程总览", "阅读路线"]
series: "vision-foundations"
order: 0
shortTitle: "总览、路线与覆盖进度"
---

> 面向基础不扎实、希望最终读懂核心论文与前沿技术的读者。每个知识点按“它是什么 → 为什么需要 → 怎么计算 → 如何验证 → 哪些条件下失效”展开。后续复杂概念会就地解释，不把先修基础当作排除读者的门槛。

## 一、写作状态与阅读入口

**2026-10-07：01—10讲已写入，共403个编号知识小节、146个深入算例与案例、202道带解析练习、32张原创图解和14个可运行教学实验。第06—10讲进入经典视觉/CNN和结构化任务；第11—80讲及前沿专题仍待写。本页目录不是正文的替代品。**

| 讲次 | 文章 | 首先解决的问题 |
| --- | --- | --- |
| 01 | [像素到理解、生成与行动](../vision-01-map/) | 术语、任务、输入输出与模型接口 |
| 02 | [数学与张量逐步精讲](../vision-02-math/) | 矩阵、相似度、反传和轴语义 |
| 03 | [概率与统计逐步精讲](../vision-03-probability/) | 似然、交叉熵、KL与学习目标 |
| 04 | [图像、信号与几何逐步精讲](../vision-04-images/) | 采样、卷积、频率和坐标 |
| 05 | [训练与实验逐步精讲](../vision-05-training/) | 优化、归一化、增强、迁移与验证 |
| 06 | [SIFT、HOG、LeNet与AlexNet](../vision-06-classical-cnn/) | 手工与可学习表示、卷积反传、原架构与现代实现 |
| 07 | [VGG与Inception逐步精讲](../vision-07-vgg-inception/) | 小核、瓶颈、多分支、GAP与架构计算账本 |
| 08 | [ResNet与DenseNet逐步精讲](../vision-08-resnet-densenet/) | 优化退化、残差梯度、预激活、密集连接与内存 |
| 09 | [高效CNN与现代卷积](../vision-09-efficient-cnn/) | DW/PW、倒残差、SE、复合缩放、Fused与ConvNeXt |
| 10 | [视觉任务、HRNet与RAFT](../vision-10-structured-tasks/) | 输出与坐标、指标、多尺度融合、对应和迭代光流 |

“已写”表示对应文章存在；后续扩充会同步更新。不要把已写十讲等同于80章完成，也不要把术语出现过等同于对应论文已经精读。

## 二、STA5007式深度怎样落实

参考站内STA5007的教学方式：逐概念拆解、公式解释、维度核对、图中元素解读、具体手算与练习详解。新专栏没有一份统一课件，因此使用原创教学图，核心技术链接原始论文与官方材料。

篇幅服从知识范围，每个概念必须有定义、例子、用途、假设与后续依赖。核心论文篇将进一步展开完整架构、目标、数据、训练阶段、主要实验、消融、失败与历史影响。不能只写“使用某某损失”就把符号交给读者。

每篇明确哪些公式已经推导，哪些会在对应专题完整展开。讲义的小节入口不是用一段概述代替后续整章。

## 三、阅读路线

- **完整路线**：A基础 → B经典/CNN → CTransformer → D自监督 → E感知 → F图文预训练 → GVLM → H数据与能力 → I推理智能体 → J/K生成 → L视频 → M空间 → N世界/具身 → O评估 → P工程研究。
- **VLM主攻**：A必要先修 → C/D/F/G/H/I → O/P；E/L/M/N按grounding、视频和空间任务扩展。
- **生成主攻**：A/C → J/K → L视频生成 → M三维生成 → O/P。
- **空间具身主攻**：A/B/C/D/E → M → L/N → I工具与记忆 → O/P。

第02—05讲可以按模块分次读。遇到新符号，先回到本章定义和数值例子，而非跳过公式继续背名字。

## 四、已写十讲覆盖核对

### 01：模型地图

像素/通道/batch/预处理；feature/representation/embedding/token/patch；架构/权重/checkpoint/训练/推理；视觉任务、双塔/生成式VLM/生成/统一/世界模型/VLA；监督目标、能力名词、反事实对照、指标和成本。

### 02：数学与张量

数与数组、索引、四类乘法、转置、线性仿射；范数/距离/余弦/投影/rank/逆/特征值/SVD/PCA/最小二乘；指数与对数、导数/积分/梯度/链式法则/Jacobian/Hessian；凸性/Jensen、常微分方程入门；完整反传/数值检查/矩阵梯度；平均、reshape、广播、reduction、attention/patch维度和精度。

### 03：概率与统计

事件/随机变量/密度/分布，Binomial/Poisson/Beta/多维Gaussian/混合分布；期望/方差/相关/独立/采样；条件/边缘/贝叶斯/链式分解；似然/MLE/MAP/MSE/BCE；softmax与交叉熵推导、温度和软标签；能量与配分函数、熵/KL/互信息/InfoNCE；潜变量、蒙特卡洛与重参数化、偏差—方差、经验风险、校准和统计评估。

### 04：图像信号与几何

图像协议、颜色、位深、压缩、透明、方向和normalize；采样/混叠/插值/letterbox；相关/卷积/padding/stride/dilation/感受野/滤波/梯度/形态学；DFT/金字塔；齐次变换/homography/crop/框坐标/针孔/内外参/畸变；预处理审计。

### 05：训练与实验

任务和loss、batch/epoch/step、模式/梯度；SGD/momentum/Adam/AdamW/lr/累积/裁剪/混合精度；初始化与方差推导、Sigmoid/Tanh/ReLU/LeakyReLU/SiLU/GELU、残差/BN/LN/RMSNorm/归一化反传/Dropout；增强/冻结/迁移/多模态训练、teacher forcing与监督位置；划分/泄漏/消融/曲线/指标/统计；可运行分类器、checkpoint与资源记录。

### 06：手工特征与早期CNN

任务/关键点/尺度/方向/描述；SIFT高斯尺度空间、DoG、26邻域、定位、边缘剔除、方向、128维、插值/归一化/匹配与几何验证；HOG/cell/block/3780维/线性SVM/滑窗/困难负例；词袋/k-means/空间布局；多通道卷积/共享参数/等变/反传/池化梯度；原LeNet稀疏连接、下采样、RBF与GTN；AlexNet尺寸歧义、groups、参数、LRN、训练和系统结果；20个深入算例、24道练习、2个教学程序。

### 07：VGG与Inception

深度/宽度/分辨率与参数/MAC/激活/延迟；小核堆叠、非线性与边界限制；VGG16逐stage/分类头/完整参数与MAC账本/尺度评估/卷积化与迁移；1×1投影与瓶颈；Inception四分支/shape/拼接梯度/原模块与全网；GAP/局部贡献/辅助头；BN与机制解释、卷积分解/reduction/label smoothing；15个深入算例与案例、20道练习、2个教学程序。残差相关演进在第08讲继续展开。

### 08：ResNet与DenseNet

退化/梯度/过拟合诊断；残差定义、同shape加法、Jacobian与多路径展开、后激活/预激活、抵消/爆炸反例；shortcut投影、Basic/Bottleneck、ResNet18/50/101/152、stride版本与完整参数/MAC；BN/零scale、Inception-ResNet；DenseNet增长、连接、瓶颈/压缩、121逐层账本、concat反传与显存；20个深入算例与案例、24道练习、2个教学程序。

### 09：高效CNN与现代卷积

效率目标、计算/带宽/延迟；group/DW/PW与函数约束、V1宽度/分辨率、V2倒残差/线性瓶颈/ReLU6/完整stage；SE/动态gate梯度、搜索/Pareto、V3配置/hard-swish/尾层；EfficientNet复合缩放/B0/SE计数、DropPath、V2 Fused与渐进训练；ConvNeXt stem/DW/LN/MLP/LayerScale/完整账本、CNN与ViT偏置、现代配方与消融；18个深入算例与案例、24道练习、2个教学程序。

### 10：任务与结构化输出

分类/检索输出与指标；检测坐标/匹配/IoU/NMS/AP、分割类别/实例/ignore/mIoU；关键点高斯/解码/crop坐标、HRNet并行尺度/对齐/融合/OKS；跟踪分配与身份、光流方向/warp/resize/EPE、深度/视差/尺度；RAFT全对相关/金字塔/内存/查找/ConvGRU/detach/凸上采样/序列loss与消融；17个深入算例与案例、24道练习、2个教学程序。

后续在对应章继续补softmax与attention、视觉对比、扩散SDE、多视几何、策略优化等专门推导。这不是声称十讲覆盖整个数学、统计和视觉学科的全部定理。第10讲的任务地图不替代后续历代检测、分割、跟踪和深度论文精读。

## 五、80章主线覆盖与进度

完整保留批准纲要。待写行没有虚构正文链接；核心论文较多的章可拆子篇并回链父章。

### A｜总览与基础

| 讲次与主题 | 讲解范围 | 状态 |
| --- | --- | --- |
| [01｜视觉大模型知识地图](../vision-01-map/) | 区分视觉基础模型、视觉语言模型（VLM/MLLM）、视觉生成模型、空间模型和视觉语言动作模型（VLA）；建立任务、表示、训练目标、数据与评估的对应关系。 | 已写 |
| [02｜线性代数、微积分与张量](../vision-02-math/) | 向量与矩阵、范数、特征值/SVD、梯度/Jacobian、链式法则、张量索引与广播；用 patch embedding、attention 与投影头贯穿讲解。 | 已写 |
| [03｜概率、信息论与统计学习](../vision-03-probability/) | 最大似然、MAP、交叉熵、KL、互信息、能量函数、偏差与方差；说明对比学习、生成建模和不确定性如何共用这些基础。 | 已写 |
| [04｜图像、信号与几何先修](../vision-04-images/) | 像素、色彩空间、采样与混叠、卷积与傅里叶、图像金字塔、坐标变换；简述成像模型并衔接站内相机标定笔记。 | 已写 |
| [05｜深度学习训练与实验基础](../vision-05-training/) | 反向传播、初始化、归一化、优化器、学习率、增强、迁移学习；训练/验证/测试划分、数据泄漏、消融和统计波动。 | 已写 |

### B｜从经典视觉到 CNN

| 讲次与主题 | 讲解范围 | 状态 |
| --- | --- | --- |
| [06｜手工特征、LeNet 与 AlexNet](../vision-06-classical-cnn/) | SIFT/HOG、局部特征与词袋；从手工设计到可学习特征；精读 LeNet/AlexNet 的卷积、池化、非线性与大数据训练。 | 已写 |
| [07｜VGG 与 Inception](../vision-07-vgg-inception/) | 精读小卷积堆叠、多分支结构、1×1 卷积与瓶颈；对比参数量、感受野、深度和计算开销。 | 已写 |
| [08｜ResNet 与 DenseNet](../vision-08-resnet-densenet/) | 精读残差学习、梯度传播、恒等映射、预激活与密集连接；区分网络退化、梯度消失和过拟合。 | 已写 |
| [09｜高效 CNN 与现代卷积](../vision-09-efficient-cnn/) | MobileNet、EfficientNet、ConvNeXt；深度可分离卷积、复合缩放和现代训练配方；比较 CNN 与 ViT 的归纳偏置。 | 已写 |
| [10｜视觉任务与结构化输出](../vision-10-structured-tasks/) | 分类、检索、检测、分割、关键点/姿态、跟踪、光流与深度；结合 HRNet、RAFT 等代表方法说明不同输出空间。 | 已写 |

### C｜视觉 Transformer

| 讲次与主题 | 讲解范围 | 状态 |
| --- | --- | --- |
| 11｜Attention 与 Transformer 原理 | 精读 Attention Is All You Need；Q/K/V、缩放点积、自注意力与交叉注意力、残差、归一化、MLP 和 mask。 | 待写 |
| 12｜ViT：图像变成 token | 精读 An Image Is Worth 16×16 Words；patchify、位置编码、CLS、预训练与迁移；分析数据规模与归纳偏置。 | 待写 |
| 13｜DeiT：数据效率与蒸馏 | 精读蒸馏 token、教师监督与训练增强；比较架构改动和训练配方的贡献。 | 待写 |
| 14｜Swin、PVT 与多尺度结构 | 精读窗口注意力、移位窗口、层级表示与金字塔；说明它们如何服务检测、分割和高分辨率输入。 | 待写 |
| 15｜视觉 token 与位置表示 | 绝对/相对位置编码、2D/3D RoPE、插值、动态尺寸、NaViT 式打包与 token 合并；区分空间位置与时间位置。 | 待写 |

### D｜自监督与视觉基础模型

| 讲次与主题 | 讲解范围 | 状态 |
| --- | --- | --- |
| 16｜对比学习：CPC、MoCo、SimCLR | 精读 InfoNCE、正负样本、温度、动量编码器、队列和大 batch；讨论增强与假负样本。 | 待写 |
| 17｜无显式负样本学习 | BYOL、SimSiam、Barlow Twins、VICReg；教师/学生、stop-gradient、预测器、方差和协方差约束。 | 待写 |
| 18｜掩码图像建模：BEiT 与 MAE | 精读离散目标、像素重建、高掩码率、非对称编码器/解码器；比较重建目标与语义表征。 | 待写 |
| 19｜DINO：自蒸馏与涌现特征 | 精读多裁剪、teacher EMA、centering、sharpening、无标签蒸馏；分析 attention 可视化和无监督分割现象。 | 待写 |
| 20｜DINOv2、iBOT、Registers 与 DINOv3 | 按论文分别讲 patch 级目标、数据策展、模型扩展、register tokens 和 DINOv3 的 Gram anchoring；对比全局与稠密特征。 | 待写 |

### E｜检测、分割与开放世界感知

| 讲次与主题 | 讲解范围 | 状态 |
| --- | --- | --- |
| 21｜R-CNN 家族、FPN 与 YOLO | 精读候选区域、RoI pooling/align、anchor、单阶段/双阶段、多尺度特征和 NMS；梳理 YOLO 的关键范式。 | 待写 |
| 22｜DETR 与端到端检测 | 精读 object queries、集合预测、匈牙利匹配、二分图损失；比较 Deformable DETR 和检测版 DINO。 | 待写 |
| 23｜FCN、U-Net、DeepLab 与 Mask2Former | 精读上采样、跳跃连接、空洞卷积、实例与全景分割、mask 分类和 query 机制。 | 待写 |
| 24｜SAM → SAM 2 → SAM 3 | 逐篇讲图像/提示编码器、mask decoder、数据引擎；SAM 2 的视频记忆与 SAM 3 的概念提示检测/分割/跟踪。 | 待写 |
| 25｜开放词汇检测与分割 | OWL-ViT、GLIP、Grounding DINO、OVSeg/ODISE；语言条件、区域词语对齐、开放词汇与开放集识别。 | 待写 |

### F｜视觉语言预训练的演进

| 讲次与主题 | 讲解范围 | 状态 |
| --- | --- | --- |
| 26｜Captioning、VQA 与早期跨模态融合 | Show and Tell、Show Attend and Tell、Bottom-Up/Top-Down attention；编码解码、区域特征、问答数据与语言偏差。 | 待写 |
| 27｜ViLBERT、LXMERT、UNITER | 逐篇比较双流/单流结构、跨模态注意力、masked region/text modeling、匹配与对齐目标。 | 待写 |
| 28｜CLIP 与 ALIGN | 精读图文双塔、对称对比损失、batch 内负样本、zero-shot 分类、prompt ensemble 和检索。 | 待写 |
| 29｜SigLIP、SigLIP 2 与 CoCa | 比较 sigmoid/softmax 目标、生成与对比联合学习、语义定位、稠密特征和多语言训练。 | 待写 |
| 30｜ALBEF 与 BLIP | 精读先对齐后融合、动量蒸馏、caption bootstrapping、图文对比/匹配/生成联合目标。 | 待写 |

### G｜大语言模型时代的 VLM 架构

| 讲次与主题 | 讲解范围 | 状态 |
| --- | --- | --- |
| 31｜视觉编码器如何接入 LLM | 投影层/MLP、Q-Former、Perceiver Resampler、交叉注意力、视觉 token 拼接；梳理冻结和训练参数。 | 待写 |
| 32｜Flamingo | 精读交错图文、Perceiver Resampler、gated cross-attention、few-shot 与混合数据训练。 | 待写 |
| 33｜BLIP-2 与 InstructBLIP | 精读 Q-Former 的 query、分阶段预训练和指令条件特征提取；比较与 Flamingo 的不同连接方式。 | 待写 |
| 34｜LLaVA 技术谱系 | 原版 Visual Instruction Tuning、LLaVA-1.5、NeXT、OneVision；视觉指令合成、连接器、数据配方与多图/视频扩展。 | 待写 |
| 35｜代表性 VLM 架构横向对比 | Qwen-VL 系列、InternVL 系列、PaLI、Idefics、Molmo；按 encoder、connector、LLM、输入协议和开放程度比较。 | 待写 |

### H｜数据、训练与精细视觉能力

| 讲次与主题 | 讲解范围 | 状态 |
| --- | --- | --- |
| 36｜图文与交错数据工程 | LAION、DataComp、OBELICS 等；去重、过滤、caption 改写、合成数据、数据混合、许可与污染审计。 | 待写 |
| 37｜高分辨率与动态视觉输入 | LLaVA-NeXT、InternVL tiling、Qwen2-VL/2.5-VL；裁剪、缩略图、动态分辨率、token merging 与 M-RoPE。 | 待写 |
| 38｜多模态训练全流程 | 预训练、对齐、mid-training、SFT；冻结/解冻、loss mask、sample packing、数据课程、多任务混合与遗忘。 | 待写 |
| 39｜OCR、文档、图表与科学视觉 | LayoutLM、Donut、Pix2Struct、Nougat 等；文字识别、布局、表格结构、图表读数、多页文档和公式。 | 待写 |
| 40｜区域、空间与多图理解 | Kosmos-2、Shikra、Ferret、Molmo；坐标表示、referential grounding、关系推理、计数和跨图对应。 | 待写 |

### I｜视觉推理、后训练与智能体

| 讲次与主题 | 讲解范围 | 状态 |
| --- | --- | --- |
| 41｜多模态思维链与视觉推理 | ScienceQA、Multimodal-CoT 等；感知、证据抽取、符号推理、语言先验和交错视觉思考。 | 待写 |
| 42｜多模态偏好学习与强化学习 | DPO、PPO/GRPO 在视觉任务中的适配；可验证奖励、过程奖励、RL 数据、reward hacking，结合 VisRL 等案例。 | 待写 |
| 43｜视觉工具调用与主动观察 | VisProg、ViperGPT、Visual Sketchpad；crop/zoom、OCR、检测、分割、深度、代码与验证器。 | 待写 |
| 44｜GUI 与屏幕智能体 | SeeClick、UI-TARS 等；屏幕 grounding、操作轨迹、动作空间、SFT/RL、离线与在线任务成功率。 | 待写 |
| 45｜多模态 RAG、记忆与持续学习 | ColPali 等视觉文档检索、多页证据聚合、图像/视频记忆、知识更新与灾难性遗忘。 | 待写 |

### J｜视觉生成的数学基础与历史

| 讲次与主题 | 讲解范围 | 状态 |
| --- | --- | --- |
| 46｜AE、VAE、GAN 与 StyleGAN | 精读 ELBO、重参数化、对抗博弈、模式坍塌、style modulation 和生成评估。 | 待写 |
| 47｜自回归图像与离散视觉 token | PixelCNN、VQ-VAE/VQGAN、ImageGPT、早期 DALL·E；码本、重建、序列建模和压缩。 | 待写 |
| 48｜DDPM 与 DDIM | 精读前向加噪、反向去噪、变分下界、噪声预测与采样；区分随机与确定性采样路径。 | 待写 |
| 49｜Score-based SDE 与 EDM | score matching、反向 SDE、probability-flow ODE、噪声参数化、预条件与采样器。 | 待写 |
| 50｜Flow Matching 与 Rectified Flow | 连续性方程、速度场、条件路径、conditional flow matching、rectification 与 distillation。 | 待写 |

### K｜现代生成、控制与理解生成统一

| 讲次与主题 | 讲解范围 | 状态 |
| --- | --- | --- |
| 51｜Latent Diffusion 与 Stable Diffusion | 精读自编码器、潜空间压缩、cross-attention 条件和训练流水线；分析压缩率与细节损失。 | 待写 |
| 52｜DiT、MMDiT 与现代生成架构 | 精读 DiT 的 patch token、adaLN、计算扩展，以及 SD3 等 MMDiT 的文本/图像交互；公开资料不足处明确标注。 | 待写 |
| 53｜引导与条件控制 | Classifier-free guidance、ControlNet、T2I-Adapter、IP-Adapter；文本、边缘、深度、姿态和参考图控制。 | 待写 |
| 54｜编辑、个性化与一致性 | InstructPix2Pix、DreamBooth、LoRA 与参考图编辑；inpainting、身份保持、局部编辑和多轮一致性。 | 待写 |
| 55｜理解与生成统一模型 | Emu、Chameleon、Show-o、Janus、BAGEL、InternVL-U；离散/连续表征、AR/diffusion、分支解耦与任务混合。 | 待写 |

### L｜视频理解、流式视觉与视频生成

| 讲次与主题 | 讲解范围 | 状态 |
| --- | --- | --- |
| 56｜视频表征的技术演进 | Two-Stream、I3D、SlowFast、TimeSformer、Video Swin、VideoMAE；时空卷积、tubelet、时间注意力。 | 待写 |
| 57｜视频语言模型 | Video-LLaMA、LLaVA-Video、Qwen-VL 视频路线等；帧采样、时间戳、压缩、音视文同步和训练数据。 | 待写 |
| 58｜长视频、流式输入与视觉记忆 | MovieChat、LongVA、Molmo2、POINTS-Long 等；事件检索、时序 grounding、历史更新、在线记忆与缓存。 | 待写 |
| 59｜视频生成模型 | Video Diffusion、SVD、CogVideoX、HunyuanVideo、Wan 等公开路线；3D VAE、时空 DiT、I2V 与长视频扩展。 | 待写 |
| 60｜生成视频的物理与时序能力 | 对象持久性、运动、相机控制、交互、因果与长时程漂移；FVD、VBench 与任务化测试。 | 待写 |

### M｜三维、几何与空间基础模型

| 讲次与主题 | 讲解范围 | 状态 |
| --- | --- | --- |
| 61｜多视几何、SfM 与 SLAM | 内外参、对极几何、三角化、PnP、BA、尺度歧义、回环与坐标系统；衔接站内标定笔记。 | 待写 |
| 62｜点云、深度与稠密几何 | PointNet/PointNet++、MiDaS/DPT、Depth Anything；单目与多目、相对与度量深度、数据合成和泛化。 | 待写 |
| 63｜DUSt3R、MASt3R 与 VGGT | 逐篇讲 pointmap、匹配、坐标对齐、camera/depth/track 联合预测与前馈多视图融合。 | 待写 |
| 64｜NeRF、Instant-NGP 与 3DGS | 逐篇讲体渲染、密度/颜色、位置编码、hash grid、Gaussian splatting、可见性与优化；与已有 3DGS 笔记衔接。 | 待写 |
| 65｜3D 语言理解与三维生成 | 3D-LLM、LEO、DreamFusion、LRM 等；对象/场景 token、3D grounding、SDS 和前馈重建。 | 待写 |

### N｜世界模型、空间智能与具身模型

| 讲次与主题 | 讲解范围 | 状态 |
| --- | --- | --- |
| 66｜I-JEPA、V-JEPA 与 V-JEPA 2 | 精读潜空间预测、teacher/target encoder、mask 策略、预测器和动作条件化；比较像素预测与语义状态预测。 | 待写 |
| 67｜交互式世界模型 | Dreamer、Genie、Cosmos 等公开方法；潜状态、latent actions、视频模拟、rollout 与规划；公开程度逐项标注。 | 待写 |
| 68｜RT-1、RT-2 与 PaLM-E | 逐篇讲机器人动作 token、视觉语言知识迁移、传感器/状态注入、不同机器人数据和泛化。 | 待写 |
| 69｜现代机器人策略与 VLA | ACT、Diffusion Policy、OpenVLA、Octo、π0、π0.5；action chunking、连续动作、flow matching 与跨任务训练。 | 待写 |
| 70｜导航、空间记忆与跨机器人泛化 | R2R/Habitat 等导航环境、Open X-Embodiment/DROID 数据；认知地图、闭环观察、sim-to-real 与不同形态。 | 待写 |

### O｜评估、可信性与失效分析

| 讲次与主题 | 讲解范围 | 状态 |
| --- | --- | --- |
| 71｜理解模型评测地图 | ImageNet/COCO/VQA、MMBench、MMMU、MathVista、OCRBench、BLINK；按感知、知识、推理、空间和时间分类。 | 待写 |
| 72｜视觉幻觉与 grounding 失败 | CHAIR、POPE、HallusionBench 等；对象、属性、关系与时序幻觉，语言先验、证据引用和拒答校准。 | 待写 |
| 73｜鲁棒性、捷径与因果实验 | OOD、分辨率、遮挡、噪声、计数/空间组合、反事实替图、text-only/vision-only 控制与数据污染。 | 待写 |
| 74｜生成、编辑与具身评测 | FID/KID、CLIPScore、GenEval、DPG-Bench、VBench、LIBERO；自动指标、人工评分和真实任务成功率。 | 待写 |
| 75｜多模态安全、隐私与负责任数据 | 图像/文档中的提示注入、对抗样本、敏感信息、偏差、版权/许可、内容溯源与模型卡。 | 待写 |

### P｜工程、效率与研究方法

| 讲次与主题 | 讲解范围 | 状态 |
| --- | --- | --- |
| 76｜视觉 token 与资源账本 | 从图像尺寸/裁剪数/帧数到 encoder FLOPs、LLM prefill、KV cache、显存和端到端延迟；建立可计算示例。 | 待写 |
| 77｜微调、蒸馏与量化 | LoRA/QLoRA、adapter、编码器/连接器微调、知识蒸馏、PTQ/QAT；检测 OCR、小目标和坐标能力退化。 | 待写 |
| 78｜视觉压缩与自适应计算 | ToMe、FastV、FastVLM 等；pruning、merging、query-based compression、动态分辨率与自适应观察。 | 待写 |
| 79｜多模态推理服务与部署 | 图像预处理、视觉编码、prefill/decode、异构请求、batching、encoder 缓存/分离、流式视频和边缘部署。 | 待写 |
| 80｜论文阅读、复现与研究选题 | 问题定义、最强基线、创新与证据、消融、复现检查、失败实验、最小决定性实验与计算预算。 | 待写 |

## 六、10个前沿专题

专题将讲原理、证据、分歧、失效和最小验证实验，不能只做排行榜。

| 专题 | 原理与问题 | 状态 |
| --- | --- | --- |
| F01｜稠密视觉表征为何再次重要 | DINOv3；Gram anchoring、全局/局部目标协调，比较 frozen features 与端到端微调。 把分类、分割、深度和匹配分开验证，讨论表征能否真正跨任务迁移。 | 待写 |
| F02｜原生多模态架构与训练 | Qwen3-VL 的 interleaved-MRoPE、DeepStack、文本时间戳；Qwen3.5 官方材料中的原生多模态、混合注意力和 MoE。；后续 Qwen3.6/3.8 作为同谱系版本对比，依据官方公开资料。 比较晚期接入、联合预训练与计算效率；只讲公开的结构和训练信息，未知细节保留未知。 | 待写 |
| F03｜视觉推理瓶颈：先看清，再推理 | CVPR 2026 的 Downscaling Intelligence（Extract+Think）与 DiG；相关奖励驱动视觉推理工作。 比较感知抽取、差异定位、推理后训练；设计相同骨干与数据预算下的因果消融。 | 待写 |
| F04｜视觉潜空间推理与选择性解码 | VL-JEPA 的目标文本 embedding 预测；CVPR 2026 Monet 的视觉 latent reasoning 与 VLPO。 区分表示预测、潜空间推理和最终文本解码；检查潜变量是否真在承担视觉计算。 | 待写 |
| F05｜理解、推理、生成与编辑统一 | BAGEL 与 2026 InternVL-U；离散/连续表征、理解与生成分支、MMDiT 生成头和训练混合。 统一是否带来实际能力迁移；控制参数量、数据和 FLOPs，分析负迁移。 | 待写 |
| F06｜长视频走向在线流式视觉 | Molmo2 与 CVPR 2026 POINTS-Long；point-driven grounding、训练数据、动态视觉 token 与可维护缓存。 评价事件召回、temporal grounding、跨帧身份、历史记忆和质量—延迟权衡。 | 待写 |
| F07｜开放概念感知与视觉工具表示 | SAM 3；CVPR 2026 Perception Programs；概念提示、硬负样本、结构化工具结果和观察接口。 比较 noun phrase、复杂指令、像素工具输出与语言化证据，测量指令到实例的可靠性。 | 待写 |
| F08｜几何基础模型与空间记忆 | VGGT；结合 CVPR 2026 CLiViS 的动态认知地图分析几何状态与语言状态。 区分预测几何、维护地图和使用地图推理；评价坐标一致、尺度、遮挡与长期重定位。 | 待写 |
| F09｜世界模型能否支持规划和评估 | V-JEPA 2 与动作条件潜状态预测；像素生成路线作为对照，讨论模型预测控制和物理可靠性。 用行动后果、rollout 误差、真实环境迁移验证；避免只以逼真视频证明世界理解。 | 待写 |
| F10｜VLA 的泛化与真实闭环能力 | π0/π0.5、OpenVLA、公开的后续 VLA 工作；连续动作、数据混合、知识迁移与在线反馈。 区分新对象、新任务、新环境和新机器人，研究小数据迁移、失败恢复与实际任务完成。 | 待写 |

## 七、实验与附录

**8个实验，待写：**小型CNN/ViT；自监督；CLIP检索；最小VLM；感知推理分离；DDPM/Flow；长视频/空间；部署和受控复现。

**6个附录，待写：**中英术语；损失推导；维度/复杂度/资源；论文时间线；数据/评测/复现；行业与特殊模态入口。

缩小实验验证机制不等于复现原论文全量指标。实验教程将明确输入、代码、预期性质与限制。

## 八、图解、练习与学习方法

先自己算再看答案。算不出时检查轴、条件、归一化分母和梯度路径，不急着背结论。读完后改变一个数字再算一遍，并用自己的话解释机制。

SVG可缩放图与正文共同解释方块、箭头和变量。图是理解工具，不能代替符号定义；文章中的教学数值也不是实际模型实验结果。

## 九、已有笔记与参考课程

可补充阅读：[CS336](../series/cs336/)、[AI Infra](../series/ai-infra-survey/)、[相机标定](../camera-calibration/)、[3DGS](../3d-gaussian-splatting/)。新专栏仍就地补所需先修，交叉链接不代替视觉特有推导。

课程参考：[Stanford CS231n](https://cs231n.stanford.edu/schedule.html)、[CMU 16-824](https://visual-learning.cs.cmu.edu/)、[Berkeley CS C280](https://cs280-berkeley.github.io/sp25)、[Oxford Computer Vision](https://www.cs.ox.ac.uk/teaching/courses/2025-2026/vision/)、[MIT生成课程官方仓库](https://github.com/eje24/iap-diffusion-class)。

课程帮助覆盖和组织，正文依据原始论文、补充材料和作者代码。明确区分定义/推导、作者报告、本地教学验证与未知细节；前沿版本在写作时重新核验。
