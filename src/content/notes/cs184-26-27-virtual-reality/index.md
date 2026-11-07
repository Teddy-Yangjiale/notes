---
title: "CS184 春季 L26–27：VR，把图像变成稳定的空间体验"
date: 2026-11-07
updated: 2026-11-07
summary: "人眼需要哪些线索 → 双眼与光学显示 → 追踪六自由度 → 在延迟预算内渲染 → 重投影 → 全景与光场。以原课件为依据，配 20 张可编辑图解、12 个数值例子、26 道带答案自测与 PDF 全页索引。"
tags: ["计算机图形学", "CS184", "课程笔记"]
series: "cs184"
order: 26
shortTitle: "春季 L26–27"
---

> UC Berkeley · CS184/284A · Spring 2026 · 文件标识 `SP26-L26-27-virtual-reality.pdf`。
> 本文的 **pN 一律是 PDF 的第 N 页**，不是封面讲次或页脚旧编号。文件名与封面可能不同，以下均按文件和页码回查。

## 0. 先抓住这一条推理链

```text
人眼需要哪些线索
    ↓
双眼与光学显示
    ↓
追踪六自由度
    ↓
在延迟预算内渲染
    ↓
重投影
    ↓
全景与光场
```

这篇笔记的阅读顺序是：先理解输入和输出，再确认公式的条件，最后用小数值检查。
正文将课件概念、补充推导和教学例子分开；示意图中的理想几何与数字不冒充真实实验测量。

| 内容 | 本文提供什么 |
|---|---|
| 来源 | Spring 2026，PDF 共 178 页；正文选择 87 张关键页 |
| 图解 | 12 张概念关系图 + 8 张几何或数值图，均有原生可编辑 PPTX |
| 手算 | 12 个带输入、结果和回代检查的教学例子 |
| 复习 | 26 道自测及答案，末尾保留全页索引 |
| 运行证据 | 数值核对脚本覆盖解析小模型，不代表完整渲染器或模拟器已经实现 |

[下载本篇 20 张可编辑图解（PPTX 与操作 JSON）](/notes/cs184/figures/26-editable.zip)

### 课件与推导的使用边界

课件截图用于对照原始定义与几何；正文用中文解释关系，并提供必要的修正与推导。
后续专题按本地文件的学期和编号组织，不假定它们与秋季一一对应。
若只做第一遍学习，先读每节前两段和数值例子，再展开原页核对。

### 与前面哪一讲接上

先回顾[相关前置讲义](/notes/cs184-19-20-color-science/)。本篇在已有表示与数学工具上增加新变量或新约束，而不是另起一套互不相关的公式。

## 1. VR 为什么把整门课放进一个系统？

VR 同时需要几何、双眼投影、光照、颜色、光学和低延迟系统。它不只是在普通显示器上画两幅图，而是随着头部运动保持虚拟世界相对稳定。

AR 还需要与真实世界对齐及处理遮挡。本讲使用课件中的历史设备作为结构示例，不把旧型号规格当成当前市场结论。

![概念关系：VR 为什么把整门课放进一个系统？](diagrams/d01-relation.png)

*读图：头部姿态 → 左右眼相机 → 稳定虚拟世界。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| T | 刚体变换 |
| head | 头部坐标 |
| eye | 左右眼相对头部位置 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
T_{eye}^{world}=T_{head}^{world}T_{eye}^{head}
$$

### 🔧 手算 1：把关系落到数字上

头部位置 x=1 米，左眼局部 x=-0.03 米，无旋转时世界 x=0.97 米。右眼 +0.03 得 1.03，间距仍 0.06 米。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 右眼 +0.03 得 1.03，间距仍 0.06 米。 |
| 适用边界 | 左右眼应共享同一世界状态与时间基准；不同步会制造额外视觉冲突。 |

### ⚠️ 易错点：先识别症状与假设

左右眼应共享同一世界状态与时间基准；不同步会制造额外视觉冲突。

### 停下来解释一次

**问题：左右眼用同一相机图像是否仍有双目视差？**

<details>
<summary>展开参考回答</summary>

没有正确的双目视差；可以看到单目深度线索，但不等于立体呈现。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Virtual Reality (VR) vs Augmented Reality (AR)

*PDF p2 · 对应本节：VR 为什么把整门课放进一个系统？*

![PDF p2：Virtual Reality (VR) vs Augmented Reality (AR)](images/p002.png)

#### Overview of VR Topics

*PDF p16 · 对应本节：VR 为什么把整门课放进一个系统？*

![PDF p16：Overview of VR Topics](images/p016.png)

#### Field of View

*PDF p18 · 对应本节：VR 为什么把整门课放进一个系统？*

![PDF p18：Field of View](images/p018.png)

#### 3D Visual Cues

*PDF p19 · 对应本节：VR 为什么把整门课放进一个系统？*

![PDF p19：3D Visual Cues](images/p019.png)

#### VR Headset Components

*PDF p20 · 对应本节：VR 为什么把整门课放进一个系统？*

![PDF p20：VR Headset Components](images/p020.png)

</details>

## 2. 近眼镜片为什么不可省略？

小屏幕靠眼睛太近，眼睛无法按普通观看距离舒适聚焦，视场也受限制。目镜把屏幕形成合适虚像，并扩大角度覆盖。

Fresnel 与 pancake 等方案改变厚度、效率和像差，不能只按外形判断画质。渲染必须配合光学畸变补偿与每眼投影。

![概念关系：近眼镜片为什么不可省略？](diagrams/d02-relation.png)

*读图：近距离面板 → 目镜形成虚像 → 宽视场观察。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| w | 有效显示宽度 |
| f | 等效焦距 |
| 限制 | 真实头显需完整光学参数 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
\mathrm{FOV}=2\arctan\frac{w}{2f}\quad\text{（简化几何模型）}
$$

### 🔧 手算 2：把关系落到数字上

w=40 mm、f=20 mm，简化 FOV=90°。若 f=40 mm，变为约 53.13°；检查 w/(2f) 从 1 降为 0.5。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 若 f=40 mm，变为约 53.13°；检查 w/(2f) 从 1 降为 0.5。 |
| 适用边界 | 不能把此式直接当真实多片目镜的完整标定模型。 |

### ⚠️ 易错点：先识别症状与假设

不能把此式直接当真实多片目镜的完整标定模型。

### 停下来解释一次

**问题：屏幕像素数相同，视场变大会有什么代价？**

<details>
<summary>展开参考回答</summary>

平均每度像素数下降，角分辨率可能变差。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Oculus Quest 2 Headset (Lens Assembly)

*PDF p27 · 对应本节：近眼镜片为什么不可省略？*

![PDF p27：Oculus Quest 2 Headset (Lens Assembly)](images/p027.png)

#### Oculus Quest 2 Display + Lens Assembly

*PDF p28 · 对应本节：近眼镜片为什么不可省略？*

![PDF p28：Oculus Quest 2 Display + Lens Assembly](images/p028.png)

#### Oculus Rift (2016)

*PDF p33 · 对应本节：近眼镜片为什么不可省略？*

![PDF p33：Oculus Rift (2016)](images/p033.png)

#### Oculus Rift Lenses

*PDF p34 · 对应本节：近眼镜片为什么不可省略？*

![PDF p34：Oculus Rift Lenses](images/p034.png)

#### Role of Eyepiece Lenses

*PDF p36 · 对应本节：近眼镜片为什么不可省略？*

![PDF p36：Role of Eyepiece Lenses](images/p036.png)

#### Pancake Lenses

*PDF p37 · 对应本节：近眼镜片为什么不可省略？*

![PDF p37：Pancake Lenses](images/p037.png)

</details>

## 3. 分辨率为什么要按每度计算？

同样的像素数铺到不同视场，眼睛看到的角细节不同。每度像素 PPD 是连接面板分辨率与视觉角度的简单指标，但透镜与投影会让它随位置变化。

课件用视觉敏锐度讨论大视场的计算量。不要把某个平均 PPD 当成所有人、所有视角下的绝对阈值。

![概念关系：分辨率为什么要按每度计算？](diagrams/d03-relation.png)

*读图：像素数量 → 角度覆盖范围 → 每度细节密度。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| Nx | 水平像素数 |
| FOVx | 水平视场，度 |
| 前提 | 这里只取平均 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
\mathrm{PPD}\approx\frac{N_x}{\mathrm{FOV}_x}
$$

### 🔧 手算 3：把关系落到数字上

2000 像素覆盖 100°，平均 20 PPD；想保持视场并达到 40 PPD，需要水平 4000 像素，二维近似像素数增四倍。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 2000 像素覆盖 100°，平均 20 PPD；想保持视场并达到 40 PPD，需要水平 4000 像素，二维近似像素数增四倍。 |
| 适用边界 | 面板分辨率不是实际可见分辨率；光学模糊、畸变与渲染采样也有影响。 |

### ⚠️ 易错点：先识别症状与假设

面板分辨率不是实际可见分辨率；光学模糊、畸变与渲染采样也有影响。

### 停下来解释一次

**问题：把 FOV 从 100° 增到 120° 而不增像素，平均 PPD 如何变化？**

<details>
<summary>展开参考回答</summary>

乘 100/120，降低为原来的约 83.3%。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Display Requirements Derive

*PDF p45 · 对应本节：分辨率为什么要按每度计算？*

![PDF p45：Display Requirements Derive](images/p045.png)

#### Human Visual Field of View

*PDF p46 · 对应本节：分辨率为什么要按每度计算？*

![PDF p46：Human Visual Field of View](images/p046.png)

#### Recall: Photoreceptor Size and Distribution Across Retina

*PDF p47 · 对应本节：分辨率为什么要按每度计算？*

![PDF p47：Recall: Photoreceptor Size and Distribution Across Retina](images/p047.png)

#### Visual Acuity

*PDF p48 · 对应本节：分辨率为什么要按每度计算？*

![PDF p48：Visual Acuity](images/p048.png)

#### Visual Acuity

*PDF p49 · 对应本节：分辨率为什么要按每度计算？*

![PDF p49：Visual Acuity](images/p049.png)

#### Current VR Headset Field of View and Resolution

*PDF p50 · 对应本节：分辨率为什么要按每度计算？*

![PDF p50：Current VR Headset Field of View and Resolution](images/p050.png)

#### A VR Display at Human Visual Acuity

*PDF p51 · 对应本节：分辨率为什么要按每度计算？*

![PDF p51：A VR Display at Human Visual Acuity](images/p051.png)

</details>

## 4. 双目视差怎样编码距离？

左右眼从不同位置观察同一点，产生视差。正确双眼投影需要真实基线与一致的相机约定；简单让两台相机朝同一点旋转可能引入不想要的垂直视差。

在校正平行相机的简化模型中，视差与深度成反比。这与三维重建中的双目几何是同一关系，只是 VR 用它生成图像而不是恢复深度。

![概念关系：双目视差怎样编码距离？](diagrams/d04-relation.png)

*读图：左右眼位置差 → 图像水平视差 → 深度线索。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| f | 以像素为单位的焦距 |
| B | 双眼基线 |
| Z | 深度 |
| d | 水平视差 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
d=\frac{fB}{Z}
$$

### 🔧 手算 4：把关系落到数字上

f=1000 px、B=0.06 m、Z=2 m，d=30 px；Z=4 m 时 d=15。由 fB/d 可反算原深度。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 由 fB/d 可反算原深度。 |
| 适用边界 | 物理单位和像素单位不能混用；左右眼视口与投影偏移也需一致。 |

![几何或数值解释 1](diagrams/d13-stereo.png)

*两个观察位置产生深度相关视差，渲染时两眼必须使用一致的世界状态。*

### ⚠️ 易错点：先识别症状与假设

物理单位和像素单位不能混用；左右眼视口与投影偏移也需一致。

### 停下来解释一次

**问题：把双眼基线加倍会怎样？**

<details>
<summary>展开参考回答</summary>

在该简化模型中视差加倍，会改变感知尺度与深度，不能随意调大。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Display Requirements Derive

*PDF p52 · 对应本节：双目视差怎样编码距离？*

![PDF p52：Display Requirements Derive](images/p052.png)

#### Two Eyes: Two Views

*PDF p53 · 对应本节：双目视差怎样编码距离？*

![PDF p53：Two Eyes: Two Views](images/p053.png)

#### Stereo Vergence

*PDF p55 · 对应本节：双目视差怎样编码距离？*

![PDF p55：Stereo Vergence](images/p055.png)

#### Stereo Vergence

*PDF p56 · 对应本节：双目视差怎样编码距离？*

![PDF p56：Stereo Vergence](images/p056.png)

#### Stereo Vergence

*PDF p57 · 对应本节：双目视差怎样编码距离？*

![PDF p57：Stereo Vergence](images/p057.png)

#### Stereo

*PDF p59 · 对应本节：双目视差怎样编码距离？*

![PDF p59：Stereo](images/p059.png)

</details>

## 5. 辐辏与调焦冲突为什么重要？

辐辏是两眼转动以看向同一目标，调焦是晶状体改变焦距以形成清晰像。真实世界中两者通常指向同一距离，固定焦平面的头显却可能让它们要求不同距离。

即使双眼视差完全正确，光学焦面仍可能不随虚拟物体变化。解决这一问题涉及可变焦、多焦面或光场等显示研究，不能只靠更高分辨率。

![概念关系：辐辏与调焦冲突为什么重要？](diagrams/d05-relation.png)

*读图：固定光学焦面 → 变化的双目目标深度 → 调焦与辐辏需求分离。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| D | 屈光度 m⁻¹ |
| z | 焦距对应距离 |
| 用途 | 量化调焦要求差异 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
D=1/z\quad\text{（z 以米计）}
$$

### 🔧 手算 5：把关系落到数字上

光学焦面 2 米对应 0.5 D，虚拟目标 0.5 米对应 2 D，差为 1.5 D。倒数换算检验两者对应距离。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 倒数换算检验两者对应距离。 |
| 适用边界 | 这里是几何需求差，不是医学不适阈值；个体反应不能由一个数直接推断。 |

![几何或数值解释 2](diagrams/d14-bars.png)

*2 米光学焦面与 0.5 米目标对应 0.5 D 和 2 D，仅说明几何需求差。*

### ⚠️ 易错点：先识别症状与假设

这里是几何需求差，不是医学不适阈值；个体反应不能由一个数直接推断。

### 停下来解释一次

**问题：增加帧率能解决固定焦面冲突吗？**

<details>
<summary>展开参考回答</summary>

不能根本解决。时间响应与焦深线索是不同问题。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Human Eye Muscles and Optical Controls

*PDF p60 · 对应本节：辐辏与调焦冲突为什么重要？*

![PDF p60：Human Eye Muscles and Optical Controls](images/p060.png)

#### Human Eye Muscles and Optical Controls

*PDF p61 · 对应本节：辐辏与调焦冲突为什么重要？*

![PDF p61：Human Eye Muscles and Optical Controls](images/p061.png)

#### Accommodation and Vergence

*PDF p62 · 对应本节：辐辏与调焦冲突为什么重要？*

![PDF p62：Accommodation and Vergence](images/p062.png)

#### Accommodation – Vergence Conﬂict

*PDF p63 · 对应本节：辐辏与调焦冲突为什么重要？*

![PDF p63：Accommodation – Vergence Conﬂict](images/p063.png)

</details>

## 6. 六自由度追踪为何要融合传感器？

头部姿态有三个平移和三个旋转自由度。惯性传感器响应快但积分可能漂移，视觉或外部光学观测可提供空间约束，但有延迟、遮挡和纹理不足等问题。

外部追踪与 inside-out 追踪的观测方式不同，核心都在估计随时间变化的刚体姿态。不能把朝向追踪等同完整位置追踪。

![概念关系：六自由度追踪为何要融合传感器？](diagrams/d06-relation.png)

*读图：快速惯性观测 → 视觉或光学约束 → 带时间戳的姿态。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| R | 三维旋转 |
| t | 三维平移 |
| 自由度 | 3+3，不等于矩阵元素数 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
T=\begin{bmatrix}R&t\\0&1\end{bmatrix}
$$

### 🔧 手算 6：把关系落到数字上

仅向前平移 0.1 米而朝向不变，R 不变、t 改变。若系统只更新 R，近处物体应有的运动视差就完全丢失。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 若系统只更新 R，近处物体应有的运动视差就完全丢失。 |
| 适用边界 | 追踪坐标轴、左右手系或时间戳不一致，会表现为头动方向反了或世界漂移。 |

### ⚠️ 易错点：先识别症状与假设

追踪坐标轴、左右手系或时间戳不一致，会表现为头动方向反了或世界漂移。

### 停下来解释一次

**问题：4×4 矩阵是否意味着姿态有 16 个自由度？**

<details>
<summary>展开参考回答</summary>

不是，旋转正交性和最后一行等约束将刚体姿态限制为 6 个自由度。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Display Requirements Derive

*PDF p64 · 对应本节：六自由度追踪为何要融合传感器？*

![PDF p64：Display Requirements Derive](images/p064.png)

#### Google Cardboard: Tracking Using Headset Camera

*PDF p65 · 对应本节：六自由度追踪为何要融合传感器？*

![PDF p65：Google Cardboard: Tracking Using Headset Camera](images/p065.png)

#### 6 DOF Head Pose Estimation

*PDF p66 · 对应本节：六自由度追踪为何要融合传感器？*

![PDF p66：6 DOF Head Pose Estimation](images/p066.png)

#### Oculus Rift IR LED Tracking System

*PDF p68 · 对应本节：六自由度追踪为何要融合传感器？*

![PDF p68：Oculus Rift IR LED Tracking System](images/p068.png)

#### Oculus Rift LED Tracking System (DK2)

*PDF p70 · 对应本节：六自由度追踪为何要融合传感器？*

![PDF p70：Oculus Rift LED Tracking System (DK2)](images/p070.png)

#### Active Optical Motion Capture

*PDF p73 · 对应本节：六自由度追踪为何要融合传感器？*

![PDF p73：Active Optical Motion Capture](images/p073.png)

#### HTC Vive Tracking System (“Lighthouse”)

*PDF p76 · 对应本节：六自由度追踪为何要融合传感器？*

![PDF p76：HTC Vive Tracking System (“Lighthouse”)](images/p076.png)

#### HTC Vive Tracking System

*PDF p81 · 对应本节：六自由度追踪为何要融合传感器？*

![PDF p81：HTC Vive Tracking System](images/p081.png)

#### • Wide-angle cameras look outward from headset

*PDF p84 · 对应本节：六自由度追踪为何要融合传感器？*

![PDF p84：• Wide-angle cameras look outward from headset](images/p084.png)

#### Tracking Summary

*PDF p85 · 对应本节：六自由度追踪为何要融合传感器？*

![PDF p85：Tracking Summary](images/p085.png)

</details>

## 7. 33 毫秒为什么会变成明显的空间错误？

端到端延迟包含追踪、应用更新、渲染、排队与显示。帧率衡量输出频率，不能单独说明输入动作多久才变成光。

用头部角速度乘延迟可以估算方向误差，再乘 PPD 得像素误差。该估算解释为什么 VR 对延迟敏感，并不替代真实动态测量。

![概念关系：33 毫秒为什么会变成明显的空间错误？](diagrams/d07-relation.png)

*读图：头部运动 → 旧姿态渲染 → 画面位置误差。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| omega | 度/秒 |
| tau | 秒 |
| PPD | 像素/度 |
| 假设 | 局部恒速与平均角采样 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
\Delta p\approx\omega\tau\,\mathrm{PPD}
$$

### 🔧 手算 7：把关系落到数字上

课件例 ω=90°/s、τ=0.033 s、PPD=20，误差约 59.4 px，接近 60。角误差 2.97° 乘 20 得同样结果。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 角误差 2.97° 乘 20 得同样结果。 |
| 适用边界 | 高 FPS 配上长排队仍可高延迟；性能日志应分阶段记录时间戳。 |

![几何或数值解释 3](diagrams/d15-bars.png)

*角速度 90°/s、20 PPD 时，像素误差与延迟近似成正比。*

### ⚠️ 易错点：先识别症状与假设

高 FPS 配上长排队仍可高延迟；性能日志应分阶段记录时间戳。

### 停下来解释一次

**问题：把帧率从 60 提高到 120，延迟一定减半吗？**

<details>
<summary>展开参考回答</summary>

不一定，其他流水线阶段和缓冲深度可能占主要部分。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Rendering Latency in VR

*PDF p87 · 对应本节：33 毫秒为什么会变成明显的空间错误？*

![PDF p87：Rendering Latency in VR](images/p087.png)

#### A VR Display at Human Visual Acuity

*PDF p88 · 对应本节：33 毫秒为什么会变成明显的空间错误？*

![PDF p88：A VR Display at Human Visual Acuity](images/p088.png)

#### Latency Requirements in VR Are Challenging

*PDF p89 · 对应本节：33 毫秒为什么会变成明显的空间错误？*

![PDF p89：Latency Requirements in VR Are Challenging](images/p089.png)

#### Thought Experiment: Effect of Latency

*PDF p90 · 对应本节：33 毫秒为什么会变成明显的空间错误？*

![PDF p90：Thought Experiment: Effect of Latency](images/p090.png)

#### Rendering Challenge:

*PDF p91 · 对应本节：33 毫秒为什么会变成明显的空间错误？*

![PDF p91：Rendering Challenge:](images/p091.png)

</details>

## 8. 注视点渲染为何仍需要抗锯齿？

中央凹分辨细节能力高，周边较低，因此可以把更多样本留给注视区域。收益来自空间分配计算，而非简单把周边画成低质量马赛克。

低分辨区域仍可能出现闪烁，过度模糊又可能产生隧道感；眼动追踪延迟还会让高质量区域追不上视线。它把感知、采样和系统延迟再次连在一起。

![概念关系：注视点渲染为何仍需要抗锯齿？](diagrams/d08-relation.png)

*读图：注视区域分配 → 不同采样密度 → 连续且及时的画质变化。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| a | 高分辨区域比例 |
| r | 周边相对采样密度 |
| 模型 | 忽略额外开销的预算估算 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
N_{work}=aN+(1-a)rN
$$

### 🔧 手算 8：把关系落到数字上

a=0.1、r=0.25，总工作为 0.325N，理论减少 67.5%。若额外开销很大，实际加速不会等于 1/0.325。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 若额外开销很大，实际加速不会等于 1/0.325。 |
| 适用边界 | 周边视觉对某些运动和闪烁仍敏感，不能把低空间敏锐度解释为“看不到错误”。 |

![几何或数值解释 4](diagrams/d16-fovea.png)

*计算预算随注视区域分配，过渡、过滤和追踪时效都要处理。*

### ⚠️ 易错点：先识别症状与假设

周边视觉对某些运动和闪烁仍敏感，不能把低空间敏锐度解释为“看不到错误”。

### 停下来解释一次

**问题：注视点渲染是否只需要一个固定圆形高质量区域？**

<details>
<summary>展开参考回答</summary>

固定中心版本可以节省开销，但眼动追踪版本需要随注视移动，并处理延迟和边界过渡。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Recall: Photoreceptor Size and Distribution Across Retina

*PDF p92 · 对应本节：注视点渲染为何仍需要抗锯齿？*

![PDF p92：Recall: Photoreceptor Size and Distribution Across Retina](images/p092.png)

#### Foveated Rendering

*PDF p93 · 对应本节：注视点渲染为何仍需要抗锯齿？*

![PDF p93：Foveated Rendering](images/p093.png)

#### Foveated Rendering - Perceptual Effects

*PDF p94 · 对应本节：注视点渲染为何仍需要抗锯齿？*

![PDF p94：Foveated Rendering - Perceptual Effects](images/p094.png)

#### Foveated Rendering - Perceptual Effects

*PDF p97 · 对应本节：注视点渲染为何仍需要抗锯齿？*

![PDF p97：Foveated Rendering - Perceptual Effects](images/p097.png)

#### Foveated Rendering

*PDF p100 · 对应本节：注视点渲染为何仍需要抗锯齿？*

![PDF p100：Foveated Rendering](images/p100.png)

</details>

## 9. 畸变补偿为什么会改变采样需求？

镜片把直线弯曲，软件需要预先施加相反变形，使经过镜片后看起来正确。重采样过程会在某些区域拉伸像素，暴露原本不足的采样密度。

逆向映射更容易保证每个输出像素都有来源；正向撒点可能留下空洞。预畸变不是给三维场景随意扭曲，而是对最终成像路径进行校正。

![概念关系：畸变补偿为什么会改变采样需求？](diagrams/d09-relation.png)

*读图：渲染图像 → 逆光学预畸变 → 经镜片后的目标图像。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| r | 归一化半径 |
| rd | 畸变后半径 |
| k1 | 示意参数 |
| 真实系统 | 需标定更完整模型 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
r_d=r(1+k_1r^2)\quad\text{（简化径向模型）}
$$

### 🔧 手算 9：把关系落到数字上

r=0.5、k1=0.2，rd=0.525。若 r=1，rd=1.2，边缘拉伸更明显；比例分别为 1.05 与 1.2。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 若 r=1，rd=1.2，边缘拉伸更明显；比例分别为 1.05 与 1.2。 |
| 适用边界 | 把一个眼睛的标定参数直接用于另一眼可能造成不一致，应按光学系统配置。 |

![几何或数值解释 5](diagrams/d17-curve.png)

*径向畸变在边缘更显著，校正后的采样密度需重新检查；曲线只示意增长趋势。*

### ⚠️ 易错点：先识别症状与假设

把一个眼睛的标定参数直接用于另一眼可能造成不一致，应按光学系统配置。

### 停下来解释一次

**问题：畸变校正后边缘变糊，可能只是镜片不好吗？**

<details>
<summary>展开参考回答</summary>

也可能是重采样拉伸与原图采样不足，需要检查渲染密度和过滤。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Rendering Challenge: Optical

*PDF p101 · 对应本节：畸变补偿为什么会改变采样需求？*

![PDF p101：Rendering Challenge: Optical](images/p101.png)

#### Requirement: Wide Field of View

*PDF p102 · 对应本节：畸变补偿为什么会改变采样需求？*

![PDF p102：Requirement: Wide Field of View](images/p102.png)

#### Software Correction of Lens Distortion in Photography

*PDF p103 · 对应本节：畸变补偿为什么会改变采样需求？*

![PDF p103：Software Correction of Lens Distortion in Photography](images/p103.png)

#### Software Compensation of Lens Distortion in VR Rendering

*PDF p104 · 对应本节：畸变补偿为什么会改变采样需求？*

![PDF p104：Software Compensation of Lens Distortion in VR Rendering](images/p104.png)

#### Software Compensation of Lens Distortion in VR Rendering

*PDF p105 · 对应本节：畸变补偿为什么会改变采样需求？*

![PDF p105：Software Compensation of Lens Distortion in VR Rendering](images/p105.png)

#### Related Challenge: Rendering via Planar Projection

*PDF p106 · 对应本节：畸变补偿为什么会改变采样需求？*

![PDF p106：Related Challenge: Rendering via Planar Projection](images/p106.png)

#### A Recent Implementation: Lens Matched Shading

*PDF p108 · 对应本节：畸变补偿为什么会改变采样需求？*

![PDF p108：A Recent Implementation: Lens Matched Shading](images/p108.png)

</details>

## 10. 时间扭曲能够修正什么，不能修正什么？

先用较旧姿态渲染完整图像，显示前再用最新姿态快速重投影，可以减少头部旋转造成的延迟误差。纯旋转模型可不依赖场景深度。

平移、物体运动与新暴露区域需要更多信息。RGB-D 与运动向量能扩展重投影能力，但看不到的区域仍不能凭旧图精确恢复。课件 ATW、ASW、AppSW 的差异正围绕这些信息来源。

![概念关系：时间扭曲能够修正什么，不能修正什么？](diagrams/d10-relation.png)

*读图：旧图与旧姿态 → 最新姿态重投影 → 降低部分显示延迟。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| K | 相机内参 |
| R | 两观察方向间旋转 |
| x | 齐次像素 |
| 限制 | 纯旋转或远景近似 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
x'\sim K R K^{-1}x\quad\text{（纯旋转针孔模型）}
$$

### 🔧 手算 10：把关系落到数字上

一维小角度近似，f=1000 px，转角 0.01 rad，位移约 10 px。若再有横移 0.01 m，深度 1 m 与 10 m 的额外位移约 10 与 1 px，不可同一旋转替代。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 若再有横移 0.01 m，深度 1 m 与 10 m 的额外位移约 10 与 1 px，不可同一旋转替代。 |
| 适用边界 | 把头部平移也套纯旋转重投影会错，尤其近景更明显。 |

![几何或数值解释 6](diagrams/d18-occlusion.png)

*平移会露出旧图没有记录的区域，仅重投影旧颜色无法精确补齐。*

![几何或数值解释 7](diagrams/d19-bars.png)

*f=1000px、横移 0.01m 时，平移像移近似 fΔx/Z，不能由单一旋转替代。*

### ⚠️ 易错点：先识别症状与假设

把头部平移也套纯旋转重投影会错，尤其近景更明显。

### 停下来解释一次

**问题：有深度图就能无损修复所有平移吗？**

<details>
<summary>展开参考回答</summary>

不能。遮挡解除后露出的新区域在旧图里没有颜色信息。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Rendering Challenge:

*PDF p137 · 对应本节：时间扭曲能够修正什么，不能修正什么？*

![PDF p137：Rendering Challenge:](images/p137.png)

#### Problem: High-Quality Rendering Can Be Slow

*PDF p138 · 对应本节：时间扭曲能够修正什么，不能修正什么？*

![PDF p138：Problem: High-Quality Rendering Can Be Slow](images/p138.png)

#### Modern VR Engineering Solution: Reprojection

*PDF p139 · 对应本节：时间扭曲能够修正什么，不能修正什么？*

![PDF p139：Modern VR Engineering Solution: Reprojection](images/p139.png)

#### Asynchronous TimeWarp (ATW)

*PDF p140 · 对应本节：时间扭曲能够修正什么，不能修正什么？*

![PDF p140：Asynchronous TimeWarp (ATW)](images/p140.png)

#### Asynchronous TimeWarp (ATW)

*PDF p141 · 对应本节：时间扭曲能够修正什么，不能修正什么？*

![PDF p141：Asynchronous TimeWarp (ATW)](images/p141.png)

#### Asynchronous TimeWarp (ATW)

*PDF p142 · 对应本节：时间扭曲能够修正什么，不能修正什么？*

![PDF p142：Asynchronous TimeWarp (ATW)](images/p142.png)

#### Modern VR Engineering Solution: Reprojection

*PDF p143 · 对应本节：时间扭曲能够修正什么，不能修正什么？*

![PDF p143：Modern VR Engineering Solution: Reprojection](images/p143.png)

#### Asynchronous SpaceWarp (ASW)

*PDF p144 · 对应本节：时间扭曲能够修正什么，不能修正什么？*

![PDF p144：Asynchronous SpaceWarp (ASW)](images/p144.png)

</details>

## 11. 刷新、持续发光与眼动怎样产生抖动？

眼睛追踪移动物体时，若显示在一帧内保持静止图像，视网膜上会形成拖影。刷新率、持续发光时间与滚动扫描分别影响时间采样。

低持续发光可以减少一帧内的运动模糊，但不会自动消除渲染延迟和帧率不足。应把保持显示的模糊与离散帧的跳跃分开分析。

![概念关系：刷新、持续发光与眼动怎样产生抖动？](diagrams/d11-relation.png)

*读图：眼睛持续运动 → 图像在帧内保持 → 视网膜时间模糊。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| omega | 眼动角速度 |
| Ton | 每帧发光持续时间 |
| 近似 | 恒速追踪 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
\Delta\theta_{blur}\approx\omega T_{on}
$$

### 🔧 手算 11：把关系落到数字上

ω=100°/s，持续发光 10 ms，角模糊约 1°；缩到 2 ms 后约 0.2°。时间缩五倍，模糊也缩五倍。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 时间缩五倍，模糊也缩五倍。 |
| 适用边界 | 只提高刷新但仍有长持续发光，改善程度可能不同；显示时序需一起看。 |

### ⚠️ 易错点：先识别症状与假设

只提高刷新但仍有长持续发光，改善程度可能不同；显示时序需一起看。

### 停下来解释一次

**问题：低持续发光是否等于缩短相机快门？**

<details>
<summary>展开参考回答</summary>

有相似的时间积分直觉，但一个发生在显示端，一个发生在采集或渲染端，不能互相替代。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Rendering Challenge: Eye Motion

*PDF p109 · 对应本节：刷新、持续发光与眼动怎样产生抖动？*

![PDF p109：Rendering Challenge: Eye Motion](images/p109.png)

#### Consider Finite VR Display Refresh Rate

*PDF p110 · 对应本节：刷新、持续发光与眼动怎样产生抖动？*

![PDF p110：Consider Finite VR Display Refresh Rate](images/p110.png)

#### Case 2: Object Moving Relative to Eye

*PDF p118 · 对应本节：刷新、持续发光与眼动怎样产生抖动？*

![PDF p118：Case 2: Object Moving Relative to Eye](images/p118.png)

#### Case 3: Eye Moving to Track Moving Object

*PDF p125 · 对应本节：刷新、持续发光与眼动怎样产生抖动？*

![PDF p125：Case 3: Eye Moving to Track Moving Object](images/p125.png)

#### Case 3: Eye Moving to Track Moving Object

*PDF p131 · 对应本节：刷新、持续发光与眼动怎样产生抖动？*

![PDF p131：Case 3: Eye Moving to Track Moving Object](images/p131.png)

#### Reducing Judder: Increase Frame Rate

*PDF p132 · 对应本节：刷新、持续发光与眼动怎样产生抖动？*

![PDF p132：Reducing Judder: Increase Frame Rate](images/p132.png)

#### Reducing Judder: Low Persistence Display

*PDF p133 · 对应本节：刷新、持续发光与眼动怎样产生抖动？*

![PDF p133：Reducing Judder: Low Persistence Display](images/p133.png)

#### Problem: Displays Exhibit “Rolling Shutter” Artifacts

*PDF p134 · 对应本节：刷新、持续发光与眼动怎样产生抖动？*

![PDF p134：Problem: Displays Exhibit “Rolling Shutter” Artifacts](images/p134.png)

#### Problem: Displays Exhibit “Rolling Shutter” Artifacts

*PDF p136 · 对应本节：刷新、持续发光与眼动怎样产生抖动？*

![PDF p136：Problem: Displays Exhibit “Rolling Shutter” Artifacts](images/p136.png)

</details>

## 12. 全景、立体全景与光场差在哪里？

单点全景记录所有观察方向，通常支持转头但没有真实平移视差。立体全景增加左右眼信息，仍受拍摄几何与视角基线变化限制；光场再加入视点位置维度。

课件指出把两台固定全景相机简单并排，转向侧面时有效基线会变化。六自由度体验需要处理新视点与遮挡，不能仅靠把全景图贴到球内侧。

![概念关系：全景、立体全景与光场差在哪里？](diagrams/d12-relation.png)

*读图：单位置全方向 → 左右眼方向采样 → 多位置光场。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| B | 相机基线 |
| theta | 观察方向相对基线横向最有效方向的转角 |
| 范围 | 解释固定双全景限制 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
B_{effective}=B\cos\theta\quad\text{（课件简化几何）}
$$

### 🔧 手算 12：把关系落到数字上

B=6 cm，θ=60° 时有效基线 3 cm；θ=90° 时趋于零。cos60=1/2，恰好减半。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | cos60=1/2，恰好减半。 |
| 适用边界 | 把单点 360 图标成完整 6DoF 场景会夸大可交互范围；应标明位置运动限制。 |

![几何或数值解释 8](diagrams/d20-bars.png)

*固定双全景的简化有效基线是 Bcosθ；90° 时为零，基线单位为厘米。*

### ⚠️ 易错点：先识别症状与假设

把单点 360 图标成完整 6DoF 场景会夸大可交互范围；应标明位置运动限制。

### 停下来解释一次

**问题：为什么一张高清全景仍不能让人侧身看见桌子背后？**

<details>
<summary>展开参考回答</summary>

新视点需要原图未记录的遮挡后信息，分辨率再高也不能补回缺失视点。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Spherical Imaging

*PDF p146 · 对应本节：全景、立体全景与光场差在哪里？*

![PDF p146：Spherical Imaging](images/p146.png)

#### Dual Fisheye

*PDF p147 · 对应本节：全景、立体全景与光场差在哪里？*

![PDF p147：Dual Fisheye](images/p147.png)

#### Stitching Challenges

*PDF p148 · 对应本节：全景、立体全景与光场差在哪里？*

![PDF p148：Stitching Challenges](images/p148.png)

#### High Quality Stitching Solution Uses Computer Vision

*PDF p151 · 对应本节：全景、立体全景与光场差在哪里？*

![PDF p151：High Quality Stitching Solution Uses Computer Vision](images/p151.png)

#### Spherical Stereo Imaging

*PDF p152 · 对应本节：全景、立体全景与光场差在哪里？*

![PDF p152：Spherical Stereo Imaging](images/p152.png)

#### Omni-Directional Stereo Approximation

*PDF p155 · 对应本节：全景、立体全景与光场差在哪里？*

![PDF p155：Omni-Directional Stereo Approximation](images/p155.png)

#### Omni-Directional Stereo Representation

*PDF p158 · 对应本节：全景、立体全景与光场差在哪里？*

![PDF p158：Omni-Directional Stereo Representation](images/p158.png)

#### Two Eyes — Two Spherical Cameras?

*PDF p160 · 对应本节：全景、立体全景与光场差在哪里？*

![PDF p160：Two Eyes — Two Spherical Cameras?](images/p160.png)

#### Problem: Stereo Baseline Fluctuates With View Angle

*PDF p161 · 对应本节：全景、立体全景与光场差在哪里？*

![PDF p161：Problem: Stereo Baseline Fluctuates With View Angle](images/p161.png)

#### Problems

*PDF p163 · 对应本节：全景、立体全景与光场差在哪里？*

![PDF p163：Problems](images/p163.png)

#### Imaging for Virtual Reality

*PDF p165 · 对应本节：全景、立体全景与光场差在哪里？*

![PDF p165：Imaging for Virtual Reality](images/p165.png)

#### Aside: Research on Near-Eye Light Field Displays

*PDF p167 · 对应本节：全景、立体全景与光场差在哪里？*

![PDF p167：Aside: Research on Near-Eye Light Field Displays](images/p167.png)

#### Multi-Camera Array ⇒ 4D Light Field

*PDF p168 · 对应本节：全景、立体全景与光场差在哪里？*

![PDF p168：Multi-Camera Array ⇒ 4D Light Field](images/p168.png)

#### Handheld Light Field Camera vs Camera Array

*PDF p169 · 对应本节：全景、立体全景与光场差在哪里？*

![PDF p169：Handheld Light Field Camera vs Camera Array](images/p169.png)

#### Imaging for Virtual Reality

*PDF p176 · 对应本节：全景、立体全景与光场差在哪里？*

![PDF p176：Imaging for Virtual Reality](images/p176.png)

</details>

## 13. 把十二个数值例子连成检查顺序

先手算再运行。随仓库提供的 `scripts/cs184-numerical-checks.py` 是小模型验证，不依赖 GPU，也不修改服务器配置。它不能替代完整渲染场景或模拟系统的验证。

| 顺序 | 本节关系 | 最容易漏掉的约定 |
| --- | --- | --- |
| 1 | VR 为什么把整门课放进一个系统？ | eye：左右眼相对头部位置 |
| 2 | 近眼镜片为什么不可省略？ | 限制：真实头显需完整光学参数 |
| 3 | 分辨率为什么要按每度计算？ | 前提：这里只取平均 |
| 4 | 双目视差怎样编码距离？ | d：水平视差 |
| 5 | 辐辏与调焦冲突为什么重要？ | 用途：量化调焦要求差异 |
| 6 | 六自由度追踪为何要融合传感器？ | 自由度：3+3，不等于矩阵元素数 |
| 7 | 33 毫秒为什么会变成明显的空间错误？ | 假设：局部恒速与平均角采样 |
| 8 | 注视点渲染为何仍需要抗锯齿？ | 模型：忽略额外开销的预算估算 |
| 9 | 畸变补偿为什么会改变采样需求？ | 真实系统：需标定更完整模型 |
| 10 | 时间扭曲能够修正什么，不能修正什么？ | 限制：纯旋转或远景近似 |
| 11 | 刷新、持续发光与眼动怎样产生抖动？ | 近似：恒速追踪 |
| 12 | 全景、立体全景与光场差在哪里？ | 范围：解释固定双全景限制 |

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
| VR 为什么把整门课放进一个系统？ | 左右眼应共享同一世界状态与时间基准；不同步会制造额外视觉冲突。 |
| 近眼镜片为什么不可省略？ | 不能把此式直接当真实多片目镜的完整标定模型。 |
| 分辨率为什么要按每度计算？ | 面板分辨率不是实际可见分辨率；光学模糊、畸变与渲染采样也有影响。 |
| 双目视差怎样编码距离？ | 物理单位和像素单位不能混用；左右眼视口与投影偏移也需一致。 |

### 阶段 2：第 5–8 节

| 涉及关系 | 错误机制 / 修正方向 |
| --- | --- |
| 辐辏与调焦冲突为什么重要？ | 这里是几何需求差，不是医学不适阈值；个体反应不能由一个数直接推断。 |
| 六自由度追踪为何要融合传感器？ | 追踪坐标轴、左右手系或时间戳不一致，会表现为头动方向反了或世界漂移。 |
| 33 毫秒为什么会变成明显的空间错误？ | 高 FPS 配上长排队仍可高延迟；性能日志应分阶段记录时间戳。 |
| 注视点渲染为何仍需要抗锯齿？ | 周边视觉对某些运动和闪烁仍敏感，不能把低空间敏锐度解释为“看不到错误”。 |

### 阶段 3：第 9–12 节

| 涉及关系 | 错误机制 / 修正方向 |
| --- | --- |
| 畸变补偿为什么会改变采样需求？ | 把一个眼睛的标定参数直接用于另一眼可能造成不一致，应按光学系统配置。 |
| 时间扭曲能够修正什么，不能修正什么？ | 把头部平移也套纯旋转重投影会错，尤其近景更明显。 |
| 刷新、持续发光与眼动怎样产生抖动？ | 只提高刷新但仍有长持续发光，改善程度可能不同；显示时序需一起看。 |
| 全景、立体全景与光场差在哪里？ | 把单点 360 图标成完整 6DoF 场景会夸大可交互范围；应标明位置运动限制。 |

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

### 自测 1. 左右眼用同一相机图像是否仍有双目视差？

<details>
<summary>参考答案</summary>

没有正确的双目视差；可以看到单目深度线索，但不等于立体呈现。

</details>

### 自测 2. 屏幕像素数相同，视场变大会有什么代价？

<details>
<summary>参考答案</summary>

平均每度像素数下降，角分辨率可能变差。

</details>

### 自测 3. 把 FOV 从 100° 增到 120° 而不增像素，平均 PPD 如何变化？

<details>
<summary>参考答案</summary>

乘 100/120，降低为原来的约 83.3%。

</details>

### 自测 4. 把双眼基线加倍会怎样？

<details>
<summary>参考答案</summary>

在该简化模型中视差加倍，会改变感知尺度与深度，不能随意调大。

</details>

### 自测 5. 增加帧率能解决固定焦面冲突吗？

<details>
<summary>参考答案</summary>

不能根本解决。时间响应与焦深线索是不同问题。

</details>

### 自测 6. 4×4 矩阵是否意味着姿态有 16 个自由度？

<details>
<summary>参考答案</summary>

不是，旋转正交性和最后一行等约束将刚体姿态限制为 6 个自由度。

</details>

### 自测 7. 把帧率从 60 提高到 120，延迟一定减半吗？

<details>
<summary>参考答案</summary>

不一定，其他流水线阶段和缓冲深度可能占主要部分。

</details>

### 自测 8. 注视点渲染是否只需要一个固定圆形高质量区域？

<details>
<summary>参考答案</summary>

固定中心版本可以节省开销，但眼动追踪版本需要随注视移动，并处理延迟和边界过渡。

</details>

### 自测 9. 畸变校正后边缘变糊，可能只是镜片不好吗？

<details>
<summary>参考答案</summary>

也可能是重采样拉伸与原图采样不足，需要检查渲染密度和过滤。

</details>

### 自测 10. 有深度图就能无损修复所有平移吗？

<details>
<summary>参考答案</summary>

不能。遮挡解除后露出的新区域在旧图里没有颜色信息。

</details>

### 自测 11. 低持续发光是否等于缩短相机快门？

<details>
<summary>参考答案</summary>

有相似的时间积分直觉，但一个发生在显示端，一个发生在采集或渲染端，不能互相替代。

</details>

### 自测 12. 为什么一张高清全景仍不能让人侧身看见桌子背后？

<details>
<summary>参考答案</summary>

新视点需要原图未记录的遮挡后信息，分辨率再高也不能补回缺失视点。

</details>

### 自测 13. 第 1 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

左右眼应共享同一世界状态与时间基准；不同步会制造额外视觉冲突。

再复算本节的例子：头部位置 x=1 米，左眼局部 x=-0.03 米，无旋转时世界 x=0.97 米。右眼 +0.03 得 1.03，间距仍 0.06 米。

</details>

### 自测 14. 第 2 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

不能把此式直接当真实多片目镜的完整标定模型。

再复算本节的例子：w=40 mm、f=20 mm，简化 FOV=90°。若 f=40 mm，变为约 53.13°；检查 w/(2f) 从 1 降为 0.5。

</details>

### 自测 15. 第 3 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

面板分辨率不是实际可见分辨率；光学模糊、畸变与渲染采样也有影响。

再复算本节的例子：2000 像素覆盖 100°，平均 20 PPD；想保持视场并达到 40 PPD，需要水平 4000 像素，二维近似像素数增四倍。

</details>

### 自测 16. 第 4 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

物理单位和像素单位不能混用；左右眼视口与投影偏移也需一致。

再复算本节的例子：f=1000 px、B=0.06 m、Z=2 m，d=30 px；Z=4 m 时 d=15。由 fB/d 可反算原深度。

</details>

### 自测 17. 第 5 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

这里是几何需求差，不是医学不适阈值；个体反应不能由一个数直接推断。

再复算本节的例子：光学焦面 2 米对应 0.5 D，虚拟目标 0.5 米对应 2 D，差为 1.5 D。倒数换算检验两者对应距离。

</details>

### 自测 18. 第 6 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

追踪坐标轴、左右手系或时间戳不一致，会表现为头动方向反了或世界漂移。

再复算本节的例子：仅向前平移 0.1 米而朝向不变，R 不变、t 改变。若系统只更新 R，近处物体应有的运动视差就完全丢失。

</details>

### 自测 19. 第 7 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

高 FPS 配上长排队仍可高延迟；性能日志应分阶段记录时间戳。

再复算本节的例子：课件例 ω=90°/s、τ=0.033 s、PPD=20，误差约 59.4 px，接近 60。角误差 2.97° 乘 20 得同样结果。

</details>

### 自测 20. 第 8 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

周边视觉对某些运动和闪烁仍敏感，不能把低空间敏锐度解释为“看不到错误”。

再复算本节的例子：a=0.1、r=0.25，总工作为 0.325N，理论减少 67.5%。若额外开销很大，实际加速不会等于 1/0.325。

</details>

### 自测 21. 第 9 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

把一个眼睛的标定参数直接用于另一眼可能造成不一致，应按光学系统配置。

再复算本节的例子：r=0.5、k1=0.2，rd=0.525。若 r=1，rd=1.2，边缘拉伸更明显；比例分别为 1.05 与 1.2。

</details>

### 自测 22. 第 10 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

把头部平移也套纯旋转重投影会错，尤其近景更明显。

再复算本节的例子：一维小角度近似，f=1000 px，转角 0.01 rad，位移约 10 px。若再有横移 0.01 m，深度 1 m 与 10 m 的额外位移约 10 与 1 px，不可同一旋转替代。

</details>

### 自测 23. 第 11 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

只提高刷新但仍有长持续发光，改善程度可能不同；显示时序需一起看。

再复算本节的例子：ω=100°/s，持续发光 10 ms，角模糊约 1°；缩到 2 ms 后约 0.2°。时间缩五倍，模糊也缩五倍。

</details>

### 自测 24. 第 12 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

把单点 360 图标成完整 6DoF 场景会夸大可交互范围；应标明位置运动限制。

再复算本节的例子：B=6 cm，θ=60° 时有效基线 3 cm；θ=90° 时趋于零。cos60=1/2，恰好减半。

</details>

### 自测 25. 本讲的输入、输出和中间表示各是什么？

<details>
<summary>参考答案</summary>

人眼需要哪些线索 → 双眼与光学显示 → 追踪六自由度 → 在延迟预算内渲染 → 重投影 → 全景与光场。请沿箭头逐项解释，尤其说清中间表示的单位、坐标或概率测度；只复述名词不算掌握。

</details>

### 自测 26. 能否只用一张“看起来正确”的图片证明实现正确？

<details>
<summary>参考答案</summary>

不能。需要将关键关系拆成可预测的小输入，检查数值、边界与对照；随机方法还要区分一次结果与统计期望，显示图还需区分编码与原始数据。

</details>

## 17. 带走的结论与仍需练习的内容

- 没有正确的双目视差；可以看到单目深度线索，但不等于立体呈现。
- 平均每度像素数下降，角分辨率可能变差。
- 乘 100/120，降低为原来的约 83.3%。
- 在该简化模型中视差加倍，会改变感知尺度与深度，不能随意调大。
- 不能根本解决。时间响应与焦深线索是不同问题。
- 不是，旋转正交性和最后一行等约束将刚体姿态限制为 6 个自由度。
- 不一定，其他流水线阶段和缓冲深度可能占主要部分。
- 固定中心版本可以节省开销，但眼动追踪版本需要随注视移动，并处理延迟和边界过渡。
- 也可能是重采样拉伸与原图采样不足，需要检查渲染密度和过滤。
- 不能。遮挡解除后露出的新区域在旧图里没有颜色信息。
- 有相似的时间积分直觉，但一个发生在显示端，一个发生在采集或渲染端，不能互相替代。
- 新视点需要原图未记录的遮挡后信息，分辨率再高也不能补回缺失视点。

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

[原课件文件与版本记录](https://github.com/Teddy-Yangjiale/CS184/blob/main/CS184_2026/sp26/lectures/SP26-L26-27-virtual-reality.pdf) · [课程官网](https://cs184.eecs.berkeley.edu/sp26/)

文件：`SP26-L26-27-virtual-reality.pdf`；PDF 页数：178；SHA-256：`ea679995b81243b9a34751a773645f706e92eaa97dcda5d2af2ab9c3e56fca78`。

“正文核对”表示本篇实际引用该页截图；“索引保留”包括演示、行政信息、补充、致谢与重复构建页，不表示逐页都有独立讲解。原视频的运动过程不能由静态 PDF 截图完整复现。

| PDF 页 | 原页可提取标题 | 本篇使用 |
| --- | --- | --- |
| 1 | Computer Graphics and Imaging | 索引保留 |
| 2 | Virtual Reality (VR) vs Augmented Reality (AR) | 正文核对 |
| 3 | Ivan Sutherland’s Virtual Reality Research in 1968 | 索引保留 |
| 4 | VR Head-Mounted Displays (HMDs) | 索引保留 |
| 5 | AR Headsets | 索引保留 |
| 6 | VR Applications | 索引保留 |
| 7 | VR Gaming | 索引保留 |
| 8 | VR Painting | 索引保留 |
| 9 | VR Painting | 索引保留 |
| 10 | VR Video | 索引保留 |
| 11 | VR Video | 索引保留 |
| 12 | VR Video | 索引保留 |
| 13 | VR Teleconference / Video Chat | 索引保留 |
| 14 | The Intimacy of VR Graphics | 索引保留 |
| 15 | The Intimacy of VR Graphics | 索引保留 |
| 16 | Overview of VR Topics | 正文核对 |
| 17 | VR Displays | 索引保留 |
| 18 | Field of View | 正文核对 |
| 19 | 3D Visual Cues | 正文核对 |
| 20 | VR Headset Components | 正文核对 |
| 21 | Oculus Quest 2 Headset (2020) | 索引保留 |
| 22 | Oculus Quest 2 Headset | 索引保留 |
| 23 | Oculus Quest 2 Headset | 索引保留 |
| 24 | Oculus Quest 2 Headset | 索引保留 |
| 25 | Oculus Quest 2 Headset (Snapdragon SoC) | 索引保留 |
| 26 | Oculus Quest 2 Headset | 索引保留 |
| 27 | Oculus Quest 2 Headset (Lens Assembly) | 正文核对 |
| 28 | Oculus Quest 2 Display + Lens Assembly | 正文核对 |
| 29 | Oculus Rift (2016) | 索引保留 |
| 30 | Oculus Rift (2016) | 索引保留 |
| 31 | Oculus Rift (2016) | 索引保留 |
| 32 | Oculus Rift (2016) | 索引保留 |
| 33 | Oculus Rift (2016) | 正文核对 |
| 34 | Oculus Rift Lenses | 正文核对 |
| 35 | Oculus Rift Lenses | 索引保留 |
| 36 | Role of Eyepiece Lenses | 正文核对 |
| 37 | Pancake Lenses | 正文核对 |
| 38 | Display Requirements Derive | 索引保留 |
| 39 | Anatomy of The Human Eye | 索引保留 |
| 40 | Display Requirements Derive | 索引保留 |
| 41 | Recall: Spectral Response of Human Cone Cells | 索引保留 |
| 42 | Recall: Metamerism | 索引保留 |
| 43 | Recall: Metamerism | 索引保留 |
| 44 | Recall: Color Reproduction | 索引保留 |
| 45 | Display Requirements Derive | 正文核对 |
| 46 | Human Visual Field of View | 正文核对 |
| 47 | Recall: Photoreceptor Size and Distribution Across Retina | 正文核对 |
| 48 | Visual Acuity | 正文核对 |
| 49 | Visual Acuity | 正文核对 |
| 50 | Current VR Headset Field of View and Resolution | 正文核对 |
| 51 | A VR Display at Human Visual Acuity | 正文核对 |
| 52 | Display Requirements Derive | 正文核对 |
| 53 | Two Eyes: Two Views | 正文核对 |
| 54 | Recall: Current VR HMD Optical Design | 索引保留 |
| 55 | Stereo Vergence | 正文核对 |
| 56 | Stereo Vergence | 正文核对 |
| 57 | Stereo Vergence | 正文核对 |
| 58 | Stereo Vergence | 索引保留 |
| 59 | Stereo | 正文核对 |
| 60 | Human Eye Muscles and Optical Controls | 正文核对 |
| 61 | Human Eye Muscles and Optical Controls | 正文核对 |
| 62 | Accommodation and Vergence | 正文核对 |
| 63 | Accommodation – Vergence Conﬂict | 正文核对 |
| 64 | Display Requirements Derive | 正文核对 |
| 65 | Google Cardboard: Tracking Using Headset Camera | 正文核对 |
| 66 | 6 DOF Head Pose Estimation | 正文核对 |
| 67 | Environment-Supported Vision-Based Tracking? | 索引保留 |
| 68 | Oculus Rift IR LED Tracking System | 正文核对 |
| 69 | Oculus Rift IR LED Tracking Hardware | 索引保留 |
| 70 | Oculus Rift LED Tracking System (DK2) | 正文核对 |
| 71 | Oculus Rift IR Camera | 索引保留 |
| 72 | Recall: Passive Optical Motion Capture | 索引保留 |
| 73 | Active Optical Motion Capture | 正文核对 |
| 74 | Oculus Rift Uses Active Marker Motion Capture | 索引保留 |
| 75 | Oculus Rift Uses Active Marker Motion Capture | 索引保留 |
| 76 | HTC Vive Tracking System (“Lighthouse”) | 正文核对 |
| 77 | Vive Headset & Controllers Have Array of IR Photodiodes | 索引保留 |
| 78 | HTC Vive Structured Light Emitter (“Lighthouse”) | 索引保留 |
| 79 | HTC Vive Structured Light Emitter (“Lighthouse”) | 索引保留 |
| 80 | HTC Vive Structured Light Emitter (“Lighthouse”) | 索引保留 |
| 81 | HTC Vive Tracking System | 正文核对 |
| 82 | HTC Vive Tracking System (“Lighthouse”) | 索引保留 |
| 83 | HTC Vive Tracking System (“Lighthouse”) | 索引保留 |
| 84 | • Wide-angle cameras look outward from headset | 正文核对 |
| 85 | Tracking Summary | 正文核对 |
| 86 | Overview of VR Topics | 索引保留 |
| 87 | Rendering Latency in VR | 正文核对 |
| 88 | A VR Display at Human Visual Acuity | 正文核对 |
| 89 | Latency Requirements in VR Are Challenging | 正文核对 |
| 90 | Thought Experiment: Effect of Latency | 正文核对 |
| 91 | Rendering Challenge: | 正文核对 |
| 92 | Recall: Photoreceptor Size and Distribution Across Retina | 正文核对 |
| 93 | Foveated Rendering | 正文核对 |
| 94 | Foveated Rendering - Perceptual Effects | 正文核对 |
| 95 | Foveated Rendering - Perceptual Effects | 索引保留 |
| 96 | Foveated Rendering - Perceptual Effects | 索引保留 |
| 97 | Foveated Rendering - Perceptual Effects | 正文核对 |
| 98 | Foveated Rendering - Perceptual Effects | 索引保留 |
| 99 | Foveated Rendering - Perceptual Effects | 索引保留 |
| 100 | Foveated Rendering | 正文核对 |
| 101 | Rendering Challenge: Optical | 正文核对 |
| 102 | Requirement: Wide Field of View | 正文核对 |
| 103 | Software Correction of Lens Distortion in Photography | 正文核对 |
| 104 | Software Compensation of Lens Distortion in VR Rendering | 正文核对 |
| 105 | Software Compensation of Lens Distortion in VR Rendering | 正文核对 |
| 106 | Related Challenge: Rendering via Planar Projection | 正文核对 |
| 107 | Related Challenge: Rendering via Planar Projection | 索引保留 |
| 108 | A Recent Implementation: Lens Matched Shading | 正文核对 |
| 109 | Rendering Challenge: Eye Motion | 正文核对 |
| 110 | Consider Finite VR Display Refresh Rate | 正文核对 |
| 111 | Consider Finite VR Display Refresh Rate | 索引保留 |
| 112 | Consider Finite VR Display Refresh Rate | 索引保留 |
| 113 | Consider Finite VR Display Refresh Rate | 索引保留 |
| 114 | Consider Finite VR Display Refresh Rate | 索引保留 |
| 115 | Consider Finite VR Display Refresh Rate | 索引保留 |
| 116 | Consider Finite VR Display Refresh Rate | 索引保留 |
| 117 | Consider Finite VR Display Refresh Rate | 索引保留 |
| 118 | Case 2: Object Moving Relative to Eye | 正文核对 |
| 119 | Case 2: Object Moving Relative to Eye | 索引保留 |
| 120 | Case 2: Object Moving Relative to Eye | 索引保留 |
| 121 | Case 2: Object Moving Relative to Eye | 索引保留 |
| 122 | Case 2: Object Moving Relative to Eye | 索引保留 |
| 123 | Case 2: Object Moving Relative to Eye | 索引保留 |
| 124 | Case 2: Object Moving Relative to Eye | 索引保留 |
| 125 | Case 3: Eye Moving to Track Moving Object | 正文核对 |
| 126 | Case 3: Eye Moving to Track Moving Object | 索引保留 |
| 127 | Case 3: Eye Moving to Track Moving Object | 索引保留 |
| 128 | Case 3: Eye Moving to Track Moving Object | 索引保留 |
| 129 | Case 3: Eye Moving to Track Moving Object | 索引保留 |
| 130 | Case 3: Eye Moving to Track Moving Object | 索引保留 |
| 131 | Case 3: Eye Moving to Track Moving Object | 正文核对 |
| 132 | Reducing Judder: Increase Frame Rate | 正文核对 |
| 133 | Reducing Judder: Low Persistence Display | 正文核对 |
| 134 | Problem: Displays Exhibit “Rolling Shutter” Artifacts | 正文核对 |
| 135 | Problem: Displays Exhibit “Rolling Shutter” Artifacts | 索引保留 |
| 136 | Problem: Displays Exhibit “Rolling Shutter” Artifacts | 正文核对 |
| 137 | Rendering Challenge: | 正文核对 |
| 138 | Problem: High-Quality Rendering Can Be Slow | 正文核对 |
| 139 | Modern VR Engineering Solution: Reprojection | 正文核对 |
| 140 | Asynchronous TimeWarp (ATW) | 正文核对 |
| 141 | Asynchronous TimeWarp (ATW) | 正文核对 |
| 142 | Asynchronous TimeWarp (ATW) | 正文核对 |
| 143 | Modern VR Engineering Solution: Reprojection | 正文核对 |
| 144 | Asynchronous SpaceWarp (ASW) | 正文核对 |
| 145 | Overview of VR Topics | 索引保留 |
| 146 | Spherical Imaging | 正文核对 |
| 147 | Dual Fisheye | 正文核对 |
| 148 | Stitching Challenges | 正文核对 |
| 149 | Spherical Array of Cameras | 索引保留 |
| 150 | Stitching Challenges | 索引保留 |
| 151 | High Quality Stitching Solution Uses Computer Vision | 正文核对 |
| 152 | Spherical Stereo Imaging | 正文核对 |
| 153 | What Pairs of Viewpoint Positions Do We Want To Sample? | 索引保留 |
| 154 | Idea: Spin a Pair of Cameras About Midpoint | 索引保留 |
| 155 | Omni-Directional Stereo Approximation | 正文核对 |
| 156 | Omni-Directional Stereo Approximation | 索引保留 |
| 157 | Spinning Camera | 索引保留 |
| 158 | Omni-Directional Stereo Representation | 正文核对 |
| 159 | Example (Rendered) | 索引保留 |
| 160 | Two Eyes — Two Spherical Cameras? | 正文核对 |
| 161 | Problem: Stereo Baseline Fluctuates With View Angle | 正文核对 |
| 162 | Problem: Both Horizontal and Vertical Disparities Fluctuate | 索引保留 |
| 163 | Problems | 正文核对 |
| 164 | Solution: Computational Photography | 索引保留 |
| 165 | Imaging for Virtual Reality | 正文核对 |
| 166 | Spherical Stereo Result | 索引保留 |
| 167 | Aside: Research on Near-Eye Light Field Displays | 正文核对 |
| 168 | Multi-Camera Array ⇒ 4D Light Field | 正文核对 |
| 169 | Handheld Light Field Camera vs Camera Array | 正文核对 |
| 170 | [Wilburn et al. SIGGRAPH 2005] | 索引保留 |
| 171 | [Wilburn et al. SIGGRAPH 2005] | 索引保留 |
| 172 | 图像或演示页（请以原页视觉内容为准） | 索引保留 |
| 173 | 图像或演示页（请以原页视觉内容为准） | 索引保留 |
| 174 | Google VR Camera Rig | 索引保留 |
| 175 | Google VR Camera Rig | 索引保留 |
| 176 | Imaging for Virtual Reality | 正文核对 |
| 177 | Imaging for Virtual Reality | 索引保留 |
| 178 | Acknowledgments | 索引保留 |
