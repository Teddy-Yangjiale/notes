---
title: "CS184 第 16–17 讲：全局光照与路径追踪"
date: 2026-11-07
updated: 2026-11-07
summary: "命中表面 → BRDF 连接入射与出射 → 光从别的表面来 → 渲染方程递归 → 随机生成路径 → 加权累积与终止。配 24 张可编辑图解、16 个手算、30 道自测；新增四组逐步推导、可运行故障对照与 PDF 全页索引。"
tags: ["计算机图形学", "CS184", "课程笔记"]
series: "cs184"
order: 16
shortTitle: "第 16–17 讲"
---

> UC Berkeley · CS184/284A · Fall 2026 · 文件标识 `L16-17-global-illumination-path-tracing.pdf`。
> 本文的 **pN 一律是 PDF 的第 N 页**，不是封面讲次或页脚旧编号。文件名与封面可能不同，以下均按文件和页码回查。

## 0. 先抓住这一条推理链

```text
命中表面
    ↓
BRDF 连接入射与出射
    ↓
光从别的表面来
    ↓
渲染方程递归
    ↓
随机生成路径
    ↓
加权累积与终止
```

这篇笔记的阅读顺序是：先理解输入和输出，再确认公式的条件，最后用小数值检查。
正文将课件概念、补充推导和教学例子分开；示意图中的理想几何与数字不冒充真实实验测量。

| 内容 | 本文提供什么 |
|---|---|
| 来源 | Fall 2026，PDF 共 173 页；正文选择 77 张关键页 |
| 图解 | 12 张概念关系图 + 12 张几何或数值图，均有原生可编辑 PPTX |
| 手算 | 16 个教学例子；深入部分展开输入、中间量、回代、反例与代码 |
| 复习 | 30 道自测及答案，末尾保留全页索引 |
| 运行证据 | 数值核对脚本覆盖解析小模型，不代表完整渲染器或模拟器已经实现 |

[下载本篇 24 张可编辑图解（PPTX 与操作 JSON）](/notes/cs184/figures/16-editable.zip)

### 课件与推导的使用边界

课件截图用于对照原始定义与几何；正文用中文解释关系，并提供必要的修正与推导。
后续专题按本地文件的学期和编号组织，不假定它们与秋季一一对应。
若只做第一遍学习，先读每节前两段和数值例子，再展开原页核对。

### 与前面哪一讲接上

先回顾[相关前置讲义](/notes/cs184-15-monte-carlo-integration/)。本篇在已有表示与数学工具上增加新变量或新约束，而不是另起一套互不相关的公式。

## 1. 局部光照遗漏了哪一部分？

第 13 讲解决求交，第 14 讲定义光的量，第 15 讲学习积分。现在把它们拼起来：照到一个表面的光不仅来自灯，还来自其他被照亮的表面。

软阴影来自扩展光源，焦散涉及聚焦的反射折射光路，颜色溢出来自间接反射。它们不是加在图片上的独立滤镜，而是不同光路对同一像素积分的贡献。

![概念关系：局部光照遗漏了哪一部分？](diagrams/d01-relation.png)

*读图：灯光传播 → 表面多次散射 → 相机接收。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| Lo | 出射辐亮度 |
| Le | 表面自身发光 |
| Lr | 反射其他来源的光 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
L_o=L_e+L_r
$$

### 🔧 手算 1：把关系落到数字上

某方向自身发光 2、反射贡献 3，总量 5。关掉自发光后剩 3；检查 5-2=3，不能把发光重复放进反射项。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 关掉自发光后剩 3；检查 5-2=3，不能把发光重复放进反射项。 |
| 适用边界 | 只把环境常数调亮不能等价替代间接照明，因为遮挡、材质颜色与方向关系都丢失了。 |

![几何或数值解释 1](diagrams/d13-path.png)

*橙色虚线是从 A 直接连灯，折线路径则经 B，二者属于不同反弹次数。*

![几何或数值解释 8](diagrams/d20-bars.png)

*发光项和反射项分别累积，不能在不同递归分支重复加入同一项。*

### ⚠️ 易错点：先识别症状与假设

只把环境常数调亮不能等价替代间接照明，因为遮挡、材质颜色与方向关系都丢失了。

### 停下来解释一次

**问题：软阴影本身一定要求多次反弹吗？**

<details>
<summary>展开参考回答</summary>

不。面光源的直接照明就能产生软阴影；全局光照还包括多次散射。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Hard Shadows

*PDF p2 · 对应本节：局部光照遗漏了哪一部分？*

![PDF p2：Hard Shadows](images/p002.png)

#### Image credit: Henrik Wann Jensen

*PDF p3 · 对应本节：局部光照遗漏了哪一部分？*

![PDF p3：Image credit: Henrik Wann Jensen](images/p003.png)

#### Image credit: Henrik Wann Jensen

*PDF p4 · 对应本节：局部光照遗漏了哪一部分？*

![PDF p4：Image credit: Henrik Wann Jensen](images/p004.png)

#### Image credit: Henrik Wann Jensen

*PDF p5 · 对应本节：局部光照遗漏了哪一部分？*

![PDF p5：Image credit: Henrik Wann Jensen](images/p005.png)

#### Visual Richness from Indirect Lighting

*PDF p6 · 对应本节：局部光照遗漏了哪一部分？*

![PDF p6：Visual Richness from Indirect Lighting](images/p006.png)

#### Cornell Box – Photograph vs Rendering

*PDF p9 · 对应本节：局部光照遗漏了哪一部分？*

![PDF p9：Cornell Box – Photograph vs Rendering](images/p009.png)

</details>

## 2. BRDF 究竟把什么变成什么？

BRDF 是微分出射辐亮度对微分入射辐照度的比值，单位 sr⁻¹。它描述特定入射方向对特定出射方向的响应，而不是一个“反射概率”。

对反射率 ρ 的理想漫反射，BRDF=ρ/π。因为出射方向无关，其半球反射功率仍要乘余弦积分，结果刚好是 ρ，满足能量约束。

![概念关系：BRDF 究竟把什么变成什么？](diagrams/d02-relation.png)

*读图：微分入射照度 → 材料散射函数 → 微分出射辐亮度。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| fr | BRDF |
| rho | 反照率 [0,1] |
| omega_i、omega_o | 都指向表面外部 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
f_r=\frac{dL_o}{dE_i},\qquad f_{Lambert}=\frac\rho\pi
$$

### 🔧 手算 2：把关系落到数字上

ρ=0.6、E=10 W/m²，Lo=6/π≈1.910。对出射半球积分 Loπ=6 W/m²，恰为入射的 60%。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 对出射半球积分 Loπ=6 W/m²，恰为入射的 60%。 |
| 适用边界 | BRDF 数值可以超过 1；应检查加权半球积分是否超过 1，而不是逐点截断。 |

### ⚠️ 易错点：先识别症状与假设

BRDF 数值可以超过 1；应检查加权半球积分是否超过 1，而不是逐点截断。

### 停下来解释一次

**问题：镜面与漫反射能否只靠一个 RGB 颜色区分？**

<details>
<summary>展开参考回答</summary>

不能。它们的方向分布根本不同，颜色只是部分参数。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Reflection at a Point

*PDF p20 · 对应本节：BRDF 究竟把什么变成什么？*

![PDF p20：Reflection at a Point](images/p020.png)

#### Definition: The bidirectional reflectance distribution function

*PDF p21 · 对应本节：BRDF 究竟把什么变成什么？*

![PDF p21：Definition: The bidirectional reflectance distribution function](images/p021.png)

#### The Reflection Equation

*PDF p22 · 对应本节：BRDF 究竟把什么变成什么？*

![PDF p22：The Reflection Equation](images/p022.png)

#### Solving the Reflection Equation

*PDF p23 · 对应本节：BRDF 究竟把什么变成什么？*

![PDF p23：Solving the Reflection Equation](images/p023.png)

</details>

## 3. 反射方程怎样变成递归方程？

反射方程积分 Li；而 Li 又等于射线下一交点沿反方向发出的 Lo。把传播关系代回，就得到渲染方程。

假设无参与介质、稳态、非荧光表面，传播段只负责可见性和方向连接。未命中几何时应查询环境光，不能无条件返回黑色；有雾时则需增加体积传输。

![概念关系：反射方程怎样变成递归方程？](diagrams/d03-relation.png)

*读图：当前表面 → 下一可见表面 → 递归查询出射光。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| hit | 最近交点 |
| 负号 | 连接两端方向反转 |
| 无命中 | 用环境辐亮度替代 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
L_o(p,\omega_o)=L_e(p,\omega_o)+\int_{H^2}f_r L_o(\operatorname{hit}(p,\omega_i),-\omega_i)\cos\theta_i\,d\omega_i
$$

### 🔧 手算 3：把关系落到数字上

一维简化反馈 L=1+0.5L，解为 2。代回 1+0.5×2=2；直接光只取 1，会漏掉后续反弹总和 1。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 代回 1+0.5×2=2；直接光只取 1，会漏掉后续反弹总和 1。 |
| 适用边界 | 递归调用如果又把当前点传回，通常是自相交；应检查射线起点、方向与最小 t。 |

### ⚠️ 易错点：先识别症状与假设

递归调用如果又把当前点传回，通常是自相交；应检查射线起点、方向与最小 t。

### 停下来解释一次

**问题：为什么同一条连接光路在两端的方向符号相反？**

<details>
<summary>展开参考回答</summary>

因为每端都采用“从该表面向外”的方向约定。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Again: Reflection Equation

*PDF p29 · 对应本节：反射方程怎样变成递归方程？*

![PDF p29：Again: Reflection Equation](images/p029.png)

#### Challenge: This is Actually A Recursive Equation

*PDF p30 · 对应本节：反射方程怎样变成递归方程？*

![PDF p30：Challenge: This is Actually A Recursive Equation](images/p030.png)

#### Transport Function & Radiance Invariance

*PDF p31 · 对应本节：反射方程怎样变成递归方程？*

![PDF p31：Transport Function & Radiance Invariance](images/p031.png)

#### The Rendering Equation

*PDF p32 · 对应本节：反射方程怎样变成递归方程？*

![PDF p32：The Rendering Equation](images/p032.png)

</details>

## 4. 多次反弹为何能写成级数？

令 K 表示一次空间传播再反射，渲染方程就是 L=Le+KL。不断代入得到 Le、KLe、K²Le 等项，每项对应不同反弹次数。

收敛需要适当的能量耗散或逃逸条件；并非只要写出几何级数就保证所有理想场景收敛。有限最大深度截断了尾项，通常引入偏差。

![概念关系：多次反弹为何能写成级数？](diagrams/d04-relation.png)

*读图：零次发光项 → 逐次反弹项 → 所有光路之和。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| K | 单次光传输算子 |
| K⁰ | 恒等算子 |
| 条件 | 级数收敛 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
L=\sum_{k=0}^{\infty}K^kL_e
$$

### 🔧 手算 4：把关系落到数字上

标量教学例 K=0.5、Le=1，前四项是 1+0.5+0.25+0.125=1.875，尾项 0.125，总和 2。代回几何级数验证。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 代回几何级数验证。 |
| 适用边界 | “一条路径多一次反弹一定更暗”不总成立；应理解整体能量传输的收敛条件，不能逐条比较不同路径。 |

![几何或数值解释 2](diagrams/d14-bars.png)

*标量传输 K=0.5 时，各阶贡献构成收敛级数。*

### ⚠️ 易错点：先识别症状与假设

“一条路径多一次反弹一定更暗”不总成立；应理解整体能量传输的收敛条件，不能逐条比较不同路径。

### 停下来解释一次

**问题：增加最大深度为何会改变平均亮度？**

<details>
<summary>展开参考回答</summary>

因为纳入了原先被截断的非零高阶项；若重复计数，也可能错误变亮。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Light Transport Operators

*PDF p57 · 对应本节：多次反弹为何能写成级数？*

![PDF p57：Light Transport Operators](images/p057.png)

#### Linear Operators

*PDF p59 · 对应本节：多次反弹为何能写成级数？*

![PDF p59：Linear Operators](images/p059.png)

#### Reflection Operator

*PDF p61 · 对应本节：多次反弹为何能写成级数？*

![PDF p61：Reflection Operator](images/p061.png)

#### Transport Operator

*PDF p62 · 对应本节：多次反弹为何能写成级数？*

![PDF p62：Transport Operator](images/p062.png)

#### Rendering Equation in Operator Notation

*PDF p63 · 对应本节：多次反弹为何能写成级数？*

![PDF p63：Rendering Equation in Operator Notation](images/p063.png)

#### Formal Solution

*PDF p68 · 对应本节：多次反弹为何能写成级数？*

![PDF p68：Formal Solution](images/p068.png)

#### Rendering Equation Solution

*PDF p69 · 对应本节：多次反弹为何能写成级数？*

![PDF p69：Rendering Equation Solution](images/p069.png)

#### i=0

*PDF p77 · 对应本节：多次反弹为何能写成级数？*

![PDF p77：i=0](images/p077.png)

</details>

## 5. 辐射度与 AO 分别近似了什么？

辐射度法假设表面漫反射，把表面分成片，建立各片间能量交换方程。由于出射量与方向无关，可以降低未知量维度，但不能直接表示尖锐镜面反射。

AO 则主要测量半球遮蔽程度，是特定假设下的可见性近似，不包含完整灯光颜色与多次反射。课件相关页符号与归一化容易混淆，本文统一用标准漫反射出射度 B 及归一化形状因子 F。

![概念关系：辐射度与 AO 分别近似了什么？](diagrams/d05-relation.png)

*读图：漫反射表面片 → 片间交换矩阵 → 出射度解。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| B | 出射度 W/m² |
| E | 自发出射度 |
| Fij | 从接收片 i 看向 j 的余弦加权几何因子 |
| rho | 反照率 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
B_i=E_i+\rho_i\sum_j F_{ij}B_j
$$

### 🔧 手算 5：把关系落到数字上

两个无自发光以外的简化片满足 B1=1+0.5B2、B2=0.5B1，解 B1=4/3、B2=2/3。代入第二式得到 2/3，第一式得到 4/3。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 代入第二式得到 2/3，第一式得到 4/3。 |
| 适用边界 | 本文为统一能量单位的教学推导；不要照抄原页中的 2π 后又使用 B=πL 的定义。 |

### ⚠️ 易错点：先识别症状与假设

本文为统一能量单位的教学推导；不要照抄原页中的 2π 后又使用 B=πL 的定义。

### 停下来解释一次

**问题：AO 能表现红墙把白球染红吗？**

<details>
<summary>展开参考回答</summary>

单纯 AO 不能，它主要编码遮挡比例；颜色溢出需要材质与光传输信息。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Radiosity

*PDF p33 · 对应本节：辐射度与 AO 分别近似了什么？*

![PDF p33：Radiosity](images/p033.png)

#### Assume Lambertian (diffuse reflections only)

*PDF p35 · 对应本节：辐射度与 AO 分别近似了什么？*

![PDF p35：Assume Lambertian (diffuse reflections only)](images/p035.png)

#### Discretize into Patches

*PDF p37 · 对应本节：辐射度与 AO 分别近似了什么？*

![PDF p37：Discretize into Patches](images/p037.png)

#### Radiosity Method

*PDF p43 · 对应本节：辐射度与 AO 分别近似了什么？*

![PDF p43：Radiosity Method](images/p043.png)

#### Progressive Radiosity

*PDF p45 · 对应本节：辐射度与 AO 分别近似了什么？*

![PDF p45：Progressive Radiosity](images/p045.png)

#### Ambient Occlusion

*PDF p53 · 对应本节：辐射度与 AO 分别近似了什么？*

![PDF p53：Ambient Occlusion](images/p053.png)

#### Ambient Occlusion

*PDF p55 · 对应本节：辐射度与 AO 分别近似了什么？*

![PDF p55：Ambient Occlusion](images/p055.png)

</details>

## 6. 路径吞吐量为何逐次相乘？

每次采样一个散射方向，就把当前权重乘 fr cosθ/p。路径吞吐量 β 是从相机到当前点所有这些因子的乘积；碰到发光体时，βLe 是该路径的加权贡献。

这个量把递归表达式变成迭代程序。需要同时保留是否镜面事件、上一采样 PDF、路径深度和介质状态等信息；基础漫反射版本可先只实现 β 与射线。

![概念关系：路径吞吐量为何逐次相乘？](diagrams/d06-relation.png)

*读图：上一跳权重 → 乘散射与采样权重 → 新的路径吞吐量。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| beta | 路径权重 |
| pdf | 必须匹配方向测度 |
| 初值 | 相机简化模型 beta=1 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
\beta_{k+1}=\beta_k\frac{f_r(\omega_i,\omega_o)\lvert n\cdot\omega_i\rvert}{p_\omega(\omega_i)}
$$

### 🔧 手算 6：把关系落到数字上

两次余弦采样漫反射反照率为 0.8、0.5，β=0.4；命中 Le=10，贡献 4。展开 1×0.8×0.5×10 也为 4。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 展开 1×0.8×0.5×10 也为 4。 |
| 适用边界 | 每一跳都乘距离平方衰减会重复计算几何；方向形式的表面辐亮度传输不这样处理。 |

![几何或数值解释 6](diagrams/d18-bars.png)

*路径权重由 0.8 到 0.4，最后乘灯的辐亮度得到贡献 4。*

### ⚠️ 易错点：先识别症状与假设

每一跳都乘距离平方衰减会重复计算几何；方向形式的表面辐亮度传输不这样处理。

### 停下来解释一次

**问题：β 是否就是路径发生的概率？**

<details>
<summary>展开参考回答</summary>

不是。它包含物理散射权重与采样概率的倒数，可能大于 1。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Light Paths

*PDF p90 · 对应本节：路径吞吐量为何逐次相乘？*

![PDF p90：Light Paths](images/p090.png)

#### 1-Bounce Path Connecting Ray to Light

*PDF p91 · 对应本节：路径吞吐量为何逐次相乘？*

![PDF p91：1-Bounce Path Connecting Ray to Light](images/p091.png)

#### 2-Bounce Paths Connecting Ray to Light

*PDF p94 · 对应本节：路径吞吐量为何逐次相乘？*

![PDF p94：2-Bounce Paths Connecting Ray to Light](images/p094.png)

#### 3-Bounce Path Connecting Ray to Light

*PDF p98 · 对应本节：路径吞吐量为何逐次相乘？*

![PDF p98：3-Bounce Path Connecting Ray to Light](images/p098.png)

#### Global Illumination Rendering

*PDF p103 · 对应本节：路径吞吐量为何逐次相乘？*

![PDF p103：Global Illumination Rendering](images/p103.png)

#### EstRadianceIn(x, ω)

*PDF p105 · 对应本节：路径吞吐量为何逐次相乘？*

![PDF p105：EstRadianceIn(x, ω)](images/p105.png)

</details>

## 7. 俄罗斯轮盘为何不会自动变暗？

以概率 q 继续路径，终止时贡献为零；存活时将后续权重除 q。期望 q×(C/q)+(1-q)×0=C，因此维持期望。

q 小能减少工作但增大幸存路径的贡献波动。真实实现常在若干跳之后启用，并避免 q=0 时仍试图求权重。有限最大深度作为安全上限仍会截断尾项。

![概念关系：俄罗斯轮盘为何不会自动变暗？](diagrams/d07-relation.png)

*读图：随机决定存活 → 存活权重除 q → 期望保持不变。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| q | 存活概率，0<q≤1 |
| C | 原后续估计量 |
| 条件 | 正确重加权 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
Y=\begin{cases}C/q,&\text{以概率 }q\\0,&\text{以概率 }1-q\end{cases},\qquad \mathbb E[Y]=C
$$

### 🔧 手算 7：把关系落到数字上

C=2、q=0.25，存活时返回 8，其余返回 0，期望 0.25×8=2。若忘除 q，期望只剩 0.5。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 若忘除 q，期望只剩 0.5。 |
| 适用边界 | 仅随机终止而不补偿会变暗；强行把过大贡献截断又会引入偏差。 |

![几何或数值解释 3](diagrams/d15-tree.png)

*轮盘用少量较大贡献代替每次都计算后续路径，保持期望。*

### ⚠️ 易错点：先识别症状与假设

仅随机终止而不补偿会变暗；强行把过大贡献截断又会引入偏差。

### 停下来解释一次

**问题：俄罗斯轮盘是否降低方差？**

<details>
<summary>展开参考回答</summary>

一般会增加单路径方差；它主要通过减少计算改善单位成本的效率。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Problem: Infinite Bounces of Light

*PDF p106 · 对应本节：俄罗斯轮盘为何不会自动变暗？*

![PDF p106：Problem: Infinite Bounces of Light](images/p106.png)

#### Russian Roulette

*PDF p107 · 对应本节：俄罗斯轮盘为何不会自动变暗？*

![PDF p107：Russian Roulette](images/p107.png)

#### Russian Roulette - Unbiased Random Termination

*PDF p108 · 对应本节：俄罗斯轮盘为何不会自动变暗？*

![PDF p108：Russian Roulette - Unbiased Random Termination](images/p108.png)

#### Russian Roulette: Unbiased Random Termination

*PDF p109 · 对应本节：俄罗斯轮盘为何不会自动变暗？*

![PDF p109：Russian Roulette: Unbiased Random Termination](images/p109.png)

#### Try 2: Russian Roulette Monte Carlo over Paths

*PDF p111 · 对应本节：俄罗斯轮盘为何不会自动变暗？*

![PDF p111：Try 2: Russian Roulette Monte Carlo over Paths](images/p111.png)

</details>

## 8. 为什么还要直接抽样灯光？

仅靠 BRDF 随机路径撞到小灯非常低效。下一事件估计在每个可散射顶点主动抽灯并测试连接可见性，直接估计本跳照明。

加上继续追踪后，两种策略可能估计相同光路。最简单教学版本可明确分割直接与间接项；通用实现常用 MIS 合并，并对相机直接命中灯、镜面链等情况分别处理。

![概念关系：为什么还要直接抽样灯光？](diagrams/d08-relation.png)

*读图：主动连接光源 → 检查遮挡 → 与继续路径正确合并。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| direct | 本顶点到灯的直接连接 |
| indirect | 经其他表面再到灯 |
| MIS | 本讲之外的扩展连接 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
L=L_{emission}+L_{direct}+L_{indirect}
$$

### 🔧 手算 8：把关系落到数字上

若直接光真实贡献为 3，灯采样估计 3，BRDF 命中灯又完整加 3，会错误得到 6。均分两种无偏估计各乘 1/2，期望回到 3，但一般 MIS 权重更高效。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 均分两种无偏估计各乘 1/2，期望回到 3，但一般 MIS 权重更高效。 |
| 适用边界 | “加 NEE 后忽略所有灯命中”也错，会漏相机可见灯和镜面路径；必须按路径类型分割。 |

### ⚠️ 易错点：先识别症状与假设

“加 NEE 后忽略所有灯命中”也错，会漏相机可见灯和镜面路径；必须按路径类型分割。

### 停下来解释一次

**问题：为什么发光物体不能既直接加一次又在递归里无条件再加一次？**

<details>
<summary>展开参考回答</summary>

可能把同一直接光路计算两遍；应分区或用满足正确权重规则的多策略估计。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Recall: Hemisphere vs Light Sampling

*PDF p24 · 对应本节：为什么还要直接抽样灯光？*

![PDF p24：Recall: Hemisphere vs Light Sampling](images/p024.png)

#### Direct Lighting Pseudocode (Uniform Random Sampling)

*PDF p25 · 对应本节：为什么还要直接抽样灯光？*

![PDF p25：Direct Lighting Pseudocode (Uniform Random Sampling)](images/p025.png)

#### Direct Lighting Pseudocode (Importance Sampling of BRDF)

*PDF p26 · 对应本节：为什么还要直接抽样灯光？*

![PDF p26：Direct Lighting Pseudocode (Importance Sampling of BRDF)](images/p026.png)

#### Direct Lighting Pseudocode (Importance Sampling of Lights)

*PDF p27 · 对应本节：为什么还要直接抽样灯光？*

![PDF p27：Direct Lighting Pseudocode (Importance Sampling of Lights)](images/p027.png)

#### Path Tracing Overview

*PDF p121 · 对应本节：为什么还要直接抽样灯光？*

![PDF p121：Path Tracing Overview](images/p121.png)

#### Partitioning the Rendering Equation

*PDF p128 · 对应本节：为什么还要直接抽样灯光？*

![PDF p128：Partitioning the Rendering Equation](images/p128.png)

#### Path Tracing Pseudocode

*PDF p130 · 对应本节：为什么还要直接抽样灯光？*

![PDF p130：Path Tracing Pseudocode](images/p130.png)

#### Path Tracing Pseudocode

*PDF p131 · 对应本节：为什么还要直接抽样灯光？*

![PDF p131：Path Tracing Pseudocode](images/p131.png)

#### Direct Lighting Pseudocode (Lights)

*PDF p132 · 对应本节：为什么还要直接抽样灯光？*

![PDF p132：Direct Lighting Pseudocode (Lights)](images/p132.png)

</details>

## 9. 多个光源与理想镜面如何处理？

先以离散概率 pj 选择灯 j，再在灯上抽样，联合概率是 pj 乘条件 PDF。漏掉 pj 会让结果随灯数量变化。

点光源和理想镜面属于 delta 类型：连续随机方向命中一个精确方向的概率为零。必须使用能够生成该离散事件的专用采样分支，不能用一个非常大的普通 BRDF 值粗暴代替。

![概念关系：多个光源与理想镜面如何处理？](diagrams/d09-relation.png)

*读图：选择哪盏灯 → 灯内采样 → 联合概率重加权。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| pj | 灯选择概率 |
| 条件 PDF | 选定灯后的密度 |
| delta | 离散事件需特殊处理 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
p(j,\omega)=p_j p(\omega\mid j)
$$

### 🔧 手算 9：把关系落到数字上

4 盏灯等概率选择，pj=1/4。条件贡献为 2，则选灯补偿后是 8；平均四种等贡献事件仍为总贡献 8。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 条件贡献为 2，则选灯补偿后是 8；平均四种等贡献事件仍为总贡献 8。 |
| 适用边界 | 灯越多画面越暗，多半是漏除灯选择概率；镜子照到点灯为黑则检查 delta 支持。 |

![几何或数值解释 4](diagrams/d16-reflection.png)

*理想镜面不能靠普通连续随机方向恰好命中。*

### ⚠️ 易错点：先识别症状与假设

灯越多画面越暗，多半是漏除灯选择概率；镜子照到点灯为黑则检查 delta 支持。

### 停下来解释一次

**问题：连续方向采样能偶然撞中理想点光源吗？**

<details>
<summary>展开参考回答</summary>

数学上概率为零，应直接采样点光源方向并采用对应的离散贡献公式。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Multiple Light Sources

*PDF p150 · 对应本节：多个光源与理想镜面如何处理？*

![PDF p150：Multiple Light Sources](images/p150.png)

#### Multiple Light Sources (Single Sample)

*PDF p151 · 对应本节：多个光源与理想镜面如何处理？*

![PDF p151：Multiple Light Sources (Single Sample)](images/p151.png)

#### Point Lights / Ideal Specular Materials – Issues

*PDF p152 · 对应本节：多个光源与理想镜面如何处理？*

![PDF p152：Point Lights / Ideal Specular Materials – Issues](images/p152.png)

#### Point Lights / Ideal Specular Materials – Issues

*PDF p154 · 对应本节：多个光源与理想镜面如何处理？*

![PDF p154：Point Lights / Ideal Specular Materials – Issues](images/p154.png)

#### Point Lights / Ideal Specular Materials – Issues

*PDF p157 · 对应本节：多个光源与理想镜面如何处理？*

![PDF p157：Point Lights / Ideal Specular Materials – Issues](images/p157.png)

</details>

## 10. 为什么有些场景噪声特别顽固？

镜面聚焦、小光源、狭窄间接通道使重要光路很难从相机随机找到。增加样本能降低方差，却可能非常昂贵。光子映射从灯出发收集传播样本，可对某些焦散更有效，但密度估计引入不同误差。

课件对比的 1、32、1024 路径展示收敛趋势，不意味着 1024 是任何场景的合格阈值。应根据误差与时间测量实际场景。

![概念关系：为什么有些场景噪声特别顽固？](diagrams/d10-relation.png)

*读图：稀少重要光路 → 高贡献低概率 → 高方差。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| sigma | 有限方差独立估计的标准差 |
| N | 每像素样本数 |
| 前提 | 估计器与场景固定 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
\sigma_N\propto N^{-1/2}
$$

### 🔧 手算 10：把关系落到数字上

从 16 增到 256 样本，样本数乘 16，典型标准差降为 1/4。反算 (√256)/(√16)=4。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 反算 (√256)/(√16)=4。 |
| 适用边界 | 明亮孤立点可能是合法高贡献，也可能是数值错误；先查 NaN、PDF 和几何，再考虑方差策略。 |

![几何或数值解释 7](diagrams/d19-spectrum.png)

*稀少重要光路造成更大的样本贡献波动，采样策略力求降低这种波动。*

### ⚠️ 易错点：先识别症状与假设

明亮孤立点可能是合法高贡献，也可能是数值错误；先查 NaN、PDF 和几何，再考虑方差策略。

### 停下来解释一次

**问题：把所有亮点剪掉是否仍无偏？**

<details>
<summary>展开参考回答</summary>

通常不是，截断贡献改变期望；可作为有偏近似但必须明确说明。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Photon Mapping

*PDF p113 · 对应本节：为什么有些场景噪声特别顽固？*

![PDF p113：Photon Mapping](images/p113.png)

#### Photon Mapping

*PDF p116 · 对应本节：为什么有些场景噪声特别顽固？*

![PDF p116：Photon Mapping](images/p116.png)

#### Photon Mapping

*PDF p119 · 对应本节：为什么有些场景噪声特别顽固？*

![PDF p119：Photon Mapping](images/p119.png)

#### One sample (path) per pixel

*PDF p135 · 对应本节：为什么有些场景噪声特别顽固？*

![PDF p135：One sample (path) per pixel](images/p135.png)

#### 32 samples (paths) per pixel

*PDF p136 · 对应本节：为什么有些场景噪声特别顽固？*

![PDF p136：32 samples (paths) per pixel](images/p136.png)

#### 1024 samples (paths) per pixel

*PDF p137 · 对应本节：为什么有些场景噪声特别顽固？*

![PDF p137：1024 samples (paths) per pixel](images/p137.png)

#### Good Scenes for Path Tracing (Diffuse, Sky Lighting)

*PDF p168 · 对应本节：为什么有些场景噪声特别顽固？*

![PDF p168：Good Scenes for Path Tracing (Diffuse, Sky Lighting)](images/p168.png)

#### A Challenging Scene for Path Tracing – Why?

*PDF p172 · 对应本节：为什么有些场景噪声特别顽固？*

![PDF p172：A Challenging Scene for Path Tracing – Why?](images/p172.png)

</details>

## 11. 精度问题为何会变成脏阴影？

浮点求交点可能落到表面内部，下一条阴影光线立即与自身相交，出现黑斑。偏移起点、限制 t 范围和使用可靠误差界都在避免把数值误差当几何。

固定 epsilon 依赖场景尺度：太小不能消除自相交，太大又会穿过薄物体。应在不同尺度的小场景上测试，而不是只在一个模型上调到看起来正常。

![概念关系：精度问题为何会变成脏阴影？](diagrams/d11-relation.png)

*读图：浮点交点 → 误差安全起点 → 有限区间可见性。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| tmin | 排除近零自相交 |
| tmax | 阴影光线到光源前的距离 |
| d | 此处为单位方向 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
r(t)=o+t d,\qquad t\in[t_{min},t_{max}]
$$

### 🔧 手算 11：把关系落到数字上

光源距离 2 米，若最近遮挡 t=3，则不遮挡；若 t=1，则遮挡。分别检查是否属于 (epsilon,2-epsilon) 即可。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 分别检查是否属于 (epsilon,2-epsilon) 即可。 |
| 适用边界 | 阴影射线不设最大距离，会把光源背后的物体误认为遮挡物。 |

![几何或数值解释 5](diagrams/d17-backtrace.png)

*阴影光线有有限有效区间，灯背后的几何不应产生遮挡。*

### ⚠️ 易错点：先识别症状与假设

阴影射线不设最大距离，会把光源背后的物体误认为遮挡物。

### 停下来解释一次

**问题：把所有光线起点都偏移同一个大常数安全吗？**

<details>
<summary>展开参考回答</summary>

不安全。小尺度细节会漏光，大尺度又可能仍不足，应考虑尺度与误差界。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Numerical Precision Issues

*PDF p158 · 对应本节：精度问题为何会变成脏阴影？*

![PDF p158：Numerical Precision Issues](images/p158.png)

#### Numerical Precision Issues

*PDF p159 · 对应本节：精度问题为何会变成脏阴影？*

![PDF p159：Numerical Precision Issues](images/p159.png)

#### Noisy Shadows

*PDF p160 · 对应本节：精度问题为何会变成脏阴影？*

![PDF p160：Noisy Shadows](images/p160.png)

#### Noisy shadows because of

*PDF p161 · 对应本节：精度问题为何会变成脏阴影？*

![PDF p161：Noisy shadows because of](images/p161.png)

#### Floating-Point Precision Remedies

*PDF p162 · 对应本节：精度问题为何会变成脏阴影？*

![PDF p162：Floating-Point Precision Remedies](images/p162.png)

#### Floating-Point Precision Remedies

*PDF p163 · 对应本节：精度问题为何会变成脏阴影？*

![PDF p163：Floating-Point Precision Remedies](images/p163.png)

#### Floating-Point Precision Remedies

*PDF p165 · 对应本节：精度问题为何会变成脏阴影？*

![PDF p165：Floating-Point Precision Remedies](images/p165.png)

#### Remedy: Project Intersection Point to Surface

*PDF p167 · 对应本节：精度问题为何会变成脏阴影？*

![PDF p167：Remedy: Project Intersection Point to Surface](images/p167.png)

</details>

## 12. 怎样验收一个最小路径追踪器？

先验证无光场景为黑，再验证发光体可见、单次漫反射、间接反射与轮盘。每次只开启一种新光路，记录线性像素均值，最后才加显示映射。

实现顺序是教学建议，不是声称已把完整追踪器部署到服务器。随笔记附带的数值核对只验证解析小模型；完整图像还需要场景、几何和采样的联合验证。

![概念关系：怎样验收一个最小路径追踪器？](diagrams/d12-relation.png)

*读图：解析极简场景 → 分项开启光路 → 统计检查与图像检查。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| rho | 反照率 |
| Lenv | 半球均匀入射辐亮度 |
| 条件 | 仅反射，无自发光 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
L_{diffuse}=\rho L_{env}\quad\text{（均匀环境与无遮挡漫反射表面）}
$$

### 🔧 手算 12：把关系落到数字上

ρ=0.4、Lenv=5，输出应为 2。由 E=5π、BRDF=0.4/π 计算也是 2，是跨三讲的一致性检查。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 由 E=5π、BRDF=0.4/π 计算也是 2，是跨三讲的一致性检查。 |
| 适用边界 | 把 gamma 后像素作为能量测试对象会混淆非线性显示与物理积分；先检查线性缓冲。 |

### ⚠️ 易错点：先识别症状与假设

把 gamma 后像素作为能量测试对象会混淆非线性显示与物理积分；先检查线性缓冲。

### 停下来解释一次

**问题：一个均匀环境下的漫反射球上每点都会一样亮吗？**

<details>
<summary>展开参考回答</summary>

若无其他遮挡、各点接收完整均匀半球且反照率相同，出射辐亮度相同；轮廓与背景仍取决于相机和环境。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Summary of Intuition on Global

*PDF p138 · 对应本节：怎样验收一个最小路径追踪器？*

![PDF p138：Summary of Intuition on Global](images/p138.png)

#### Summary of Intuition on G.I. & P.T.

*PDF p140 · 对应本节：怎样验收一个最小路径追踪器？*

![PDF p140：Summary of Intuition on G.I. & P.T.](images/p140.png)

#### Implementation Notes

*PDF p145 · 对应本节：怎样验收一个最小路径追踪器？*

![PDF p145：Implementation Notes](images/p145.png)

#### Paths vs Trees

*PDF p146 · 对应本节：怎样验收一个最小路径追踪器？*

![PDF p146：Paths vs Trees](images/p146.png)

#### 64 image samples x 1 light sample, 13.2 seconds

*PDF p147 · 对应本节：怎样验收一个最小路径追踪器？*

![PDF p147：64 image samples x 1 light sample, 13.2 seconds](images/p147.png)

#### 1 image sample x 64 light samples, 7.0 seconds

*PDF p148 · 对应本节：怎样验收一个最小路径追踪器？*

![PDF p148：1 image sample x 64 light samples, 7.0 seconds](images/p148.png)

#### 8 image samples x 8 light samples, 7.7 seconds

*PDF p149 · 对应本节：怎样验收一个最小路径追踪器？*

![PDF p149：8 image samples x 8 light samples, 7.7 seconds](images/p149.png)

</details>

## 深入 1. 从两块漫反射面解出无限次反弹

本节是根据前文课件主题展开的**补充推导与独立教学实验**，数值不是课件测量结果。

回查原课件：p29、p30、p31、p32、p33、p35、p37、p43、p45、p53、p55、p57、p59、p61、p62、p63、p68、p69、p77。

路径追踪中的递归并不神秘：当前表面收到另一个表面发出的光，而另一个表面的亮度也依赖当前表面。把整个场景缩成两个互相交换能量的面，就可以用线性方程精确解出“无限次反弹”，再与逐次迭代比较。

### 先固定问题的边界

- **未知量**：B1、B2 是各自面积上均匀的出射度，不是某个方向的辐亮度。
- **交换**：两个面等面积，互见形状因子 F12=F21=0.5，其余能量逃向黑环境。
- **材质**：ρ1=ρ2=0.5；发射出射度 E1=1、E2=0。

### 从定义逐步推到可计算形式

**第 1 步。** 每个面的出射由自身发光与反射收到的能量组成。用 B 表示出射度时，Lambertian 的 π 已吸收在定义中。

$$
B_1=E_1+\rho_1 F_{12}B_2,\qquad B_2=E_2+\rho_2 F_{21}B_1
$$

**第 2 步。** 本例两个耦合系数都为 1/4，代入第二式即可消去一个未知量。

$$
B_2=\tfrac14B_1,\qquad B_1=1+\tfrac1{16}B_1
$$

**第 3 步。** 移项得到精确解。分母 1−1/16 表示每完成一轮往返后仅保留原贡献的 1/16。

$$
B_1=\frac{16}{15},\qquad B_2=\frac4{15}
$$

**第 4 步。** 反复代入相当于把矩阵算子 K 展开成 Neumann 级数；每一项对应增加一次交换。

$$
B=E+KE+K^2E+\cdots=(I-K)^{-1}E
$$

**第 5 步。** 收敛依赖传输算子的谱半径小于 1。完全封闭、无吸收且持续发光的理想模型不能假装仍有有限稳态解。

$$
\rho(K)<1
$$

![从两块漫反射面解出无限次反弹](diagrams/d21-workshop.png)

*两面之间的箭头表示能量往返，数列 1、1/16、1/256 表示连续往返的贡献。它们的无限和与有限截断之差，就是正文手算的剩余尾项。*

### 🔧 手算 13：从两块漫反射面解出无限次反弹

| 已知量 | 数值与含义 |
| --- | --- |
| 初始迭代 | B⁽⁰⁾=(0,0) |
| 一次交换系数 | 0.25 |
| 精确 B1 | 16/15≈1.066667 |
| 精确 B2 | 4/15≈0.266667 |

1. 第 1 次更新得到 (1,0)，只有自发光。

2. 第 2 次得到 (1,0.25)，光第一次到达第二面。

3. 第 3 次得到 (1.0625,0.25)，反射光回到第一面。

4. 第 4 次得到 (1.0625,0.265625)。

5. 代回精确解：1+0.25×4/15=16/15；0.25×16/15=4/15。

6. 第一面比自身发射略亮，因为接收了第二面的反射；这不违反能量守恒，完整账本还包含吸收与逃逸。

### 回代与第二条验证路线

线性方程求解与逐反弹级数提供两条独立路线。

将 E1 翻倍，两个 B 都应翻倍；若没有，可能在传输中做了非线性裁剪。

### 改变一个条件，原结论还成立吗？

等面积保证本例两个形状因子相等；一般只满足 AiFij=AjFji，不能随便写 Fij=Fji。

这是均匀面元离散化模型，不能表示同一面内的阴影边界或镜面路径。

### 真正运行一次：保留正确与错误对照

下列程序只依赖 Python 标准库，复制到一个文件即可运行。断言验证本节明确给出的解析关系；它不替代完整场景测试。

```python
from math import isclose
b1=b2=0.
for k in range(1,21):
    b1,b2=1+.25*b2,.25*b1
    if k<=4: print(k,round(b1,6),round(b2,6))
exact1,exact2=16/15,4/15
assert abs(b1-exact1)<1e-10
assert abs(b2-exact2)<1e-10
assert isclose(exact1,1+.25*exact2)
assert isclose(exact2,.25*exact1)
wrong_b1=1+.25*(.25*1)
assert wrong_b1 < exact1
print('finite bounce / infinite =',wrong_b1,round(exact1,6))
```

实际运行输出：

```text
1 1.0 0.0
2 1.0 0.25
3 1.0625 0.25
4 1.0625 0.265625
finite bounce / infinite = 1.0625 1.066667
```

### 实现坑：从可观察症状回到原因

**症状：** 增加反弹数后图像仍在系统性变亮，却把这种变化当成随机噪声。

**定位与修正：** 先用两面模型测固定深度的截断偏差。有限反弹会漏掉尾项；增加每条路径的样本数只能降低方差，不能补回被深度上限删除的传输。

### 自测 27. 若两个面之间一次交换的系数从 0.25 变成 0.9，迭代会怎样？

<details>
<summary>推理与答案</summary>

仍可收敛，但往返系数从 0.0625 增至 0.81，尾项衰减慢得多。高反射率封闭空间需要更多反弹，这不是单纯提高每像素样本即可消除的深度截断问题。

</details>

## 深入 2. 路径吞吐量与俄罗斯轮盘共用一份概率账本

本节是根据前文课件主题展开的**补充推导与独立教学实验**，数值不是课件测量结果。

回查原课件：p90、p91、p94、p98、p103、p105、p106、p107、p108、p109、p111。

路径吞吐量 β 记录的是“后面遇到的光应乘多少权重”。它同时包含材质响应、几何余弦和采样概率。俄罗斯轮盘只是额外引入一个是否继续的随机选择，因此也必须把这一选择的概率补偿进同一份账本。

### 先固定问题的边界

- **表面**：使用余弦采样的 Lambertian 表面。
- **路径**：两次反射率分别 0.8、0.5，之后遇到辐亮度 10 的光源。
- **轮盘**：第二次反射后以 q=0.4 继续；q 代表生存概率，不是终止概率。

### 从定义逐步推到可计算形式

**第 1 步。** 每次表面采样更新吞吐量，使用真实返回方向对应的 PDF。

$$
\beta_{k+1}=\beta_k\frac{f_r(\omega_i,\omega_o)|\cos\theta_i|}{p(\omega_i)}
$$

**第 2 步。** Lambertian 配余弦采样时，ρ/π 与 cosθ/π 恰好抵消，只剩反射率。这个简化依赖材质和采样配对。

$$
\frac{(\rho/\pi)\cos\theta}{\cos\theta/\pi}=\rho
$$

**第 3 步。** 两次反射后的吞吐量为两个反射率的乘积，命中光源贡献为 βLe。

$$
\beta=0.8\times0.5=0.4,\qquad C=0.4\times10=4
$$

**第 4 步。** 轮盘继续事件用 Bernoulli 随机变量 Z 表示。只在生存路径上除以 q。

$$
\widehat C=Z\frac Cq,\qquad P(Z=1)=q
$$

**第 5 步。** 期望恢复 C，但方差增加。轮盘节省计算的同时付出了噪声成本。

$$
\mathbb E[\widehat C]=C,\qquad\operatorname{Var}(\widehat C)=C^2(1/q-1)
$$

![路径吞吐量与俄罗斯轮盘共用一份概率账本](diagrams/d22-workshop.png)

*树的两支分别是概率 0.6 的终止和概率 0.4 的存活；存活权重放大到 10，平均仍为 4。*

### 🔧 手算 14：路径吞吐量与俄罗斯轮盘共用一份概率账本

| 已知量 | 数值与含义 |
| --- | --- |
| 两次反射 | ρ1=0.8，ρ2=0.5 |
| 光源 | Le=10 |
| 生存概率 | q=0.4 |
| 正确存活贡献 | C/q=10 |

1. 没有轮盘时每条该路径的贡献是 4。

2. 40% 的路径存活，存活时贡献 10；60% 的路径贡献 0。

3. 期望 0.4×10+0.6×0=4。

4. 二阶矩为 0.4×100=40，减均值平方 16 得方差 24。

5. 如果忘除 q，期望只剩 0.4×4=1.6。

6. 如果把终止概率 0.6 当分母，期望变为 0.4×4/0.6≈2.666667，同样偏暗。

### 回代与第二条验证路线

用离散结果表求期望，与公式 C²(1/q−1) 求方差一致。

q=1 时每条路径继续，方差应归零；q 越小，单条生存路径的贡献越大。

### 改变一个条件，原结论还成立吗？

若按历史吞吐量自适应选 q，只要对当前已知历史使用同一个条件生存概率补偿，仍能保持条件无偏。

q=0 会完全丢弃非零后续贡献，不能靠除零补偿。固定最大深度与轮盘也不是同一种无偏性保证。

### 真正运行一次：保留正确与错误对照

下列程序只依赖 Python 标准库，复制到一个文件即可运行。断言验证本节明确给出的解析关系；它不替代完整场景测试。

```python
from math import isclose
from random import Random
beta=.8*.5; Le=10.; q=.4
C=beta*Le
mean=q*(C/q)
variance=q*(C/q)**2-mean**2
assert isclose(mean,4)
assert isclose(variance,24)
wrong_mean=q*C
assert isclose(wrong_mean,1.6)
rng=Random(16); n=50000
estimate=sum(C/q if rng.random()<q else 0 for _ in range(n))/n
assert abs(estimate-C)<.08
print('expected mean / variance =',mean,variance)
print('sample estimate =',round(estimate,5))
print('without compensation =',wrong_mean)
```

实际运行输出：

```text
expected mean / variance = 4.0 24.0
sample estimate = 3.998
without compensation = 1.6
```

### 实现坑：从可观察症状回到原因

**症状：** 开启俄罗斯轮盘后平均亮度下降；或者亮度正确但少数像素突然很亮。

**定位与修正：** 前者通常是漏除生存概率或混淆终止概率，后者可能是低 q 带来的高方差。先统计多批均值与分布，再决定是否是错误；不能把所有大贡献都直接裁掉。

### 自测 28. 轮盘保持均值，是否意味着它一定提高同时间下的图像质量？

<details>
<summary>推理与答案</summary>

不保证。它用更高的单路径方差换取更多可完成路径，是否划算取决于后续计算成本和贡献分布。需要固定总时间比较误差，而不是只证明均值不变。

</details>

## 深入 3. 直接光与继续追踪为什么会重复计数

本节是根据前文课件主题展开的**补充推导与独立教学实验**，数值不是课件测量结果。

回查原课件：p24、p25、p26、p27、p121、p128、p130、p131、p132、p138、p140、p145、p146、p147、p148、p149、p150、p151、p152、p154、p157。

增加显式光源采样后，路径继续追踪仍可能命中光源。两种方法如果估计同一条积分，却各自按完整权重加入，结果会多算。先在一个两区域离散模型里看清问题，再理解多重重要性采样的权重为何要相加为 1。

### 先固定问题的边界

- **目标积分**：把域简化为两个区域，积分贡献 F=(2,6)，总值 I=8。
- **策略**：策略 A 的概率为 (0.8,0.2)，策略 B 为 (0.25,0.75)，每种各抽一个样本。
- **权重**：使用每策略一个样本时的 balance heuristic；所有区域两种概率均正。

### 从定义逐步推到可计算形式

**第 1 步。** 每种策略单独估计完整积分，只需贡献除其选择概率。

$$
\mathbb E[F(X_A)/p_A(X_A)]=\sum_jF_j=I
$$

**第 2 步。** 两个完整无偏估计直接相加，会得到两倍期望；独立性不能修复重复计数。

$$
\mathbb E[\widehat I_A+\widehat I_B]=2I
$$

**第 3 步。** 把每个区域的积分贡献分配给两种策略，要求逐区域权重和为 1。

$$
w_A(j)+w_B(j)=1
$$

**第 4 步。** 平衡启发式按两种概率的相对大小分配权重。

$$
w_A(j)=\frac{p_A(j)}{p_A(j)+p_B(j)},\qquad w_B(j)=1-w_A(j)
$$

**第 5 步。** 最终每种策略贡献自己的那部分，取期望后权重相加恢复一次完整积分。

$$
\widehat I=\frac{w_A(X_A)F(X_A)}{p_A(X_A)}+\frac{w_B(X_B)F(X_B)}{p_B(X_B)}
$$

![直接光与继续追踪为什么会重复计数](diagrams/d23-workshop.png)

*同一个光源贡献被两条策略覆盖；每个区域的两份权重拼成 1，错误版本则把整份贡献画了两遍。*

### 🔧 手算 15：直接光与继续追踪为什么会重复计数

| 已知量 | 数值与含义 |
| --- | --- |
| 区域 1 | F1=2，pA=0.8，pB=0.25 |
| 区域 2 | F2=6，pA=0.2，pB=0.75 |
| 参考积分 | 2+6=8 |
| 样本预算 | 策略 A、B 各 1 个 |

1. 区域 1 的 wA=0.8/1.05=16/21，wB=5/21。

2. 区域 2 的 wA=0.2/0.95=4/19，wB=15/19。

3. 策略 A 的期望份额为 2×16/21+6×4/19≈2.786967。

4. 策略 B 的期望份额为 2×5/21+6×15/19≈5.213033。

5. 两份相加为 8。

6. 若 A 抽到区域 1、B 抽到区域 2，本次结果约为 1.904762+6.315789=8.220551；一次结果仍不必等于期望。

### 回代与第二条验证路线

枚举两个策略的四种样本组合，乘各自联合概率，再求和，应该得到 8。

同时枚举不加权的错误版本，应得到 16。这个对照不依赖随机数或大样本近似。

### 改变一个条件，原结论还成立吗？

理想镜面 delta 分布与普通连续方向密度不能直接用同一数值 PDF 相加。实际实现需要标记事件类型。

多个样本数不相同时，平衡权重还包含各策略样本数 ni；此处各一个的简式不能直接照搬。

### 真正运行一次：保留正确与错误对照

下列程序只依赖 Python 标准库，复制到一个文件即可运行。断言验证本节明确给出的解析关系；它不替代完整场景测试。

```python
from math import isclose
F=(2.,6.); pa=(.8,.2); pb=(.25,.75)
wa=[a/(a+b) for a,b in zip(pa,pb)]
wb=[1-x for x in wa]
expected=wrong=0.
for a in range(2):
    for b in range(2):
        probability=pa[a]*pb[b]
        estimate=wa[a]*F[a]/pa[a]+wb[b]*F[b]/pb[b]
        expected+=probability*estimate
        wrong+=probability*(F[a]/pa[a]+F[b]/pb[b])
assert isclose(expected,8)
assert isclose(wrong,16)
assert all(isclose(a+b,1) for a,b in zip(wa,wb))
print('weighted expectation =',round(expected,6))
print('unweighted double count =',wrong)
```

实际运行输出：

```text
weighted expectation = 8.0
unweighted double count = 16.0
```

### 实现坑：从可观察症状回到原因

**症状：** 添加直接光采样后画面更亮，尤其直接可见灯光或一跳反射贡献接近翻倍。

**定位与修正：** 列出每种策略究竟在估计哪段路径。若它们覆盖同一积分，应正确分配 MIS 权重，或明确只由一种策略负责该类贡献；不要简单把“命中发光物就加 Le”和直接光结果无条件并列。

### 自测 29. 把两个完整估计简单取平均能否无偏？

<details>
<summary>推理与答案</summary>

能，在两种策略都覆盖完整积分并各自无偏时，固定各 1/2 的平均是无偏的。但它未利用局部概率匹配，方差可能更大；支持集缺失、delta 事件和不等预算仍需单独处理。

</details>

## 深入 4. 阴影射线为什么是一条有范围的查询

本节是根据前文课件主题展开的**补充推导与独立教学实验**，数值不是课件测量结果。

回查原课件：p138、p140、p145、p146、p147、p148、p149、p158、p159、p160、p161、p162、p163、p165、p167。

阴影测试的目标是判断交点与采到的灯之间是否有遮挡，而不是判断这条无限射线是否碰到任何东西。自相交和光源后方物体都可能让一个本应可见的点变黑，因此必须同时说明方向归一化、起点偏移和有效距离区间。

### 先固定问题的边界

- **简化场景**：一维沿射线的候选交点距离，用于隔离查询逻辑；不冒充三角形求交误差模型。
- **方向**：归一化，t 的单位与场景距离一致。
- **灯距离**：d=5，允许的遮挡区间为 ε<t<d−ε。

### 从定义逐步推到可计算形式

**第 1 步。** 光线参数化中，只有单位方向才让 t 等于欧氏距离。

$$
r(t)=o+t\widehat d,\qquad\|\widehat d\|=1
$$

**第 2 步。** 首先排除起点附近的数值自命中。ε 是场景尺度相关的容差，不能写成适用于所有单位的魔法常数。

$$
t>t_{min}
$$

**第 3 步。** 还必须排除采样灯位置之后的交点，避免远处几何遮住近处灯。

$$
t<t_{max}\approx\|y-o\|
$$

**第 4 步。** 遮挡是区间内存在任一合法交点，不需要寻找光源后的最近物体。

$$
V(o,y)=1-\mathbf1[\exists\ t\in(t_{min},t_{max})\text{ with a hit}]
$$

**第 5 步。** 若整个场景按 s 倍缩放，距离区间也应相应缩放。偏移策略在尺度变化下是否仍合理，需要专门测试。

$$
(d,t,\epsilon)\mapsto(sd,st,s\epsilon)
$$

![阴影射线为什么是一条有范围的查询](diagrams/d24-workshop.png)

*同一条射线上，自命中在有效区间之前，灯后物体在区间之后，只有中间候选会令可见性变为零。*

### 🔧 手算 16：阴影射线为什么是一条有范围的查询

| 已知量 | 数值与含义 |
| --- | --- |
| 灯距离 | d=5 |
| 起点容差 | ε=0.001，仅为本例单位 |
| 候选交点 | 0.00001 与 8 |
| 真实遮挡变体 | 另外加入 t=2 |

1. 0.00001 小于 ε，作为自命中排除。

2. 8 大于 4.999，在灯后方，排除。

3. 剩余区间没有命中，因此灯可见。

4. 加入 t=2 后，它位于 (0.001,4.999)，灯被遮挡。

5. 若只检查 t>0，第一组数据会因自命中返回错误遮挡。

6. 若只排除自命中却不给上界，第一组数据仍会因 t=8 返回错误遮挡。

### 回代与第二条验证路线

程序对有遮挡与无遮挡两组都验证，再把全部距离乘 1000，结果应保持一致。

另用未归一化方向解释 t 的变化：方向扩大两倍时同一交点的参数 t 减半，不能仍拿物理距离 5 当参数上界。

### 改变一个条件，原结论还成立吗？

靠近接触面时，过大的 ε 会跳过真实遮挡，出现漏光；过小则保留自命中，出现痤疮状噪点。

可靠生产实现通常结合浮点误差界与几何法线偏移。本例仅验证范围逻辑，不声称固定 ε 解决所有精度问题。

### 真正运行一次：保留正确与错误对照

下列程序只依赖 Python 标准库，复制到一个文件即可运行。断言验证本节明确给出的解析关系；它不替代完整场景测试。

```python
def blocked(hits,d,eps):
    return any(eps<t<d-eps for t in hits)
hits=[.00001,8.]
d,eps=5.,.001
assert not blocked(hits,d,eps)
assert blocked(hits+[2.],d,eps)
wrong_unbounded=any(t>eps for t in hits)
wrong_self=any(0<t<d for t in hits)
assert wrong_unbounded and wrong_self
scale=1000
assert not blocked([scale*t for t in hits],scale*d,scale*eps)
assert blocked([scale*t for t in hits+[2.]],scale*d,scale*eps)
print('correct visible =',not blocked(hits,d,eps))
print('unbounded / no self exclusion =',wrong_unbounded,wrong_self)
```

实际运行输出：

```text
correct visible = True
unbounded / no self exclusion = True True
```

### 实现坑：从可观察症状回到原因

**症状：** 物体表面出现脏阴影，或者灯后方加一堵墙就让前面的物体变黑。

**定位与修正：** 分别关闭下界和上界，复现两类错误，再恢复完整区间。只有这两个故障都被测试，才能把“加一个 ε 看起来好了”升级为可解释的修复。

### 自测 30. 如果将射线起点偏移后，仍使用偏移前到灯的距离作为上界，会有什么风险？

<details>
<summary>推理与答案</summary>

端点范围与实际射线不再一致，可能包含灯后方很近的几何或排除灯前几何。应从实际新起点构造方向与距离，并考虑端点误差；不能只更新起点而保留所有旧参数。

</details>

## 深入练习的跨讲连接：这些工具会在哪里再出现？

| 相关讲次 | 借用的工具 | 本次实际使用位置 |
| --- | --- | --- |
| [L13](/notes/cs184-13-ray-tracing-acceleration/) | 有限射线区间 | 阴影只查询交点到灯之间 |
| [L14](/notes/cs184-14-radiometry/) | 能量密度 | 区分出射度 B 与方向辐亮度 L |
| [L15](/notes/cs184-15-monte-carlo-integration/) | 条件概率 | 吞吐量与轮盘补偿使用真实概率 |
| [L18](/notes/cs184-18-material-modeling/) | 散射事件 | 镜面 delta 不能当普通方向 PDF |

### 回头看才明白

1. 固定反弹深度删除积分尾项；增加样本只能减噪，不能修复这类截断偏差。

2. 直接光和继续追踪是对路径空间的不同抽样策略，覆盖重叠处必须明确归属或权重。

3. 一张脏阴影图可能来自几何精度，也可能来自查询范围；用两个候选交点就能把问题拆开。

### 这组实验已经验证什么，还差什么

| 证据 | 可以支持的结论 | 下一步 |
| --- | --- | --- |
| 逐步推导与回代 | 在明确假设下，数值和关系一致 | 改变一个假设，重新预测边界行为 |
| 本篇四段实际运行的程序 | 小模型和故障对照可复现 | 接入完整项目后继续核对坐标、单位和输入范围 |
| 原生图解 | 几何与数值对应关系可检查 | 不把示意图当成真实设备或场景的测量 |

## 13. 把基础数值例子连成检查顺序

先手算再运行。随仓库提供的 `scripts/cs184-numerical-checks.py` 是小模型验证，不依赖 GPU，也不修改服务器配置。它不能替代完整渲染场景或模拟系统的验证。

| 顺序 | 本节关系 | 最容易漏掉的约定 |
| --- | --- | --- |
| 1 | 局部光照遗漏了哪一部分？ | Lr：反射其他来源的光 |
| 2 | BRDF 究竟把什么变成什么？ | omega_i、omega_o：都指向表面外部 |
| 3 | 反射方程怎样变成递归方程？ | 无命中：用环境辐亮度替代 |
| 4 | 多次反弹为何能写成级数？ | 条件：级数收敛 |
| 5 | 辐射度与 AO 分别近似了什么？ | rho：反照率 |
| 6 | 路径吞吐量为何逐次相乘？ | 初值：相机简化模型 beta=1 |
| 7 | 俄罗斯轮盘为何不会自动变暗？ | 条件：正确重加权 |
| 8 | 为什么还要直接抽样灯光？ | MIS：本讲之外的扩展连接 |
| 9 | 多个光源与理想镜面如何处理？ | delta：离散事件需特殊处理 |
| 10 | 为什么有些场景噪声特别顽固？ | 前提：估计器与场景固定 |
| 11 | 精度问题为何会变成脏阴影？ | d：此处为单位方向 |
| 12 | 怎样验收一个最小路径追踪器？ | 条件：仅反射，无自发光 |

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
| 局部光照遗漏了哪一部分？ | 只把环境常数调亮不能等价替代间接照明，因为遮挡、材质颜色与方向关系都丢失了。 |
| BRDF 究竟把什么变成什么？ | BRDF 数值可以超过 1；应检查加权半球积分是否超过 1，而不是逐点截断。 |
| 反射方程怎样变成递归方程？ | 递归调用如果又把当前点传回，通常是自相交；应检查射线起点、方向与最小 t。 |
| 多次反弹为何能写成级数？ | “一条路径多一次反弹一定更暗”不总成立；应理解整体能量传输的收敛条件，不能逐条比较不同路径。 |

### 阶段 2：第 5–8 节

| 涉及关系 | 错误机制 / 修正方向 |
| --- | --- |
| 辐射度与 AO 分别近似了什么？ | 本文为统一能量单位的教学推导；不要照抄原页中的 2π 后又使用 B=πL 的定义。 |
| 路径吞吐量为何逐次相乘？ | 每一跳都乘距离平方衰减会重复计算几何；方向形式的表面辐亮度传输不这样处理。 |
| 俄罗斯轮盘为何不会自动变暗？ | 仅随机终止而不补偿会变暗；强行把过大贡献截断又会引入偏差。 |
| 为什么还要直接抽样灯光？ | “加 NEE 后忽略所有灯命中”也错，会漏相机可见灯和镜面路径；必须按路径类型分割。 |

### 阶段 3：第 9–12 节

| 涉及关系 | 错误机制 / 修正方向 |
| --- | --- |
| 多个光源与理想镜面如何处理？ | 灯越多画面越暗，多半是漏除灯选择概率；镜子照到点灯为黑则检查 delta 支持。 |
| 为什么有些场景噪声特别顽固？ | 明亮孤立点可能是合法高贡献，也可能是数值错误；先查 NaN、PDF 和几何，再考虑方差策略。 |
| 精度问题为何会变成脏阴影？ | 阴影射线不设最大距离，会把光源背后的物体误认为遮挡物。 |
| 怎样验收一个最小路径追踪器？ | 把 gamma 后像素作为能量测试对象会混淆非线性显示与物理积分；先检查线性缓冲。 |

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

### 自测 1. 软阴影本身一定要求多次反弹吗？

<details>
<summary>参考答案</summary>

不。面光源的直接照明就能产生软阴影；全局光照还包括多次散射。

</details>

### 自测 2. 镜面与漫反射能否只靠一个 RGB 颜色区分？

<details>
<summary>参考答案</summary>

不能。它们的方向分布根本不同，颜色只是部分参数。

</details>

### 自测 3. 为什么同一条连接光路在两端的方向符号相反？

<details>
<summary>参考答案</summary>

因为每端都采用“从该表面向外”的方向约定。

</details>

### 自测 4. 增加最大深度为何会改变平均亮度？

<details>
<summary>参考答案</summary>

因为纳入了原先被截断的非零高阶项；若重复计数，也可能错误变亮。

</details>

### 自测 5. AO 能表现红墙把白球染红吗？

<details>
<summary>参考答案</summary>

单纯 AO 不能，它主要编码遮挡比例；颜色溢出需要材质与光传输信息。

</details>

### 自测 6. β 是否就是路径发生的概率？

<details>
<summary>参考答案</summary>

不是。它包含物理散射权重与采样概率的倒数，可能大于 1。

</details>

### 自测 7. 俄罗斯轮盘是否降低方差？

<details>
<summary>参考答案</summary>

一般会增加单路径方差；它主要通过减少计算改善单位成本的效率。

</details>

### 自测 8. 为什么发光物体不能既直接加一次又在递归里无条件再加一次？

<details>
<summary>参考答案</summary>

可能把同一直接光路计算两遍；应分区或用满足正确权重规则的多策略估计。

</details>

### 自测 9. 连续方向采样能偶然撞中理想点光源吗？

<details>
<summary>参考答案</summary>

数学上概率为零，应直接采样点光源方向并采用对应的离散贡献公式。

</details>

### 自测 10. 把所有亮点剪掉是否仍无偏？

<details>
<summary>参考答案</summary>

通常不是，截断贡献改变期望；可作为有偏近似但必须明确说明。

</details>

### 自测 11. 把所有光线起点都偏移同一个大常数安全吗？

<details>
<summary>参考答案</summary>

不安全。小尺度细节会漏光，大尺度又可能仍不足，应考虑尺度与误差界。

</details>

### 自测 12. 一个均匀环境下的漫反射球上每点都会一样亮吗？

<details>
<summary>参考答案</summary>

若无其他遮挡、各点接收完整均匀半球且反照率相同，出射辐亮度相同；轮廓与背景仍取决于相机和环境。

</details>

### 自测 13. 第 1 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

只把环境常数调亮不能等价替代间接照明，因为遮挡、材质颜色与方向关系都丢失了。

再复算本节的例子：某方向自身发光 2、反射贡献 3，总量 5。关掉自发光后剩 3；检查 5-2=3，不能把发光重复放进反射项。

</details>

### 自测 14. 第 2 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

BRDF 数值可以超过 1；应检查加权半球积分是否超过 1，而不是逐点截断。

再复算本节的例子：ρ=0.6、E=10 W/m²，Lo=6/π≈1.910。对出射半球积分 Loπ=6 W/m²，恰为入射的 60%。

</details>

### 自测 15. 第 3 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

递归调用如果又把当前点传回，通常是自相交；应检查射线起点、方向与最小 t。

再复算本节的例子：一维简化反馈 L=1+0.5L，解为 2。代回 1+0.5×2=2；直接光只取 1，会漏掉后续反弹总和 1。

</details>

### 自测 16. 第 4 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

“一条路径多一次反弹一定更暗”不总成立；应理解整体能量传输的收敛条件，不能逐条比较不同路径。

再复算本节的例子：标量教学例 K=0.5、Le=1，前四项是 1+0.5+0.25+0.125=1.875，尾项 0.125，总和 2。代回几何级数验证。

</details>

### 自测 17. 第 5 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

本文为统一能量单位的教学推导；不要照抄原页中的 2π 后又使用 B=πL 的定义。

再复算本节的例子：两个无自发光以外的简化片满足 B1=1+0.5B2、B2=0.5B1，解 B1=4/3、B2=2/3。代入第二式得到 2/3，第一式得到 4/3。

</details>

### 自测 18. 第 6 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

每一跳都乘距离平方衰减会重复计算几何；方向形式的表面辐亮度传输不这样处理。

再复算本节的例子：两次余弦采样漫反射反照率为 0.8、0.5，β=0.4；命中 Le=10，贡献 4。展开 1×0.8×0.5×10 也为 4。

</details>

### 自测 19. 第 7 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

仅随机终止而不补偿会变暗；强行把过大贡献截断又会引入偏差。

再复算本节的例子：C=2、q=0.25，存活时返回 8，其余返回 0，期望 0.25×8=2。若忘除 q，期望只剩 0.5。

</details>

### 自测 20. 第 8 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

“加 NEE 后忽略所有灯命中”也错，会漏相机可见灯和镜面路径；必须按路径类型分割。

再复算本节的例子：若直接光真实贡献为 3，灯采样估计 3，BRDF 命中灯又完整加 3，会错误得到 6。均分两种无偏估计各乘 1/2，期望回到 3，但一般 MIS 权重更高效。

</details>

### 自测 21. 第 9 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

灯越多画面越暗，多半是漏除灯选择概率；镜子照到点灯为黑则检查 delta 支持。

再复算本节的例子：4 盏灯等概率选择，pj=1/4。条件贡献为 2，则选灯补偿后是 8；平均四种等贡献事件仍为总贡献 8。

</details>

### 自测 22. 第 10 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

明亮孤立点可能是合法高贡献，也可能是数值错误；先查 NaN、PDF 和几何，再考虑方差策略。

再复算本节的例子：从 16 增到 256 样本，样本数乘 16，典型标准差降为 1/4。反算 (√256)/(√16)=4。

</details>

### 自测 23. 第 11 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

阴影射线不设最大距离，会把光源背后的物体误认为遮挡物。

再复算本节的例子：光源距离 2 米，若最近遮挡 t=3，则不遮挡；若 t=1，则遮挡。分别检查是否属于 (epsilon,2-epsilon) 即可。

</details>

### 自测 24. 第 12 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

把 gamma 后像素作为能量测试对象会混淆非线性显示与物理积分；先检查线性缓冲。

再复算本节的例子：ρ=0.4、Lenv=5，输出应为 2。由 E=5π、BRDF=0.4/π 计算也是 2，是跨三讲的一致性检查。

</details>

### 自测 25. 本讲的输入、输出和中间表示各是什么？

<details>
<summary>参考答案</summary>

命中表面 → BRDF 连接入射与出射 → 光从别的表面来 → 渲染方程递归 → 随机生成路径 → 加权累积与终止。请沿箭头逐项解释，尤其说清中间表示的单位、坐标或概率测度；只复述名词不算掌握。

</details>

### 自测 26. 能否只用一张“看起来正确”的图片证明实现正确？

<details>
<summary>参考答案</summary>

不能。需要将关键关系拆成可预测的小输入，检查数值、边界与对照；随机方法还要区分一次结果与统计期望，显示图还需区分编码与原始数据。

</details>

## 17. 带走的结论与仍需练习的内容

- 不。面光源的直接照明就能产生软阴影；全局光照还包括多次散射。
- 不能。它们的方向分布根本不同，颜色只是部分参数。
- 因为每端都采用“从该表面向外”的方向约定。
- 因为纳入了原先被截断的非零高阶项；若重复计数，也可能错误变亮。
- 单纯 AO 不能，它主要编码遮挡比例；颜色溢出需要材质与光传输信息。
- 不是。它包含物理散射权重与采样概率的倒数，可能大于 1。
- 一般会增加单路径方差；它主要通过减少计算改善单位成本的效率。
- 可能把同一直接光路计算两遍；应分区或用满足正确权重规则的多策略估计。
- 数学上概率为零，应直接采样点光源方向并采用对应的离散贡献公式。
- 通常不是，截断贡献改变期望；可作为有偏近似但必须明确说明。
- 不安全。小尺度细节会漏光，大尺度又可能仍不足，应考虑尺度与误差界。
- 若无其他遮挡、各点接收完整均匀半球且反照率相同，出射辐亮度相同；轮廓与背景仍取决于相机和环境。

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

[原课件文件与版本记录](https://github.com/Teddy-Yangjiale/CS184/blob/main/CS184_2026/fa26/lectures/L16-17-global-illumination-path-tracing.pdf) · [课程官网](https://cs184.eecs.berkeley.edu/fa26/)

文件：`L16-17-global-illumination-path-tracing.pdf`；PDF 页数：173；SHA-256：`34cc6f266c19ea3be4d18f60efa5e10ee6197f83e1281e61b3d29a54a9e93fe7`。

“正文核对”表示本篇实际引用该页截图；“索引保留”包括演示、行政信息、补充、致谢与重复构建页，不表示逐页都有独立讲解。原视频的运动过程不能由静态 PDF 截图完整复现。

| PDF 页 | 原页可提取标题 | 本篇使用 |
| --- | --- | --- |
| 1 | Computer Graphics and Imaging | 索引保留 |
| 2 | Hard Shadows | 正文核对 |
| 3 | Image credit: Henrik Wann Jensen | 正文核对 |
| 4 | Image credit: Henrik Wann Jensen | 正文核对 |
| 5 | Image credit: Henrik Wann Jensen | 正文核对 |
| 6 | Visual Richness from Indirect Lighting | 正文核对 |
| 7 | Visual Richness from Complex Lighting | 索引保留 |
| 8 | Visual Richness from Complex Materials | 索引保留 |
| 9 | Cornell Box – Photograph vs Rendering | 正文核对 |
| 10 | Ray Tracer Samples Radiance Along A Ray | 索引保留 |
| 11 | Mini-Intro To Material Reflection | 索引保留 |
| 12 | Reflection | 索引保留 |
| 13 | Categories of Reflection Functions | 索引保留 |
| 14 | Materials: Mirror | 索引保留 |
| 15 | Materials: Diffuse | 索引保留 |
| 16 | Materials: Gold | 索引保留 |
| 17 | Materials: Plastic | 索引保留 |
| 18 | Materials: Red Semi-Gloss Paint | 索引保留 |
| 19 | Materials: Ford Mystic Lacquer Paint | 索引保留 |
| 20 | Reflection at a Point | 正文核对 |
| 21 | Definition: The bidirectional reflectance distribution function | 正文核对 |
| 22 | The Reflection Equation | 正文核对 |
| 23 | Solving the Reflection Equation | 正文核对 |
| 24 | Recall: Hemisphere vs Light Sampling | 正文核对 |
| 25 | Direct Lighting Pseudocode (Uniform Random Sampling) | 正文核对 |
| 26 | Direct Lighting Pseudocode (Importance Sampling of BRDF) | 正文核对 |
| 27 | Direct Lighting Pseudocode (Importance Sampling of Lights) | 正文核对 |
| 28 | Global Illumination: | 索引保留 |
| 29 | Again: Reflection Equation | 正文核对 |
| 30 | Challenge: This is Actually A Recursive Equation | 正文核对 |
| 31 | Transport Function & Radiance Invariance | 正文核对 |
| 32 | The Rendering Equation | 正文核对 |
| 33 | Radiosity | 正文核对 |
| 34 | from Hanrahan 2000 | 索引保留 |
| 35 | Assume Lambertian (diffuse reflections only) | 正文核对 |
| 36 | Rewrite in Terms of Radiosity (aka Radiant Existence) | 索引保留 |
| 37 | Discretize into Patches | 正文核对 |
| 38 | Discretize into Patches | 索引保留 |
| 39 | Discretize into Patches | 索引保留 |
| 40 | Hi = Ei +ρi∑ | 索引保留 |
| 41 | Hi = Ei +ρi∑ | 索引保留 |
| 42 | Hi = Ei +ρi∑ | 索引保留 |
| 43 | Radiosity Method | 正文核对 |
| 44 | Radiosity Method | 索引保留 |
| 45 | Progressive Radiosity | 正文核对 |
| 46 | Progressive Radiosity | 索引保留 |
| 47 | Touchup | 索引保留 |
| 48 | Other Things | 索引保留 |
| 49 | White Light by Paul Cocksedge | 索引保留 |
| 50 | White Light by Paul Cocksedge | 索引保留 |
| 51 | Hierarchical Radiosity | 索引保留 |
| 52 | Hierarchical Radiosity | 索引保留 |
| 53 | Ambient Occlusion | 正文核对 |
| 54 | Ambient Occlusion | 索引保留 |
| 55 | Ambient Occlusion | 正文核对 |
| 56 | Ambient Occlusion | 索引保留 |
| 57 | Light Transport Operators | 正文核对 |
| 58 | Operators Are Higher-Order Functions | 索引保留 |
| 59 | Linear Operators | 正文核对 |
| 60 | Light Transport Functions & Operators | 索引保留 |
| 61 | Reflection Operator | 正文核对 |
| 62 | Transport Operator | 正文核对 |
| 63 | Rendering Equation in Operator Notation | 正文核对 |
| 64 | Solving the Rendering Equation | 索引保留 |
| 65 | Solving the Rendering Equation | 索引保留 |
| 66 | Solution Intuition | 索引保留 |
| 67 | Solving the Rendering Equation | 索引保留 |
| 68 | Formal Solution | 正文核对 |
| 69 | Rendering Equation Solution | 正文核对 |
| 70 | 图像或演示页（请以原页视觉内容为准） | 索引保留 |
| 71 | K(Le) | 索引保留 |
| 72 | (K ◦K)(Le) | 索引保留 |
| 73 | (K ◦K ◦K)(Le) | 索引保留 |
| 74 | (K ◦K ◦K ◦K)(Le) | 索引保留 |
| 75 | (K ◦K ◦K ◦K ◦K)(Le) | 索引保留 |
| 76 | (K ◦K ◦K ◦K ◦K ◦K)(Le) | 索引保留 |
| 77 | i=0 | 正文核对 |
| 78 | i=0 | 索引保留 |
| 79 | i=0 | 索引保留 |
| 80 | i=0 | 索引保留 |
| 81 | i=0 | 索引保留 |
| 82 | i=0 | 索引保留 |
| 83 | i=0 | 索引保留 |
| 84 | Direct illumination | 索引保留 |
| 85 | One-bounce global illumination | 索引保留 |
| 86 | Two-bounce global illumination | 索引保留 |
| 87 | Four-bounce global illumination | 索引保留 |
| 88 | Eight-bounce global illumination | 索引保留 |
| 89 | Sixteen-bounce global illumination | 索引保留 |
| 90 | Light Paths | 正文核对 |
| 91 | 1-Bounce Path Connecting Ray to Light | 正文核对 |
| 92 | 1-Bounce Paths Connecting Ray to Light | 索引保留 |
| 93 | 2-Bounce Path Connecting Ray to Light | 索引保留 |
| 94 | 2-Bounce Paths Connecting Ray to Light | 正文核对 |
| 95 | 2-Bounce Paths Connecting Ray to Light | 索引保留 |
| 96 | 3-Bounce Paths Connecting Ray to Light | 索引保留 |
| 97 | 3-Bounce Path Connecting Ray to Light | 索引保留 |
| 98 | 3-Bounce Path Connecting Ray to Light | 正文核对 |
| 99 | 3-Bounce Path Connecting Ray to Light | 索引保留 |
| 100 | 3-Bounce Path Connecting Ray to Light | 索引保留 |
| 101 | 3-Bounce Path Connecting Ray to Light | 索引保留 |
| 102 | 3-Bounce Path Connecting Ray to Light | 索引保留 |
| 103 | Global Illumination Rendering | 正文核对 |
| 104 | Sum Over Paths | 索引保留 |
| 105 | EstRadianceIn(x, ω) | 正文核对 |
| 106 | Problem: Infinite Bounces of Light | 正文核对 |
| 107 | Russian Roulette | 正文核对 |
| 108 | Russian Roulette - Unbiased Random Termination | 正文核对 |
| 109 | Russian Roulette: Unbiased Random Termination | 正文核对 |
| 110 | i=0 | 索引保留 |
| 111 | Try 2: Russian Roulette Monte Carlo over Paths | 正文核对 |
| 112 | Recall: Importance Sampling | 索引保留 |
| 113 | Photon Mapping | 正文核对 |
| 114 | Photon Mapping | 索引保留 |
| 115 | Photon Mapping | 索引保留 |
| 116 | Photon Mapping | 正文核对 |
| 117 | Photon Mapping | 索引保留 |
| 118 | Photon Mapping | 索引保留 |
| 119 | Photon Mapping | 正文核对 |
| 120 | Path Tracing | 索引保留 |
| 121 | Path Tracing Overview | 正文核对 |
| 122 | Partitioning the Rendering Equation | 索引保留 |
| 123 | Partitioning the Rendering Equation | 索引保留 |
| 124 | Partitioning the Rendering Equation | 索引保留 |
| 125 | Partitioning the Rendering Equation | 索引保留 |
| 126 | Partitioning the Rendering Equation | 索引保留 |
| 127 | Consider Evaluation of &gt;1 Bounce of Light | 索引保留 |
| 128 | Partitioning the Rendering Equation | 正文核对 |
| 129 | ▪Sample incoming direction from some distribution | 索引保留 |
| 130 | Path Tracing Pseudocode | 正文核对 |
| 131 | Path Tracing Pseudocode | 正文核对 |
| 132 | Direct Lighting Pseudocode (Lights) | 正文核对 |
| 133 | Direct Lighting (0 and 1 Bounce Only) | 索引保留 |
| 134 | Path Tracing (All Bounces of Light) | 索引保留 |
| 135 | One sample (path) per pixel | 正文核对 |
| 136 | 32 samples (paths) per pixel | 正文核对 |
| 137 | 1024 samples (paths) per pixel | 正文核对 |
| 138 | Summary of Intuition on Global | 正文核对 |
| 139 | Summary of Intuition on G.I. & P.T. | 索引保留 |
| 140 | Summary of Intuition on G.I. & P.T. | 正文核对 |
| 141 | Summary of Intuition on G.I. & P.T. | 索引保留 |
| 142 | Summary of Intuition on G.I. & P.T. | 索引保留 |
| 143 | Summary of Intuition on G.I. & P.T. | 索引保留 |
| 144 | Summary of Intuition on G.I. & P.T. | 索引保留 |
| 145 | Implementation Notes | 正文核对 |
| 146 | Paths vs Trees | 正文核对 |
| 147 | 64 image samples x 1 light sample, 13.2 seconds | 正文核对 |
| 148 | 1 image sample x 64 light samples, 7.0 seconds | 正文核对 |
| 149 | 8 image samples x 8 light samples, 7.7 seconds | 正文核对 |
| 150 | Multiple Light Sources | 正文核对 |
| 151 | Multiple Light Sources (Single Sample) | 正文核对 |
| 152 | Point Lights / Ideal Specular Materials – Issues | 正文核对 |
| 153 | Point Lights / Ideal Specular Materials – Issues | 索引保留 |
| 154 | Point Lights / Ideal Specular Materials – Issues | 正文核对 |
| 155 | Point Lights / Ideal Specular Materials – Issues | 索引保留 |
| 156 | Point Lights / Ideal Specular Materials – Issues | 索引保留 |
| 157 | Point Lights / Ideal Specular Materials – Issues | 正文核对 |
| 158 | Numerical Precision Issues | 正文核对 |
| 159 | Numerical Precision Issues | 正文核对 |
| 160 | Noisy Shadows | 正文核对 |
| 161 | Noisy shadows because of | 正文核对 |
| 162 | Floating-Point Precision Remedies | 正文核对 |
| 163 | Floating-Point Precision Remedies | 正文核对 |
| 164 | Floating-Point Precision Remedies | 索引保留 |
| 165 | Floating-Point Precision Remedies | 正文核对 |
| 166 | Floating-Point Precision Remedies | 索引保留 |
| 167 | Remedy: Project Intersection Point to Surface | 正文核对 |
| 168 | Good Scenes for Path Tracing (Diffuse, Sky Lighting) | 正文核对 |
| 169 | Good Scenes for Path Tracing (Diffuse, Sky Lighting) | 索引保留 |
| 170 | Good Scenes for Path Tracing (Diffuse, Sky Lighting) | 索引保留 |
| 171 | Good Scenes for Path Tracing (Diffuse, Sky Lighting) | 索引保留 |
| 172 | A Challenging Scene for Path Tracing – Why? | 正文核对 |
| 173 | Acknowledgments | 索引保留 |

外部核对：[PBRT 4e：Path Tracing](https://pbr-book.org/4ed/Light_Transport_I_Surface_Reflection/Path_Tracing)。用于核对随机终止与路径采样的解释；本文标量例子为自行推导。
