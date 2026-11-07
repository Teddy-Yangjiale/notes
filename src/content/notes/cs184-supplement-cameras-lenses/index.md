---
title: "CS184 补充 A：相机与镜头，从针孔到景深"
date: 2026-11-07
updated: 2026-11-07
summary: "视场与透视 → 光圈快门与曝光 → 薄透镜对焦 → 离焦形成光斑 → 孔径采样 → 真实镜头与传感器。以原课件为依据，配 20 张可编辑图解、12 个数值例子、26 道带答案自测与 PDF 全页索引。"
tags: ["计算机图形学", "CS184", "课程笔记"]
series: "cs184"
order: 91
shortTitle: "补充 A"
---

> UC Berkeley · CS184/284A · Summer 2026 · 文件标识 `SU26-L16-17-cameras-lenses.pdf`。
> 本文的 **pN 一律是 PDF 的第 N 页**，不是封面讲次或页脚旧编号。文件名与封面可能不同，以下均按文件和页码回查。

## 0. 先抓住这一条推理链

```text
视场与透视
    ↓
光圈快门与曝光
    ↓
薄透镜对焦
    ↓
离焦形成光斑
    ↓
孔径采样
    ↓
真实镜头与传感器
```

这篇笔记的阅读顺序是：先理解输入和输出，再确认公式的条件，最后用小数值检查。
正文将课件概念、补充推导和教学例子分开；示意图中的理想几何与数字不冒充真实实验测量。

| 内容 | 本文提供什么 |
|---|---|
| 来源 | Summer 2026，PDF 共 132 页；正文选择 90 张关键页 |
| 图解 | 12 张概念关系图 + 8 张几何或数值图，均有原生可编辑 PPTX |
| 手算 | 12 个带输入、结果和回代检查的教学例子 |
| 复习 | 26 道自测及答案，末尾保留全页索引 |
| 运行证据 | 数值核对脚本覆盖解析小模型，不代表完整渲染器或模拟器已经实现 |

[下载本篇 20 张可编辑图解（PPTX 与操作 JSON）](/notes/cs184/figures/90-editable.zip)

### 课件与推导的使用边界

课件截图用于对照原始定义与几何；正文用中文解释关系，并提供必要的修正与推导。
后续专题按本地文件的学期和编号组织，不假定它们与秋季一一对应。
若只做第一遍学习，先读每节前两段和数值例子，再展开原页核对。

### 与前面哪一讲接上

先回顾[相关前置讲义](/notes/cs184-14-radiometry/)。本篇在已有表示与数学工具上增加新变量或新约束，而不是另起一套互不相关的公式。

## 1. 相机为什么不只是一个投影矩阵？

投影矩阵决定几何怎样落到图像上，真实相机还决定哪些光线进入、曝光多久以及如何转成数字信号。景深、运动模糊和噪声都来自这些过程。

本专题放在颜色与光传输之后，是为了把“沿一条射线返回 L”推广到像素、孔径和时间上的积分。公式的物距、像距和传感器尺寸必须使用统一单位。

![概念关系：相机为什么不只是一个投影矩阵？](diagrams/d01-relation.png)

*读图：光学形成像 → 快门积分能量 → 传感器与图像处理。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| H | 辐射曝光量 J/m² |
| E | 传感器辐照度 |
| 时间 | 快门开放区间 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
H=\int_{t_0}^{t_1}E(t)dt
$$

### 🔧 手算 1：把关系落到数字上

恒定 E=2 W/m²、曝光 0.01 秒，H=0.02 J/m²。曝光翻倍为 0.02 秒，H=0.04；回除时间仍得 E=2。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 曝光翻倍为 0.02 秒，H=0.04；回除时间仍得 E=2。 |
| 适用边界 | ISO 增益不是镜头多收到了光子；区分采集光量与信号放大。 |

### ⚠️ 易错点：先识别症状与假设

ISO 增益不是镜头多收到了光子；区分采集光量与信号放大。

### 停下来解释一次

**问题：两个相机投影相同，照片一定完全一样吗？**

<details>
<summary>展开参考回答</summary>

不。孔径、曝光、传感器响应、噪声和图像处理都可能不同。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Image Capture Overview

*PDF p4 · 对应本节：相机为什么不只是一个投影矩阵？*

![PDF p4：Image Capture Overview](images/p004.png)

#### What’s Happening Inside the Camera?

*PDF p5 · 对应本节：相机为什么不只是一个投影矩阵？*

![PDF p5：What’s Happening Inside the Camera?](images/p005.png)

#### Pinholes & Lenses Form Image on Sensor

*PDF p6 · 对应本节：相机为什么不只是一个投影矩阵？*

![PDF p6：Pinholes & Lenses Form Image on Sensor](images/p006.png)

#### Shutter Exposes Sensor For Precise Duration

*PDF p7 · 对应本节：相机为什么不只是一个投影矩阵？*

![PDF p7：Shutter Exposes Sensor For Precise Duration](images/p007.png)

#### Sensor Accumulates Irradiance During Exposure

*PDF p8 · 对应本节：相机为什么不只是一个投影矩阵？*

![PDF p8：Sensor Accumulates Irradiance During Exposure](images/p008.png)

#### Image Processing: From Sensor Values to Image

*PDF p9 · 对应本节：相机为什么不只是一个投影矩阵？*

![PDF p9：Image Processing: From Sensor Values to Image](images/p009.png)

</details>

## 2. 焦距与传感器怎样共同决定视场？

同一焦距配更大传感器会覆盖更大视场，同一传感器配更长焦距则视场更窄。等效焦距是比较视角的约定，不等于小相机镜头的实际物理焦距。

课件给出的 35mm 格式视场数字常对应对角线；计算时必须说明用水平、垂直还是对角尺寸。否则相同 50mm 会出现看似矛盾的角度。

![概念关系：焦距与传感器怎样共同决定视场？](diagrams/d02-relation.png)

*读图：传感器尺寸 → 与焦距形成比值 → 视场角。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| w | 传感器水平宽度 |
| f | 实际焦距 |
| 假设 | 针孔或远距离薄透镜近似 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
\mathrm{FOV}_x=2\arctan\frac{w}{2f}
$$

### 🔧 手算 2：把关系落到数字上

w=36 mm、f=50 mm，水平 FOV≈39.60°；对角尺寸约 43.27 mm，得到约 46.79°。两个结果对应不同方向。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 两个结果对应不同方向。 |
| 适用边界 | 不要把水平宽度代入公式后去对照课件的对角视场。 |

![几何或数值解释 1](diagrams/d13-fov.png)

*视场由传感器尺寸与焦距共同决定，必须明确水平或对角方向。*

### ⚠️ 易错点：先识别症状与假设

不要把水平宽度代入公式后去对照课件的对角视场。

### 停下来解释一次

**问题：焦距不变，把传感器宽度减半会怎样？**

<details>
<summary>展开参考回答</summary>

水平视场变窄；角度不是一般地精确减半，因为还有 arctan 非线性。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Optics of Image Formation:

*PDF p10 · 对应本节：焦距与传感器怎样共同决定视场？*

![PDF p10：Optics of Image Formation:](images/p010.png)

#### Effect of Focal Length on FOV

*PDF p11 · 对应本节：焦距与传感器怎样共同决定视场？*

![PDF p11：Effect of Focal Length on FOV](images/p011.png)

#### Effect of Sensor Size on FOV

*PDF p12 · 对应本节：焦距与传感器怎样共同决定视场？*

![PDF p12：Effect of Sensor Size on FOV](images/p012.png)

#### Sensor Sizes

*PDF p13 · 对应本节：焦距与传感器怎样共同决定视场？*

![PDF p13：Sensor Sizes](images/p013.png)

#### Maintain FOV on Smaller Sensor?

*PDF p14 · 对应本节：焦距与传感器怎样共同决定视场？*

![PDF p14：Maintain FOV on Smaller Sensor?](images/p014.png)

#### Focal Length v. Field of View

*PDF p15 · 对应本节：焦距与传感器怎样共同决定视场？*

![PDF p15：Focal Length v. Field of View](images/p015.png)

#### Focal Length v. Field of View

*PDF p18 · 对应本节：焦距与传感器怎样共同决定视场？*

![PDF p18：Focal Length v. Field of View](images/p018.png)

</details>

## 3. 透视压缩究竟由什么造成？

保持相机位置，只改变焦距，相当于改变成像尺度与裁切范围，物体的相对透视关系不变。为了让主体同样大而移动相机，才改变近远物体的相对投影比例。

Dolly zoom 同时移动相机与改变焦距，固定主体大小，却让背景关系变化。这是投影几何与摄影构图之间的重要桥梁。

![概念关系：透视压缩究竟由什么造成？](diagrams/d03-relation.png)

*读图：改变相机位置 → 改变深度比例 → 改变透视关系。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| H | 物体高度 |
| Z | 距离 |
| f | 焦距 |
| 条件 | 针孔近似 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
h_{image}\approx\frac{fH}{Z}
$$

### 🔧 手算 3：把关系落到数字上

主体 H=1、Z=5、f=0.05，像高 0.01。后退到 Z=10 并把 f 改成 0.1，主体仍为 0.01；原来更远的背景距离变化比例却不同。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 后退到 Z=10 并把 f 改成 0.1，主体仍为 0.01；原来更远的背景距离变化比例却不同。 |
| 适用边界 | “长焦改变透视”常省略了摄影师后退的条件；先问相机中心是否移动。 |

### ⚠️ 易错点：先识别症状与假设

“长焦改变透视”常省略了摄影师后退的条件；先问相机中心是否移动。

### 停下来解释一次

**问题：原地变焦后裁到相同画面，透视会不同吗？**

<details>
<summary>展开参考回答</summary>

理想投影下不会，透视由观察位置决定；实际镜头像差等可能另外影响图像。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Perspective Composition

*PDF p28 · 对应本节：透视压缩究竟由什么造成？*

![PDF p28：Perspective Composition](images/p028.png)

#### Perspective Composition – Camera Position / Focal Length

*PDF p29 · 对应本节：透视压缩究竟由什么造成？*

![PDF p29：Perspective Composition – Camera Position / Focal Length](images/p029.png)

#### Perspective Composition – Camera Position / Focal Length

*PDF p30 · 对应本节：透视压缩究竟由什么造成？*

![PDF p30：Perspective Composition – Camera Position / Focal Length](images/p030.png)

#### Perspective Composition – Camera Position / Focal Length

*PDF p31 · 对应本节：透视压缩究竟由什么造成？*

![PDF p31：Perspective Composition – Camera Position / Focal Length](images/p031.png)

#### Perspective Composition – Camera Position / Focal Length

*PDF p34 · 对应本节：透视压缩究竟由什么造成？*

![PDF p34：Perspective Composition – Camera Position / Focal Length](images/p034.png)

#### Perspective Composition

*PDF p35 · 对应本节：透视压缩究竟由什么造成？*

![PDF p35：Perspective Composition](images/p035.png)

#### Dolly-Zoom Cinema Technique – a.k.a. “Vertigo Effect”

*PDF p38 · 对应本节：透视压缩究竟由什么造成？*

![PDF p38：Dolly-Zoom Cinema Technique – a.k.a. “Vertigo Effect”](images/p038.png)

#### A Photographer’s Mindset

*PDF p39 · 对应本节：透视压缩究竟由什么造成？*

![PDF p39：A Photographer’s Mindset](images/p039.png)

</details>

## 4. 曝光档位为何是对数？

增加一档曝光意味着接收光量乘二。快门时间直接按比例改变光量，光圈通光面积与直径平方成正比，所以 f-number 相邻一档通常按 √2 变化。

同一曝光可以由不同快门与光圈组合得到，但运动模糊、景深和衍射等副作用不同，不能把相同亮度当成相同照片。

![概念关系：曝光档位为何是对数？](diagrams/d04-relation.png)

*读图：孔径面积与时间 → 曝光乘法 → 用档位表达倍数。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| N | f-number |
| D | 有效孔径直径 |
| t | 曝光时间 |
| 条件 | 其他光学因素固定 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
N=f/D,\qquad H\propto t/N^2
$$

### 🔧 手算 4：把关系落到数字上

50 mm 镜头 f/2 的孔径直径 25 mm，f/4 为 12.5 mm，面积降为 1/4。要保持曝光，1/200 秒需改为 1/50 秒。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 要保持曝光，1/200 秒需改为 1/50 秒。 |
| 适用边界 | f/2 到 f/4 是两档而不是一档，因为面积变化四倍。 |

![几何或数值解释 2](diagrams/d14-aperture.png)

*同焦距下孔径直径依次减半，面积依次减为四分之一。*

### ⚠️ 易错点：先识别症状与假设

f/2 到 f/4 是两档而不是一档，因为面积变化四倍。

### 停下来解释一次

**问题：快门加倍且 f-number 乘 √2，曝光怎样变化？**

<details>
<summary>展开参考回答</summary>

时间增光两倍、面积减半，理想条件下相互抵消。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Exposure

*PDF p40 · 对应本节：曝光档位为何是对数？*

![PDF p40：Exposure](images/p040.png)

#### Exposure Levels - “Stops” are Logarithmic

*PDF p41 · 对应本节：曝光档位为何是对数？*

![PDF p41：Exposure Levels - “Stops” are Logarithmic](images/p041.png)

#### Exposure

*PDF p42 · 对应本节：曝光档位为何是对数？*

![PDF p42：Exposure](images/p042.png)

#### Exposure Controls: Aperture, Shutter, Gain (ISO)

*PDF p43 · 对应本节：曝光档位为何是对数？*

![PDF p43：Exposure Controls: Aperture, Shutter, Gain (ISO)](images/p043.png)

#### Many Ways to Achieve the Same Exposure

*PDF p46 · 对应本节：曝光档位为何是对数？*

![PDF p46：Many Ways to Achieve the Same Exposure](images/p046.png)

#### Definition: F-Number of a Lens

*PDF p47 · 对应本节：曝光档位为何是对数？*

![PDF p47：Definition: F-Number of a Lens](images/p047.png)

#### Example F-Number Calculations

*PDF p48 · 对应本节：曝光档位为何是对数？*

![PDF p48：Example F-Number Calculations](images/p048.png)

</details>

## 5. ISO 为什么不能替代进光量？

提高增益会让信号数值更大，也会影响噪声与动态范围表现，但不会让已曝光的传感器接收到更多光子。提高曝光光量与提高输出增益是不同操作。

噪声机制不止一种。下面用光子计数的 Poisson 模型说明采光量与信噪比，属于教学补充，不能据此判断某台相机所有 ISO 档位的实际优劣。

![概念关系：ISO 为什么不能替代进光量？](diagrams/d05-relation.png)

*读图：接收到的光子 → 噪声随采光变化 → 增益放大信号。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| Np | 平均光子或等效电子数 |
| 条件 | 仅考虑散粒噪声 |
| 未含 | 读出噪声与饱和 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
\operatorname{SNR}\approx\frac{N_p}{\sqrt{N_p}}=\sqrt{N_p}
$$

### 🔧 手算 5：把关系落到数字上

Np=100 时 SNR≈10；Np=400 时≈20。把前者信号和噪声同时乘 4，SNR 仍是 10，不会变成 40。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 把前者信号和噪声同时乘 4，SNR 仍是 10，不会变成 40。 |
| 适用边界 | 不要把增益后的像素值当作真实采光量；还需考虑黑电平与饱和。 |

![几何或数值解释 7](diagrams/d19-bars.png)

*仅考虑散粒噪声时，信噪比近似为光子计数平方根。*

### ⚠️ 易错点：先识别症状与假设

不要把增益后的像素值当作真实采光量；还需考虑黑电平与饱和。

### 停下来解释一次

**问题：提高 ISO 后照片变亮，是否证明信噪比必然提高？**

<details>
<summary>展开参考回答</summary>

不能。增益、读出链路与曝光设置共同影响结果，需要具体测量。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Exposure Controls: Aperture, Shutter, Gain (ISO)

*PDF p43 · 对应本节：ISO 为什么不能替代进光量？*

![PDF p43：Exposure Controls: Aperture, Shutter, Gain (ISO)](images/p043.png)

#### Gain (ISO) — Noise Increases

*PDF p44 · 对应本节：ISO 为什么不能替代进光量？*

![PDF p44：Gain (ISO) — Noise Increases](images/p044.png)

#### ISO (Gain)

*PDF p45 · 对应本节：ISO 为什么不能替代进光量？*

![PDF p45：ISO (Gain)](images/p045.png)

#### Many Ways to Achieve the Same Exposure

*PDF p46 · 对应本节：ISO 为什么不能替代进光量？*

![PDF p46：Many Ways to Achieve the Same Exposure](images/p046.png)

</details>

## 6. 快门怎样连接到运动模糊与滚动畸变？

曝光期间移动的物体会在传感器上扫过轨迹。滚动快门则让不同图像行在不同时间开始采集，因此直杆或快速移动物体可能倾斜。

缩短每行曝光能减少每行模糊，但若整幅扫描仍花较长时间，跨行形变可能继续存在。曝光时长和读出时差必须分开。

![概念关系：快门怎样连接到运动模糊与滚动畸变？](diagrams/d06-relation.png)

*读图：每行曝光时间 → 行间起始时间差 → 模糊与几何形变。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| b | 像面模糊长度 |
| v_image | 像素/秒 |
| 条件 | 匀速且无遮挡 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
b\approx v_{image}t_{exposure}
$$

### 🔧 手算 6：把关系落到数字上

v=200 px/s、曝光 0.005 秒，模糊约 1 px。若上下行时间差 0.02 秒，物体跨行位置差仍可达 4 px。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 若上下行时间差 0.02 秒，物体跨行位置差仍可达 4 px。 |
| 适用边界 | 短快门不自动消除滚动快门形变；这两种时间效应来源不同。 |

![几何或数值解释 6](diagrams/d18-motion.png)

*曝光时长影响运动轨迹积分，与行间扫描时差不是同一参数。*

### ⚠️ 易错点：先识别症状与假设

短快门不自动消除滚动快门形变；这两种时间效应来源不同。

### 停下来解释一次

**问题：全局快门是否就不会有运动模糊？**

<details>
<summary>展开参考回答</summary>

仍会。它让各行曝光时刻一致，但曝光本身仍有有限时长。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Physical Shutter (1/25 Sec Exposure)

*PDF p50 · 对应本节：快门怎样连接到运动模糊与滚动畸变？*

![PDF p50：Physical Shutter (1/25 Sec Exposure)](images/p050.png)

#### Main Side Effect of Shutter Speed

*PDF p51 · 对应本节：快门怎样连接到运动模糊与滚动畸变？*

![PDF p51：Main Side Effect of Shutter Speed](images/p051.png)

#### Electronic Shutter

*PDF p53 · 对应本节：快门怎样连接到运动模糊与滚动畸变？*

![PDF p53：Electronic Shutter](images/p053.png)

#### Electronic Rolling Shutter

*PDF p54 · 对应本节：快门怎样连接到运动模糊与滚动畸变？*

![PDF p54：Electronic Rolling Shutter](images/p054.png)

#### Electronic Rolling Shutter

*PDF p55 · 对应本节：快门怎样连接到运动模糊与滚动畸变？*

![PDF p55：Electronic Rolling Shutter](images/p055.png)

#### Physical Shutter (Fast Exposures)

*PDF p58 · 对应本节：快门怎样连接到运动模糊与滚动畸变？*

![PDF p58：Physical Shutter (Fast Exposures)](images/p058.png)

#### High-Speed Photography (Short Shutter)

*PDF p60 · 对应本节：快门怎样连接到运动模糊与滚动畸变？*

![PDF p60：High-Speed Photography (Short Shutter)](images/p060.png)

#### Long-Exposure Photography

*PDF p62 · 对应本节：快门怎样连接到运动模糊与滚动畸变？*

![PDF p62：Long-Exposure Photography](images/p062.png)

#### Long-Exposure Photography

*PDF p64 · 对应本节：快门怎样连接到运动模糊与滚动畸变？*

![PDF p64：Long-Exposure Photography](images/p064.png)

</details>

## 7. 薄透镜如何把一个物平面变清晰？

薄透镜将同一物点的不同入射光线汇聚到对应像点。固定焦距 f 后，物距 zo 决定清晰像距 zi；传感器必须位于对应像面。

推导可用平行主轴光线经焦点、过光心光线近似不偏折的几何关系。本文物距像距取正值讨论实物实像，倒像方向另外说明，不混用带符号光学约定。

![概念关系：薄透镜如何把一个物平面变清晰？](diagrams/d07-relation.png)

*读图：物距与焦距 → 求清晰像距 → 传感器对准像面。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| f | 焦距 |
| zo | 物距 |
| zi | 像距 |
| m | 放大率绝对值 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
\frac1f=\frac1{z_o}+\frac1{z_i},\qquad m=\frac{z_i}{z_o}\ \text{（大小）}
$$

### 🔧 手算 7：把关系落到数字上

f=50 mm、zo=1000 mm，则 zi=50×1000/950≈52.6316 mm，m≈0.05263。代回 1/1000+1/52.6316≈1/50。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 代回 1/1000+1/52.6316≈1/50。 |
| 适用边界 | 远处对焦时 zi≈f，不代表任何距离都可直接把传感器固定在 f 而保持清晰。 |

![几何或数值解释 3](diagrams/d15-lens.png)

*理想薄透镜把同一物点的光线汇聚到像点，图形是几何示意。*

### ⚠️ 易错点：先识别症状与假设

远处对焦时 zi≈f，不代表任何距离都可直接把传感器固定在 f 而保持清晰。

### 停下来解释一次

**问题：物体移近透镜但仍在焦外，传感器清晰像面怎样移动？**

<details>
<summary>展开参考回答</summary>

像距增大，需要把传感器或等效成像组件调整到更远的像面。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Optics of Lenses

*PDF p65 · 对应本节：薄透镜如何把一个物平面变清晰？*

![PDF p65：Optics of Lenses](images/p065.png)

#### First: Thin Lens Approximation

*PDF p68 · 对应本节：薄透镜如何把一个物平面变清晰？*

![PDF p68：First: Thin Lens Approximation](images/p068.png)

#### Ideal Thin Lens – Focal Point

*PDF p69 · 对应本节：薄透镜如何把一个物平面变清晰？*

![PDF p69：Ideal Thin Lens – Focal Point](images/p069.png)

#### Gauss’ Ray Diagrams

*PDF p70 · 对应本节：薄透镜如何把一个物平面变清晰？*

![PDF p70：Gauss’ Ray Diagrams](images/p070.png)

#### Gauss’ Ray Tracing Construction

*PDF p71 · 对应本节：薄透镜如何把一个物平面变清晰？*

![PDF p71：Gauss’ Ray Tracing Construction](images/p071.png)

#### Gauss’ Ray Tracing Construction

*PDF p74 · 对应本节：薄透镜如何把一个物平面变清晰？*

![PDF p74：Gauss’ Ray Tracing Construction](images/p074.png)

#### The Thin Lens Equation

*PDF p75 · 对应本节：薄透镜如何把一个物平面变清晰？*

![PDF p75：The Thin Lens Equation](images/p075.png)

#### Magnification

*PDF p76 · 对应本节：薄透镜如何把一个物平面变清晰？*

![PDF p76：Magnification](images/p076.png)

#### Magnification Example – Focus at Infinity

*PDF p77 · 对应本节：薄透镜如何把一个物平面变清晰？*

![PDF p77：Magnification Example – Focus at Infinity](images/p077.png)

#### Magnification Example – Focus at 1:1 Macro

*PDF p78 · 对应本节：薄透镜如何把一个物平面变清晰？*

![PDF p78：Magnification Example – Focus at 1:1 Macro](images/p078.png)

</details>

## 8. 离焦为什么形成圆而不是一个点？

光束本应在 zi 汇聚，但传感器位于 zs，截到了还未汇聚或已经发散的光锥。由相似三角形，弥散圆直径与孔径直径以及像面偏差成正比。

光斑形状也会受光圈形状和像差影响，所谓 bokeh 不是简单的统一高斯模糊。离焦尺度随物距变化，前景和背景也有遮挡关系。

![概念关系：离焦为什么形成圆而不是一个点？](diagrams/d08-relation.png)

*读图：光锥汇聚点 → 传感器偏离 → 有限弥散圆。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| C | 弥散圆直径 |
| D | 孔径直径 |
| zs | 实际传感器位置 |
| zi | 该物点清晰像距 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
C=D\frac{\lvert z_s-z_i\rvert}{z_i}
$$

### 🔧 手算 8：把关系落到数字上

D=10 mm、zi=50 mm、zs=51 mm，C=0.2 mm。孔径缩为 5 mm，C=0.1 mm；回乘 C zi/D 得像面误差 1 mm。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 孔径缩为 5 mm，C=0.1 mm；回乘 C zi/D 得像面误差 1 mm。 |
| 适用边界 | 对焦平面与焦平面在口语中易混用，本文用清晰物平面和清晰像面区分。 |

![几何或数值解释 4](diagrams/d16-coc.png)

*紫色传感器面偏离清晰像点，光束截面产生有限离焦光斑。*

### ⚠️ 易错点：先识别症状与假设

对焦平面与焦平面在口语中易混用，本文用清晰物平面和清晰像面区分。

### 停下来解释一次

**问题：收小光圈为什么常能扩大景深？**

<details>
<summary>展开参考回答</summary>

同一像面误差下光斑变小，更多物距落在允许清晰阈值内。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Defocus Blur

*PDF p80 · 对应本节：离焦为什么形成圆而不是一个点？*

![PDF p80：Defocus Blur](images/p080.png)

#### Circle of Confusion

*PDF p81 · 对应本节：离焦为什么形成圆而不是一个点？*

![PDF p81：Circle of Confusion](images/p081.png)

#### Circle of Confusion

*PDF p82 · 对应本节：离焦为什么形成圆而不是一个点？*

![PDF p82：Circle of Confusion](images/p082.png)

#### Circle of Confusion

*PDF p83 · 对应本节：离焦为什么形成圆而不是一个点？*

![PDF p83：Circle of Confusion](images/p083.png)

#### Circle of Confusion

*PDF p84 · 对应本节：离焦为什么形成圆而不是一个点？*

![PDF p84：Circle of Confusion](images/p084.png)

#### Computing Circle of Confusion Diameter (C)

*PDF p85 · 对应本节：离焦为什么形成圆而不是一个点？*

![PDF p85：Computing Circle of Confusion Diameter (C)](images/p085.png)

#### Circle of Confusion – Example

*PDF p86 · 对应本节：离焦为什么形成圆而不是一个点？*

![PDF p86：Circle of Confusion – Example](images/p086.png)

#### Size of Circle of Confusion is Inversely Proportional to F-Number for Photo

*PDF p87 · 对应本节：离焦为什么形成圆而不是一个点？*

![PDF p87：Size of Circle of Confusion is Inversely Proportional to F-Number for Photo](images/p087.png)

</details>

## 9. 景深为何依赖观看条件？

严格几何成像只在一个物平面完全聚焦，景深则把光斑小于阈值的范围称为“可接受清晰”。阈值依赖显示尺寸、观看距离、像素大小与质量目标。

因此景深不是只由镜头型号决定。宏观摄影与远距离风景的景深分布不同，过度收光圈还会涉及衍射，薄透镜几何模型不能覆盖所有限制。

![概念关系：景深为何依赖观看条件？](diagrams/d09-relation.png)

*读图：离焦光斑 → 最终显示尺度 → 可接受景深范围。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| C | 传感器上的光斑直径 |
| 阈值 | 与最终观看条件相联系 |
| 判断 | 连续误差被划分为可接受区间 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
C\le C_{acceptable}
$$

### 🔧 手算 9：把关系落到数字上

像素间距 0.005 mm，C=0.01 mm 对应 2 像素；若图像缩小四倍显示，光斑约半个输出像素。光学没变，呈现阈值改变了。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 光学没变，呈现阈值改变了。 |
| 适用边界 | 不要把课件给出的某个弥散圆数值当成所有传感器与输出尺寸的固定标准。 |

![几何或数值解释 8](diagrams/d20-backtrace.png)

*弥散圆、像素间距和最终像素数通过除法联系，不以柱高比较不同单位。*

### ⚠️ 易错点：先识别症状与假设

不要把课件给出的某个弥散圆数值当成所有传感器与输出尺寸的固定标准。

### 停下来解释一次

**问题：为什么手机小图看着全清晰，放大后背景又糊？**

<details>
<summary>展开参考回答</summary>

最终观看尺度改变了可辨认的光斑大小。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Exposure Tradeoffs

*PDF p88 · 对应本节：景深为何依赖观看条件？*

![PDF p88：Exposure Tradeoffs](images/p088.png)

#### f / 4

*PDF p89 · 对应本节：景深为何依赖观看条件？*

![PDF p89：f / 4](images/p089.png)

#### Shallow Depth of Field Can Create a Stronger Image

*PDF p90 · 对应本节：景深为何依赖观看条件？*

![PDF p90：Shallow Depth of Field Can Create a Stronger Image](images/p090.png)

#### Depth of Field

*PDF p93 · 对应本节：景深为何依赖观看条件？*

![PDF p93：Depth of Field](images/p093.png)

#### Depth of Field (DOF)

*PDF p94 · 对应本节：景深为何依赖观看条件？*

![PDF p94：Depth of Field (DOF)](images/p094.png)

#### Circle of Confusion for Depth of Field

*PDF p95 · 对应本节：景深为何依赖观看条件？*

![PDF p95：Circle of Confusion for Depth of Field](images/p095.png)

#### Depth of Field

*PDF p96 · 对应本节：景深为何依赖观看条件？*

![PDF p96：Depth of Field](images/p096.png)

#### Other Focus / DOF Situations to Consider

*PDF p97 · 对应本节：景深为何依赖观看条件？*

![PDF p97：Other Focus / DOF Situations to Consider](images/p097.png)

</details>

## 10. 渲染景深要怎样生成光线？

先从像素构造理想针孔方向，与指定清晰物平面求交得到目标点；再在孔径上抽样一个起点，让光线指向同一目标。焦平面上的点因此对所有孔径样本对齐，其他深度则散开。

孔径圆盘必须按面积均匀采样，正好用到 Monte Carlo 的平方根半径映射。相机模型若需要物理曝光，还要考虑采样权重，不能仅凭模糊外观宣称能量正确。

![概念关系：渲染景深要怎样生成光线？](diagrams/d10-relation.png)

*读图：像素对应焦平面点 → 随机孔径起点 → 共同指向焦平面。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| R | 孔径半径 |
| pf | 清晰物平面目标 |
| xi | 独立均匀随机数 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
o_{lens}=(R\sqrt{\xi_1}\cos2\pi\xi_2,R\sqrt{\xi_1}\sin2\pi\xi_2,0),\quad d=\frac{p_f-o_{lens}}{\|p_f-o_{lens}\|}
$$

### 🔧 手算 10：把关系落到数字上

R=1、ξ1=1/4、ξ2=0，孔径点为 (0.5,0,0)。目标 (0,0,5)，未归一化方向 (-0.5,0,5)，走到 z=5 恰到目标。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 目标 (0,0,5)，未归一化方向 (-0.5,0,5)，走到 z=5 恰到目标。 |
| 适用边界 | 把所有光线仍从针孔发出，仅改变方向，无法正确模拟有限孔径视差。 |

![几何或数值解释 5](diagrams/d17-disk.png)

*薄透镜相机的圆孔径采样需使用平方根半径映射。*

### ⚠️ 易错点：先识别症状与假设

把所有光线仍从针孔发出，仅改变方向，无法正确模拟有限孔径视差。

### 停下来解释一次

**问题：为什么焦平面上的内容不会随孔径样本变糊？**

<details>
<summary>展开参考回答</summary>

因为所有该像素的孔径光线都被构造为经过同一个焦平面目标。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Ray Tracing Ideal Thin Lenses

*PDF p100 · 对应本节：渲染景深要怎样生成光线？*

![PDF p100：Ray Tracing Ideal Thin Lenses](images/p100.png)

#### Example of Rendering with Lens Focus

*PDF p101 · 对应本节：渲染景深要怎样生成光线？*

![PDF p101：Example of Rendering with Lens Focus](images/p101.png)

#### Example of Rendering with Lens Focus

*PDF p103 · 对应本节：渲染景深要怎样生成光线？*

![PDF p103：Example of Rendering with Lens Focus](images/p103.png)

#### Ray Tracing for Defocus Blur (Thin Lens)

*PDF p104 · 对应本节：渲染景深要怎样生成光线？*

![PDF p104：Ray Tracing for Defocus Blur (Thin Lens)](images/p104.png)

#### Ray Tracing for Defocus Blur (Thin Lens)

*PDF p105 · 对应本节：渲染景深要怎样生成光线？*

![PDF p105：Ray Tracing for Defocus Blur (Thin Lens)](images/p105.png)

#### Example of Rendering with Lens Focus

*PDF p106 · 对应本节：渲染景深要怎样生成光线？*

![PDF p106：Example of Rendering with Lens Focus](images/p106.png)

#### Bokeh

*PDF p107 · 对应本节：渲染景深要怎样生成光线？*

![PDF p107：Bokeh](images/p107.png)

#### Bokeh

*PDF p108 · 对应本节：渲染景深要怎样生成光线？*

![PDF p108：Bokeh](images/p108.png)

#### Bokeh

*PDF p110 · 对应本节：渲染景深要怎样生成光线？*

![PDF p110：Bokeh](images/p110.png)

</details>

## 11. 真实镜头为何比薄透镜复杂？

真实镜头有多片曲面、不同折射率与孔径，需逐面求交和折射。像差、渐晕、透射损耗与视场相关光量都超出理想薄透镜的单一平面模型。

课件给出的 cos⁴ 因子来自特定几何近似下的传感器照度推导，不是所有真实镜头通用的唯一渐晕规律。使用模型时要保留假设。

![概念关系：真实镜头为何比薄透镜复杂？](diagrams/d11-relation.png)

*读图：逐面求交折射 → 孔径与遮挡 → 传感器辐射积分。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| A | 后镜面或等效孔径采样区域 |
| 两余弦 | 两端面积投影 |
| r | 连接距离 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
E(x')=\int_A L(x''\to x')\frac{\cos\theta'\cos\theta''}{r^2}\,dA''
$$

### 🔧 手算 11：把关系落到数字上

教学小面元 L=2、面积 0.01、两余弦均 0.5、距离 0.1，贡献近似 2×0.01×0.25/0.01=0.5。单位应为 W/m²。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 单位应为 W/m²。 |
| 适用边界 | 真实镜头采样 PDF、遮挡和透射率不能省略，否则曝光随镜头参数异常变化。 |

### ⚠️ 易错点：先识别症状与假设

真实镜头采样 PDF、遮挡和透射率不能省略，否则曝光随镜头参数异常变化。

### 停下来解释一次

**问题：只让光线几何正确通过镜头，就一定曝光正确吗？**

<details>
<summary>展开参考回答</summary>

不。还需正确的光通量权重、采样 PDF 与透射模型。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Real Compound Lenses

*PDF p111 · 对应本节：真实镜头为何比薄透镜复杂？*

![PDF p111：Real Compound Lenses](images/p111.png)

#### Modern Lens Designs Are Highly Complex

*PDF p112 · 对应本节：真实镜头为何比薄透镜复杂？*

![PDF p112：Modern Lens Designs Are Highly Complex](images/p112.png)

#### Modern Lens Designs Are Highly Complex

*PDF p114 · 对应本节：真实镜头为何比薄透镜复杂？*

![PDF p114：Modern Lens Designs Are Highly Complex](images/p114.png)

#### Recall: Snell’s Law of Refraction

*PDF p116 · 对应本节：真实镜头为何比薄透镜复杂？*

![PDF p116：Recall: Snell’s Law of Refraction](images/p116.png)

#### Real Refraction Through A Lens Is Not Ideal – Aberrations

*PDF p117 · 对应本节：真实镜头为何比薄透镜复杂？*

![PDF p117：Real Refraction Through A Lens Is Not Ideal – Aberrations](images/p117.png)

#### Real Lenses vs Ideal Thin Lenses

*PDF p118 · 对应本节：真实镜头为何比薄透镜复杂？*

![PDF p118：Real Lenses vs Ideal Thin Lenses](images/p118.png)

#### Example Lens Formula: Double Gauss

*PDF p119 · 对应本节：真实镜头为何比薄透镜复杂？*

![PDF p119：Example Lens Formula: Double Gauss](images/p119.png)

#### Ray Tracing Through Real Lens Designs

*PDF p120 · 对应本节：真实镜头为何比薄透镜复杂？*

![PDF p120：Ray Tracing Through Real Lens Designs](images/p120.png)

#### Ray Tracing Real Lens Designs

*PDF p123 · 对应本节：真实镜头为何比薄透镜复杂？*

![PDF p123：Ray Tracing Real Lens Designs](images/p123.png)

#### Radiometry for Tracing Lens Designs

*PDF p124 · 对应本节：真实镜头为何比薄透镜复杂？*

![PDF p124：Radiometry for Tracing Lens Designs](images/p124.png)

</details>

## 12. 自动对焦与学习实验如何连接？

对比度对焦通过搜索清晰度峰值决定调整方向与位置，相位对焦利用不同孔径区域的成像偏移提供离焦信息。它们是在估计当前设置距离清晰状态有多远。

建议自学实验固定相机与场景，分别只改孔径、焦平面、快门和焦距，每次保留对照。输出清晰度或光斑大小比仅说“背景更虚”更容易复核。

![概念关系：自动对焦与学习实验如何连接？](diagrams/d12-relation.png)

*读图：测量离焦迹象 → 调整镜头设置 → 验证清晰平面。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| I | 图像 |
| 梯度 | 局部对比变化 |
| 限制 | 噪声也可能增大这个指标 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
\mathrm{sharpness}\propto\sum_{x,y}\|\nabla I(x,y)\|^2\quad\text{（教学简化）}
$$

### 🔧 手算 12：把关系落到数字上

一维差分为 (1,2,1) 时平方和 6，模糊后若变成 (1,1,1) 则为 3。加噪也可提高平方和，所以不能只凭此断言更清晰。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 加噪也可提高平方和，所以不能只凭此断言更清晰。 |
| 适用边界 | 自动对焦失败可能来自低纹理、运动或噪声，不一定是薄透镜公式错误。 |

### ⚠️ 易错点：先识别症状与假设

自动对焦失败可能来自低纹理、运动或噪声，不一定是薄透镜公式错误。

### 停下来解释一次

**问题：同亮度、同构图、同景深的两张照片还可能不同吗？**

<details>
<summary>展开参考回答</summary>

可能。噪声、运动模糊、像差、色彩响应和处理链仍可不同。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Things to Remember

*PDF p125 · 对应本节：自动对焦与学习实验如何连接？*

![PDF p125：Things to Remember](images/p125.png)

#### Auto Focus

*PDF p128 · 对应本节：自动对焦与学习实验如何连接？*

![PDF p128：Auto Focus](images/p128.png)

#### Contrast Detection Autofocus

*PDF p129 · 对应本节：自动对焦与学习实验如何连接？*

![PDF p129：Contrast Detection Autofocus](images/p129.png)

#### Phase Detection Autofocus

*PDF p130 · 对应本节：自动对焦与学习实验如何连接？*

![PDF p130：Phase Detection Autofocus](images/p130.png)

#### Phase Detection AF Used in DSLRs

*PDF p131 · 对应本节：自动对焦与学习实验如何连接？*

![PDF p131：Phase Detection AF Used in DSLRs](images/p131.png)

#### Phase Detection Pixels Embedded in Sensor

*PDF p132 · 对应本节：自动对焦与学习实验如何连接？*

![PDF p132：Phase Detection Pixels Embedded in Sensor](images/p132.png)

</details>

## 13. 把十二个数值例子连成检查顺序

先手算再运行。随仓库提供的 `scripts/cs184-numerical-checks.py` 是小模型验证，不依赖 GPU，也不修改服务器配置。它不能替代完整渲染场景或模拟系统的验证。

| 顺序 | 本节关系 | 最容易漏掉的约定 |
| --- | --- | --- |
| 1 | 相机为什么不只是一个投影矩阵？ | 时间：快门开放区间 |
| 2 | 焦距与传感器怎样共同决定视场？ | 假设：针孔或远距离薄透镜近似 |
| 3 | 透视压缩究竟由什么造成？ | 条件：针孔近似 |
| 4 | 曝光档位为何是对数？ | 条件：其他光学因素固定 |
| 5 | ISO 为什么不能替代进光量？ | 未含：读出噪声与饱和 |
| 6 | 快门怎样连接到运动模糊与滚动畸变？ | 条件：匀速且无遮挡 |
| 7 | 薄透镜如何把一个物平面变清晰？ | m：放大率绝对值 |
| 8 | 离焦为什么形成圆而不是一个点？ | zi：该物点清晰像距 |
| 9 | 景深为何依赖观看条件？ | 判断：连续误差被划分为可接受区间 |
| 10 | 渲染景深要怎样生成光线？ | xi：独立均匀随机数 |
| 11 | 真实镜头为何比薄透镜复杂？ | r：连接距离 |
| 12 | 自动对焦与学习实验如何连接？ | 限制：噪声也可能增大这个指标 |

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
| 相机为什么不只是一个投影矩阵？ | ISO 增益不是镜头多收到了光子；区分采集光量与信号放大。 |
| 焦距与传感器怎样共同决定视场？ | 不要把水平宽度代入公式后去对照课件的对角视场。 |
| 透视压缩究竟由什么造成？ | “长焦改变透视”常省略了摄影师后退的条件；先问相机中心是否移动。 |
| 曝光档位为何是对数？ | f/2 到 f/4 是两档而不是一档，因为面积变化四倍。 |

### 阶段 2：第 5–8 节

| 涉及关系 | 错误机制 / 修正方向 |
| --- | --- |
| ISO 为什么不能替代进光量？ | 不要把增益后的像素值当作真实采光量；还需考虑黑电平与饱和。 |
| 快门怎样连接到运动模糊与滚动畸变？ | 短快门不自动消除滚动快门形变；这两种时间效应来源不同。 |
| 薄透镜如何把一个物平面变清晰？ | 远处对焦时 zi≈f，不代表任何距离都可直接把传感器固定在 f 而保持清晰。 |
| 离焦为什么形成圆而不是一个点？ | 对焦平面与焦平面在口语中易混用，本文用清晰物平面和清晰像面区分。 |

### 阶段 3：第 9–12 节

| 涉及关系 | 错误机制 / 修正方向 |
| --- | --- |
| 景深为何依赖观看条件？ | 不要把课件给出的某个弥散圆数值当成所有传感器与输出尺寸的固定标准。 |
| 渲染景深要怎样生成光线？ | 把所有光线仍从针孔发出，仅改变方向，无法正确模拟有限孔径视差。 |
| 真实镜头为何比薄透镜复杂？ | 真实镜头采样 PDF、遮挡和透射率不能省略，否则曝光随镜头参数异常变化。 |
| 自动对焦与学习实验如何连接？ | 自动对焦失败可能来自低纹理、运动或噪声，不一定是薄透镜公式错误。 |

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

### 自测 1. 两个相机投影相同，照片一定完全一样吗？

<details>
<summary>参考答案</summary>

不。孔径、曝光、传感器响应、噪声和图像处理都可能不同。

</details>

### 自测 2. 焦距不变，把传感器宽度减半会怎样？

<details>
<summary>参考答案</summary>

水平视场变窄；角度不是一般地精确减半，因为还有 arctan 非线性。

</details>

### 自测 3. 原地变焦后裁到相同画面，透视会不同吗？

<details>
<summary>参考答案</summary>

理想投影下不会，透视由观察位置决定；实际镜头像差等可能另外影响图像。

</details>

### 自测 4. 快门加倍且 f-number 乘 √2，曝光怎样变化？

<details>
<summary>参考答案</summary>

时间增光两倍、面积减半，理想条件下相互抵消。

</details>

### 自测 5. 提高 ISO 后照片变亮，是否证明信噪比必然提高？

<details>
<summary>参考答案</summary>

不能。增益、读出链路与曝光设置共同影响结果，需要具体测量。

</details>

### 自测 6. 全局快门是否就不会有运动模糊？

<details>
<summary>参考答案</summary>

仍会。它让各行曝光时刻一致，但曝光本身仍有有限时长。

</details>

### 自测 7. 物体移近透镜但仍在焦外，传感器清晰像面怎样移动？

<details>
<summary>参考答案</summary>

像距增大，需要把传感器或等效成像组件调整到更远的像面。

</details>

### 自测 8. 收小光圈为什么常能扩大景深？

<details>
<summary>参考答案</summary>

同一像面误差下光斑变小，更多物距落在允许清晰阈值内。

</details>

### 自测 9. 为什么手机小图看着全清晰，放大后背景又糊？

<details>
<summary>参考答案</summary>

最终观看尺度改变了可辨认的光斑大小。

</details>

### 自测 10. 为什么焦平面上的内容不会随孔径样本变糊？

<details>
<summary>参考答案</summary>

因为所有该像素的孔径光线都被构造为经过同一个焦平面目标。

</details>

### 自测 11. 只让光线几何正确通过镜头，就一定曝光正确吗？

<details>
<summary>参考答案</summary>

不。还需正确的光通量权重、采样 PDF 与透射模型。

</details>

### 自测 12. 同亮度、同构图、同景深的两张照片还可能不同吗？

<details>
<summary>参考答案</summary>

可能。噪声、运动模糊、像差、色彩响应和处理链仍可不同。

</details>

### 自测 13. 第 1 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

ISO 增益不是镜头多收到了光子；区分采集光量与信号放大。

再复算本节的例子：恒定 E=2 W/m²、曝光 0.01 秒，H=0.02 J/m²。曝光翻倍为 0.02 秒，H=0.04；回除时间仍得 E=2。

</details>

### 自测 14. 第 2 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

不要把水平宽度代入公式后去对照课件的对角视场。

再复算本节的例子：w=36 mm、f=50 mm，水平 FOV≈39.60°；对角尺寸约 43.27 mm，得到约 46.79°。两个结果对应不同方向。

</details>

### 自测 15. 第 3 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

“长焦改变透视”常省略了摄影师后退的条件；先问相机中心是否移动。

再复算本节的例子：主体 H=1、Z=5、f=0.05，像高 0.01。后退到 Z=10 并把 f 改成 0.1，主体仍为 0.01；原来更远的背景距离变化比例却不同。

</details>

### 自测 16. 第 4 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

f/2 到 f/4 是两档而不是一档，因为面积变化四倍。

再复算本节的例子：50 mm 镜头 f/2 的孔径直径 25 mm，f/4 为 12.5 mm，面积降为 1/4。要保持曝光，1/200 秒需改为 1/50 秒。

</details>

### 自测 17. 第 5 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

不要把增益后的像素值当作真实采光量；还需考虑黑电平与饱和。

再复算本节的例子：Np=100 时 SNR≈10；Np=400 时≈20。把前者信号和噪声同时乘 4，SNR 仍是 10，不会变成 40。

</details>

### 自测 18. 第 6 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

短快门不自动消除滚动快门形变；这两种时间效应来源不同。

再复算本节的例子：v=200 px/s、曝光 0.005 秒，模糊约 1 px。若上下行时间差 0.02 秒，物体跨行位置差仍可达 4 px。

</details>

### 自测 19. 第 7 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

远处对焦时 zi≈f，不代表任何距离都可直接把传感器固定在 f 而保持清晰。

再复算本节的例子：f=50 mm、zo=1000 mm，则 zi=50×1000/950≈52.6316 mm，m≈0.05263。代回 1/1000+1/52.6316≈1/50。

</details>

### 自测 20. 第 8 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

对焦平面与焦平面在口语中易混用，本文用清晰物平面和清晰像面区分。

再复算本节的例子：D=10 mm、zi=50 mm、zs=51 mm，C=0.2 mm。孔径缩为 5 mm，C=0.1 mm；回乘 C zi/D 得像面误差 1 mm。

</details>

### 自测 21. 第 9 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

不要把课件给出的某个弥散圆数值当成所有传感器与输出尺寸的固定标准。

再复算本节的例子：像素间距 0.005 mm，C=0.01 mm 对应 2 像素；若图像缩小四倍显示，光斑约半个输出像素。光学没变，呈现阈值改变了。

</details>

### 自测 22. 第 10 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

把所有光线仍从针孔发出，仅改变方向，无法正确模拟有限孔径视差。

再复算本节的例子：R=1、ξ1=1/4、ξ2=0，孔径点为 (0.5,0,0)。目标 (0,0,5)，未归一化方向 (-0.5,0,5)，走到 z=5 恰到目标。

</details>

### 自测 23. 第 11 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

真实镜头采样 PDF、遮挡和透射率不能省略，否则曝光随镜头参数异常变化。

再复算本节的例子：教学小面元 L=2、面积 0.01、两余弦均 0.5、距离 0.1，贡献近似 2×0.01×0.25/0.01=0.5。单位应为 W/m²。

</details>

### 自测 24. 第 12 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

自动对焦失败可能来自低纹理、运动或噪声，不一定是薄透镜公式错误。

再复算本节的例子：一维差分为 (1,2,1) 时平方和 6，模糊后若变成 (1,1,1) 则为 3。加噪也可提高平方和，所以不能只凭此断言更清晰。

</details>

### 自测 25. 本讲的输入、输出和中间表示各是什么？

<details>
<summary>参考答案</summary>

视场与透视 → 光圈快门与曝光 → 薄透镜对焦 → 离焦形成光斑 → 孔径采样 → 真实镜头与传感器。请沿箭头逐项解释，尤其说清中间表示的单位、坐标或概率测度；只复述名词不算掌握。

</details>

### 自测 26. 能否只用一张“看起来正确”的图片证明实现正确？

<details>
<summary>参考答案</summary>

不能。需要将关键关系拆成可预测的小输入，检查数值、边界与对照；随机方法还要区分一次结果与统计期望，显示图还需区分编码与原始数据。

</details>

## 17. 带走的结论与仍需练习的内容

- 不。孔径、曝光、传感器响应、噪声和图像处理都可能不同。
- 水平视场变窄；角度不是一般地精确减半，因为还有 arctan 非线性。
- 理想投影下不会，透视由观察位置决定；实际镜头像差等可能另外影响图像。
- 时间增光两倍、面积减半，理想条件下相互抵消。
- 不能。增益、读出链路与曝光设置共同影响结果，需要具体测量。
- 仍会。它让各行曝光时刻一致，但曝光本身仍有有限时长。
- 像距增大，需要把传感器或等效成像组件调整到更远的像面。
- 同一像面误差下光斑变小，更多物距落在允许清晰阈值内。
- 最终观看尺度改变了可辨认的光斑大小。
- 因为所有该像素的孔径光线都被构造为经过同一个焦平面目标。
- 不。还需正确的光通量权重、采样 PDF 与透射模型。
- 可能。噪声、运动模糊、像差、色彩响应和处理链仍可不同。

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

[原课件文件与版本记录](https://github.com/Teddy-Yangjiale/CS184/blob/main/CS184_2026/su26/lectures/SU26-L16-17-cameras-lenses.pdf) · [课程官网](https://cs184.eecs.berkeley.edu/su26/)

文件：`SU26-L16-17-cameras-lenses.pdf`；PDF 页数：132；SHA-256：`dfe1948ec660c4fb297f0ff38ab76d6372e16f5ff49e01b310e0ee4fbb959cf6`。

“正文核对”表示本篇实际引用该页截图；“索引保留”包括演示、行政信息、补充、致谢与重复构建页，不表示逐页都有独立讲解。原视频的运动过程不能由静态 PDF 截图完整复现。

| PDF 页 | 原页可提取标题 | 本篇使用 |
| --- | --- | --- |
| 1 | Computer Graphics and Imaging | 索引保留 |
| 2 | Rendering with Realistic Camera Model | 索引保留 |
| 3 | Rendering with Realistic Camera Model | 索引保留 |
| 4 | Image Capture Overview | 正文核对 |
| 5 | What’s Happening Inside the Camera? | 正文核对 |
| 6 | Pinholes & Lenses Form Image on Sensor | 正文核对 |
| 7 | Shutter Exposes Sensor For Precise Duration | 正文核对 |
| 8 | Sensor Accumulates Irradiance During Exposure | 正文核对 |
| 9 | Image Processing: From Sensor Values to Image | 正文核对 |
| 10 | Optics of Image Formation: | 正文核对 |
| 11 | Effect of Focal Length on FOV | 正文核对 |
| 12 | Effect of Sensor Size on FOV | 正文核对 |
| 13 | Sensor Sizes | 正文核对 |
| 14 | Maintain FOV on Smaller Sensor? | 正文核对 |
| 15 | Focal Length v. Field of View | 正文核对 |
| 16 | Focal Length v. Field of View | 索引保留 |
| 17 | Focal Length v. Field of View | 索引保留 |
| 18 | Focal Length v. Field of View | 正文核对 |
| 19 | Focal Length v. Field of View | 索引保留 |
| 20 | Wide angle: 15mm, f/2.8 | 索引保留 |
| 21 | Wide angle: 18mm, 1/750, f/8 | 索引保留 |
| 22 | Normal: 50mm, 1/80, f/1.4 | 索引保留 |
| 23 | Normal: 64mm, 1/3200, f/2.8 | 索引保留 |
| 24 | Telephoto: 150mm, 1/640, f/1.8 | 索引保留 |
| 25 | Telephoto: 200mm, 1/200, f/2.8 | 索引保留 |
| 26 | Telephoto: 420mm, 1/1600, f/4 | 索引保留 |
| 27 | Telephoto: 420mm, 1.0s, f/4 | 索引保留 |
| 28 | Perspective Composition | 正文核对 |
| 29 | Perspective Composition – Camera Position / Focal Length | 正文核对 |
| 30 | Perspective Composition – Camera Position / Focal Length | 正文核对 |
| 31 | Perspective Composition – Camera Position / Focal Length | 正文核对 |
| 32 | Perspective Composition – Camera Position / Focal Length | 索引保留 |
| 33 | Perspective Composition – Camera Position / Focal Length | 索引保留 |
| 34 | Perspective Composition – Camera Position / Focal Length | 正文核对 |
| 35 | Perspective Composition | 正文核对 |
| 36 | Perspective Composition | 索引保留 |
| 37 | Improve Your Own Photography | 索引保留 |
| 38 | Dolly-Zoom Cinema Technique – a.k.a. “Vertigo Effect” | 正文核对 |
| 39 | A Photographer’s Mindset | 正文核对 |
| 40 | Exposure | 正文核对 |
| 41 | Exposure Levels - “Stops” are Logarithmic | 正文核对 |
| 42 | Exposure | 正文核对 |
| 43 | Exposure Controls: Aperture, Shutter, Gain (ISO) | 正文核对 |
| 44 | Gain (ISO) — Noise Increases | 正文核对 |
| 45 | ISO (Gain) | 正文核对 |
| 46 | Many Ways to Achieve the Same Exposure | 正文核对 |
| 47 | Definition: F-Number of a Lens | 正文核对 |
| 48 | Example F-Number Calculations | 正文核对 |
| 49 | Lens’s F-Number vs F-Number for Photo | 索引保留 |
| 50 | Physical Shutter (1/25 Sec Exposure) | 正文核对 |
| 51 | Main Side Effect of Shutter Speed | 正文核对 |
| 52 | Main Side Effect of Shutter Speed | 索引保留 |
| 53 | Electronic Shutter | 正文核对 |
| 54 | Electronic Rolling Shutter | 正文核对 |
| 55 | Electronic Rolling Shutter | 正文核对 |
| 56 | Electronic Rolling Shutter | 索引保留 |
| 57 | Exposure Controls: Aperture, Shutter, Gain (ISO) | 索引保留 |
| 58 | Physical Shutter (Fast Exposures) | 正文核对 |
| 59 | Exposure Duration: | 索引保留 |
| 60 | High-Speed Photography (Short Shutter) | 正文核对 |
| 61 | High-Speed Photography (Short Shutter) | 索引保留 |
| 62 | Long-Exposure Photography | 正文核对 |
| 63 | Long-Exposure Photography | 索引保留 |
| 64 | Long-Exposure Photography | 正文核对 |
| 65 | Optics of Lenses | 正文核对 |
| 66 | Real Lens Designs Are Highly Complex | 索引保留 |
| 67 | Real Lens Elements Are Not Ideal – Aberrations | 索引保留 |
| 68 | First: Thin Lens Approximation | 正文核对 |
| 69 | Ideal Thin Lens – Focal Point | 正文核对 |
| 70 | Gauss’ Ray Diagrams | 正文核对 |
| 71 | Gauss’ Ray Tracing Construction | 正文核对 |
| 72 | Gauss’ Ray Tracing Construction | 索引保留 |
| 73 | Gauss’ Ray Tracing Construction | 索引保留 |
| 74 | Gauss’ Ray Tracing Construction | 正文核对 |
| 75 | The Thin Lens Equation | 正文核对 |
| 76 | Magnification | 正文核对 |
| 77 | Magnification Example – Focus at Infinity | 正文核对 |
| 78 | Magnification Example – Focus at 1:1 Macro | 正文核对 |
| 79 | Thin Lens Effects — Observations in 3D | 索引保留 |
| 80 | Defocus Blur | 正文核对 |
| 81 | Circle of Confusion | 正文核对 |
| 82 | Circle of Confusion | 正文核对 |
| 83 | Circle of Confusion | 正文核对 |
| 84 | Circle of Confusion | 正文核对 |
| 85 | Computing Circle of Confusion Diameter (C) | 正文核对 |
| 86 | Circle of Confusion – Example | 正文核对 |
| 87 | Size of Circle of Confusion is Inversely Proportional to F-Number for Photo | 正文核对 |
| 88 | Exposure Tradeoffs | 正文核对 |
| 89 | f / 4 | 正文核对 |
| 90 | Shallow Depth of Field Can Create a Stronger Image | 正文核对 |
| 91 | Motion Blur Can Help Tell The Story | 索引保留 |
| 92 | Attendance Time | 索引保留 |
| 93 | Depth of Field | 正文核对 |
| 94 | Depth of Field (DOF) | 正文核对 |
| 95 | Circle of Confusion for Depth of Field | 正文核对 |
| 96 | Depth of Field | 正文核对 |
| 97 | Other Focus / DOF Situations to Consider | 正文核对 |
| 98 | View Camera, Scheimpflug Rule | 索引保留 |
| 99 | View Camera, Scheimpflug Rule | 索引保留 |
| 100 | Ray Tracing Ideal Thin Lenses | 正文核对 |
| 101 | Example of Rendering with Lens Focus | 正文核对 |
| 102 | Example of Rendering with Lens Focus | 索引保留 |
| 103 | Example of Rendering with Lens Focus | 正文核对 |
| 104 | Ray Tracing for Defocus Blur (Thin Lens) | 正文核对 |
| 105 | Ray Tracing for Defocus Blur (Thin Lens) | 正文核对 |
| 106 | Example of Rendering with Lens Focus | 正文核对 |
| 107 | Bokeh | 正文核对 |
| 108 | Bokeh | 正文核对 |
| 109 | Bokeh | 索引保留 |
| 110 | Bokeh | 正文核对 |
| 111 | Real Compound Lenses | 正文核对 |
| 112 | Modern Lens Designs Are Highly Complex | 正文核对 |
| 113 | Modern Lens Designs Are Highly Complex | 索引保留 |
| 114 | Modern Lens Designs Are Highly Complex | 正文核对 |
| 115 | Modern Lens Designs Are Highly Complex | 索引保留 |
| 116 | Recall: Snell’s Law of Refraction | 正文核对 |
| 117 | Real Refraction Through A Lens Is Not Ideal – Aberrations | 正文核对 |
| 118 | Real Lenses vs Ideal Thin Lenses | 正文核对 |
| 119 | Example Lens Formula: Double Gauss | 正文核对 |
| 120 | Ray Tracing Through Real Lens Designs | 正文核对 |
| 121 | Ray Tracing Through Real Lens Designs | 索引保留 |
| 122 | Ray Tracing Through Real Lens Designs | 索引保留 |
| 123 | Ray Tracing Real Lens Designs | 正文核对 |
| 124 | Radiometry for Tracing Lens Designs | 正文核对 |
| 125 | Things to Remember | 正文核对 |
| 126 | Acknowledgments | 索引保留 |
| 127 | Extra | 索引保留 |
| 128 | Auto Focus | 正文核对 |
| 129 | Contrast Detection Autofocus | 正文核对 |
| 130 | Phase Detection Autofocus | 正文核对 |
| 131 | Phase Detection AF Used in DSLRs | 正文核对 |
| 132 | Phase Detection Pixels Embedded in Sensor | 正文核对 |
