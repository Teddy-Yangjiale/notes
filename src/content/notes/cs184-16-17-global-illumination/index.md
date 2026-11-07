---
title: "CS184 第 16–17 讲：全局光照与路径追踪"
date: 2026-11-07
updated: 2026-11-07
summary: "命中表面 → BRDF 连接入射与出射 → 光从别的表面来 → 渲染方程递归 → 随机生成路径 → 加权累积与终止。以原课件为依据，配 20 张可编辑图解、12 个数值例子、26 道带答案自测与 PDF 全页索引。"
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
| 图解 | 12 张概念关系图 + 8 张几何或数值图，均有原生可编辑 PPTX |
| 手算 | 12 个带输入、结果和回代检查的教学例子 |
| 复习 | 26 道自测及答案，末尾保留全页索引 |
| 运行证据 | 数值核对脚本覆盖解析小模型，不代表完整渲染器或模拟器已经实现 |

[下载本篇 20 张可编辑图解（PPTX 与操作 JSON）](/notes/cs184/figures/16-editable.zip)

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

## 13. 把十二个数值例子连成检查顺序

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
