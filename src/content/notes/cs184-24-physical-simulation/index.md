---
title: "CS184 春季 L24：物理模拟，从弹簧到稳定的时间积分"
date: 2026-11-07
updated: 2026-11-07
summary: "选择状态 → 建立受力 → 写成微分方程 → 离散时间 → 分析稳定性 → 施加碰撞和约束。以原课件为依据，配 20 张可编辑图解、12 个数值例子、26 道带答案自测与 PDF 全页索引。"
tags: ["计算机图形学", "CS184", "课程笔记"]
series: "cs184"
order: 24
shortTitle: "春季 L24"
---

> UC Berkeley · CS184/284A · Spring 2026 · 文件标识 `SP26-L24-physical-simulation.pdf`。
> 本文的 **pN 一律是 PDF 的第 N 页**，不是封面讲次或页脚旧编号。文件名与封面可能不同，以下均按文件和页码回查。

## 0. 先抓住这一条推理链

```text
选择状态
    ↓
建立受力
    ↓
写成微分方程
    ↓
离散时间
    ↓
分析稳定性
    ↓
施加碰撞和约束
```

这篇笔记的阅读顺序是：先理解输入和输出，再确认公式的条件，最后用小数值检查。
正文将课件概念、补充推导和教学例子分开；示意图中的理想几何与数字不冒充真实实验测量。

| 内容 | 本文提供什么 |
|---|---|
| 来源 | Spring 2026，PDF 共 116 页；正文选择 57 张关键页 |
| 图解 | 12 张概念关系图 + 8 张几何或数值图，均有原生可编辑 PPTX |
| 手算 | 12 个带输入、结果和回代检查的教学例子 |
| 复习 | 26 道自测及答案，末尾保留全页索引 |
| 运行证据 | 数值核对脚本覆盖解析小模型，不代表完整渲染器或模拟器已经实现 |

[下载本篇 20 张可编辑图解（PPTX 与操作 JSON）](/notes/cs184/figures/24-editable.zip)

### 课件与推导的使用边界

课件截图用于对照原始定义与几何；正文用中文解释关系，并提供必要的修正与推导。
后续专题按本地文件的学期和编号组织，不假定它们与秋季一一对应。
若只做第一遍学习，先读每节前两段和数值例子，再展开原页核对。

### 与前面哪一讲接上

先回顾[相关前置讲义](/notes/cs184-21-23-animation/)。本篇在已有表示与数学工具上增加新变量或新约束，而不是另起一套互不相关的公式。

## 1. 模拟从哪些状态开始？

动画课可以直接控制姿态，物理模拟则从状态和力推下一时刻。粒子常用位置 x、速度 v、质量 m，合力决定加速度。

将二阶位置方程改写为一阶状态系统后，显式、隐式和其他积分器都可以用同一接口。渲染只读取状态，显示帧率不应偷偷改变模拟单位。

![概念关系：模拟从哪些状态开始？](diagrams/d01-relation.png)

*读图：当前状态 → 计算合力 → 状态变化率。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| x | m |
| v | m/s |
| F | N |
| m | kg |
| 状态 | 位置与速度一起更新 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
\dot x=v,\qquad \dot v=F(x,v,t)/m
$$

### 🔧 手算 1：把关系落到数字上

m=2 kg、F=6 N，加速度 3 m/s²。0.1 秒内速度变化近似 0.3 m/s；用 mΔv/Δt 得回 6 N。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 0.1 秒内速度变化近似 0.3 m/s；用 mΔv/Δt 得回 6 N。 |
| 适用边界 | 质量为零不能直接做除法；固定点一般用逆质量零表示并跳过动力学更新。 |

### ⚠️ 易错点：先识别症状与假设

质量为零不能直接做除法；固定点一般用逆质量零表示并跳过动力学更新。

### 停下来解释一次

**问题：相同重力场中质量加倍，加速度是否加倍？**

<details>
<summary>展开参考回答</summary>

不。重力也随质量加倍，F/m 仍为相同的 g。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Physically Based Animation

*PDF p2 · 对应本节：模拟从哪些状态开始？*

![PDF p2：Physically Based Animation](images/p002.png)

#### Particle Systems

*PDF p7 · 对应本节：模拟从哪些状态开始？*

![PDF p7：Particle Systems](images/p007.png)

#### • Single particles are very simple

*PDF p10 · 对应本节：模拟从哪些状态开始？*

![PDF p10：• Single particles are very simple](images/p010.png)

#### Basic Particles

*PDF p12 · 对应本节：模拟从哪些状态开始？*

![PDF p12：Basic Particles](images/p012.png)

#### Dot Notation for Derivatives

*PDF p13 · 对应本节：模拟从哪些状态开始？*

![PDF p13：Dot Notation for Derivatives](images/p013.png)

#### Simple Gravity

*PDF p14 · 对应本节：模拟从哪些状态开始？*

![PDF p14：Simple Gravity](images/p014.png)

</details>

## 2. 弹簧为什么要有静止长度？

零静止长度弹簧总想把两点拉到一起，非零静止长度则在长度超过 l0 时拉回、短于 l0 时推开。力方向沿连线，大小由伸长量决定。

先明确力作用在哪个端点，再写符号。两端内力应相反，才能保证系统整体动量不凭空变化；零长度附近需要防止方向归一化除零。

![概念关系：弹簧为什么要有静止长度？](diagrams/d02-relation.png)

*读图：当前长度 → 减去静止长度 → 成对恢复力。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| k | N/m |
| ell0 | 静止长度 |
| Fa | 作用于 a 的力 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
F_a=k(\ell-\ell_0)\frac{b-a}{\ell},\quad F_b=-F_a,\quad\ell=\|b-a\|
$$

### 🔧 手算 2：把关系落到数字上

a=0、b=1.2 m、l0=1 m、k=100 N/m，则 Fa=+20 N、Fb=-20 N，合力为零。压缩到 0.8 m 时 Fa=-20 N。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 压缩到 0.8 m 时 Fa=-20 N。 |
| 适用边界 | 把方向或伸长量符号写反，弹簧会越拉越远；用伸长和压缩两个例子同时检查。 |

![几何或数值解释 1](diagrams/d13-spring.png)

*弹簧内力成对反向；压缩时两端受力反转。*

### ⚠️ 易错点：先识别症状与假设

把方向或伸长量符号写反，弹簧会越拉越远；用伸长和压缩两个例子同时检查。

### 停下来解释一次

**问题：力为零时弹簧是否一定长度为零？**

<details>
<summary>展开参考回答</summary>

不是。非零静止长度弹簧在长度等于 l0 时恢复力为零。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### A Simple Spring

*PDF p28 · 对应本节：弹簧为什么要有静止长度？*

![PDF p28：A Simple Spring](images/p028.png)

#### A Simple Spring

*PDF p30 · 对应本节：弹簧为什么要有静止长度？*

![PDF p30：A Simple Spring](images/p030.png)

#### A Simple Spring

*PDF p31 · 对应本节：弹簧为什么要有静止长度？*

![PDF p31：A Simple Spring](images/p031.png)

#### Non-Zero Length Spring

*PDF p32 · 对应本节：弹簧为什么要有静止长度？*

![PDF p32：Non-Zero Length Spring](images/p032.png)

#### Non-Zero Length Springs

*PDF p34 · 对应本节：弹簧为什么要有静止长度？*

![PDF p34：Non-Zero Length Springs](images/p034.png)

#### Comments on Springs

*PDF p35 · 对应本节：弹簧为什么要有静止长度？*

![PDF p35：Comments on Springs](images/p035.png)

</details>

## 3. 阻尼为什么要区分整体运动与相对运动？

简单阻力 -cv 会减慢粒子相对世界的运动；弹簧内部阻尼只惩罚两端沿弹簧方向的相对速度，因此整体平移不应被削弱。

以 e=(b-a)/长度为方向、Fa 为 a 端受力，内部阻尼写成 c((vb-va)·e)e，另一端取反。这个符号可由总功率不大于零验证，比死记课件中的端点下标更可靠。

![概念关系：阻尼为什么要区分整体运动与相对运动？](diagrams/d03-relation.png)

*读图：两端相对速度 → 投影到弹簧方向 → 只耗散内部运动。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| c | 阻尼系数 |
| P | 两端力做功率之和 |
| e | 单位弹簧方向 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
F_{a,d}=c[(v_b-v_a)\cdot e]e,\qquad P_d=-c[(v_b-v_a)\cdot e]^2\le0
$$

### 🔧 手算 3：把关系落到数字上

一维 va=0、vb=2、c=3，Fa=6、Fb=-6，总功率 6×0-6×2=-12。若两端都以 2 移动，相对速度零，阻尼力也为零。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 若两端都以 2 移动，相对速度零，阻尼力也为零。 |
| 适用边界 | 内部阻尼符号反了会注入能量；课件不同端点标记下需重新推功率。 |

![几何或数值解释 5](diagrams/d17-tree.png)

*内部阻尼只惩罚相对伸缩，不应阻止刚体平移。*

### ⚠️ 易错点：先识别症状与假设

内部阻尼符号反了会注入能量；课件不同端点标记下需重新推功率。

### 停下来解释一次

**问题：内部阻尼会阻止整个系统刚体平移吗？**

<details>
<summary>展开参考回答</summary>

理想成对相对速度阻尼不会，整体平移不改变弹簧长度。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Simple Motion Damping

*PDF p36 · 对应本节：阻尼为什么要区分整体运动与相对运动？*

![PDF p36：Simple Motion Damping](images/p036.png)

#### Simple Motion Damping

*PDF p37 · 对应本节：阻尼为什么要区分整体运动与相对运动？*

![PDF p37：Simple Motion Damping](images/p037.png)

#### Internal Damping for Spring

*PDF p38 · 对应本节：阻尼为什么要区分整体运动与相对运动？*

![PDF p38：Internal Damping for Spring](images/p038.png)

</details>

## 4. 网格变细为什么材料会变硬或变软？

把同一个物体分成更多弹簧并继续使用相同 k，会改变整体等效刚度与质量分布。分辨率不是只改变外观，还改变离散模型。

应从长度、截面积、应变或连续材料参数出发缩放离散参数。只有水平和竖直边的方格可能容易剪切，加斜向弹簧才能约束另一类变形。

![概念关系：网格变细为什么材料会变硬或变软？](diagrams/d04-relation.png)

*读图：离散分辨率 → 参数随尺度变化 → 一致的宏观材料。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| epsilon | 应变 |
| 串联刚度 | 一维教学模型 |
| 适用 | 小形变线性弹簧 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
\varepsilon=\frac{\ell-\ell_0}{\ell_0},\qquad k_{series}=\left(\sum_i\frac1{k_i}\right)^{-1}
$$

### 🔧 手算 4：把关系落到数字上

原弹簧 k=10，拆成两段串联要各取 k=20，等效为 1/(1/20+1/20)=10。若各取 10，整体变为 5。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 若各取 10，整体变为 5。 |
| 适用边界 | 布料参数缩放不能一律照搬一维串联公式；还要看拓扑、面积与弯曲模型。 |

![几何或数值解释 6](diagrams/d18-bars.png)

*一维串联模型中，细分时需调整弹簧常数以保持整体刚度。*

### ⚠️ 易错点：先识别症状与假设

布料参数缩放不能一律照搬一维串联公式；还要看拓扑、面积与弯曲模型。

### 停下来解释一次

**问题：更多弹簧是否自然意味着更真实？**

<details>
<summary>展开参考回答</summary>

不。若材料参数与约束不一致，只是更精细地模拟错误材料。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Spring Constants

*PDF p39 · 对应本节：网格变细为什么材料会变硬或变软？*

![PDF p39：Spring Constants](images/p039.png)

#### Spring Constants

*PDF p40 · 对应本节：网格变细为什么材料会变硬或变软？*

![PDF p40：Spring Constants](images/p040.png)

#### Spring Constants

*PDF p41 · 对应本节：网格变细为什么材料会变硬或变软？*

![PDF p41：Spring Constants](images/p041.png)

#### Spring Constants

*PDF p42 · 对应本节：网格变细为什么材料会变硬或变软？*

![PDF p42：Spring Constants](images/p042.png)

#### Structures from Springs

*PDF p43 · 对应本节：网格变细为什么材料会变硬或变软？*

![PDF p43：Structures from Springs](images/p043.png)

#### Structures from Springs

*PDF p44 · 对应本节：网格变细为什么材料会变硬或变软？*

![PDF p44：Structures from Springs](images/p044.png)

#### Behavior is determined by structure linkages

*PDF p45 · 对应本节：网格变细为什么材料会变硬或变软？*

![PDF p45：Behavior is determined by structure linkages](images/p045.png)

#### Edge Springs

*PDF p48 · 对应本节：网格变细为什么材料会变硬或变软？*

![PDF p48：Edge Springs](images/p048.png)

</details>

## 5. 显式 Euler 一步究竟做了什么？

显式 Euler 用旧状态的导数预测新状态。位置用旧速度，速度用旧位置和旧速度算出的加速度；必须保留旧值，避免不知不觉改成其他积分器。

它是局部切线近似，一步截断误差会随时间累积。小步可以减小有限时间误差，但某些无阻尼振荡系统对任何非零步长都会长期增能。

![概念关系：显式 Euler 一步究竟做了什么？](diagrams/d05-relation.png)

*读图：旧状态导数 → 线性外推一步 → 新的状态。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| h | 时间步长 |
| 下标 n | 旧状态 |
| 更新顺序 | 两式都读旧值 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
x_{n+1}=x_n+h v_n,\qquad v_{n+1}=v_n+h a_n
$$

### 🔧 手算 5：把关系落到数字上

x=1、v=0、a=-1、h=0.1，则 x'=1、v'=-0.1。若先更新 v 再用新 v 更新位置，会得到 x'=0.99，是另一方法。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 若先更新 v 再用新 v 更新位置，会得到 x'=0.99，是另一方法。 |
| 适用边界 | 代码语句顺序决定数学方法，不能都叫“Euler”而不注明。 |

### ⚠️ 易错点：先识别症状与假设

代码语句顺序决定数学方法，不能都叫“Euler”而不注明。

### 停下来解释一次

**问题：Euler 方法是不是直接精确求解牛顿定律？**

<details>
<summary>展开参考回答</summary>

不是。定律定义连续模型，积分器只是有限步长下的数值近似。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Euler’s Method

*PDF p58 · 对应本节：显式 Euler 一步究竟做了什么？*

![PDF p58：Euler’s Method](images/p058.png)

#### Single Particle Simulation

*PDF p59 · 对应本节：显式 Euler 一步究竟做了什么？*

![PDF p59：Single Particle Simulation](images/p059.png)

#### Ordinary Differential Equation (ODE)

*PDF p65 · 对应本节：显式 Euler 一步究竟做了什么？*

![PDF p65：Ordinary Differential Equation (ODE)](images/p065.png)

#### Ordinary Differential Equation (ODE)

*PDF p66 · 对应本节：显式 Euler 一步究竟做了什么？*

![PDF p66：Ordinary Differential Equation (ODE)](images/p066.png)

#### Solving for Particle Position

*PDF p69 · 对应本节：显式 Euler 一步究竟做了什么？*

![PDF p69：Solving for Particle Position](images/p069.png)

</details>

## 6. 为什么一个无阻尼弹簧会自己加速？

对 x''=-ω²x，显式 Euler 的状态更新会让相空间轨迹向外螺旋。力在一步内已经变化，算法仍使用旧力，导致离散能量系统性增加。

这说明“爆炸”不一定是物理方程错，也可能是积分器与步长不适合。缩步可延缓长期增能，却不能把无阻尼振子的显式 Euler 变成真正能量守恒方法。

![概念关系：为什么一个无阻尼弹簧会自己加速？](diagrams/d06-relation.png)

*读图：旧力被保持 → 离散能量增加 → 振幅逐渐扩大。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| omega² | k/m |
| E | 单位质量能量 |
| 前提 | 线性无阻尼振子与显式 Euler |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
E_{n+1}=(1+h^2\omega^2)E_n,\qquad E=\frac12(v^2+\omega^2x^2)
$$

### 🔧 手算 6：把关系落到数字上

ω=1、h=0.1、x=1、v=0，初能 0.5，新能 (1²+0.1²)/2=0.505，增长因子 1.01。100 步因子约 2.705。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 100 步因子约 2.705。 |
| 适用边界 | 添加很强阻尼可能掩盖积分错误，但会改变物理效果；应先辨认能量增长机制。 |

![几何或数值解释 2](diagrams/d14-phase.png)

*同一无阻尼振子、h=0.1、160 步，轨迹展示增能、近似有界与数值耗散；横纵是位置与速度相图。*

### ⚠️ 易错点：先识别症状与假设

添加很强阻尼可能掩盖积分错误，但会改变物理效果；应先辨认能量增长机制。

### 停下来解释一次

**问题：把步长减半能使这一增长因子怎样变化？**

<details>
<summary>展开参考回答</summary>

单步增长项 h²ω² 变为四分之一；但相同总时长需要更多步，仍要分析累计误差。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Euler’s Method - Errors

*PDF p70 · 对应本节：为什么一个无阻尼弹簧会自己加速？*

![PDF p70：Euler’s Method - Errors](images/p070.png)

#### Errors and Instability

*PDF p74 · 对应本节：为什么一个无阻尼弹簧会自己加速？*

![PDF p74：Errors and Instability](images/p074.png)

#### Errors and Instability

*PDF p75 · 对应本节：为什么一个无阻尼弹簧会自己加速？*

![PDF p75：Errors and Instability](images/p075.png)

#### Instability of Forward Euler Method

*PDF p78 · 对应本节：为什么一个无阻尼弹簧会自己加速？*

![PDF p78：Instability of Forward Euler Method](images/p078.png)

#### Instability Example (Spring)

*PDF p79 · 对应本节：为什么一个无阻尼弹簧会自己加速？*

![PDF p79：Instability Example (Spring)](images/p079.png)

#### Instability Example (Spring)

*PDF p80 · 对应本节：为什么一个无阻尼弹簧会自己加速？*

![PDF p80：Instability Example (Spring)](images/p080.png)

#### Instability Example (Spring)

*PDF p83 · 对应本节：为什么一个无阻尼弹簧会自己加速？*

![PDF p83：Instability Example (Spring)](images/p083.png)

</details>

## 7. 改进与半隐式方法差在哪里？

课件的 modified Euler 使用起点与预测终点信息修正斜率；实践中还常见先更新速度再更新位置的半隐式 Euler。名称相近不代表公式相同。

对振荡系统，半隐式方法在一定步长范围内通常比显式 Euler 稳定，但不能宣称任意大步都安全。比较时应列出具体更新式和同一能量曲线。

![概念关系：改进与半隐式方法差在哪里？](diagrams/d07-relation.png)

*读图：先更新速度 → 用新速度更新位置 → 改变离散稳定性。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| 方法 | 半隐式 Euler，教学补充 |
| h | 步长 |
| 线性振子稳定范围 | 0<h omega<2 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
v_{n+1}=v_n-h\omega^2x_n,\qquad x_{n+1}=x_n+h v_{n+1}
$$

### 🔧 手算 7：把关系落到数字上

x=1、v=0、ω=1、h=0.1，则 v'=-0.1、x'=0.99，新能 0.49505。它不是精确守恒，但与显式第一步增能不同。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 它不是精确守恒，但与显式第一步增能不同。 |
| 适用边界 | 不要把一次能量下降当作长期稳定证明；需分析更新矩阵或观察长时间界限。 |

![几何或数值解释 3](diagrams/d15-bars.png)

*相同初值 x=1,v=0,h=0.1 下的一步能量，不能用单步结果替代长期稳定分析。*

### ⚠️ 易错点：先识别症状与假设

不要把一次能量下降当作长期稳定证明；需分析更新矩阵或观察长时间界限。

### 停下来解释一次

**问题：半隐式 Euler 与隐式 Euler 是否相同？**

<details>
<summary>展开参考回答</summary>

不是。前者仍可显式逐项计算，后者通常需求解未来状态方程。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Some Methods to Combat Instability

*PDF p84 · 对应本节：改进与半隐式方法差在哪里？*

![PDF p84：Some Methods to Combat Instability](images/p084.png)

#### Modified Euler

*PDF p85 · 对应本节：改进与半隐式方法差在哪里？*

![PDF p85：Modified Euler](images/p085.png)

#### Midpoint Method

*PDF p86 · 对应本节：改进与半隐式方法差在哪里？*

![PDF p86：Midpoint Method](images/p086.png)

</details>

## 8. 自适应步长为什么要比较两种结果？

一次大步和两次半步对同一个终点给出不同近似，差值可以估计局部误差趋势。误差太大就缩小步长，小到足够安全才接受。

自适应不是只看粒子速度；刚性力、碰撞与约束也可能要求更小步。真正的误差估计还依赖积分器阶数，不能把差值无条件当精确误差。

![概念关系：自适应步长为什么要比较两种结果？](diagrams/d08-relation.png)

*读图：一步预测 → 两半步预测 → 比较并调整步长。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| y | 完整状态 |
| 两个结果 | 相同起点与终点 |
| 用途 | 步长控制指标 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
e_{local}\approx\|y_{h}-y_{h/2,h/2}\|
$$

### 🔧 手算 8：把关系落到数字上

一步结果 1.02，两半步结果 1.005，差为 0.015。容差 0.01 时应拒绝或缩步；容差不是“每秒总误差”。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 容差 0.01 时应拒绝或缩步；容差不是“每秒总误差”。 |
| 适用边界 | 只比较位置可能漏掉速度误差；不同量的尺度也需归一化。 |

![几何或数值解释 7](diagrams/d19-backtrace.png)

*自适应步长比较同起点同终点的两种离散近似，而不是比较不同时间的位置。*

### ⚠️ 易错点：先识别症状与假设

只比较位置可能漏掉速度误差；不同量的尺度也需归一化。

### 停下来解释一次

**问题：自适应方法能自动发现所有碰撞吗？**

<details>
<summary>展开参考回答</summary>

不能保证。离散碰撞检测仍可能隧穿，需要合适的连续检测或步长约束。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Adaptive Step Size

*PDF p87 · 对应本节：自适应步长为什么要比较两种结果？*

![PDF p87：Adaptive Step Size](images/p087.png)

#### Adaptive Step Size

*PDF p88 · 对应本节：自适应步长为什么要比较两种结果？*

![PDF p88：Adaptive Step Size](images/p088.png)

#### Adaptive Step Size

*PDF p89 · 对应本节：自适应步长为什么要比较两种结果？*

![PDF p89：Adaptive Step Size](images/p089.png)

</details>

## 9. 隐式 Euler 为什么要解方程？

隐式 Euler 使用未来状态的导数，未知量出现在等式两边，必须解线性或非线性系统。它能抑制某些刚性系统的数值爆炸，但会引入数值阻尼。

“无条件稳定”需要说明系统与稳定性定义，绝不等于任意步长都准确。一个钟摆用过大步长可能稳定地停住，画面不爆炸但动力学已经不对。

![概念关系：隐式 Euler 为什么要解方程？](diagrams/d09-relation.png)

*读图：未来状态未知 → 建立耦合方程 → 数值求解新状态。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| 公式 | 由线性振子的隐式 Euler 联立消元 |
| 非线性系统 | 通常迭代求解 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
x_{n+1}=\frac{x_n+h v_n}{1+h^2\omega^2},\qquad v_{n+1}=v_n-h\omega^2x_{n+1}
$$

### 🔧 手算 9：把关系落到数字上

x=1、v=0、ω=1、h=1，得到 x'=0.5、v'=-0.5，能量 0.25，原来为 0.5。代入 x'=1+v'=0.5 验证。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 代入 x'=1+v'=0.5 验证。 |
| 适用边界 | 求解器没收敛就接受未来状态，可能既不准确也不稳定；应监测残差。 |

### ⚠️ 易错点：先识别症状与假设

求解器没收敛就接受未来状态，可能既不准确也不稳定；应监测残差。

### 停下来解释一次

**问题：隐式方法更稳定是否意味着总是首选？**

<details>
<summary>展开参考回答</summary>

不。求解成本、阻尼、实现复杂度和目标效果共同决定选择。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Implicit methods

*PDF p90 · 对应本节：隐式 Euler 为什么要解方程？*

![PDF p90：Implicit methods](images/p090.png)

#### Implicit methods

*PDF p91 · 对应本节：隐式 Euler 为什么要解方程？*

![PDF p91：Implicit methods](images/p091.png)

#### Implicit Euler Method

*PDF p92 · 对应本节：隐式 Euler 为什么要解方程？*

![PDF p92：Implicit Euler Method](images/p092.png)

</details>

## 10. 位置约束怎样把布料拉回合法状态？

位置式方法先预测位置，再投影满足长度、碰撞等约束，最后用位置变化重建速度。它强调约束满足与视觉稳定，不能直接等同于准确求解某个连续弹性模型。

约束迭代次数、顺序、时间步长和质量都会影响结果；固定点逆质量为零，把所有修正分给可移动点。Verlet 与 PBD 相关但不是同一个概念。

![概念关系：位置约束怎样把布料拉回合法状态？](diagrams/d10-relation.png)

*读图：预测位置 → 约束投影 → 由新位置重建速度。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| p | 预测并修正的位置 |
| h | 时间步长 |
| 约束投影 | 先于速度重建 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
v_{n+1}=\frac{p_{corrected}-x_n}{h}
$$

### 🔧 手算 10：把关系落到数字上

两等质量点在 0 和 1.4，目标距离 1，各向内移动 0.2，得到 0.2 和 1.2。新距离 1，质心仍为 0.7。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 新距离 1，质心仍为 0.7。 |
| 适用边界 | 只修位置不修速度，会让下一帧重新冲回非法状态并产生抖动。 |

![几何或数值解释 4](diagrams/d16-backtrace.png)

*两端各移动 0.2，将距离 1.4 修回 1，同时保持质心。*

### ⚠️ 易错点：先识别症状与假设

只修位置不修速度，会让下一帧重新冲回非法状态并产生抖动。

### 停下来解释一次

**问题：固定一端时还能两边各修一半吗？**

<details>
<summary>展开参考回答</summary>

不能。固定端保持不动，修正按逆质量分配给可动端。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Strain Limiting

*PDF p49 · 对应本节：位置约束怎样把布料拉回合法状态？*

![PDF p49：Strain Limiting](images/p049.png)

#### Strain Limiting

*PDF p50 · 对应本节：位置约束怎样把布料拉回合法状态？*

![PDF p50：Strain Limiting](images/p050.png)

#### Position-Based / Verlet Integration

*PDF p93 · 对应本节：位置约束怎样把布料拉回合法状态？*

![PDF p93：Position-Based / Verlet Integration](images/p093.png)

#### Position-Based / Verlet Integration

*PDF p94 · 对应本节：位置约束怎样把布料拉回合法状态？*

![PDF p94：Position-Based / Verlet Integration](images/p094.png)

</details>

## 11. 碰撞与群体行为怎样加入同一框架？

粒子系统可以加碰撞约束，也可以用局部规则模拟群体。鸟群常用聚合、分离与速度对齐；它们是行为模型，不是每项都来自真实物理力。

碰撞响应应明确法向与切向处理，恢复系数控制法向反弹，摩擦处理切向。渲染粒子的形状并不改变其动力学模型，球体外观不保证碰撞也按球处理。

![概念关系：碰撞与群体行为怎样加入同一框架？](diagrams/d11-relation.png)

*读图：局部邻域与接触 → 附加力或约束 → 统一时间推进。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| vn | 撞击前法向速度 |
| e | 恢复系数 |
| 忽略 | 旋转与复杂接触耦合 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
v_n'=-e v_n,\qquad 0\le e\le1
$$

### 🔧 手算 11：把关系落到数字上

向地面法向速度 -4 m/s、e=0.5，反弹 +2 m/s。法向动能比为 (2/4)²=1/4，其余能量被耗散。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 法向动能比为 (2/4)²=1/4，其余能量被耗散。 |
| 适用边界 | 只翻转全部速度会连切向运动一起反向；应先分解法向与切向。 |

![几何或数值解释 8](diagrams/d20-reflection.png)

*碰撞响应需分解法向和切向，不能简单翻转整个速度向量。*

### ⚠️ 易错点：先识别症状与假设

只翻转全部速度会连切向运动一起反向；应先分解法向与切向。

### 停下来解释一次

**问题：鸟群规则能否当作生物行为的精确证明？**

<details>
<summary>展开参考回答</summary>

不能。它是产生某些集体运动特征的计算模型，适用性需要额外验证。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Other Particle Systems

*PDF p95 · 对应本节：碰撞与群体行为怎样加入同一框架？*

![PDF p95：Other Particle Systems](images/p095.png)

#### Example: Granular Materials

*PDF p98 · 对应本节：碰撞与群体行为怎样加入同一框架？*

![PDF p98：Example: Granular Materials](images/p098.png)

#### Example: Flocking Birds

*PDF p100 · 对应本节：碰撞与群体行为怎样加入同一框架？*

![PDF p100：Example: Flocking Birds](images/p100.png)

#### Simulated Flocking as an ODE

*PDF p102 · 对应本节：碰撞与群体行为怎样加入同一框架？*

![PDF p102：Simulated Flocking as an ODE](images/p102.png)

#### Simulated Flocking as an ODE

*PDF p108 · 对应本节：碰撞与群体行为怎样加入同一框架？*

![PDF p108：Simulated Flocking as an ODE](images/p108.png)

#### Example: Crowds

*PDF p110 · 对应本节：碰撞与群体行为怎样加入同一框架？*

![PDF p110：Example: Crowds](images/p110.png)

#### Example: Crowds + “Rock” Dynamics

*PDF p112 · 对应本节：碰撞与群体行为怎样加入同一框架？*

![PDF p112：Example: Crowds + “Rock” Dynamics](images/p112.png)

</details>

## 12. 稳定、准确、守恒如何分开验收？

稳定指误差不失控，准确指接近目标连续解，守恒则检查特定不变量。三者相关但不能互换。无外力系统检查动量，保守弹簧检查能量，阻尼系统则检查能量不应上升。

建议先跑单粒子自由落体、单弹簧与双粒子内力，再扩到布料。随笔记的脚本验证这些小模型，不宣称已经完成高质量布料求解器。

![概念关系：稳定、准确、守恒如何分开验收？](diagrams/d12-relation.png)

*读图：解析小模型 → 误差与不变量 → 复杂场景验证。箭头表示本节的推理或处理顺序，具体条件见正文。*

### 先读符号与条件

| 符号 / 条件 | 含义 |
| --- | --- |
| a | 恒定加速度 |
| 解析解 | 用于数值误差对照 |
| 条件 | 没有碰撞与其他力 |

### 核心关系与推导入口

以下关系使用上述条件；标为教学简化或补充的内容是为理解而推导，不是逐字转录课件。

$$
x(t)=x_0+v_0t+\tfrac12at^2
$$

### 🔧 手算 12：把关系落到数字上

x0=0、v0=0、a=-10、t=0.2，精确位移 -0.2 米。一步显式 Euler 位置仍 0；两步 h=0.1 得 -0.1，能看出缩步改善但仍有误差。

| 检查步骤 | 操作 |
| --- | --- |
| 输入 | 先从例子中抄下给定量及单位，不引入未给定的数值。 |
| 计算 | 按本节关系求中间量，再得到结果；不要在第一步就做显示裁剪或整数舍入。 |
| 回查 | 一步显式 Euler 位置仍 0；两步 h=0.1 得 -0.1，能看出缩步改善但仍有误差。 |
| 适用边界 | 截图看着平稳不能证明积分正确；记录轨迹、误差与能量才可区分机制。 |

### ⚠️ 易错点：先识别症状与假设

截图看着平稳不能证明积分正确；记录轨迹、误差与能量才可区分机制。

### 停下来解释一次

**问题：为什么不先用一整件衣服调积分器？**

<details>
<summary>展开参考回答</summary>

复杂约束会掩盖错误来源，最小模型更容易判断力、符号、时间步和求解器各自的问题。

</details>

<details>
<summary>展开原课件关键页，对照术语与图形</summary>

#### Errors and Instability

*PDF p74 · 对应本节：稳定、准确、守恒如何分开验收？*

![PDF p74：Errors and Instability](images/p074.png)

#### Errors and Instability

*PDF p75 · 对应本节：稳定、准确、守恒如何分开验收？*

![PDF p75：Errors and Instability](images/p075.png)

#### Just Scratching the Surface…

*PDF p114 · 对应本节：稳定、准确、守恒如何分开验收？*

![PDF p114：Just Scratching the Surface…](images/p114.png)

#### Things to Remember

*PDF p115 · 对应本节：稳定、准确、守恒如何分开验收？*

![PDF p115：Things to Remember](images/p115.png)

</details>

## 13. 把十二个数值例子连成检查顺序

先手算再运行。随仓库提供的 `scripts/cs184-numerical-checks.py` 是小模型验证，不依赖 GPU，也不修改服务器配置。它不能替代完整渲染场景或模拟系统的验证。

| 顺序 | 本节关系 | 最容易漏掉的约定 |
| --- | --- | --- |
| 1 | 模拟从哪些状态开始？ | 状态：位置与速度一起更新 |
| 2 | 弹簧为什么要有静止长度？ | Fa：作用于 a 的力 |
| 3 | 阻尼为什么要区分整体运动与相对运动？ | e：单位弹簧方向 |
| 4 | 网格变细为什么材料会变硬或变软？ | 适用：小形变线性弹簧 |
| 5 | 显式 Euler 一步究竟做了什么？ | 更新顺序：两式都读旧值 |
| 6 | 为什么一个无阻尼弹簧会自己加速？ | 前提：线性无阻尼振子与显式 Euler |
| 7 | 改进与半隐式方法差在哪里？ | 线性振子稳定范围：0<h omega<2 |
| 8 | 自适应步长为什么要比较两种结果？ | 用途：步长控制指标 |
| 9 | 隐式 Euler 为什么要解方程？ | 非线性系统：通常迭代求解 |
| 10 | 位置约束怎样把布料拉回合法状态？ | 约束投影：先于速度重建 |
| 11 | 碰撞与群体行为怎样加入同一框架？ | 忽略：旋转与复杂接触耦合 |
| 12 | 稳定、准确、守恒如何分开验收？ | 条件：没有碰撞与其他力 |

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
| 模拟从哪些状态开始？ | 质量为零不能直接做除法；固定点一般用逆质量零表示并跳过动力学更新。 |
| 弹簧为什么要有静止长度？ | 把方向或伸长量符号写反，弹簧会越拉越远；用伸长和压缩两个例子同时检查。 |
| 阻尼为什么要区分整体运动与相对运动？ | 内部阻尼符号反了会注入能量；课件不同端点标记下需重新推功率。 |
| 网格变细为什么材料会变硬或变软？ | 布料参数缩放不能一律照搬一维串联公式；还要看拓扑、面积与弯曲模型。 |

### 阶段 2：第 5–8 节

| 涉及关系 | 错误机制 / 修正方向 |
| --- | --- |
| 显式 Euler 一步究竟做了什么？ | 代码语句顺序决定数学方法，不能都叫“Euler”而不注明。 |
| 为什么一个无阻尼弹簧会自己加速？ | 添加很强阻尼可能掩盖积分错误，但会改变物理效果；应先辨认能量增长机制。 |
| 改进与半隐式方法差在哪里？ | 不要把一次能量下降当作长期稳定证明；需分析更新矩阵或观察长时间界限。 |
| 自适应步长为什么要比较两种结果？ | 只比较位置可能漏掉速度误差；不同量的尺度也需归一化。 |

### 阶段 3：第 9–12 节

| 涉及关系 | 错误机制 / 修正方向 |
| --- | --- |
| 隐式 Euler 为什么要解方程？ | 求解器没收敛就接受未来状态，可能既不准确也不稳定；应监测残差。 |
| 位置约束怎样把布料拉回合法状态？ | 只修位置不修速度，会让下一帧重新冲回非法状态并产生抖动。 |
| 碰撞与群体行为怎样加入同一框架？ | 只翻转全部速度会连切向运动一起反向；应先分解法向与切向。 |
| 稳定、准确、守恒如何分开验收？ | 截图看着平稳不能证明积分正确；记录轨迹、误差与能量才可区分机制。 |

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

### 自测 1. 相同重力场中质量加倍，加速度是否加倍？

<details>
<summary>参考答案</summary>

不。重力也随质量加倍，F/m 仍为相同的 g。

</details>

### 自测 2. 力为零时弹簧是否一定长度为零？

<details>
<summary>参考答案</summary>

不是。非零静止长度弹簧在长度等于 l0 时恢复力为零。

</details>

### 自测 3. 内部阻尼会阻止整个系统刚体平移吗？

<details>
<summary>参考答案</summary>

理想成对相对速度阻尼不会，整体平移不改变弹簧长度。

</details>

### 自测 4. 更多弹簧是否自然意味着更真实？

<details>
<summary>参考答案</summary>

不。若材料参数与约束不一致，只是更精细地模拟错误材料。

</details>

### 自测 5. Euler 方法是不是直接精确求解牛顿定律？

<details>
<summary>参考答案</summary>

不是。定律定义连续模型，积分器只是有限步长下的数值近似。

</details>

### 自测 6. 把步长减半能使这一增长因子怎样变化？

<details>
<summary>参考答案</summary>

单步增长项 h²ω² 变为四分之一；但相同总时长需要更多步，仍要分析累计误差。

</details>

### 自测 7. 半隐式 Euler 与隐式 Euler 是否相同？

<details>
<summary>参考答案</summary>

不是。前者仍可显式逐项计算，后者通常需求解未来状态方程。

</details>

### 自测 8. 自适应方法能自动发现所有碰撞吗？

<details>
<summary>参考答案</summary>

不能保证。离散碰撞检测仍可能隧穿，需要合适的连续检测或步长约束。

</details>

### 自测 9. 隐式方法更稳定是否意味着总是首选？

<details>
<summary>参考答案</summary>

不。求解成本、阻尼、实现复杂度和目标效果共同决定选择。

</details>

### 自测 10. 固定一端时还能两边各修一半吗？

<details>
<summary>参考答案</summary>

不能。固定端保持不动，修正按逆质量分配给可动端。

</details>

### 自测 11. 鸟群规则能否当作生物行为的精确证明？

<details>
<summary>参考答案</summary>

不能。它是产生某些集体运动特征的计算模型，适用性需要额外验证。

</details>

### 自测 12. 为什么不先用一整件衣服调积分器？

<details>
<summary>参考答案</summary>

复杂约束会掩盖错误来源，最小模型更容易判断力、符号、时间步和求解器各自的问题。

</details>

### 自测 13. 第 1 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

质量为零不能直接做除法；固定点一般用逆质量零表示并跳过动力学更新。

再复算本节的例子：m=2 kg、F=6 N，加速度 3 m/s²。0.1 秒内速度变化近似 0.3 m/s；用 mΔv/Δt 得回 6 N。

</details>

### 自测 14. 第 2 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

把方向或伸长量符号写反，弹簧会越拉越远；用伸长和压缩两个例子同时检查。

再复算本节的例子：a=0、b=1.2 m、l0=1 m、k=100 N/m，则 Fa=+20 N、Fb=-20 N，合力为零。压缩到 0.8 m 时 Fa=-20 N。

</details>

### 自测 15. 第 3 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

内部阻尼符号反了会注入能量；课件不同端点标记下需重新推功率。

再复算本节的例子：一维 va=0、vb=2、c=3，Fa=6、Fb=-6，总功率 6×0-6×2=-12。若两端都以 2 移动，相对速度零，阻尼力也为零。

</details>

### 自测 16. 第 4 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

布料参数缩放不能一律照搬一维串联公式；还要看拓扑、面积与弯曲模型。

再复算本节的例子：原弹簧 k=10，拆成两段串联要各取 k=20，等效为 1/(1/20+1/20)=10。若各取 10，整体变为 5。

</details>

### 自测 17. 第 5 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

代码语句顺序决定数学方法，不能都叫“Euler”而不注明。

再复算本节的例子：x=1、v=0、a=-1、h=0.1，则 x'=1、v'=-0.1。若先更新 v 再用新 v 更新位置，会得到 x'=0.99，是另一方法。

</details>

### 自测 18. 第 6 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

添加很强阻尼可能掩盖积分错误，但会改变物理效果；应先辨认能量增长机制。

再复算本节的例子：ω=1、h=0.1、x=1、v=0，初能 0.5，新能 (1²+0.1²)/2=0.505，增长因子 1.01。100 步因子约 2.705。

</details>

### 自测 19. 第 7 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

不要把一次能量下降当作长期稳定证明；需分析更新矩阵或观察长时间界限。

再复算本节的例子：x=1、v=0、ω=1、h=0.1，则 v'=-0.1、x'=0.99，新能 0.49505。它不是精确守恒，但与显式第一步增能不同。

</details>

### 自测 20. 第 8 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

只比较位置可能漏掉速度误差；不同量的尺度也需归一化。

再复算本节的例子：一步结果 1.02，两半步结果 1.005，差为 0.015。容差 0.01 时应拒绝或缩步；容差不是“每秒总误差”。

</details>

### 自测 21. 第 9 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

求解器没收敛就接受未来状态，可能既不准确也不稳定；应监测残差。

再复算本节的例子：x=1、v=0、ω=1、h=1，得到 x'=0.5、v'=-0.5，能量 0.25，原来为 0.5。代入 x'=1+v'=0.5 验证。

</details>

### 自测 22. 第 10 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

只修位置不修速度，会让下一帧重新冲回非法状态并产生抖动。

再复算本节的例子：两等质量点在 0 和 1.4，目标距离 1，各向内移动 0.2，得到 0.2 和 1.2。新距离 1，质心仍为 0.7。

</details>

### 自测 23. 第 11 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

只翻转全部速度会连切向运动一起反向；应先分解法向与切向。

再复算本节的例子：向地面法向速度 -4 m/s、e=0.5，反弹 +2 m/s。法向动能比为 (2/4)²=1/4，其余能量被耗散。

</details>

### 自测 24. 第 12 节的数值例子，哪一项假设不能悄悄删掉？

<details>
<summary>参考答案与反例入口</summary>

截图看着平稳不能证明积分正确；记录轨迹、误差与能量才可区分机制。

再复算本节的例子：x0=0、v0=0、a=-10、t=0.2，精确位移 -0.2 米。一步显式 Euler 位置仍 0；两步 h=0.1 得 -0.1，能看出缩步改善但仍有误差。

</details>

### 自测 25. 本讲的输入、输出和中间表示各是什么？

<details>
<summary>参考答案</summary>

选择状态 → 建立受力 → 写成微分方程 → 离散时间 → 分析稳定性 → 施加碰撞和约束。请沿箭头逐项解释，尤其说清中间表示的单位、坐标或概率测度；只复述名词不算掌握。

</details>

### 自测 26. 能否只用一张“看起来正确”的图片证明实现正确？

<details>
<summary>参考答案</summary>

不能。需要将关键关系拆成可预测的小输入，检查数值、边界与对照；随机方法还要区分一次结果与统计期望，显示图还需区分编码与原始数据。

</details>

## 17. 带走的结论与仍需练习的内容

- 不。重力也随质量加倍，F/m 仍为相同的 g。
- 不是。非零静止长度弹簧在长度等于 l0 时恢复力为零。
- 理想成对相对速度阻尼不会，整体平移不改变弹簧长度。
- 不。若材料参数与约束不一致，只是更精细地模拟错误材料。
- 不是。定律定义连续模型，积分器只是有限步长下的数值近似。
- 单步增长项 h²ω² 变为四分之一；但相同总时长需要更多步，仍要分析累计误差。
- 不是。前者仍可显式逐项计算，后者通常需求解未来状态方程。
- 不能保证。离散碰撞检测仍可能隧穿，需要合适的连续检测或步长约束。
- 不。求解成本、阻尼、实现复杂度和目标效果共同决定选择。
- 不能。固定端保持不动，修正按逆质量分配给可动端。
- 不能。它是产生某些集体运动特征的计算模型，适用性需要额外验证。
- 复杂约束会掩盖错误来源，最小模型更容易判断力、符号、时间步和求解器各自的问题。

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

[原课件文件与版本记录](https://github.com/Teddy-Yangjiale/CS184/blob/main/CS184_2026/sp26/lectures/SP26-L24-physical-simulation.pdf) · [课程官网](https://cs184.eecs.berkeley.edu/sp26/)

文件：`SP26-L24-physical-simulation.pdf`；PDF 页数：116；SHA-256：`2c230f50f39789dc28cf54d26d74f8d4b509fc97b88728e625730107f7fc3721`。

“正文核对”表示本篇实际引用该页截图；“索引保留”包括演示、行政信息、补充、致谢与重复构建页，不表示逐页都有独立讲解。原视频的运动过程不能由静态 PDF 截图完整复现。

| PDF 页 | 原页可提取标题 | 本篇使用 |
| --- | --- | --- |
| 1 | Computer Graphics and Imaging | 索引保留 |
| 2 | Physically Based Animation | 正文核对 |
| 3 | Example: Cloth Simulation | 索引保留 |
| 4 | Example: Cloth Simulation | 索引保留 |
| 5 | Example: Fluids | 索引保留 |
| 6 | Example: Fluids | 索引保留 |
| 7 | Particle Systems | 正文核对 |
| 8 | 图像或演示页（请以原页视觉内容为准） | 索引保留 |
| 9 | 图像或演示页（请以原页视觉内容为准） | 索引保留 |
| 10 | • Single particles are very simple | 正文核对 |
| 11 | • Single particles are very simple | 索引保留 |
| 12 | Basic Particles | 正文核对 |
| 13 | Dot Notation for Derivatives | 正文核对 |
| 14 | Simple Gravity | 正文核对 |
| 15 | Gravitational Attraction | 索引保留 |
| 16 | Example: Galaxy Simulation | 索引保留 |
| 17 | Example: Galaxy Simulation | 索引保留 |
| 18 | Rendering Particles | 索引保留 |
| 19 | Mass + Spring Systems: | 索引保留 |
| 20 | Example: Mass Spring Mesh | 索引保留 |
| 21 | Example: Mass Spring Mesh | 索引保留 |
| 22 | Example: Mass Spring Rope | 索引保留 |
| 23 | Example: Mass Spring Rope | 索引保留 |
| 24 | Example: Hair | 索引保留 |
| 25 | Example: Hair | 索引保留 |
| 26 | Huamin Wang, Ravi Ramamoorthi, and James F. O'Brien. "Data-Driven Elastic Models for Cloth: Modeling and | 索引保留 |
| 27 | Huamin Wang, Ravi Ramamoorthi, and James F. O'Brien. "Data-Driven Elastic Models for Cloth: Modeling and | 索引保留 |
| 28 | A Simple Spring | 正文核对 |
| 29 | A Simple Spring | 索引保留 |
| 30 | A Simple Spring | 正文核对 |
| 31 | A Simple Spring | 正文核对 |
| 32 | Non-Zero Length Spring | 正文核对 |
| 33 | Non-Zero Length Spring | 索引保留 |
| 34 | Non-Zero Length Springs | 正文核对 |
| 35 | Comments on Springs | 正文核对 |
| 36 | Simple Motion Damping | 正文核对 |
| 37 | Simple Motion Damping | 正文核对 |
| 38 | Internal Damping for Spring | 正文核对 |
| 39 | Spring Constants | 正文核对 |
| 40 | Spring Constants | 正文核对 |
| 41 | Spring Constants | 正文核对 |
| 42 | Spring Constants | 正文核对 |
| 43 | Structures from Springs | 正文核对 |
| 44 | Structures from Springs | 正文核对 |
| 45 | Behavior is determined by structure linkages | 正文核对 |
| 46 | Structures from Springs | 索引保留 |
| 47 | Structures from Springs | 索引保留 |
| 48 | Edge Springs | 正文核对 |
| 49 | Strain Limiting | 正文核对 |
| 50 | Strain Limiting | 正文核对 |
| 51 | Adaptive Simulation | 索引保留 |
| 52 | Adaptive Simulation | 索引保留 |
| 53 | Example: Mass Spring Dress + Character | 索引保留 |
| 54 | Example: Mass Spring Dress + Character | 索引保留 |
| 55 | Aside: FEM (Finite Element Method) Instead of Springs | 索引保留 |
| 56 | Aside: FEM (Finite Element Method) Instead of Springs | 索引保留 |
| 57 | Combating Instability | 索引保留 |
| 58 | Euler’s Method | 正文核对 |
| 59 | Single Particle Simulation | 正文核对 |
| 60 | Single Particle Simulation | 索引保留 |
| 61 | Single Particle Simulation | 索引保留 |
| 62 | Single Particle Simulation | 索引保留 |
| 63 | Single Particle Simulation | 索引保留 |
| 64 | Single Particle Simulation | 索引保留 |
| 65 | Ordinary Differential Equation (ODE) | 正文核对 |
| 66 | Ordinary Differential Equation (ODE) | 正文核对 |
| 67 | Ordinary Differential Equation (ODE) | 索引保留 |
| 68 | Ordinary Differential Equation (ODE) | 索引保留 |
| 69 | Solving for Particle Position | 正文核对 |
| 70 | Euler’s Method - Errors | 正文核对 |
| 71 | Euler’s Method - Errors | 索引保留 |
| 72 | Euler’s Method - Errors | 索引保留 |
| 73 | Euler’s Method - Errors | 索引保留 |
| 74 | Errors and Instability | 正文核对 |
| 75 | Errors and Instability | 正文核对 |
| 76 | Errors and Instability | 索引保留 |
| 77 | Errors and Instability | 索引保留 |
| 78 | Instability of Forward Euler Method | 正文核对 |
| 79 | Instability Example (Spring) | 正文核对 |
| 80 | Instability Example (Spring) | 正文核对 |
| 81 | Instability Example (Spring) | 索引保留 |
| 82 | Instability Example (Spring) | 索引保留 |
| 83 | Instability Example (Spring) | 正文核对 |
| 84 | Some Methods to Combat Instability | 正文核对 |
| 85 | Modified Euler | 正文核对 |
| 86 | Midpoint Method | 正文核对 |
| 87 | Adaptive Step Size | 正文核对 |
| 88 | Adaptive Step Size | 正文核对 |
| 89 | Adaptive Step Size | 正文核对 |
| 90 | Implicit methods | 正文核对 |
| 91 | Implicit methods | 正文核对 |
| 92 | Implicit Euler Method | 正文核对 |
| 93 | Position-Based / Verlet Integration | 正文核对 |
| 94 | Position-Based / Verlet Integration | 正文核对 |
| 95 | Other Particle Systems | 正文核对 |
| 96 | Example: Particle-Based Fluids | 索引保留 |
| 97 | Example: Particle-Based Fluids | 索引保留 |
| 98 | Example: Granular Materials | 正文核对 |
| 99 | Example: Granular Materials | 索引保留 |
| 100 | Example: Flocking Birds | 正文核对 |
| 101 | Example: Flocking Birds | 索引保留 |
| 102 | Simulated Flocking as an ODE | 正文核对 |
| 103 | Simulated Flocking as an ODE | 索引保留 |
| 104 | Simulated Flocking as an ODE | 索引保留 |
| 105 | Simulated Flocking as an ODE | 索引保留 |
| 106 | Simulated Flocking as an ODE | 索引保留 |
| 107 | Simulated Flocking as an ODE | 索引保留 |
| 108 | Simulated Flocking as an ODE | 正文核对 |
| 109 | Simulated Flocking as an ODE | 索引保留 |
| 110 | Example: Crowds | 正文核对 |
| 111 | Example: Crowds | 索引保留 |
| 112 | Example: Crowds + “Rock” Dynamics | 正文核对 |
| 113 | Example: Crowds + “Rock” Dynamics | 索引保留 |
| 114 | Just Scratching the Surface… | 正文核对 |
| 115 | Things to Remember | 正文核对 |
| 116 | Acknowledgments | 索引保留 |
