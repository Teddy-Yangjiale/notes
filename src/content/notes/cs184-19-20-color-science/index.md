---
title: "CS184 春季 L19–20：颜色科学，从光谱到屏幕"
date: 2026-11-07
updated: 2026-11-07
summary: "光谱进入眼睛 → 三类感受器积分 → 同色异谱 → 三基色匹配 → 颜色空间与色域 → 线性运算与显示。以原课件为依据，配 20 张可编辑图解、12 个数值例子、26 道带答案自测与 PDF 全页索引。"
tags: ["计算机图形学", "CS184", "课程笔记"]
series: "cs184"
order: 19
shortTitle: "春季 L19–20"
---

> UC Berkeley · CS184/284A · Spring 2026 · 文件标识 `SP26-L19-20-color-science.pdf`。
> 本文的 **pN 一律是 PDF 的第 N 页**，不是封面讲次或页脚旧编号。文件名与封面可能不同，以下均按文件和页码回查。

## 0. 先抓住这一条推理链

```text
光谱进入眼睛
    ↓
三类感受器积分
    ↓
同色异谱
    ↓
三基色匹配
    ↓
颜色空间与色域
    ↓
线性运算与显示
```

这篇笔记的阅读顺序是：先理解输入和输出，再确认公式的条件，最后用小数值检查。
正文将课件概念、补充推导和教学例子分开；示意图中的理想几何与数字不冒充真实实验测量。

| 内容 | 本文提供什么 |
|---|---|
| 来源 | Spring 2026，PDF 共 112 页；正文选择 70 张关键页 |
| 图解 | 12 张概念关系图 + 8 张几何或数值图，均有原生可编辑 PPTX |
| 手算 | 12 个带输入、结果和回代检查的教学例子 |
| 复习 | 26 道自测及答案，末尾保留全页索引 |
| 运行证据 | 数值核对脚本覆盖解析小模型，不代表完整渲染器或模拟器已经实现 |

[下载本篇 20 张可编辑图解（PPTX 与操作 JSON）](/notes/cs184/figures/19-editable.zip)

### 课件与推导的使用边界

课件截图用于对照原始定义与几何；正文用中文解释关系，并提供必要的修正与推导。
后续专题按本地文件的学期和编号组织，不假定它们与秋季一一对应。
若只做第一遍学习，先读每节前两段和数值例子，再展开原页核对。

### 与前面哪一讲接上

先回顾[相关前置讲义](/notes/cs184-18-material-modeling/)。本篇在已有表示与数学工具上增加新变量或新约束，而不是另起一套互不相关的公式。

## 1. 颜色为什么不是波长的别名？

单色光可以用一个波长描述，但日常颜色通常来自多个波长的混合。物体的反射光谱是照明光谱与反射率光谱共同作用的结果。

屏幕显示课件的光谱照片只是颜色再现，无法真正输出原来那条窄谱。首先分清物理光谱、感受器响应和屏幕编码，后面的“相同颜色”才有明确含义。

![概念关系：颜色为什么不是波长的别名？](diagrams/d01-relation.png)

*读图：照明光谱 → 材料光谱响应 → 进入眼睛的光谱。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| Phi | 光谱功率分布 |
| R | 光谱反射率 |
| 假设 | 不含荧光等波长转换 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
\Phi_{out}(\lambda)=\Phi_{in}(\lambda)R(\lambda)
$$

### 🔧 手算 1：把关系落到数字上

两个波段输入为 (4,2)，反射率 (0.25,0.5)，输出 (1,1)。逐项反算 1/4=0.25、1/2=0.5；同样输出可由其他输入与反射率组合产生。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 逐项反算 1/4=0.25、1/2=0.5；同样输出可由其他输入与反射率组合产生。 |
| 适用边界 | RGB 通道不是三条固定波长的能量计；不能直接把某个 R 值等同于某个波长功率。 |

![几何或数值解释 1](diagrams/d13-spectrum.png)

*光谱形状不同不自动意味着感知不同；图中未声称两条任意曲线是实测同色异谱。*

### ⚠️ 易错点：先识别症状与假设

RGB 通道不是三条固定波长的能量计；不能直接把某个 R 值等同于某个波长功率。

### 停下来解释一次

**问题：白物体在红灯下必然仍显示白色吗？**

<details>
<summary>展开参考回答</summary>

不。入射光谱改变后反射光谱会变，感知还受适应与环境影响。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### What is Light?

*PDF p2 · 对应本节：颜色为什么不是波长的别名？*

![PDF p2：What is Light?](images/p002.png)

#### Monochromator

*PDF p5 · 对应本节：颜色为什么不是波长的别名？*

![PDF p5：Monochromator](images/p005.png)

#### Spectrometer

*PDF p6 · 对应本节：颜色为什么不是波长的别名？*

![PDF p6：Spectrometer](images/p006.png)

#### Spectral Colors

*PDF p7 · 对应本节：颜色为什么不是波长的别名？*

![PDF p7：Spectral Colors](images/p007.png)

#### Other Colors

*PDF p12 · 对应本节：颜色为什么不是波长的别名？*

![PDF p12：Other Colors](images/p012.png)

#### Reflected Light

*PDF p15 · 对应本节：颜色为什么不是波长的别名？*

![PDF p15：Reflected Light](images/p015.png)

#### Simple Model of a Detector

*PDF p16 · 对应本节：颜色为什么不是波长的别名？*

![PDF p16：Simple Model of a Detector](images/p016.png)

</details>

## 2. 视锥如何把光谱压成三个数？

三类视锥各有宽谱且重叠的敏感度。响应是光谱与敏感度函数乘积的积分，不是只取红绿蓝三个波长。

原页把该式称为 convolution integral；按这里的固定波长响应模型，更准确是积分内积，而不是平移卷积。这个线性测量模型解释颜色匹配，但完整视觉感知还包含非线性与空间环境。

![概念关系：视锥如何把光谱压成三个数？](diagrams/d02-relation.png)

*读图：连续光谱 → 三条敏感度积分 → 三个响应数。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| s_j | 感受器敏感度 |
| Phi | 入射光谱 |
| cj | 模型响应 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
c_j=\int \Phi(\lambda)s_j(\lambda)\,d\lambda,\quad j\in\{L,M,S\}
$$

### 🔧 手算 2：把关系落到数字上

离散教学敏感度 (0.2,0.8)，光谱 (3,1)，响应 3×0.2+1×0.8=1.4。光谱全部加倍后响应 2.8，验证线性。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 光谱全部加倍后响应 2.8，验证线性。 |
| 适用边界 | 不要把 L、M、S 直接叫显示器 R、G、B；两者基底不同。 |

### ⚠️ 易错点：先识别症状与假设

不要把 L、M、S 直接叫显示器 R、G、B；两者基底不同。

### 停下来解释一次

**问题：三类视锥是否分别只响应红、绿、蓝？**

<details>
<summary>展开参考回答</summary>

不是，响应曲线较宽且重叠，名称表示相对长中短波敏感性。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Eyes as Sensors

*PDF p34 · 对应本节：视锥如何把光谱压成三个数？*

![PDF p34：Eyes as Sensors](images/p034.png)

#### Photoreceptor Size and Distribution Vary Across Retina

*PDF p37 · 对应本节：视锥如何把光谱压成三个数？*

![PDF p37：Photoreceptor Size and Distribution Vary Across Retina](images/p037.png)

#### On the Retina, Three Types of Cone Cells

*PDF p38 · 对应本节：视锥如何把光谱压成三个数？*

![PDF p38：On the Retina, Three Types of Cone Cells](images/p038.png)

#### Cones

*PDF p42 · 对应本节：视锥如何把光谱压成三个数？*

![PDF p42：Cones](images/p042.png)

#### Cones

*PDF p44 · 对应本节：视锥如何把光谱压成三个数？*

![PDF p44：Cones](images/p044.png)

#### Cones

*PDF p45 · 对应本节：视锥如何把光谱压成三个数？*

![PDF p45：Cones](images/p045.png)

#### Cones

*PDF p47 · 对应本节：视锥如何把光谱压成三个数？*

![PDF p47：Cones](images/p047.png)

</details>

## 3. 同色异谱为什么允许显示器工作？

光谱有许多自由度，感受器只返回三个测量值，因此不同光谱可以产生相同三响应，这叫同色异谱。显示器不需要复现每个波长，只需在一定观看条件下匹配响应。

匹配依赖观察者和光照条件。两块颜料在一种灯下匹配，换灯后可能分开；相机传感器敏感度也不必与人眼相同。

![概念关系：同色异谱为什么允许显示器工作？](diagrams/d03-relation.png)

*读图：不同光谱 → 相同三响应 → 同色异谱匹配。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| S | 三通道光谱测量矩阵 |
| Phi | 多波段向量 |
| 零空间 | 被测量压缩掉的差异 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
S\Phi_1=S\Phi_2\quad\text{即}\quad S(\Phi_1-\Phi_2)=0
$$

### 🔧 手算 3：把关系落到数字上

教学单通道 S=(1,1)，光谱 (1,0) 与 (0,1) 都给 1。若传感器换成 (1,2)，响应变为 1 与 2，匹配消失。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 若传感器换成 (1,2)，响应变为 1 与 2，匹配消失。 |
| 适用边界 | 这个两波段例是降维直觉，不是真实人眼同色异谱数据。 |

### ⚠️ 易错点：先识别症状与假设

这个两波段例是降维直觉，不是真实人眼同色异谱数据。

### 停下来解释一次

**问题：相机看起来一样的颜色，人眼一定也一样吗？**

<details>
<summary>展开参考回答</summary>

不一定。两者光谱敏感度不同，尤其在窄谱光源下可能出现明显差异。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Cones and Metamers

*PDF p50 · 对应本节：同色异谱为什么允许显示器工作？*

![PDF p50：Cones and Metamers](images/p050.png)

#### Metamerism is a Big Effect

*PDF p51 · 对应本节：同色异谱为什么允许显示器工作？*

![PDF p51：Metamerism is a Big Effect](images/p051.png)

#### Trichromaticity

*PDF p52 · 对应本节：同色异谱为什么允许显示器工作？*

![PDF p52：Trichromaticity](images/p052.png)

#### Cone Responses are Linear

*PDF p53 · 对应本节：同色异谱为什么允许显示器工作？*

![PDF p53：Cone Responses are Linear](images/p053.png)

#### Superposition (Linearity) of Spectral Power Distributions

*PDF p54 · 对应本节：同色异谱为什么允许显示器工作？*

![PDF p54：Superposition (Linearity) of Spectral Power Distributions](images/p054.png)

#### Additive Mixing

*PDF p58 · 对应本节：同色异谱为什么允许显示器工作？*

![PDF p58：Additive Mixing](images/p058.png)

</details>

## 4. 三基色匹配为何会出现负数？

选定三种物理基色后，能够用非负强度混合出来的颜色只占有限范围。某些目标无法落在这个范围内，实验中可把一种基色加到目标一侧，再把它记作负系数。

负系数不是负光，而是匹配实验的记账方法。换基底可改变坐标，但不会让实际设备产生无限色域。

![概念关系：三基色匹配为何会出现负数？](diagrams/d04-relation.png)

*读图：固定物理基色 → 求匹配系数 → 发现不可非负表示的颜色。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| c | 目标三响应 |
| P | 三基色响应组成的矩阵 |
| a | 基色混合系数 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
c=P a
$$

### 🔧 手算 4：把关系落到数字上

二维示意 P 的列为 (1,0)、(1,1)，要得到 c=(0,1)，解 a=(-1,1)。验证 -1×(1,0)+(1,1)=(0,1)，说明非负混合做不到。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 验证 -1×(1,0)+(1,1)=(0,1)，说明非负混合做不到。 |
| 适用边界 | 直接把负 RGB 截成零会改变颜色；这是色域映射选择，不是无损数学变换。 |

### ⚠️ 易错点：先识别症状与假设

直接把负 RGB 截成零会改变颜色；这是色域映射选择，不是无损数学变换。

### 停下来解释一次

**问题：负匹配系数是否说明实验错误？**

<details>
<summary>展开参考回答</summary>

不。它可能反映目标在所选物理基色的非负混合范围之外。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### CRT Primaries

*PDF p59 · 对应本节：三基色匹配为何会出现负数？*

![PDF p59：CRT Primaries](images/p059.png)

#### LCD Primaries

*PDF p60 · 对应本节：三基色匹配为何会出现负数？*

![PDF p60：LCD Primaries](images/p060.png)

#### Additive Color Matching

*PDF p61 · 对应本节：三基色匹配为何会出现负数？*

![PDF p61：Additive Color Matching](images/p061.png)

#### Experiment 1

*PDF p65 · 对应本节：三基色匹配为何会出现负数？*

![PDF p65：Experiment 1](images/p065.png)

#### Experiment 2

*PDF p69 · 对应本节：三基色匹配为何会出现负数？*

![PDF p69：Experiment 2](images/p069.png)

#### Color Matching Functions

*PDF p70 · 对应本节：三基色匹配为何会出现负数？*

![PDF p70：Color Matching Functions](images/p070.png)

#### Color Matching Functions

*PDF p71 · 对应本节：三基色匹配为何会出现负数？*

![PDF p71：Color Matching Functions](images/p071.png)

</details>

## 5. XYZ 与色度坐标各保留了什么？

XYZ 是标准颜色表示；把 X、Y、Z 除以总和得到 x、y、z，只剩相对比例。三者和为 1，所以色度图只需两个坐标。

归一化丢掉了整体亮度尺度，xy 相同不代表一样亮；通常还需要 Y 才能恢复 XYZ。黑色总和为零，色度归一化在数学上未定义，代码应单独处理。

![概念关系：XYZ 与色度坐标各保留了什么？](diagrams/d05-relation.png)

*读图：XYZ 三刺激值 → 归一化比例 → xy 色度与独立 Y。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| XYZ | 三刺激值 |
| xy | 色度 |
| Y | 另行保存的亮度相关分量 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
x=\frac X{X+Y+Z},\quad y=\frac Y{X+Y+Z},\quad z=1-x-y
$$

### 🔧 手算 5：把关系落到数字上

XYZ=(2,3,5)，xy=(0.2,0.3)。全部乘二为 (4,6,10) 仍得同一 xy；用 Y=3 恢复总和 Y/y=10，再得 X=2、Z=5。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 全部乘二为 (4,6,10) 仍得同一 xy；用 Y=3 恢复总和 Y/y=10，再得 X=2、Z=5。 |
| 适用边界 | 不要把 xy 平面上的欧氏距离直接当通用感知色差。 |

![几何或数值解释 7](diagrams/d19-bars.png)

*XYZ=(2,3,5) 的色度为 (0.2,0.3)，归一化会丢掉亮度尺度。*

### ⚠️ 易错点：先识别症状与假设

不要把 xy 平面上的欧氏距离直接当通用感知色差。

### 停下来解释一次

**问题：只知道 xy 能否恢复原始 XYZ？**

<details>
<summary>展开参考回答</summary>

不能，还缺整体尺度；给定非零 y 和 Y 后可以恢复。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Φ =

*PDF p72 · 对应本节：XYZ 与色度坐标各保留了什么？*

![PDF p72：Φ =](images/p072.png)

#### Using Color Matching Functions

*PDF p73 · 对应本节：XYZ 与色度坐标各保留了什么？*

![PDF p73：Using Color Matching Functions](images/p073.png)

#### Using Color Matching Functions

*PDF p74 · 对应本节：XYZ 与色度坐标各保留了什么？*

![PDF p74：Using Color Matching Functions](images/p074.png)

#### CIE XYZ

*PDF p75 · 对应本节：XYZ 与色度坐标各保留了什么？*

![PDF p75：CIE XYZ](images/p075.png)

#### Rescaled XYZ to xyz

*PDF p76 · 对应本节：XYZ 与色度坐标各保留了什么？*

![PDF p76：Rescaled XYZ to xyz](images/p076.png)

#### CIE Chromaticity Diagram

*PDF p77 · 对应本节：XYZ 与色度坐标各保留了什么？*

![PDF p77：CIE Chromaticity Diagram](images/p077.png)

</details>

## 6. 色域为什么是有边界的？

设备基色限制可产生的颜色。三种基色的非负加法混合在色度图上形成三角形，目标在三角形外时需要映射或裁剪。

提高位深只是在设备可达范围内增加编码精度，不会自动把基色边界推远。色域、动态范围与位深是三个不同维度，应分别描述。

![概念关系：色域为什么是有边界的？](diagrams/d06-relation.png)

*读图：设备三基色 → 非负混合 → 可达色域。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| c | 色度点 |
| 权重 | 对应适当亮度归一化后的混合比例 |
| 三角形 | 凸组合范围 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
c=\alpha c_1+\beta c_2+\gamma c_3,\quad \alpha+\beta+\gamma=1,\quad \alpha,\beta,\gamma\ge0
$$

### 🔧 手算 6：把关系落到数字上

取 c1=(0,0)、c2=(1,0)、c3=(0,1)，点 (0.2,0.3) 的权重为 (0.5,0.2,0.3)。点 (0.8,0.8) 需要第一权重 -0.6，落在域外。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 点 (0.8,0.8) 需要第一权重 -0.6，落在域外。 |
| 适用边界 | 二维示意坐标不是某个真实设备的色度实测；只用于说明凸包。 |

![几何或数值解释 2](diagrams/d14-gamut.png)

*非负三基色混合覆盖凸三角形，域外目标需要映射。*

### ⚠️ 易错点：先识别症状与假设

二维示意坐标不是某个真实设备的色度实测；只用于说明凸包。

### 停下来解释一次

**问题：从 8 位升级到 10 位一定能显示更饱和的绿色吗？**

<details>
<summary>展开参考回答</summary>

不一定。位深提高精度，是否扩大色域还取决于基色光谱与显示能力。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Gamut

*PDF p78 · 对应本节：色域为什么是有边界的？*

![PDF p78：Gamut](images/p078.png)

#### CIE 1931 RGB Gamut

*PDF p79 · 对应本节：色域为什么是有边界的？*

![PDF p79：CIE 1931 RGB Gamut](images/p079.png)

#### Other Gamuts  (LCDs and NTSC)

*PDF p80 · 对应本节：色域为什么是有边界的？*

![PDF p80：Other Gamuts  (LCDs and NTSC)](images/p080.png)

#### Additive & Subtractive Primaries

*PDF p83 · 对应本节：色域为什么是有边界的？*

![PDF p83：Additive & Subtractive Primaries](images/p083.png)

#### Additive & Subtractive Primaries

*PDF p84 · 对应本节：色域为什么是有边界的？*

![PDF p84：Additive & Subtractive Primaries](images/p084.png)

</details>

## 7. 加色与减色为何不能混为一谈？

显示器把不同发光源的光谱相加；颜料和滤镜则通过吸收改变透过或反射光谱。两者的组合规律不同，“红加绿”的口语在这两个场景中含义也不同。

简单串联滤镜的透过率相乘，是减色的直觉模型；真实颜料还包含散射，不能用这个模型精确预测任何颜料混合。

![概念关系：加色与减色为何不能混为一谈？](diagrams/d07-relation.png)

*读图：光源相加 → 滤镜相乘 → 不同的物理混合规则。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| Phi | 光谱功率 |
| T | 无散射滤镜的光谱透过率 |
| 假设 | 忽略界面多次反射 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
\Phi_{lights}=\Phi_1+\Phi_2,\qquad T_{stack}=T_1T_2
$$

### 🔧 手算 7：把关系落到数字上

某波段两片滤镜透过率 0.5 与 0.2，串联为 0.1；输入 10 输出 1。与发光源 5+2=7 的加法不是同一操作。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 与发光源 5+2=7 的加法不是同一操作。 |
| 适用边界 | “减色”不是把 RGB 数值直接相减；需要知道材料的光谱作用。 |

![几何或数值解释 8](diagrams/d20-bars.png)

*简单滤镜的光谱透过率相乘，与发光源光谱相加不同。*

### ⚠️ 易错点：先识别症状与假设

“减色”不是把 RGB 数值直接相减；需要知道材料的光谱作用。

### 停下来解释一次

**问题：两块显示屏并排显示与叠两片滤镜有什么差别？**

<details>
<summary>展开参考回答</summary>

前者把到眼睛的光相加，后者依次衰减同一束光。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Subtractive Mixing

*PDF p81 · 对应本节：加色与减色为何不能混为一谈？*

![PDF p81：Subtractive Mixing](images/p081.png)

#### Subtractive Mixing

*PDF p82 · 对应本节：加色与减色为何不能混为一谈？*

![PDF p82：Subtractive Mixing](images/p082.png)

#### Additive & Subtractive Primaries

*PDF p83 · 对应本节：加色与减色为何不能混为一谈？*

![PDF p83：Additive & Subtractive Primaries](images/p083.png)

#### Additive & Subtractive Primaries

*PDF p84 · 对应本节：加色与减色为何不能混为一谈？*

![PDF p84：Additive & Subtractive Primaries](images/p084.png)

</details>

## 8. RGB、HSV、Lab 为什么各有用途？

RGB 方便描述设备或线性基底，HSV 方便交互选择色相与饱和度，Lab 试图让坐标距离更接近感知差异。它们不是互相优劣的单一排名，而是服务不同问题。

HSV 中色相是周期变量，低饱和时色相不稳定；Lab 依赖参考白点，跨白点比较需谨慎。不要把任意空间的直线插值都解释为物理混光。

![概念关系：RGB、HSV、Lab 为什么各有用途？](diagrams/d08-relation.png)

*读图：设备编码 RGB → 交互参数 HSV → 感知近似 Lab。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| h | HSV 色相 |
| 周期 | 360 度 |
| 注意 | 灰色附近色相可无意义 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
h\equiv h+360^\circ
$$

### 🔧 手算 8：把关系落到数字上

从 350° 到 10°，短弧中点是 0°，普通算术平均却是 180°。检查两端到 0° 的角距都是 10°。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 检查两端到 0° 的角距都是 10°。 |
| 适用边界 | 直接线性插值色相会绕远路；应选择周期短弧或明确设计路径。 |

### ⚠️ 易错点：先识别症状与假设

直接线性插值色相会绕远路；应选择周期短弧或明确设计路径。

### 停下来解释一次

**问题：Lab 中相同欧氏距离是否在所有条件下都严格同样明显？**

<details>
<summary>展开参考回答</summary>

不是。它是感知均匀性的近似，复杂色差评价与观看条件还需更专门模型。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Color Spaces

*PDF p85 · 对应本节：RGB、HSV、Lab 为什么各有用途？*

![PDF p85：Color Spaces](images/p085.png)

#### Color Spaces

*PDF p86 · 对应本节：RGB、HSV、Lab 为什么各有用途？*

![PDF p86：Color Spaces](images/p086.png)

#### HSV Color Space (Hue-Saturation-Value)

*PDF p87 · 对应本节：RGB、HSV、Lab 为什么各有用途？*

![PDF p87：HSV Color Space (Hue-Saturation-Value)](images/p087.png)

#### Color Spaces

*PDF p89 · 对应本节：RGB、HSV、Lab 为什么各有用途？*

![PDF p89：Color Spaces](images/p089.png)

#### CIELAB Space (AKA L*a*b*)

*PDF p91 · 对应本节：RGB、HSV、Lab 为什么各有用途？*

![PDF p91：CIELAB Space (AKA L*a*b*)](images/p091.png)

</details>

## 9. 为什么平均黑白不能直接平均编码？

物理光叠加在线性量上进行，显示编码通常是非线性的。教学幂律 I=a^γ 描述了编码值与显示强度之间的区别；真实 sRGB 是分段函数，不应简单等同 γ=2.2。

渲染累积、混光与通常的颜色过滤要在线性光空间中做，再编码输出；数据纹理不走颜色解码。把这条路径弄反，会造成暗边、错误透明混合和曝光异常。

![概念关系：为什么平均黑白不能直接平均编码？](diagrams/d09-relation.png)

*读图：解码为线性光 → 运算与平均 → 编码为显示值。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| I | 线性强度 [0,1] |
| a | 非线性编码 |
| gamma | 这里只是幂律模型 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
a=I^{1/\gamma},\qquad \gamma=2.2\ \text{（教学近似）}
$$

### 🔧 手算 9：把关系落到数字上

黑白各一半，线性均值 I=0.5，编码约 0.72974；直接平均编码得 0.5，显示强度约 0.21764。把 0.72974 的 2.2 次方算回约 0.5。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 把 0.72974 的 2.2 次方算回约 0.5。 |
| 适用边界 | 不要把幂律近似写成 sRGB 标准公式；实际代码应使用所选编码的正确传递函数。 |

![几何或数值解释 3](diagrams/d15-curve.png)

*幂律演示编码值与线性光量的区别，不是完整 sRGB 标准曲线。*

![几何或数值解释 4](diagrams/d16-bars.png)

*前两列数值相同但语义不同，正确线性均值 0.5 编码后约 0.72974。*

### ⚠️ 易错点：先识别症状与假设

不要把幂律近似写成 sRGB 标准公式；实际代码应使用所选编码的正确传递函数。

### 停下来解释一次

**问题：为什么第一课渐变图不适合直接判断物理亮度均匀？**

<details>
<summary>展开参考回答</summary>

它通常把编码值均匀写入文件，显示强度未必随像素位置线性变化。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Monitor Intensity and Gamma

*PDF p92 · 对应本节：为什么平均黑白不能直接平均编码？*

![PDF p92：Monitor Intensity and Gamma](images/p092.png)

#### Determining Gamma

*PDF p93 · 对应本节：为什么平均黑白不能直接平均编码？*

![PDF p93：Determining Gamma](images/p093.png)

#### Determining Gamma

*PDF p94 · 对应本节：为什么平均黑白不能直接平均编码？*

![PDF p94：Determining Gamma](images/p094.png)

</details>

## 10. HDR 为什么不是把所有值截到 1？

高动态范围图像记录较大亮度跨度，而显示器只能呈现有限范围。曝光先调整尺度，色调映射再压缩范围，同时尽量保留可见结构与合理外观。

裁剪会让所有超出上限的高光变成同一个值；非线性压缩能保留差异，但也会改变局部或整体对比。色调映射不等于显示编码，两步作用不同。

![概念关系：HDR 为什么不是把所有值截到 1？](diagrams/d10-relation.png)

*读图：线性 HDR → 曝光与色调映射 → 显示编码。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| L | 曝光后的非负线性值 |
| T | 压缩后的值 |
| 限制 | 此式仅示范动态范围压缩 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
T(L)=\frac L{1+L}\quad\text{（教学示例，不代表原页指定算法）}
$$

### 🔧 手算 10：把关系落到数字上

L=1、3、9 分别得到 0.5、0.75、0.9。反解 L=T/(1-T)，0.75 恢复为 3；硬裁剪则三者都为 1。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 反解 L=T/(1-T)，0.75 恢复为 3；硬裁剪则三者都为 1。 |
| 适用边界 | 先裁剪再做 tone mapping 已经丢失高光信息，之后无法恢复差别。 |

![几何或数值解释 6](diagrams/d18-curve.png)

*教学色调映射保留高亮值差异，而硬裁剪会把它们全部压成 1。*

### ⚠️ 易错点：先识别症状与假设

先裁剪再做 tone mapping 已经丢失高光信息，之后无法恢复差别。

### 停下来解释一次

**问题：调高曝光与改 gamma 是否等价？**

<details>
<summary>展开参考回答</summary>

不。前者主要缩放线性光量，后者改变编码或显示响应曲线。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Dynamic Range

*PDF p95 · 对应本节：HDR 为什么不是把所有值截到 1？*

![PDF p95：Dynamic Range](images/p095.png)

#### Dynamic Range

*PDF p96 · 对应本节：HDR 为什么不是把所有值截到 1？*

![PDF p96：Dynamic Range](images/p096.png)

#### Fake High Dynamic Range

*PDF p97 · 对应本节：HDR 为什么不是把所有值截到 1？*

![PDF p97：Fake High Dynamic Range](images/p097.png)

#### Tone Mapping

*PDF p98 · 对应本节：HDR 为什么不是把所有值截到 1？*

![PDF p98：Tone Mapping](images/p098.png)

</details>

## 11. 为什么相同像素看起来不同？

视觉系统会适应环境亮度，并利用周围对比判断颜色和结构。Mach bands 等现象提醒我们，像素数值相同不代表主观外观一定相同。

感受器的线性测量是局部基础模型，不能推导出完整视觉感知必然线性。调图时应同时检查数值与观看背景，尤其不要用单次肉眼判断替代颜色管理。

![概念关系：为什么相同像素看起来不同？](diagrams/d11-relation.png)

*读图：固定目标数值 → 改变背景与适应 → 改变感知外观。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| L | 目标亮度 |
| Lb | 背景亮度 |
| 说明 | 教学对比指标，非完整感知模型 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
C_{Weber}=\frac{L-L_b}{L_b}\quad(L_b>0)
$$

### 🔧 手算 11：把关系落到数字上

目标亮度 6，背景 4 时对比为 0.5；背景 5 时为 0.2。目标没变，关系却变了；反算 4×1.5=6。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 目标没变，关系却变了；反算 4×1.5=6。 |
| 适用边界 | 对比指标不是个体视觉反应的精确预测，不能把课堂错觉图当测量仪。 |

![几何或数值解释 5](diagrams/d17-contrast.png)

*相同中心灰块处在不同背景中；数值相同与感知相同是不同问题。*

### ⚠️ 易错点：先识别症状与假设

对比指标不是个体视觉反应的精确预测，不能把课堂错觉图当测量仪。

### 停下来解释一次

**问题：视觉错觉是否证明物理测量没有意义？**

<details>
<summary>展开参考回答</summary>

不。它说明测量与感知是不同层次，需要分别建模。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Everything is Relative

*PDF p18 · 对应本节：为什么相同像素看起来不同？*

![PDF p18：Everything is Relative](images/p018.png)

#### Adapt

*PDF p20 · 对应本节：为什么相同像素看起来不同？*

![PDF p20：Adapt](images/p020.png)

#### Mach Bands

*PDF p22 · 对应本节：为什么相同像素看起来不同？*

![PDF p22：Mach Bands](images/p022.png)

#### Everything’s Still Relative

*PDF p24 · 对应本节：为什么相同像素看起来不同？*

![PDF p24：Everything’s Still Relative](images/p024.png)

#### Bezold Effect

*PDF p26 · 对应本节：为什么相同像素看起来不同？*

![PDF p26：Bezold Effect](images/p026.png)

#### Perception

*PDF p27 · 对应本节：为什么相同像素看起来不同？*

![PDF p27：Perception](images/p027.png)

#### Watercolor Illusion

*PDF p31 · 对应本节：为什么相同像素看起来不同？*

![PDF p31：Watercolor Illusion](images/p031.png)

#### Rods vs Cones

*PDF p48 · 对应本节：为什么相同像素看起来不同？*

![PDF p48：Rods vs Cones](images/p048.png)

#### Rods Contribute to Color

*PDF p99 · 对应本节：为什么相同像素看起来不同？*

![PDF p99：Rods Contribute to Color](images/p099.png)

</details>

## 12. 哪些颜色现象超出了普通 RGB 表面反射？

散射、干涉、荧光和热辐射有不同机制。薄膜干涉与尺度接近波长的结构需要波动光学解释，荧光改变波长，热辐射随温度改变光谱。

基础 RGB 渲染把连续光谱压缩成三通道，很多情况下够用，但不保证重现这些机制。研究或实现前先确定想重现的现象，再决定是否需要光谱或波动模型。

![概念关系：哪些颜色现象超出了普通 RGB 表面反射？](diagrams/d12-relation.png)

*读图：微观光学机制 → 改变输出光谱 → 重新计算感受器响应。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| h | Planck 常数 |
| c | 光速 |
| lambda | 波长 |
| 范围 | 单光子能量关系 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
E_{photon}=\frac{hc}{\lambda}
$$

### 🔧 手算 12：把关系落到数字上

只比较比例：400 nm 光子能量是 800 nm 的两倍，因为 E400/E800=800/400=2；这不表示同功率的 400 nm 光一定看起来两倍亮。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 只比较比例：400 nm 光子能量是 800 nm 的两倍，因为 E400/E800=800/400=2；这不表示同功率的 400 nm 光一定看起来两倍亮。 |
| 适用边界 | 物理能量、光子数和感知亮度是不同量；“颜色更蓝所以更亮”没有普遍依据。 |

### ⚠️ 易错点：先识别症状与假设

物理能量、光子数和感知亮度是不同量；“颜色更蓝所以更亮”没有普遍依据。

### 停下来解释一次

**问题：只匹配一个光照下的 RGB 能证明光谱材质正确吗？**

<details>
<summary>展开参考回答</summary>

不能。同色异谱允许不同光谱给出同样 RGB，换灯或观察者可能暴露差异。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Color Phenomena

*PDF p100 · 对应本节：哪些颜色现象超出了普通 RGB 表面反射？*

![PDF p100：Color Phenomena](images/p100.png)

#### Reflection

*PDF p101 · 对应本节：哪些颜色现象超出了普通 RGB 表面反射？*

![PDF p101：Reflection](images/p101.png)

#### Transmission

*PDF p102 · 对应本节：哪些颜色现象超出了普通 RGB 表面反射？*

![PDF p102：Transmission](images/p102.png)

#### Scattering

*PDF p103 · 对应本节：哪些颜色现象超出了普通 RGB 表面反射？*

![PDF p103：Scattering](images/p103.png)

#### Interference

*PDF p104 · 对应本节：哪些颜色现象超出了普通 RGB 表面反射？*

![PDF p104：Interference](images/p104.png)

#### Iridescence

*PDF p105 · 对应本节：哪些颜色现象超出了普通 RGB 表面反射？*

![PDF p105：Iridescence](images/p105.png)

#### Fluorescence / Phosphorescence

*PDF p108 · 对应本节：哪些颜色现象超出了普通 RGB 表面反射？*

![PDF p108：Fluorescence / Phosphorescence](images/p108.png)

#### Black Body Radiation

*PDF p110 · 对应本节：哪些颜色现象超出了普通 RGB 表面反射？*

![PDF p110：Black Body Radiation](images/p110.png)

#### Black Body Radiation

*PDF p111 · 对应本节：哪些颜色现象超出了普通 RGB 表面反射？*

![PDF p111：Black Body Radiation](images/p111.png)

</details>

## 13. 把十二个数值例子连成检查顺序

先手算再运行。随仓库提供的 `scripts/cs184-numerical-checks.py` 是小模型验证，不依赖 GPU，也不修改服务器配置。它不能替代完整渲染场景或模拟系统的验证。

| 顺序 | 本节关系 | 最容易漏掉的约定 |
| --- | --- | --- |
| 1 | 颜色为什么不是波长的别名？ | 假设：不含荧光等波长转换 |
| 2 | 视锥如何把光谱压成三个数？ | cj：模型响应 |
| 3 | 同色异谱为什么允许显示器工作？ | 零空间：被测量压缩掉的差异 |
| 4 | 三基色匹配为何会出现负数？ | a：基色混合系数 |
| 5 | XYZ 与色度坐标各保留了什么？ | Y：另行保存的亮度相关分量 |
| 6 | 色域为什么是有边界的？ | 三角形：凸组合范围 |
| 7 | 加色与减色为何不能混为一谈？ | 假设：忽略界面多次反射 |
| 8 | RGB、HSV、Lab 为什么各有用途？ | 注意：灰色附近色相可无意义 |
| 9 | 为什么平均黑白不能直接平均编码？ | gamma：这里只是幂律模型 |
| 10 | HDR 为什么不是把所有值截到 1？ | 限制：此式仅示范动态范围压缩 |
| 11 | 为什么相同像素看起来不同？ | 说明：教学对比指标，非完整感知模型 |
| 12 | 哪些颜色现象超出了普通 RGB 表面反射？ | 范围：单光子能量关系 |

### 复现实验的最小记录

| 记录项 | 用途 |
| --- | --- |
| 固定输入 | 相同几何、材质、网格或信号，避免一次改变多个因素。 |
| 参数与单位 | 包括采样数、步长、分辨率、角度单位、颜色空间。 |
| 输出量 | 保留线性值、误差或状态，再生成展示图。 |
| 参考 | 解析解、手算或高精度结果必须说明来源。 |
| 失败样例 | 边界和极端条件是检查假设的入口。 |

## 14. 实现排查：把公式错误与系统错误分开

本节列出由模型和手算能够判断的排查方向；没有把尚未写出的完整应用测试说成已完成。最小数值检查的真实执行结果见本次发布核对报告。

### 阶段 1：第 1–4 节

| 涉及关系 | 错误机制 / 修正方向 |
| --- | --- |
| 颜色为什么不是波长的别名？ | RGB 通道不是三条固定波长的能量计；不能直接把某个 R 值等同于某个波长功率。 |
| 视锥如何把光谱压成三个数？ | 不要把 L、M、S 直接叫显示器 R、G、B；两者基底不同。 |
| 同色异谱为什么允许显示器工作？ | 这个两波段例是降维直觉，不是真实人眼同色异谱数据。 |
| 三基色匹配为何会出现负数？ | 直接把负 RGB 截成零会改变颜色；这是色域映射选择，不是无损数学变换。 |

### 阶段 2：第 5–8 节

| 涉及关系 | 错误机制 / 修正方向 |
| --- | --- |
| XYZ 与色度坐标各保留了什么？ | 不要把 xy 平面上的欧氏距离直接当通用感知色差。 |
| 色域为什么是有边界的？ | 二维示意坐标不是某个真实设备的色度实测；只用于说明凸包。 |
| 加色与减色为何不能混为一谈？ | “减色”不是把 RGB 数值直接相减；需要知道材料的光谱作用。 |
| RGB、HSV、Lab 为什么各有用途？ | 直接线性插值色相会绕远路；应选择周期短弧或明确设计路径。 |

### 阶段 3：第 9–12 节

| 涉及关系 | 错误机制 / 修正方向 |
| --- | --- |
| 为什么平均黑白不能直接平均编码？ | 不要把幂律近似写成 sRGB 标准公式；实际代码应使用所选编码的正确传递函数。 |
| HDR 为什么不是把所有值截到 1？ | 先裁剪再做 tone mapping 已经丢失高光信息，之后无法恢复差别。 |
| 为什么相同像素看起来不同？ | 对比指标不是个体视觉反应的精确预测，不能把课堂错觉图当测量仪。 |
| 哪些颜色现象超出了普通 RGB 表面反射？ | 物理能量、光子数和感知亮度是不同量；“颜色更蓝所以更亮”没有普遍依据。 |

## 15. 跨讲连接：同一工具在哪些尺度重复出现？

| 前置工具 | 在整门课里的用途 | 回查 |
| --- | --- | --- |
| 采样与积分 | 像素、光源、孔径、时间、方向都需要有限样本估计连续量。 | [L03](/notes/cs184-03-sampling-aliasing/) / [L15](/notes/cs184-15-monte-carlo-integration/) |
| 坐标与线性代数 | 相机、法线、骨架与局部速度都需要一致的参考系。 | [L04–05](/notes/cs184-04-05-transforms/) |
| 几何表示 | 可见性、接触、遮挡与网格邻域依赖可靠的几何关系。 | [L11–12](/notes/cs184-11-12-meshes-geometry/) |
| 物理量与单位 | 把颜色值、概率密度、力和能量区别开，防止错误补偿。 | [L14](/notes/cs184-14-radiometry/) |
| 颜色与显示 | 展示图不等于线性数据；显示变换会改变视觉比较。 | [L19–20](/notes/cs184-19-20-color-science/) |

回头看，许多错误并非来自复杂公式，而是来自“同一个词指了不同的量”：方向密度与概率、位置与方向、线性颜色与编码颜色、稳定与准确。先说清对象，再选择算法。

## 16. 自测：能否不看公式说清楚？

### 自测 1. 白物体在红灯下必然仍显示白色吗？

<details>
<summary>参考答案</summary>

不。入射光谱改变后反射光谱会变，感知还受适应与环境影响。

</details>

### 自测 2. 三类视锥是否分别只响应红、绿、蓝？

<details>
<summary>参考答案</summary>

不是，响应曲线较宽且重叠，名称表示相对长中短波敏感性。

</details>

### 自测 3. 相机看起来一样的颜色，人眼一定也一样吗？

<details>
<summary>参考答案</summary>

不一定。两者光谱敏感度不同，尤其在窄谱光源下可能出现明显差异。

</details>

### 自测 4. 负匹配系数是否说明实验错误？

<details>
<summary>参考答案</summary>

不。它可能反映目标在所选物理基色的非负混合范围之外。

</details>

### 自测 5. 只知道 xy 能否恢复原始 XYZ？

<details>
<summary>参考答案</summary>

不能，还缺整体尺度；给定非零 y 和 Y 后可以恢复。

</details>

### 自测 6. 从 8 位升级到 10 位一定能显示更饱和的绿色吗？

<details>
<summary>参考答案</summary>

不一定。位深提高精度，是否扩大色域还取决于基色光谱与显示能力。

</details>

### 自测 7. 两块显示屏并排显示与叠两片滤镜有什么差别？

<details>
<summary>参考答案</summary>

前者把到眼睛的光相加，后者依次衰减同一束光。

</details>

### 自测 8. Lab 中相同欧氏距离是否在所有条件下都严格同样明显？

<details>
<summary>参考答案</summary>

不是。它是感知均匀性的近似，复杂色差评价与观看条件还需更专门模型。

</details>

### 自测 9. 为什么第一课渐变图不适合直接判断物理亮度均匀？

<details>
<summary>参考答案</summary>

它通常把编码值均匀写入文件，显示强度未必随像素位置线性变化。

</details>

### 自测 10. 调高曝光与改 gamma 是否等价？

<details>
<summary>参考答案</summary>

不。前者主要缩放线性光量，后者改变编码或显示响应曲线。

</details>

### 自测 11. 视觉错觉是否证明物理测量没有意义？

<details>
<summary>参考答案</summary>

不。它说明测量与感知是不同层次，需要分别建模。

</details>

### 自测 12. 只匹配一个光照下的 RGB 能证明光谱材质正确吗？

<details>
<summary>参考答案</summary>

不能。同色异谱允许不同光谱给出同样 RGB，换灯或观察者可能暴露差异。

</details>

### 自测 13. 第 1 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

RGB 通道不是三条固定波长的能量计；不能直接把某个 R 值等同于某个波长功率。

再复算本节的例子：两个波段输入为 (4,2)，反射率 (0.25,0.5)，输出 (1,1)。逐项反算 1/4=0.25、1/2=0.5；同样输出可由其他输入与反射率组合产生。

</details>

### 自测 14. 第 2 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

不要把 L、M、S 直接叫显示器 R、G、B；两者基底不同。

再复算本节的例子：离散教学敏感度 (0.2,0.8)，光谱 (3,1)，响应 3×0.2+1×0.8=1.4。光谱全部加倍后响应 2.8，验证线性。

</details>

### 自测 15. 第 3 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

这个两波段例是降维直觉，不是真实人眼同色异谱数据。

再复算本节的例子：教学单通道 S=(1,1)，光谱 (1,0) 与 (0,1) 都给 1。若传感器换成 (1,2)，响应变为 1 与 2，匹配消失。

</details>

### 自测 16. 第 4 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

直接把负 RGB 截成零会改变颜色；这是色域映射选择，不是无损数学变换。

再复算本节的例子：二维示意 P 的列为 (1,0)、(1,1)，要得到 c=(0,1)，解 a=(-1,1)。验证 -1×(1,0)+(1,1)=(0,1)，说明非负混合做不到。

</details>

### 自测 17. 第 5 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

不要把 xy 平面上的欧氏距离直接当通用感知色差。

再复算本节的例子：XYZ=(2,3,5)，xy=(0.2,0.3)。全部乘二为 (4,6,10) 仍得同一 xy；用 Y=3 恢复总和 Y/y=10，再得 X=2、Z=5。

</details>

### 自测 18. 第 6 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

二维示意坐标不是某个真实设备的色度实测；只用于说明凸包。

再复算本节的例子：取 c1=(0,0)、c2=(1,0)、c3=(0,1)，点 (0.2,0.3) 的权重为 (0.5,0.2,0.3)。点 (0.8,0.8) 需要第一权重 -0.6，落在域外。

</details>

### 自测 19. 第 7 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

“减色”不是把 RGB 数值直接相减；需要知道材料的光谱作用。

再复算本节的例子：某波段两片滤镜透过率 0.5 与 0.2，串联为 0.1；输入 10 输出 1。与发光源 5+2=7 的加法不是同一操作。

</details>

### 自测 20. 第 8 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

直接线性插值色相会绕远路；应选择周期短弧或明确设计路径。

再复算本节的例子：从 350° 到 10°，短弧中点是 0°，普通算术平均却是 180°。检查两端到 0° 的角距都是 10°。

</details>

### 自测 21. 第 9 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

不要把幂律近似写成 sRGB 标准公式；实际代码应使用所选编码的正确传递函数。

再复算本节的例子：黑白各一半，线性均值 I=0.5，编码约 0.72974；直接平均编码得 0.5，显示强度约 0.21764。把 0.72974 的 2.2 次方算回约 0.5。

</details>

### 自测 22. 第 10 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

先裁剪再做 tone mapping 已经丢失高光信息，之后无法恢复差别。

再复算本节的例子：L=1、3、9 分别得到 0.5、0.75、0.9。反解 L=T/(1-T)，0.75 恢复为 3；硬裁剪则三者都为 1。

</details>

### 自测 23. 第 11 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

对比指标不是个体视觉反应的精确预测，不能把课堂错觉图当测量仪。

再复算本节的例子：目标亮度 6，背景 4 时对比为 0.5；背景 5 时为 0.2。目标没变，关系却变了；反算 4×1.5=6。

</details>

### 自测 24. 第 12 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

物理能量、光子数和感知亮度是不同量；“颜色更蓝所以更亮”没有普遍依据。

再复算本节的例子：只比较比例：400 nm 光子能量是 800 nm 的两倍，因为 E400/E800=800/400=2；这不表示同功率的 400 nm 光一定看起来两倍亮。

</details>

### 自测 25. 本讲的输入、输出和中间表示各是什么？

<details>
<summary>参考答案</summary>

光谱进入眼睛 → 三类感受器积分 → 同色异谱 → 三基色匹配 → 颜色空间与色域 → 线性运算与显示。请沿箭头逐项解释，尤其说清中间表示的单位、坐标或概率测度；只复述名词不算掌握。

</details>

### 自测 26. 能否只用一张“看起来正确”的图片证明实现正确？

<details>
<summary>参考答案</summary>

不能。需要将关键关系拆成可预测的小输入，检查数值、边界与对照；随机方法还要区分一次结果与统计期望，显示图还需区分编码与原始数据。

</details>

## 17. 带走的结论与仍需练习的内容

- 不。入射光谱改变后反射光谱会变，感知还受适应与环境影响。
- 不是，响应曲线较宽且重叠，名称表示相对长中短波敏感性。
- 不一定。两者光谱敏感度不同，尤其在窄谱光源下可能出现明显差异。
- 不。它可能反映目标在所选物理基色的非负混合范围之外。
- 不能，还缺整体尺度；给定非零 y 和 Y 后可以恢复。
- 不一定。位深提高精度，是否扩大色域还取决于基色光谱与显示能力。
- 前者把到眼睛的光相加，后者依次衰减同一束光。
- 不是。它是感知均匀性的近似，复杂色差评价与观看条件还需更专门模型。
- 它通常把编码值均匀写入文件，显示强度未必随像素位置线性变化。
- 不。前者主要缩放线性光量，后者改变编码或显示响应曲线。
- 不。它说明测量与感知是不同层次，需要分别建模。
- 不能。同色异谱允许不同光谱给出同样 RGB，换灯或观察者可能暴露差异。

| 层次 | 已经说明 | 还需动手验证 |
| --- | --- | --- |
| 概念 | 本篇十二个问题、公式与原页对应。 | 用自己的话重新解释，并给出一个反例。 |
| 数值 | 正文手算与解析小模型。 | 改变一个输入，预测再运行。 |
| 系统 | 指出实现条件和典型错误。 | 完整应用需另外检查场景、性能和边界。 |

## 18. 整门课闭环与继续阅读

| 讲义 | 起点问题 | 得到的工具或终点 |
| --- | --- | --- |
| [L01 · 导论](/notes/cs184-01-introduction/) | 这门课在求什么？ | 从场景到像素与感知 |
| [L02 · 三角形与覆盖](/notes/cs184-02-drawing-triangles/) | 像素由哪些图元覆盖？ | 半平面判定与插值 |
| [L03 · 采样与抗锯齿](/notes/cs184-03-sampling-aliasing/) | 离散图像为何锯齿？ | 区域积分、过滤与采样 |
| [L04–05 · 变换](/notes/cs184-04-05-transforms/) | 怎样放置物体和相机？ | 坐标系、矩阵与投影 |
| [L06–07 · 纹理](/notes/cs184-06-07-texture-mapping/) | 表面参数如何随位置变化？ | UV、过滤与像素足迹 |
| [L08–09 · 着色](/notes/cs184-08-09-rasterization-shading/) | 看见哪个表面、怎样着色？ | 深度、管线与局部照明 |
| [L10 · 曲线曲面](/notes/cs184-10-bezier-curves-surfaces/) | 怎样控制连续形状？ | 插值、逼近与连续性 |
| [L11–12 · 几何](/notes/cs184-11-12-meshes-geometry/) | 复杂表面如何表示和操作？ | 网格、拓扑与几何处理 |
| [L13 · 光线追踪](/notes/cs184-13-ray-tracing-acceleration/) | 光线怎样快速找到最近表面？ | 求交与 BVH |
| [第 14 讲](/notes/cs184-14-radiometry/) | 能量 | 半球积分 |
| [第 15 讲](/notes/cs184-15-monte-carlo-integration/) | 像素是积分 | 降低方差 |
| [第 16–17 讲](/notes/cs184-16-17-global-illumination/) | 命中表面 | 加权累积与终止 |
| [春季 L18](/notes/cs184-18-material-modeling/) | 材质是散射规律 | 更细结构与体积传播 |
| [春季 L19–20](/notes/cs184-19-20-color-science/) | 光谱进入眼睛 | 线性运算与显示 |
| [春季 L21–23](/notes/cs184-21-23-animation/) | 表达运动意图 | 从末端目标反求关节 |
| [春季 L24](/notes/cs184-24-physical-simulation/) | 选择状态 | 施加碰撞和约束 |
| [春季 L25](/notes/cs184-25-fluid-simulation/) | 粒子或网格表示 | 边界与数值误差 |
| [春季 L26–27](/notes/cs184-26-27-virtual-reality/) | 人眼需要哪些线索 | 全景与光场 |
| [补充 A](/notes/cs184-supplement-cameras-lenses/) | 视场与透视 | 真实镜头与传感器 |
| [补充 B](/notes/cs184-supplement-image-processing/) | 图像是离散信号 | 频率量化与压缩 |

春季 L18–27 与夏季补充专题保留本地文件标识，**不冒充不存在的秋季同编号讲次**。可以按上表顺序学习，也可在相机、颜色、采样之间按依赖往返。

## 19. 原课件全页索引与来源

[原课件文件与版本记录](https://github.com/Teddy-Yangjiale/CS184/blob/main/CS184_2026/sp26/lectures/SP26-L19-20-color-science.pdf) · [课程官网](https://cs184.eecs.berkeley.edu/sp26/)

文件：`SP26-L19-20-color-science.pdf`；PDF 页数：112；SHA-256：`446026f8a93ce4d8a1d154467d2ad3f1560aaa7de11c5bb53e401b0b8a6ffc83`。

“正文核对”表示本篇实际引用该页截图；“索引保留”包括演示、行政信息、补充、致谢与重复构建页，不表示逐页都有独立讲解。原视频的运动过程不能由静态 PDF 截图完整复现。

| PDF 页 | 原页可提取标题 | 本篇使用 |
| --- | --- | --- |
| 1 | Computer Graphics and Imaging | 索引保留 |
| 2 | What is Light? | 正文核对 |
| 3 | credit:  Science Media Group. | 索引保留 |
| 4 | credit:  Science Media Group. | 索引保留 |
| 5 | Monochromator | 正文核对 |
| 6 | Spectrometer | 正文核对 |
| 7 | Spectral Colors | 正文核对 |
| 8 | Spectral Colors | 索引保留 |
| 9 | Other Colors | 索引保留 |
| 10 | Other Colors | 索引保留 |
| 11 | Other Colors | 索引保留 |
| 12 | Other Colors | 正文核对 |
| 13 | Other Colors | 索引保留 |
| 14 | Other Colors | 索引保留 |
| 15 | Reflected Light | 正文核对 |
| 16 | Simple Model of a Detector | 正文核对 |
| 17 | Perception -vs- Measurement | 索引保留 |
| 18 | Everything is Relative | 正文核对 |
| 19 | Everything is Relative | 索引保留 |
| 20 | Adapt | 正文核对 |
| 21 | Adapt | 索引保留 |
| 22 | Mach Bands | 正文核对 |
| 23 | Mach Bands | 索引保留 |
| 24 | Everything’s Still Relative | 正文核对 |
| 25 | Everything’s Still Relative | 索引保留 |
| 26 | Bezold Effect | 正文核对 |
| 27 | Perception | 正文核对 |
| 28 | Perception | 索引保留 |
| 29 | Perception | 索引保留 |
| 30 | Perception | 索引保留 |
| 31 | Watercolor Illusion | 正文核对 |
| 32 | Watercolor Illusion | 索引保留 |
| 33 | Watercolor Illusion | 索引保留 |
| 34 | Eyes as Sensors | 正文核对 |
| 35 | Eyes as Sensors | 索引保留 |
| 36 | Eyes as Sensors | 索引保留 |
| 37 | Photoreceptor Size and Distribution Vary Across Retina | 正文核对 |
| 38 | On the Retina, Three Types of Cone Cells | 正文核对 |
| 39 | On the Retina, Three Types of Cone Cells | 索引保留 |
| 40 | 图像或演示页（请以原页视觉内容为准） | 索引保留 |
| 41 | 图像或演示页（请以原页视觉内容为准） | 索引保留 |
| 42 | Cones | 正文核对 |
| 43 | Recall | 索引保留 |
| 44 | Cones | 正文核对 |
| 45 | Cones | 正文核对 |
| 46 | Cones | 索引保留 |
| 47 | Cones | 正文核对 |
| 48 | Rods vs Cones | 正文核对 |
| 49 | 图像或演示页（请以原页视觉内容为准） | 索引保留 |
| 50 | Cones and Metamers | 正文核对 |
| 51 | Metamerism is a Big Effect | 正文核对 |
| 52 | Trichromaticity | 正文核对 |
| 53 | Cone Responses are Linear | 正文核对 |
| 54 | Superposition (Linearity) of Spectral Power Distributions | 正文核对 |
| 55 | Superposition (Linearity) of Spectral Power Distributions | 索引保留 |
| 56 | Superposition (Linearity) of Spectral Power Distributions | 索引保留 |
| 57 | Superposition (Linearity) of Spectral Power Distributions | 索引保留 |
| 58 | Additive Mixing | 正文核对 |
| 59 | CRT Primaries | 正文核对 |
| 60 | LCD Primaries | 正文核对 |
| 61 | Additive Color Matching | 正文核对 |
| 62 | Experiment 1 | 索引保留 |
| 63 | Experiment 1 | 索引保留 |
| 64 | Experiment 1 | 索引保留 |
| 65 | Experiment 1 | 正文核对 |
| 66 | Experiment 2 | 索引保留 |
| 67 | Experiment 2 | 索引保留 |
| 68 | Experiment 2 | 索引保留 |
| 69 | Experiment 2 | 正文核对 |
| 70 | Color Matching Functions | 正文核对 |
| 71 | Color Matching Functions | 正文核对 |
| 72 | Φ = | 正文核对 |
| 73 | Using Color Matching Functions | 正文核对 |
| 74 | Using Color Matching Functions | 正文核对 |
| 75 | CIE XYZ | 正文核对 |
| 76 | Rescaled XYZ to xyz | 正文核对 |
| 77 | CIE Chromaticity Diagram | 正文核对 |
| 78 | Gamut | 正文核对 |
| 79 | CIE 1931 RGB Gamut | 正文核对 |
| 80 | Other Gamuts  (LCDs and NTSC) | 正文核对 |
| 81 | Subtractive Mixing | 正文核对 |
| 82 | Subtractive Mixing | 正文核对 |
| 83 | Additive & Subtractive Primaries | 正文核对 |
| 84 | Additive & Subtractive Primaries | 正文核对 |
| 85 | Color Spaces | 正文核对 |
| 86 | Color Spaces | 正文核对 |
| 87 | HSV Color Space (Hue-Saturation-Value) | 正文核对 |
| 88 | HSV Color Space (Hue-Saturation-Value) | 索引保留 |
| 89 | Color Spaces | 正文核对 |
| 90 | Color Spaces | 索引保留 |
| 91 | CIELAB Space (AKA L*a*b*) | 正文核对 |
| 92 | Monitor Intensity and Gamma | 正文核对 |
| 93 | Determining Gamma | 正文核对 |
| 94 | Determining Gamma | 正文核对 |
| 95 | Dynamic Range | 正文核对 |
| 96 | Dynamic Range | 正文核对 |
| 97 | Fake High Dynamic Range | 正文核对 |
| 98 | Tone Mapping | 正文核对 |
| 99 | Rods Contribute to Color | 正文核对 |
| 100 | Color Phenomena | 正文核对 |
| 101 | Reflection | 正文核对 |
| 102 | Transmission | 正文核对 |
| 103 | Scattering | 正文核对 |
| 104 | Interference | 正文核对 |
| 105 | Iridescence | 正文核对 |
| 106 | Iridescence | 索引保留 |
| 107 | Iridescence | 索引保留 |
| 108 | Fluorescence / Phosphorescence | 正文核对 |
| 109 | Fluorescence / Phosphorescence | 索引保留 |
| 110 | Black Body Radiation | 正文核对 |
| 111 | Black Body Radiation | 正文核对 |
| 112 | Acknowledgments | 索引保留 |
