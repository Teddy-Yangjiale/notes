---
title: "CS184 第 8–9 讲：可见性、着色与光栅化管线"
date: 2026-11-05
summary: "前七讲拼出了半条管线：能算出三角形覆盖了哪些像素、能从纹理取色。这一讲补上最后两块——谁挡住谁（z-buffer），以及这个颜色在光下该是多少（Blinn-Phong）。最后把五个阶段串成完整管线，并用 shader 与 GPU 收尾。配 22 张原创图解、12 个手算、127 页全索引。"
tags: ["计算机图形学", "光栅化", "着色", "z-buffer", "CS184"]
series: "cs184"
order: 8
shortTitle: "L08–09 · 可见性与着色"
---

> UC Berkeley · CS184/284A Computer Graphics and Imaging · Fall 2026 · Lecture 8–9

到这里，前面几讲讲的东西终于要拼成一台完整的机器：

```
前七讲已有：变换 → 投影 → 光栅化覆盖 → 纹理取色
   ↓ 但还有两个空白
① 谁挡住谁？        → z-buffer（逐像素记最小深度）
② 这个颜色在光下多亮？→ Blinn-Phong（环境 + 漫反射 + 高光）
   ↓ 着色在哪里算？
逐面 / 逐顶点 / 逐像素 —— 三种频率，代价与效果不同
   ↓ 法线怎么来、怎么变换？
顶点法线平均；法线要用 M⁻ᵀ 而不是 M
   ↓ 全部装进管线
Vertex → Triangle → Raster → Fragment → Framebuffer
```

![光栅化管线的五个阶段](diagrams/d01-five-stages.png)

*前两段加工「顶点 / 三角形」，后三段加工「片段 / 像素」。中间那道栅格化就是第 2 讲的采样，而这一讲新增的是：③ 之前的深度测试、④ 里的着色计算、⑤ 里的深度与混合。*

*127 页 · 102 张关键页截图 · 22 张原创图解 · 12 个手算 · 30 道自测*

> **💡 这一讲的定位**
>
> 讲义（P12）自己给的路线图里，今天这一格叫 **「Visibility, Shading, Overall Pipeline」** —— 注意最后那个词 **Overall**：这一讲的主要作用是**把前面所有零件装起来**，新知识其实只有两块（可见性 + 局部着色）。

## 0. 这一讲在补什么

前七讲拼出了**半条管线**：

```
变换（L04-05）→ 投影 → 光栅化覆盖（L02）→ 插值属性（L06）→ 纹理取色（L06-07）
```

**已经能画出一个带纹理的立方体了** —— 但它看起来完全不像真实世界，因为还缺两块：

| 缺什么 | 后果 | 本讲解法 |
|---|---|---|
| **谁挡住谁** | 所有三角形都画上去，后面的盖住前面的 | **z-buffer** |
| **颜色在光下是多少** | 只有纹理的本色，没有明暗 | **Blinn-Phong** |

补完这两块，再把五个阶段串起来，就是**完整的光栅化管线**。

**这一讲的结构因此是"两个问题 + 一次总装"**：

```
① 可见性
   画家算法（要排序，可能无解）→ z-buffer（逐像素比较，O(n)）→ 阴影贴图（复用 z-buffer）
② 着色
   Lambert 漫反射 → Blinn-Phong 高光 → 加环境光 → 三项求和
   ↓ 在哪算？
   flat / Gouraud / Phong ← 三种频率，代价与病灶不同
③ 总装
   五个阶段 + shader + GPU
```

## 1. 我们已经有什么，还缺什么

#### P1　Section 6: The Rasterization Pipeline

![P1 · 课程封面](images/p001.png)

注意这次的标题是 **The Rasterization Pipeline**（整条管线），而不是某个具体算法 —— 这一讲是"总装"。

#### P2　What We've Covered So Far

![P2 · 已覆盖的五步](images/p002.png)

一页图上标出了前七讲的全部成果：

| 步骤 | 来自哪讲 |
|---|---|
| 在世界里摆放物体和相机 | L04–05 变换 |
| 算物体相对相机的位置 | L04–05 变换 |
| 投影到屏幕 | L04–05 透视 |
| 采样三角形覆盖 | L02 光栅化 |
| 插值三角形属性 | L06–07 重心坐标 |
| 采样纹理 | L06–07 纹理映射 |

**这一页的价值**：它说明"能画出一个带纹理的立方体"已经做完了。**那还缺什么？**

#### P3–P8　Rotating Cubes in Perspective

![P3 · 旋转的立方体（第一帧）](images/p003.png)

六页旋转立方体的连续帧。**这是"目前能做到的最好效果"** —— 几何正确、有透视、有遮挡（立方体自身遮挡自己）。

**但它看起来完全不像真实世界。**

#### P9–P10　What Else Are We Missing?

![P9 · 还缺什么（渲染图）](images/p009.png)

![P10 · 另一张高质量渲染](images/p010.png)

两张照片级渲染（Bertrand Benoit 的 *Sweet Feast*、Giuseppe Albergo 的 *Colibri*）。

#### P11　What Else Are We Missing?

![P11 · 三个缺口](images/p011.png)

讲义列了三条，**这就是后面几讲的地图**：

| 缺口 | 说明 | 谁来补 |
|---|---|---|
| **Surface representations** | 真实世界的几何细节极其复杂 | L09–11 曲线曲面、L11–12 网格 |
| **Lighting and materials** | 外观是光在复杂材质上反射的结果 | **本讲 + L16–17** |
| **Camera models** | 真实镜头有聚焦等光学效应 | L14 相机与镜头 |

#### P12　Course Roadmap

![P12 · 课程地图](images/p012.png)

路线图上高亮了 **Today: Visibility, Shading, Overall Pipeline**。

**注意左边那列 "Core Concepts"**：Sampling、Antialiasing、Transforms —— 这三个是贯穿全课的骨架，而不是某一讲的专属内容。

## 2. 可见性：画家算法

#### P13　Visibility

*章节点*

![P13 · 可见性](images/p013.png)

分节页。要解决的第一个问题：**屏幕上一个像素被多个三角形覆盖时，该显示哪个？**

#### P14–P23　Inspired by how painters paint

![P15 · 画家作画](images/p015.png)

![P17 · 画家算法的思路](images/p017.png)

*"从后往前画"在纸上是自然操作，在帧缓冲里就是**直接覆盖**。**代价是需要排序。***

*油画家先画远景、再画近景，**后画的颜料自然盖住先画的** —— 这就是"画家算法"这个名字的由来。*

*Paint from back to front, overwrite in the framebuffer*

![P14 · 画家算法](images/p014.png)

一页画家作画的照片（Wikipedia），配一句加粗：

> **从后往前画，直接覆盖帧缓冲里的值。**

**这个类比很准**：油画家先画远景、再画中景、最后画近景，后画的颜料自然盖住先画的。**图形学里的"画家算法"就是这个策略**。

![画家算法：从远到近覆盖](diagrams/d02-painter.png)

*三个不同深度的物体，从远到近依次画上去，后画的直接覆盖先画的像素值。*

**优点**：极其简单，不需要额外的深度缓冲。

**但 P24 给出了两个致命问题。**

#### P24　Painter's Algorithm

*Requires sorting in depth (O(n log n) for n triangles) · Can have unresolvable depth order · (BSP Trees will provide a way of dealing with both issues.)*

![P24 · 画家算法的两个问题](images/p024.png)

![P21 · 从后往前画](images/p021.png)

![P23 · 排序后的绘制](images/p023.png)

*排序之后，后画的一定更近 —— 所以直接覆盖就是对的。**但对"循环遮挡"就无解了**（下一节）。*

*实现上就是**按深度排序，从远到近依次绘制**。简单、直观，但对几何有要求。*

两条加粗：

| 问题 | 说明 |
|---|---|
| **要排序** | `O(n log n)`，n 是三角形数。场景有几百万三角形时很贵 |
| **可能无解** | 存在**无法排序**的三角形排列 |

**"无法排序"是什么意思？** 看下一张图。

![循环遮挡：任何顺序都错](diagrams/d03-cyclic-overlap.png)

*三个三角形两两互相遮挡：A 挡 B、B 挡 C、C 挡 A。**这不是全序关系**（不是"甲在乙前面、乙在丙前面"），所以不存在任何一个"正确的绘制顺序"。*

**这就是画家算法出局的原因**：它要求一个**全局顺序**，而遮挡关系本质上**不是全局的**（不同像素上的前后关系可能相反）。

> **📌 括号里那句话值得注意**
>
> 讲义写：***"(BSP Trees will provide a way of dealing with both issues.)"***
>
> BSP 树（二叉空间分割）能给出一个"可用的"绘制顺序 —— 它递归地把空间切成两半，直到每个区域里只剩一个不交叉的多边形。这样得到的顺序**保证正确**，而且不需要排序。
>
> 但 BSP 树的构建本身很贵（`O(n log n)` 到 `O(n²)`），且只适合静态场景。**所以工业界最终选了 z-buffer。**

## 3. z-buffer：赢下可见性的算法

#### P25–P31　Z-Buffer

![P029 · 深度缓冲需要额外内存](images/p029.png)

*"需要一块额外的缓冲"这句是 z-buffer 的唯一成本：**每像素多 16–32 bit**。相比之下，它带来的性能收益是数量级的。*

![P027 · 只保留深度](images/p027.png)

*z-buffer 的关键洞察：**不需要知道正确顺序，只需要每个像素记住"谁最近"**。*

*This is the hidden-surface-removal algorithm that eventually won.*

![P26 · z-buffer 自述](images/p026.png)

一句很自信的加粗：

> ***"This is the hidden-surface-removal algorithm that eventually won."***
>
> 这就是最终赢下「隐面消除」的那个算法。

**思路（P28–P31 逐条累加）**：

| 要点 | 说明 |
|---|---|
| **每个采样位置存当前最小的 z** | 谁离相机最近，就记谁 |
| **需要一块额外缓冲** | 帧缓冲存 RGB，**深度缓冲（z-buffer）存深度** |
| 深度精度 | 16 到 32 bit |

**关键洞察**：**我们不需要知道"正确的绘制顺序"，只需要知道"每个像素上谁最近"。**

- 画家算法：**全局顺序** → 排序问题
- z-buffer：**逐像素比较** → 无排序

这个转变把一个"全局难题"化成了"局部比较"。

#### P32　Z-Buffer Example

#### z-buffer 的三个实现细节

| 细节 | 说明 |
|---|---|
| **深度精度** | 16 bit 常用于低端；24 bit 是标准；32 bit 用于大场景。**精度不够会出现"远处闪烁"（z-fighting）** |
| **early-Z** | 现代 GPU 在**着**色之前先做深度测试 —— 被挡住的像素**根本不着色**，省一大笔 |
| **非线性深度** | 透视投影后的 `z` 不是均匀分布的（近处密、远处疏），所以**远处精度差** —— 这是 z-fighting 的主因 |

**early-Z 为什么重要**：一个典型的游戏场景 **overdraw 有 2–3 倍**（每个像素被画 2–3 次）。early-Z 让被遮挡的那些**跳过片元着色**（包括纹理采样），能省 50% 以上的带宽。

**非线性深度的量化**：透视投影 `z_ndc = (f+n)/(f−n) − 2fn/((f−n)·z_eye)`。当 `n=0.1`、`f=1000` 时，**80% 的深度精度花在 `z_eye ∈ [0.1, 1]` 这 1 米的范围内**。远处的 999 米只占 20% 精度 —— 所以远处的两个物体容易"打架"。

![透视对插值的影响](diagrams/d20-perspective-interp.png)

*同一条屏幕边，两端 `w` 不同（1 和 4）。**屏幕中点处线性插值给 `u=0.5`，透视正确给 `u=0.2`** —— 差 0.3，这就是"挤扁"的来源。*

![P32 · 渲染结果与深度缓冲](images/p032.png)

两张图并排：左边是正常渲染（一个放在棋盘地面上的镂空立方体），右边是**深度缓冲的可视化**（越近越暗/越亮，取决于映射）。

**深度缓冲长什么样**：它是一张**灰度的"距离图"**，没有颜色、没有纹理、只有远近。**它和渲染图在几何轮廓上完全一致**，因为两者都是"这张图里每个像素对应的那个表面"的属性。

#### P33　Z-Buffer Algorithm

![P33 · 算法伪代码](images/p033.png)

```c
Initialize depth buffer to ∞
During rasterization:
  for (each triangle T)
    for (each sample (x,y,z) in T)
      if (z < zbuffer[x,y]) {        // closest sample so far
        framebuffer[x,y] = rgb;      // update (compute) color
        zbuffer[x,y]     = z;        // update z
      } else
        ;                            // do nothing, this sample is not closest
// Careful with Z vs -Z. No point in storing sign bit.
```

**四行核心逻辑**，但有两个注释值得说：

**① `// Careful with Z vs -Z`**
观察空间里相机看向 `−z`（第 4–5 讲 P197），所以"更近"意味着 `z` **更大**（更接近 0）。而深度缓冲通常存"正的距离"，于是判定方向要反过来。**这是实现时最常见的符号错误**。

**② `// No point in storing sign bit`**
因为深度总是正的（距离），所以可以把符号位省掉，换成一个额外的精度位。**这是真实硬件的做法** —— 深度缓冲常常是 24 位无符号。

![z-buffer：逐像素记最小深度](diagrams/d04-zbuffer.png)

*先画远的 A（z=5），缓冲里填 5；再画近的 B（z=2），因为 2 < 5 所以覆盖 —— **整个过程不需要知道三角形的绘制顺序**，只要每个像素比一次就够了。*

#### P34　Z-Buffer Algorithm

*（In this example positive values are further.）*

![P34 · 两个三角形的深度测试](images/p034.png)

一页图示：两个三角形分别光栅化（红、蓝掩码），然后合并（z 测试决定谁保留）。

**注意小字**：*"In this example positive values are further."* —— 这一页假设 `z` 越大越远，即 `z` 是"距离"而非"观察空间坐标"。**两种约定都常见，但绝不能混用。**

#### P35　Z-Buffer Complexity

*Complexity: O(n) for n triangles · How can we sort n triangles in linear time? · Most important visibility algorithm · Implemented in hardware for all GPUs · Used by OpenGL · Issues: Overdraw · Transparency*

![P35 · 复杂度与问题](images/p035.png)

**复杂度 `O(n)`** —— 注意这里有个反问：*"How can we sort n triangles in linear time?"*（怎么能线性时间排序 n 个三角形？）

**答案是：我们没有排序。** 每个样本只做一次比较，总工作量 = 所有三角形覆盖的样本总数 = `O(n)`（在三角形面积有限的前提下）。

**三条地位**：

| 事实 | 意义 |
|---|---|
| **最重要的可见性算法** | 没有之一 |
| **所有 GPU 硬件实现** | 不是软件优化，是固定功能电路 |
| **OpenGL 采用** | 也是 DirectX / Vulkan 的默认行为 |

**两个问题（P35 列出的）**：

| 问题 | 说明 |
|---|---|
| **Overdraw** | 被遮挡的像素也要跑一遍片元着色（先着色后测深度），浪费带宽。现代 GPU 用"early-Z"优化 |
| **Transparency** | 半透明物体不能用这个算法（见 P36） |

#### P36–P37　Z-Buffer and Transparency

![P036 · 透明需要排序](images/p036.png)

*透明物体不能"覆盖"，必须"混合"。**所以 z-buffer 对透明无效** —— 它只保留最近的一个。*

*Transparency requires partial sorting*

![P36 · 透明需要部分排序](images/p036.png)

![P37 · 深透明缓冲](images/p037.png)

**问题**：半透明像素不能"覆盖"，必须"混合"（把已有颜色和新颜色按权重加起来）。而 z-buffer 只保留**最近的一个** —— 后面的信息全被丢掉了。

**两种解法**：

| 方案 | 说明 | 问题 |
|---|---|---|
| **先画不透明，再画透明**（理想情况下透明物体从远到近） | 常规做法 | 透明物体之间仍需要排序，而且可能无解（P24 的循环） |
| **Deep Alpha Buffer** | 每个像素存一个"RGB-Z 链表"，事后统一合成 | 需要可变长存储，硬件不友好 |

![透明度必须从远到近混](diagrams/d14-transparency.png)

*左：按"不透明 → 不透明 → 半透明"的顺序，正确。右：先画半透明，它后面再画的不透明物体就会把它覆盖掉 —— 错的。*

> **⚠️ 为什么"先画不透明"就能缓解**
>
> 不透明物体之间的正确性由 z-buffer 保证（不需要排序）。只有**不透明与半透明之间**需要顺序。
>
> 所以"先不透明、后透明"把问题缩小到了"透明物体内部"—— 而透明物体通常数量少、且常常可以接受轻微错误。

## 4. 阴影贴图：可见性的第二次利用

#### P38　Shadow Maps

![阴影贴图的两个失真](diagrams/d19-shadow-bias.png)

*bias 太小 → 表面自己遮自己（条纹状 acne）；bias 太大 → 阴影脱离物体（peter-panning）。**正解是让偏移量随入射角变大。***

*Pre-render scene from perspective of light source · Only render Z-Buffer (the shadow buffer) · Render scene from camera perspective · Compare with shadow buffer · If nearer light, if further shadow*

![P38 · 阴影贴图](images/p038.png)

**四步算法，全在复用 z-buffer**：

| 步骤 | 做什么 |
|---|---|
| 1 | 从**光源**视角渲染场景 |
| 2 | 只保留**深度缓冲**（叫 shadow buffer） |
| 3 | 从**相机**视角渲染场景 |
| 4 | 逐像素比较：到光源的距离 vs shadow buffer 里的值 |

**判据**：

- **比 shadow buffer 里更远** ⇒ 中间有东西挡光 ⇒ **在阴影里**
- **更近或相等** ⇒ 光源能直接看到 ⇒ 正常光照

![阴影贴图：把可见性算两遍](diagrams/d15-shadow-map.png)

*本质是"把可见性问题再算一遍"，只不过换成"从光源看谁在前"。**这是本讲最漂亮的复用** —— 一个 z-buffer，解决了两个完全不同的需求。*

#### P39　Shadow Maps

#### 阴影贴图的三个实用扩展

基础版 shadow map 有两个硬伤：**分辨率不够**（阴影边缘是像素块）和**一张图覆盖不了大场景**。

| 扩展 | 解决什么 | 代价 |
|---|---|---|
| **PCF**（百分比渐近过滤） | 阴影边缘有锯齿 → 采样周围几个 texel 求平均 | 4–16 次采样 |
| **级联阴影贴图（CSM）** | 一张图覆盖不了远近 → 按视距分成 3–4 级，各用一张 | 3–4 次 shadow pass |
| **虚拟阴影贴图（VSM）** | 动态场景的高效更新 | 复杂，需要 GPU 特性 |

**PCF 的原理**：阴影贴图只有"通/不通"两种结果，所以边缘是硬的。PCF 在判断时**采样邻域并平均**，得到一个 `0..1` 的"遮挡比例" —— 视觉上就是**软阴影**。

**级联阴影的直觉**：近处需要高分辨率（阴影细），远处可以低分辨率（反正看不清）。所以**近处一张小范围的图、远处一张大范围的图**，按深度切换。

![P39 · 阴影效果](images/p039.png)

一张有阴影的渲染（Stamminger & Drettakis, SIGGRAPH 2002）。

**小字有个诚实的免责声明**：*"Note: These images don't really go together, see the paper..."* —— 讲义用了论文里的图，但两张图其实不是同一份数据的。**这种标注值得学：不假装严谨。**

#### P40　Deep Shadow Maps

*Some objects only partially occlude light · A single shadow value will not work · Similar to transparency in Z-Buffer*

![P40 · 深阴影贴图](images/p040.png)

**问题和 P36 完全同构**：如果遮挡物是**半透明**的（比如树叶、烟、毛发），那么"完全挡住"和"完全没挡"都不对 —— 需要记录**衰减比例**。

**解法**：每个 texel 存一个**透射率函数**（transmittance as a function of depth），而不只是一个深度值。

#### P41　Attendance

*Word of the day: visibility · Lecture number: 8*

![P41 · 课堂签到](images/p041.png)

签到页，写着 **"Word of the day: visibility"，Lecture number 8**。

**这个细节确认了讲次编号**：这一讲在课程里是 **Lecture 8**（对应 fa26 的 L08–09 合并讲义第一半）。

## 5. 简单着色：为什么不用物理

#### P42　Simple Shading（Blinn-Phong Reflection Model）

*章节点*

![P42 · 简单着色](images/p042.png)

分节页。可见性解决"看到谁"，现在解决"它有多亮"。

#### P43　Simple Shading vs Realistic Lighting & Materials

*What we will cover today: A local shading model: simple, per-pixel, fast · Based on perceptual observations, not physics*

![P43 · 今天讲的 vs 后面讲的](images/p043.png)

**这一页把"取舍"讲得很直白**：

| 今天 | 后面 |
|---|---|
| **局部（local）** 着色模型 | 基于物理的光照与材质 |
| 简单、逐像素、快 | 全局光传输模拟 |
| **基于感知观察，不是物理** | 有物理依据 |

**"Based on perceptual observations"** 是关键词：Blinn-Phong 不是从物理推导出来的，而是**观察"真实物体看起来有哪几种亮"然后手工凑出来的公式**。

#### P44　Perceptual Observations

![三个参数各管一件事](diagrams/d17-param-matrix.png)

*`k_d` 管整体明暗、`k_s` 管亮斑强弱、`p` 管亮斑大小。**三者独立可调** —— 这就是为什么它适合做美术工具。*

*Specular highlights · Diffuse reflection · Ambient lighting*

![P44 · 感知观察](images/p044.png)

一摞彩色茶杯的照片（Jessica Andrews），三处用箭头标出：

| 观察 | 在图上的位置 |
|---|---|
| **Specular highlights（高光）** | 杯子釉面上那几块亮斑 |
| **Diffuse reflection（漫反射）** | 杯身的平滑明暗过渡 |
| **Ambient lighting（环境光）** | 背光面也不是全黑 |

**这就是 Blinn-Phong 三项的由来** —— 先看见三种现象，再各造一项去模拟。

#### P45　Local Shading

![P043 · 今天的 vs 后面的](images/p043.png)

*讲义把"取舍"讲得很直白：**今天讲的是"基于感知观察、不是物理"的局部模型**。后面（L16–17）才是物理的。*

*Compute light reflected toward camera · No "global" effects · Unit length (normalized) vectors!!!*

![P45 · 局部着色的输入](images/p045.png)

图上是 `l`（光源方向）、`n`（法线）、`v`（视线）三个箭头从同一点出发。

**四个输入**：

| 输入 | 含义 |
|---|---|
| `v` | 观察方向（surface → eye） |
| `n` | 表面法线 |
| `l` | 光源方向（surface → light），**对每个光源各一个** |
| 表面参数 | 颜色、光泽度…… |

**加粗的警告**：***"Unit length (normalized) vectors!!!"*** —— 三个向量必须归一化。

> **⚠️ 为什么归一化这么重要**
>
> 因为公式里全是点积 `n·l`、`n·h`。**点积的定义是 `|a||b|cos θ`** —— 只有单位向量时，点积才等于 `cos θ`。
>
> 用了非单位向量，亮度会随向量长度缩放，出现"离得远就变暗"之类的怪现象，而且很难排查。

## 6. 漫反射：Lambert 余弦定律

#### P46–P48　Light Falloff

![P47 · 平方反比](images/p047.png)

*光从点光源向外扩散，**同样多的能量摊到越来越大的球面上** ⇒ 单位面积的能量按 `1/r²` 下降。*

*intensity here: I/r²*

![P46 · 光强衰减](images/p046.png)

光源发出的光向四周扩散，**单位面积上的能量按 `1/r²` 衰减**（平方反比定律）。

![光强随距离衰减](diagrams/d09-falloff.png)

*物理上是 `1/r²`。但局部着色模型里用它常常很难看 —— 因为"远处全黑"这件事，物理上是由**间接光**填回来的，而局部模型没有间接光。*

#### P49　Falloff

*Physically correct: 1/r² light intensity falloff · Tends to look bad with local shading (why?) · Sometimes compromise of 1/r used · Very important to use 1/r² for correct global illumination methods*

![P49 · 衰减的取舍](images/p049.png)

**三个要点**：

| 说法 | 含义 |
|---|---|
| 物理正确是 `1/r²` | 平方反比 |
| **但配局部着色会难看（为什么？）** | 因为局部模型没有间接光填底，远处直接变黑 |
| 有时折中用 `1/r` | 衰减更慢，视觉上更"耐看" |
| **做全局光照时必须用 `1/r²`** | 否则能量不守恒 |

**🔧 手算 1：`1/r²` 有多陡**

设 `r=1` 处强度为 1：

| 距离 `r` | `1/r²` | `1/r` |
|---|---|---|
| 1 | 1.0 | 1.0 |
| 2 | 0.25 | 0.5 |
| 4 | 0.0625 | 0.25 |
| 10 | 0.01 | 0.1 |

**`r=10` 时 `1/r²` 只剩 1%** —— 这就是"远处全黑"的来源。而 `1/r` 还有 10%，视觉上更像真实照片（真实照片里远处是暗但不是纯黑，因为环境光/间接光在起作用）。

#### P50　Diffuse Reflection

![P048 · 衰减与余弦的叠加](images/p048.png)

*最终亮度是**两个因子的乘积**：`1/r²`（离多远）和 `cos θ`（斜多少）。**任何一个为 0，结果就为 0**。*

*Light is scattered uniformly in all directions · Surface color is the same for all viewing directions · Lambert's cosine law*

![P50 · 漫反射与余弦定律](images/p050.png)

图上是三块板：

| 图 | 说明 |
|---|---|
| 左：正对光源 | *Top face of cube receives a certain amount of light* |
| 中：旋转 60° | *Top face of 60° rotated cube intercepts **half** the light* |
| 右：一般情况 | *light per unit area is proportional to `cos θ = l · n`* |

![Lambert 余弦定律](diagrams/d06-lambert.png)

*光通量是恒定的，但板子倾斜后**同样的光摊到更大的面积**上，所以单位面积收到的能量按 `cos θ` 下降。*

**🔧 手算 2：为什么 60° 恰好是一半**

$$
\cos 60° = 0.5
$$

**所以 `60°` 倾斜的板，单位面积上只收到一半的光。** 这也是为什么 P50 的图特意选 60° —— 一半是个好记的数。

**两个性质**（P50 列出的）：

1. **光向所有方向均匀散射** → 从哪个角度看都一样
2. **表面颜色与观察方向无关**

#### P51　Lambertian (Diffuse) Shading

*Shading independent of view direction*

![P51 · 兰伯特公式](images/p051.png)

$$
L_d=k_d\,\frac{I}{r^2}\,\max(0,\ \mathbf{n}\cdot\mathbf{l})
$$

四个符号的含义（图上逐一标注）：

| 符号 | 含义 |
|---|---|
| `k_d` | **漫反射系数**（材质颜色） |
| `I/r²` | 到达表面的**光照强度**（含衰减） |
| `max(0, n·l)` | **余弦项**（斜着的面收光少） |
| `max(0, ...)` | **避免背面为负**（`n·l < 0` 说明光在背面） |

> **📌 `max(0, ...)` 为什么不能省**
>
> 如果 `n·l < 0`（光从背面来），点积是负的。不裁剪的话会得到**负的光照** —— 比黑还黑，在后续加法里会把其他项也吃掉，出现黑斑。
>
> 这个 `max` 在 shader 里对应 `saturate()` 或 `clamp(x, 0, 1)`，是每个图形程序员写的第一行防御性代码。

#### P52　Lambertian (Diffuse) Shading

![P050 · 余弦定律的图示](images/p050.png)

*三块板：正对、转 60°、一般角度。**中间那块正好接住一半的光** —— 这是 `cos 60° = 0.5` 的几何意义。*

*Produces matte appearance*

![P52 · 漫反射的哑光效果](images/p052.png)

一排球，`k_d` 从左到右递增。

**"matte"（哑光）的视觉特征**：明暗过渡很柔和，**没有亮斑**。粉笔、橡皮、未上釉的陶器都是这样。

## 7. 高光：Blinn-Phong 的核心技巧

#### P53　Perceptual Observations

![P53 · 高光观察](images/p053.png)

同一张茶杯照片，这次只标 **Specular highlights**。

**高光的视觉特征**：**小而亮的一块**，而且**位置会随着观察方向移动**（你歪一下头，高光也在动）。

#### P54　Specular Shading (Blinn-Phong)

![P053 · 高光的视觉特征](images/p053.png)

*高光**小而亮**，而且**随视角移动**。这两条是它和漫反射的根本区别。*

*Intensity depends on view direction · Bright near mirror reflection direction*

![P54 · 高光取决于观察方向](images/p054.png)

一个球在黑色背景上，右上方一块明亮的高光。

**关键区别**：漫反射"从哪个角度看都一样"，而高光"只在一个特定方向附近亮"。

#### P55　Specular Shading (Blinn-Phong)

![Blinn 的 n·h vs Phong 的 r·v](diagrams/d18-blinn-vs-phong.png)

*`n·h` 在偏离镜面方向后**衰减得更慢**，所以 Blinn 的高光更宽、更"润"。代价是掠射角时会高估。*

*Close to mirror direction ⇔ half vector near normal · Measure "near" by dot product of unit vectors*

![P55 · 半角向量 h](images/p055.png)

**这是全讲最漂亮的一个技巧**：

$$
\mathbf{h}=\operatorname{bisector}(\mathbf{v},\mathbf{l})=\frac{\mathbf{v}+\mathbf{l}}{\|\mathbf{v}+\mathbf{l}\|}
$$

$$
L_s=k_s\,\frac{I}{r^2}\,\max(0,\cos\alpha)^p=k_s\,\frac{I}{r^2}\,\max(0,\mathbf{n}\cdot\mathbf{h})^p
$$

**为什么用 `h` 而不是反射方向 `r`**：

| 用 `r`（Phong 1975 的做法） | 用 `h`（Blinn 1977 的改进） |
|---|---|
| 要算反射方向 `r = 2(l·n)n − l` | 只要 `h = (v+l)/‖v+l‖` |
| 一次反射计算 | 一次加法 + 一次归一化 |
| 镜面条件：`r` 与 `v` 重合 | 镜面条件：`h` 与 `n` 重合 |

![为什么用半角向量](diagrams/d07-half-vector.png)

*`h` 是 `v` 与 `l` 的角平分线。**镜面反射成立 ⟺ `r` 与 `v` 重合 ⟺ `h` 与 `n` 重合** —— 所以用 `n·h` 判断"是否接近镜面方向"是等价的，而且更便宜。*

> **📌 "等价"不是"完全相等"**
>
> 严格说 `n·h` 与 `r·v` 不是同一个量。它们的差别在**掠射角**（grazing angle）变大时明显 —— Blinn 的近似会让高光在掠射时偏大。
>
> 但工程上这个近似"看起来更好"，所以 Blinn-Phong 成了标准。**这也是一个"感知优先于物理"的例子**（呼应 P43）。

#### P56–P58　Cosine Power Plots / 高光指数 p

![P56 · 余弦幂曲线](images/p056.png)

![P57 · p 从 1 到 256 的球](images/p057.png)

![P58 · 同时变化 ks 与 p](images/p058.png)

$$
\max(0,\mathbf{n}\cdot\mathbf{h})^p
$$

**`p` 的物理含义**：**材质的"光滑程度"**。

![p 越大叶瓣越窄](diagrams/d08-specular-lobe.png)

*`p=1` 时高光一大片（粗糙）；`p=64` 时高光是一个点（光滑）。*

**🔧 手算 3：`p` 有多敏感**

取 `n·h = 0.9`（偏离镜面方向约 26°），算 `0.9^p`：

| `p` | `0.9^p` | 视觉 |
|---|---|---|
| 1 | 0.90 | 几乎满亮 |
| 4 | 0.656 | 还挺亮 |
| 16 | 0.185 | 明显变暗 |
| 64 | 0.0012 | 基本没有 |
| 256 | 1.5×10⁻¹² | 完全没有 |

**结论**：`p` 从 16 变到 64，`n·h=0.9` 处的亮度掉了 **150 倍**。所以 `p` 是**控制高光"紧不紧"的核心参数**，而它对数值极其敏感 —— 调参时建议在对数尺度上试（1, 4, 16, 64, 256）。

#### P59　Direction vs Point Lights

*For a point light, the light direction changes over the surface · For "distant" light, the direction is constant*

![P59 · 点光源 vs 平行光](images/p059.png)

两个圆柱体，标注对比：

| 光源类型 | `l` 怎么算 |
|---|---|
| **点光源** | `l = (light_pos − surface_pos) / ‖...‖`，**每个像素都不同** |
| **平行光（distant）** | `l` 是**常量**，全场一样（太阳） |

**视觉差别**：平行光的明暗带是**直的、平行的**；点光源的明暗带会**弯曲、发散**（图上是两个圆柱，左边隐约看到差别）。

**这个区别在性能上很重要**：平行光不需要逐像素算 `l`，可以提到片元着色之外。

#### P60　Spot and Other Lights

![P059 · 点光源 vs 平行光](images/p059.png)

*两个圆柱：**平行光的明暗带是直的，点光源的会弯曲**。因为点光源的 `l` 随位置变化。*

*Other calculations for useful effects: Spot light · Only light certain objects · Negative lights · etc.*

![P60 · 聚光灯等](images/p060.png)

一个**聚光灯（spot light）**的示意图（圆锥 + 一个圆形亮斑）。

**聚光灯的额外计算**：除了方向，还要判断"这个点是否在光锥内"，常用 `cos(angle)` 与锥角比较，并用平滑衰减（否则边缘是硬的圆环）。

**"Negative lights"**（负光源）：用来**减光**，做"挖掉一块光照"的调试效果 —— 不是物理，但是实用的美术工具。

## 8. 环境光与三项求和

#### P61–P62　Ugly....

![P062 · 只有漫反射 + 高光](images/p062.png)

*背光面是**纯黑**的，硬邦邦地"断"掉。真实世界的背光面会被周围物体反射的光照亮 —— 而局部模型做不出这件事。*

![P61 · 只有漫反射+高光会很丑](images/p061.png)

标题只有两个字：**"Ugly...."** —— 展示**只用漫反射 + 高光**的渲染结果。

**为什么丑**：背光面是**纯黑**的，硬邦邦地"断"掉。真实世界里，背光面会被周围物体反射的光照亮（间接光）。

**局部模型做不出间接光**，于是"造"一项来假装它。

#### P63–P64　Ambient Shading

*Shading that does not depend on anything · Add constant color to account for disregarded illumination and fill in black shadows*

![P64 · 环境光](images/p064.png)

$$
L_a=k_a\,I_a
$$

**只有两个量**：环境光系数 `k_a` 和环境光强度 `I_a` 的乘积。**不依赖任何方向**。

加粗小字说得很直白：*"add constant color to account for **disregarded illumination** and **fill in black shadows**"* —— 加一个常数，来**补偿被忽略的光照**、**填补纯黑的阴影**。

> **⚠️ 环境光是"承认失败"的项**
>
> 它没有任何物理依据 —— 它的全部作用就是**让阴影不要黑得那么假**。
>
> 这也是为什么 L16–17（全局光照）之后，环境光项会被**真正算出来的间接光**取代。**Blinn-Phong 里的 `k_a` 本质上是一个"手工调节的间接光近似"。**

#### P65–P66　Blinn-Phong Reflection Model

![P063 · 环境光](images/p063.png)

*环境光项的效果：**背光面从纯黑变成深灰**。它不物理，但视觉上必需。*

![P65 · 三项求和](images/p065.png)

![P66 · 完整公式](images/p066.png)

$$
L=L_a+L_d+L_s
=k_aI_a+k_d\frac{I}{r^2}\max(0,\mathbf{n}\cdot\mathbf{l})
+k_s\frac{I}{r^2}\max(0,\mathbf{n}\cdot\mathbf{h})^p
$$

**注意最后那行小字**：***"Note: Sum over lights for multiple lights."***

**多光源时，要把每个光源的 `L_d + L_s` 加起来**（环境光只加一次）：

$$
L=k_aI_a+\sum_{i}\left(k_{d}\frac{I_i}{r_i^2}\max(0,\mathbf{n}\cdot\mathbf{l}_i)
+k_{s}\frac{I_i}{r_i^2}\max(0,\mathbf{n}\cdot\mathbf{h}_i)^{p}\right)
$$

![三项分解](diagrams/d05-three-components.png)

*从左到右：只有环境光（死板的平色）、只有漫反射（有立体感但没亮斑）、只有高光（黑底上一个亮点）、三项相加。*

**🔧 手算 4：算一个点的颜色**

设 `k_a=0.1, I_a=1`；`k_d=0.6, k_s=0.4, p=32`；一个光源在 `r=2` 处、`I=4`；该点 `n·l = 0.8`、`n·h = 0.95`。

| 项 | 计算 | 值 |
|---|---|---|
| 环境 | `0.1 × 1` | **0.10** |
| 到达强度 | `I/r² = 4/4` | `1.0` |
| 漫反射 | `0.6 × 1.0 × 0.8` | **0.48** |
| 高光 | `0.4 × 1.0 × 0.95^32` | `0.4 × 0.194 =` **0.078** |
| **合计** | `0.10 + 0.48 + 0.078` | **0.658** |

**注意高光项**：`0.95` 看起来"很接近 1"，但 `0.95^32` 只有 `0.194` —— 这就是 P56 说的"`p` 让叶瓣变窄"。

## 9. 从 Blinn-Phong 到 BRDF

#### P67–P73　Ashikhmin-Shirley BRDF

![P067 · 更真实的 BRDF](images/p067.png)

*讲义用七页介绍一个更真实的模型。**它的动机不是"更准"，而是"Blinn-Phong 做不出这几种效果"**。*

![P070 · 各向异性高光](images/p070.png)

![P069 · 能量守恒](images/p069.png)

*Blinn-Phong 的 `k_d + k_s` 可以超过 1（凭空发光）。**Ashikhmin-Shirley 的改进之一就是让两者能量守恒。***

*拉丝金属、头发、丝绸的高光是**长条**而不是圆点 —— 这叫各向异性，Blinn-Phong 表达不了。*

*More realistic specular term (for some materials) · Anisotropic specularities · Fresnel behavior (grazing angle highlights) · Energy preserving diffuse term*

![P67 · 更真实的 BRDF](images/p067.png)

讲义用七页介绍一个**比 Blinn-Phong 更真实**的模型（Ashikhmin & Shirley, 2000），四个改进点：

| 改进 | 解决什么 |
|---|---|
| **各向异性高光** | 拉丝金属、头发、丝绸的高光是**长条**的，不是圆点 |
| **菲涅耳行为** | 掠射角时反射变强（所以水面远处格外亮） |
| **能量守恒的漫反射项** | Blinn-Phong 的 `k_d + k_s` 可以超过 1（凭空发光） |
| 漫反射 + 高光两部分（和原来一样） | 结构不变 |

#### 微表面模型：Blinn-Phong 的"物理版"

Blinn-Phong 的高光项 `(n·h)^p` 是一个**手工拟合**。物理上正确的做法是把表面看成**无数微小镜面**：

$$
f_{\text{spec}}(l,v)=\frac{F(l,h)\,D(h)\,G(l,v)}{4(n\cdot l)(n\cdot v)}
$$

| 因子 | 管什么 | 常用模型 |
|---|---|---|
| **`F`** 菲涅耳 | 掠射角反射变强 | Schlick 近似 |
| **`D`** 法线分布 | 微表面朝向的统计 | GGX / Beckmann |
| **`G`** 几何遮蔽 | 微表面互相遮挡 | Smith |

**为什么它比 Blinn-Phong 好**：

- **能量守恒**（`k_d` 和 `k_s` 自动平衡）
- **掠射角正确变亮**（菲涅耳）
- **粗糙度有物理含义**（`D` 的宽度）

**但你仍然需要知道 Blinn-Phong** —— 因为：

1. 它是**最便宜的可用模型**（几个乘加）
2. 它的参数直觉（`k_d`/`k_s`/`p`）**直接对应美术的手感**
3. 微表面模型的很多实现**仍然用 Blinn-Phong 的 `(n·h)^p` 作为 `D` 的近似**

#### P74　BRDF

![P076 · 超越 BRDF](images/p076.png)

![P073 · 各向异性的效果](images/p073.png)

*同一材质在不同观察方向下的高光形状。**各向异性不是"更真实"，而是"更符合某类材质"**（拉丝金属、头发）。*

*BRDF 假设"光在同一进同一点出"。但蜡、皮肤、大理石**光会进到内部再散射出来** —— 那需要 BSSRDF。*

*The Bi-directional Reflectance Distribution Function · Given: surface material, incoming light direction, direction of viewer, orientation of surface · Return: fraction of light that reaches the viewer*

![P74 · BRDF 的定义](images/p074.png)

**定义**：给定**材质、入射方向、出射方向、表面朝向**，返回"有多少比例的光被反射到观察者"。

$$
\rho(v,l,n)
$$

**关键一句**：***"Phong shading is one example of a computed BRDF."***
> Blinn-Phong 就是一个"手工设计出来的 BRDF"。

![BRDF：四维的方向函数](diagrams/d16-brdf.png)

*BRDF 是一个四维函数（入射方向二维 + 出射方向二维）。Blinn-Phong 只是其中一个特例；真实材质需要更复杂的函数，甚至**实测**得到。*

#### P75–P76　Beyond BRDFs

*The BRDF model does not capture everything · e.g. Subsurface scattering (BSSRDF) · Inter-frequency interactions*

![P75 · 次表面散射](images/p075.png)

**BRDF 的两个局限**：

| 局限 | 例子 |
|---|---|
| **次表面散射（BSSRDF）** | 蜡、皮肤、大理石、牛奶 —— 光**进到材料内部**散射后再出来，不满足"同点进出" |
| **跨频率交互** | 荧光材料：入射是紫外（看不见），出射是可见光。BRDF 假设"进什么频率出什么频率" |

#### P77–P81　Measuring BRDF

![P080 · 实测的 BRDF 数据](images/p080.png)

*用机械臂把光源和相机绕样本转一圈，记录每个角度组合的反射率。**这就是"用数据代替公式"**。*

*Images from Marc Levoy · Cornell University Program of Computer Graphics*

![P77 · 测量 BRDF 的装置](images/p077.png)

![P78 · 实测的车漆 BRDF](images/p078.png)

五页展示**实测 BRDF**：用机械臂把光源和相机绕样本转一圈，记录每个角度组合下的反射率。

**P78–P81 的四张图分别对应**：汽车漆、气雾喷漆、房屋涂料、有机玻璃板。

> **🔭 实测数据为什么重要**
>
> 因为**没有一个解析公式能准确描述真实材质**。车漆里有金属薄片（各向异性 + 菲涅耳），喷漆有颗粒感，这些都超出 Blinn-Phong 的表达能力。
>
> 所以工业界（尤其是产品渲染、影视）直接**测一张四维查找表**，渲染时插值查表。**这就是"用数据代替公式"** —— 和第 6 讲"用纹理代替几何"是同一个思路。

#### P82　Other Color Effects

*Images from Gooch et. al, 1998*

![P82 · 暖冷色调技术插图](images/p082.png)

**Gooch 着色**（Gooch et al. 1998）：一种**非真实感渲染**（NPR）技术，用"冷色到暖色"的渐变代替明暗，让技术插图更易读。

**图上的三个箭头**：`pure blue to yellow` + `pure black to object color` = 最终色调。

**为什么放在这里**：说明着色模型不一定非要"像照片" —— **有时候"看得懂"比"真实"更重要**（工程图、医学插图、动画）。

## 10. 着色频率：逐面、逐顶点、逐像素

#### P83　Shading Triangle Meshes

![P91 · 管线结果（分节）](images/p091.png)

*接下来几页展示**同一条管线的不同阶段**：先只有 z-buffer（无色），再逐级加上着色。*

*章节点*

![P83 · 三角网格的着色](images/p083.png)

分节页。前面讲的公式都是"一个点的颜色"。但我们的模型是**三角形**，所以问题是：**在哪里算这个公式？**

#### P84　Shading Frequency: Triangle, Vertex or Pixel

![P84 · 三种着色频率](images/p084.png)

**三种选择，代价与效果都不同**：

| 方法 | 在哪算 | 插值什么 |
|---|---|---|
| **Flat shading**（逐面） | 每个三角形算一次 | 不插值，整个面一个颜色 |
| **Gouraud shading**（逐顶点） | 每个顶点算一次光照 | **插颜色** |
| **Phong shading**（逐像素） | 每个像素算一次 | **插法线**，再算光照 |

![三种频率：插的是什么](diagrams/d10-shading-frequency.png)

*差别只在"插值对象"上：flat 不插；Gouraud 插颜色（法线不插）；Phong 插法线（光照每次重算）。*

> **⚠️ 一个命名陷阱**
>
> 这里的 "Phong shading"（逐像素着色）和反射模型里的 "Phong"（Blinn-Phong 的前身，1975）**是两件事**，只是都叫 Phong。
>
> - **Phong reflection model** = 一个着色公式
> - **Phong shading** = 一种着色频率（逐像素）
>
> 考试里常拿这个混淆。

#### P85–P88　Shading Frequency: Face, Vertex or Pixel

*Num Vertices × Shading freq. × Shading type*

![P85 · 面数 × 频率的对照矩阵](images/p085.png)

**这一页是"九宫格"矩阵**：横轴是着色频率（Face / Vertex / Pixel），纵轴是网格密度（Num Vertices 三档）。

**读法**：**提高网格密度和提高着色频率，效果类似但代价完全不同** —— 加密网格要更多三角形（几何成本），提高着色频率只是多算几次（计算成本）。

#### P86–P88　局部放大：三种方法的病灶

![Gouraud 的高光会消失](diagrams/d21-gouraud-highlight.png)

*高光落在三角形**内部**时，三个顶点都不亮 → 插值出来整片都是暗的 → **高光消失**。反过来落在顶点上，又会被插值**摊满整个三角形**。*

![P86 · Flat 的两个问题](images/p086.png)

![P87 · Gouraud 的两个问题](images/p087.png)

![P88 · Phong 的一个问题](images/p088.png)

三页逐一把病灶圈出来（这是全讲最有价值的三张图）：

| 方法 | 病灶 | 讲义原话 |
|---|---|---|
| **Flat** | ① 相邻面的亮度差形成**假的边缘** | *"Note apparent edge enhancement"* |
| | ② 高光会**整个面都亮** | *"Note specular 'taking over' entire face"* |
| **Gouraud** | ① **C1 不连续**（颜色导数跳变，出现条带） | *"Note C1 interpolation artifacts"* |
| | ② 高光被**摊到好几个三角形上** | *"Note specular spread out over several triangles"* |
| **Phong** | ① 轮廓仍然是**多边形**（因为几何没变） | *"Smooth shading, faceted silhouette"* |
| | ② 高光中心可能出现**过曝截断**（平坦的亮斑） | *"clipping ... where center of specularity appears flat"* |

![三种频率的球体对比](diagrams/d11-shading-artifact.png)

*同一个球：Flat 是分块的（每个面一个法线）；Gouraud 是"块状渐变"（顶点算法线、块内插颜色）；Phong 才是光滑的，高光是圆的。*

> **📌 为什么 Gouraud 的高光会"摊开"**
>
> 因为 Gouraud 在**顶点**上算光照。如果高光恰好落在三角形**内部**（没碰到任何顶点），那么三个顶点都不亮 —— **插值出来的整个面都不亮，高光就消失了**。
>
> 反过来，如果高光碰到了一个顶点，那个顶点会很亮，然后这个亮度被**线性插值铺满整个三角形**，高光就"摊"成一大片。
>
> **这就是"逐顶点"的根本局限：采样点（顶点）太稀疏，抓不住小而锐的特征。**

#### P89–P94　Result of ... Pipeline

![P094 · 逐像素着色的结果](images/p094.png)

*逐像素着色的最终效果。**注意小字提醒"做了曝光校正"** —— 否则高光会溢出 255 变成死白。*

![P89 · z-buffer 管线的结果](images/p089.png)

![P92 · Gouraud 的结果](images/p092.png)

![P93 · 逐像素着色的结果](images/p093.png)

六页展示同一场景（两个球）在管线不同阶段的输出：

| 页 | 阶段 | 现象 |
|---|---|---|
| P89 | z-buffer 之后（无色） | 只有轮廓，没有光照 |
| P90–P91 | Flat shading | 球变成"多面体" |
| P92 | Gouraud | 光滑但高光不对 |
| P93–P94 | 逐像素 | 正确 |

**P94 的小字很有意思**：*"Note that this image is correctly 'exposed' so that the specularities don't overflow 255 max display value."*
> 这张图**做了曝光校正**，所以高光没有溢出 255。

**这提醒一件事**：即使着色公式正确，**显示器只有 8 位**（0–255）。高光值常常远超 1.0，直接截断就会变成一片死白（P88 那个"高光中心发平"的病灶）。**这就是后来 HDR + tone mapping 要解决的问题。**

## 11. 法线：从哪来，怎么变换

#### P95–P98　Defining Per-Vertex Normal Vectors

![P097 · 球面法线的解析解](images/p097.png)

*球面的顶点法线可以直接从位置算：**`n = normalize(p − center)`**。这比"平均面法线"更准也更便宜 —— **有解析解时优先用解析解**。*

#### 为什么现代引擎一律用逐像素

除了画质，还有一个**工程原因**：**着色频率和"材质表现力"直接绑定**。

| 想做的事 | 需要什么频率 |
|---|---|
| 纹理贴图 | 逐像素（纹理坐标要在片元里查） |
| 法线贴图 | **逐像素**（法线来自纹理，顶点上根本没有） |
| 环境光遮蔽 | 逐像素（查 AO 贴图） |
| 粗糙度/金属度贴图 | 逐像素 |
| 各向异性高光 | 逐像素（要切线方向） |

**关键洞察**：**所有"PBR 材质"都依赖逐像素法线**。一旦有了法线贴图，Gouraud 就彻底出局了 —— 因为顶点上的法线根本不能代表"贴图里那个起伏的表面"。

**所以 Gouraud 在今天的位置**：**只在极低端设备或极远处物体上用**（远处一个像素覆盖几十个三角形，逐顶点足够了）。

![P095 · 法线从哪来](images/p095.png)

*分节页：**顶点没有天然的法线**，必须从几何或邻面推出来。*

*Best to get vertex normals from the underlying geometry · Otherwise have to infer vertex normals from triangle faces · Simple scheme: average surrounding face normals*

![P96 · 顶点法线 = 面法线加权平均](images/p096.png)

![P98 · 平均的示意](images/p098.png)

$$
\mathbf{N}_v=\frac{\sum_i w_i\mathbf{N}_i}{\sum_i w_i}
$$

**两种来源**：

| 来源 | 说明 |
|---|---|
| **从底层几何直接取** | 比如球面：顶点法线就是归一化的顶点位置。**最好** |
| **从面法线反推** | 把周围的面法线加权平均 |

**讲义留了个问题**：***"What weights to use?"***（用什么权重？）

![顶点法线的平均](diagrams/d12-vertex-normal.png)

*一个顶点周围有若干面，把它们的法线加权平均。权重可以取等权、按面积、或按夹角。*

**🔧 手算 5：等权平均一个"角"**

设某顶点被三个面共用，面法线（已归一化）为：

$$
\mathbf{N}_1=(0,1,0),\quad \mathbf{N}_2=(0.6,0.8,0),\quad \mathbf{N}_3=(-0.6,0.8,0)
$$

等权平均：

$$
\mathbf{N}_v=\frac{(0,1,0)+(0.6,0.8,0)+(-0.6,0.8,0)}{3}=\frac{(0,\ 2.6,\ 0)}{3}=(0,\ 0.867,\ 0)
$$

**归一化后是 `(0,1,0)`** —— 正好朝上 ✓（三个法线关于 `y` 轴对称，所以平均后回到 `y` 轴）

**注意分母 `Σw_i`**：平均之后再**归一化一次**。很多实现漏了这步，导致法线长度不是 1，光照强度出错。

#### P99–P100　Where are the normals?

*Per-Face normals · Per-Vertex normals · Per-Vertex-Per-Face normals*

![P99 · 三种法线](images/p099.png)

![P100 · 平滑边 vs 尖锐边](images/p100.png)

**三种法线的区别**（图上画了正方体的一角）：

| 类型 | 数量 | 用在哪 |
|---|---|---|
| **Per-Face** | 每个面一个 | Flat shading |
| **Per-Vertex** | 每个顶点一个（所有共用面共享） | Gouraud/Phong 的**光滑**表面 |
| **Per-Vertex-Per-Face** | "顶点 × 面"一个 | 既能光滑又能保留**硬边** |

最后那种叫 **"split vertex"**（拆点）：在**尖锐的边**上，同一个顶点位置存**多个**不同法线，每个面用自己那个。

**P100 的标注**：
- `a) is a smooth edge/vertex` —— 相邻面夹角小，可以共享法线
- `b) is a sharp edge/vertex` —— 夹角大，必须拆开，否则倒角会被"抹圆"

#### P101　Smooth Shading

![P105 · 一般网格的规则](images/p105.png)

*面法线平均得到顶点法线。**权重怎么选**是讲义留的问题 —— 等权、按面积、或按夹角。*

![P101 · 平滑着色](images/p101.png)

一组带"尖锐边"的物体（blender.stackexchange 的图）。

**这一页在展示"硬边与软边可以共存"**：同一个模型上，有些边要光滑（曲面部分），有些边要保持锐利（倒角）。**靠的就是 split vertex + 自定义法线。**

#### P102–P103　Defining Per-Pixel Normal Vectors

*Barycentric interpolation of vertex normals · Problem: length of vectors?*

![P102 · 插值法线](images/p102.png)

![P103 · 问题：长度](images/p103.png)

**做法**：用第 6 讲的重心坐标插值法线：

$$
\mathbf{n}=\alpha\mathbf{n}_A+\beta\mathbf{n}_B+\gamma\mathbf{n}_C
$$

**但有个问题（标题就是问句）**：***"Problem: length of vectors?"***

**为什么**：三个单位向量线性插值，结果**一般不是单位向量**。例如两个相反的法线 `(1,0,0)` 和 `(-1,0,0)` 插值中点得到 `(0,0,0)` —— **零向量**，归一化就炸了。

**解法**：**插值后必须重新归一化**。

> **⚠️ 这是法线插值的必修课**
>
> ```glsl
> vec3 n = normalize(a * nA + b * nB + c * nC);  // normalize 不能省
> ```
>
> 漏掉 `normalize` 的后果：光照强度随位置轻微变化（因为点积 `n·l` 被 `|n|` 缩放），在法线变化剧烈的地方尤其明显。

#### P104–P107　Careful: Transforming Normal Vectors

*Must use inverse transpose matrix · Derivation*

![P104 · 原物体与法线](images/p104.png)

![P106 · 用 M 变换法线是错的](images/p106.png)

![P107 · 推导](images/p107.png)

**这是全讲最容易忘的一个细节**：

> 变换**顶点**用 `M`，变换**法线**必须用 **`M⁻ᵀ`（逆转置）**。

**P107 的推导**（很干净，值得跟一遍）：

设切向量 `t`、法线 `n`，它们垂直：`tᵀn = 0`。
变换后切向是 `Mt`，法线是 `Xn`（待定）。要求仍然垂直：

$$
(Mt)^T(Xn)=t^T(M^TX)n=0
$$

要让这个式子对任意 `t` 成立，需要 `MᵀX = I`，即：

$$
X=(M^T)^{-1}=M^{-T}
$$

**所以 `X = M⁻ᵀ`。**

![法线要用逆转置](diagrams/d13-normal-transform.png)

*左：原始正方形和它的法线。中：用 `M` 变换法线 —— 法线跟着错切，不再垂直于表面。右：用 `M⁻ᵀ` —— 恢复垂直。*

**🔧 手算 6：一个错切的例子**

取一个把 `x` 方向拉伸的矩阵（`M` 只缩放 `x`）：

$$
M=\begin{bmatrix}2&0\\0&1\end{bmatrix}
$$

法线是 `n = (1,0)`（水平面朝 `x`）。表面被"拉宽"后，法线**应该仍然指向 `x` 方向**（因为表面只是变宽，没倾斜）。

**用 `M` 变换**：`M n = (2, 0)` → 归一化 `(1,0)` ✓ **看起来对**。

**但换个法线**：`n = (1,1)/√2`（斜 45° 的面）。表面被横向拉宽 2 倍后，这个面会**变缓**，法线应该**更偏向 `y`**。

**用 `M` 变换**：`M n = (2,1)/√2` → 归一化 `(0.894, 0.447)` —— **更偏 `x` 了，错**。

**用 `M⁻ᵀ`**：`M⁻ᵀ = [[0.5,0],[0,1]]`，`M⁻ᵀ n = (0.5,1)/√2` → 归一化 `(0.447, 0.894)` —— **更偏 `y` 了 ✓**

**所以非均匀缩放是最容易暴露这个错误的情形。** 纯旋转时 `M⁻ᵀ = M`，所以很多 demo 看不出问题 —— 一旦有人给物体加了非均匀缩放，光照就突然不对了。

## 12. 完整管线与 shader

#### P108　Rasterization Pipeline

![P108 附 · 管线全貌](images/p108.png)

*最后一块拼图：把前面所有技术**装进五个阶段**。*

*章节点*

![P108 · 光栅化管线](images/p108.png)

分节页。最后把五个阶段串起来。

#### P109–P114　Rasterization Pipeline

![P110 · 顶点处理](images/p110.png)

*阶段 ①：**顶点处理**。把顶点变换到屏幕空间，并算出后续要插值的属性（`varying`）。*

*Vertex Processing · Triangle Processing · Rasterization · Fragment Processing · Framebuffer Operations*

![P109 · 管线示意（起点）](images/p109.png)

![P112 · 管线全貌](images/p112.png)

讲义用六页把管线逐步展开：

| 阶段 | 输入 | 输出 | 这一讲讲过的对应 |
|---|---|---|---|
| **① Vertex Processing** | 3D 顶点 | 屏幕空间顶点 + 变换后的法线 | L04–05 变换；本讲 P104 法线变换 |
| **② Triangle Processing** | 顶点流 | 三角形流（已装配、剔除、裁剪） | — |
| **③ Rasterization** | 三角形 | **片段流**（每个被覆盖的样本一个） | L02 覆盖判定；L06 重心坐标插值 |
| **④ Fragment Processing** | 片段 | 着色后的片段 | **本讲 Blinn-Phong**；L06 纹理 |
| **⑤ Framebuffer Operations** | 着色片段 | 像素 | **本讲 z-buffer**；混合 |

**图上还有两个词值得注意**：

- **Application**（最左）：CPU 侧的逻辑（碰撞、AI、场景图）
- **Display**（最右）：送到显示器

**所以"图形管线"是 CPU → GPU → 显示器的一条完整流水线**，而不只是 GPU 内部的事。

#### P115–P117　Shader Programs

![P116 · 顶点 shader 与片元 shader](images/p116.png)

*两个可编程阶段：**vertex shader 处理顶点**、**fragment shader 处理片段**。中间的光栅化和插值是硬件做的。*

*Program vertex and fragment processing stages · Describe operation on a single vertex (or fragment)*

![P115 · 一个 GLSL 片元着色器](images/p115.png)

```glsl
uniform sampler2D myTexture;
uniform vec3 lightDir;
varying vec2 uv;
varying vec3 norm;

void diffuseShader() {
  vec3 kd;
  kd = texture2d(myTexture, uv);
  kd *= clamp(dot(-lightDir, norm), 0.0, 1.0);
  gl_FragColor = vec4(kd, 1.0);
}
```

**这七行代码把前三讲全串起来了**：

| 行 | 用到什么 |
|---|---|
| `texture2d(myTexture, uv)` | **L06 纹理映射**（在 `uv` 处重采样） |
| `clamp(dot(-lightDir, norm), 0, 1)` | **本讲 Lambert 余弦定律**（含 `max(0,·)` 的防御） |
| `varying vec2 uv` / `varying vec3 norm` | **L06 重心插值**（`varying` = 由光栅化器插值） |
| `uniform` | CPU 侧传进来的常量 |

**三条说明（讲义原文）**：

> - Shader function executes **once per fragment**
> - Outputs color of surface at the current fragment's screen sample position
> - This shader performs a texture lookup ... then performs a **diffuse lighting calculation**

**`varying` 这个关键字特别值得注意**：它标记"这个变量**会被光栅化器插值**"。也就是说，三角形三个顶点各自的 `uv`、`norm` 会在片上被**自动插值** —— 而这正是 P102 那个"插值后要归一化"的责任落点（实际上 shader 里通常自己 `normalize(norm)`）。

#### P118　Shader Programs

*Measuring and Modeling the Appearance of Finished Wood · Stephen R. Marschner et al., SIGGRAPH 2005 · Code on GitHub*

![P118 · 木纹 shader](images/p118.png)

一个研究项目的 shader（Marschner 等人关于木材外观的论文），代码开源在 GitHub。

**为什么放这一页**：说明 **shader 是表达复杂材质的地方** —— 木纹那种层层叠叠的纹理，用固定管线做不出来，必须写程序。

#### P119　Unreal Engine Kite Demo

*Goal: Highly Complex 3D Scenes in Realtime*

![P119 · Unreal 风筝 demo](images/p119.png)

Epic 的 "Kite" 实时 demo（2015）。四个指标：

| 指标 | 数量级 |
|---|---|
| 三角形 | **十万到百万级** |
| shader 复杂度 | 复杂的 vertex + fragment 计算 |
| 分辨率 | 3–5+ 百万像素（还开超采样） |
| 帧率 | 30–60 fps（VR 要更高） |

**这个 demo 的意义**：它是"这一讲所有技术全开"的样子 —— z-buffer + 逐像素 Blinn-Phong + 纹理 + 阴影贴图 + 各种 shader 技巧。

#### P120　Graphics Pipeline Implementation: GPUs

![着色发生在哪个阶段](diagrams/d22-shading-stage.png)

*Flat/Gouraud 把光照算在 **vertex shader**；Phong 把法线传到 **fragment shader** 逐像素重算。**`varying` 的插值由硬件完成**，所以"逐像素"只增加计算量，不增加顶点数据量。*

*Specialized processors for executing graphics pipeline computations*

![P120 · 独立 GPU 与集成 GPU](images/p120.png)

两块硬件：**独立显卡**（NVIDIA Titan X）和**集成 GPU**（Intel CPU 晶片的一部分）。

**"Specialized processors"（专用处理器）** 是关键：GPU 不是"更快的 CPU"，而是**为这条管线专门设计的芯片** —— 里面有大量并行单元 + 固定功能的纹理/光栅硬件。

#### P121–P124　CPU vs GPU

![P122 · GPU 的并行结构](images/p122.png)

*GPU 有**几千个简单核心**，CPU 只有几十个复杂核心。**光栅化和着色天然是数据并行的**，所以 GPU 赢了。*

![P121 · CPU](images/p121.png)

![P123 · GPU](images/p123.png)

四页引用一个 YouTube 视频（`ZrJeYFxpUyQ`）做对比。

**常见的经典对比**：用 CPU 和 GPU 同时做图像处理/物理模拟，GPU 快几十倍。**但更重要的对比是"架构"**：

| | CPU | GPU |
|---|---|---|
| 核心数 | 几个到几十个 | 几千个 |
| 单核能力 | 强（分支预测、乱序、缓存） | 弱 |
| 适合 | 串行、分支多、不规则 | **数据并行、分支少** |
| 图形管线 | 提交绘制命令 | **执行整条管线** |

#### P125　GPU: Heterogeneous, Multi-Core Processor

*Modern GPUs offer ~2-4 Tera-FLOPs of performance for executing vertex and fragment shader programs · Tera-Op's of fixed-function compute capability over here*

![P125 · 异构多核](images/p125.png)

**"Heterogeneous"（异构）是关键词**：GPU 里住着两种完全不同的东西 ——

| 部分 | 能力 |
|---|---|
| **可编程核心** | 2–4 TFLOPs，跑 vertex / fragment shader |
| **固定功能硬件** | "Tera-Op's"（万亿次操作/秒），做光栅化、纹理采样、深度测试 |

**这个数字对比很值得体会**：固定功能硬件的吞吐（Tera-Op）**远高于**可编程部分（Tera-FLOP）—— 因为专用电路不需要取指、译码、调度。

**这也是为什么光栅化、纹理过滤、z-buffer 都是硬件实现的**（第 2 讲 P85 那句"all modern GPUs have special-purpose hardware"在这里得到量化）。

## 13. 定量细节：六个「算一遍就懂」

前面各节给了公式，但很多量只有真的算一次才知道大小。

#### 🔧 手算 7：z-buffer 逐像素走一遍

两个三角形投影到屏幕上，覆盖同一列像素 `x = 0..2`：

| 像素 | 三角形 A 的 `z` | 三角形 B 的 `z` |
|---|---|---|
| `x=0` | 5.0 | —（未覆盖） |
| `x=1` | 5.0 | 2.0 |
| `x=2` | 5.0 | 2.0 |

**初始**：`zbuffer = [∞, ∞, ∞]`，`framebuffer = [背景, 背景, 背景]`。

**先画 A**（`z = 5.0`）：

| 像素 | 比较 | 结果 |
|---|---|---|
| `x=0` | `5.0 < ∞` ✓ | 写 A 的颜色，`z = 5.0` |
| `x=1` | `5.0 < ∞` ✓ | 写 A 的颜色，`z = 5.0` |
| `x=2` | `5.0 < ∞` ✓ | 写 A 的颜色，`z = 5.0` |

**再画 B**（`z = 2.0`）：

| 像素 | 比较 | 结果 |
|---|---|---|
| `x=0` | 未覆盖 | 不变 |
| `x=1` | `2.0 < 5.0` ✓ | 覆盖成 B 的颜色，`z = 2.0` |
| `x=2` | `2.0 < 5.0` ✓ | 覆盖成 B 的颜色，`z = 2.0` |

**最终**：`zbuffer = [5.0, 2.0, 2.0]`，颜色是 A 在 `x=0`、B 在 `x=1,2`。

**关键验证：把绘制顺序反过来。**

**先画 B**（`z=2.0`）：`x=1,2` 写上 B，`z=2.0`。

**再画 A**（`z=5.0`）：

| 像素 | 比较 | 结果 |
|---|---|---|
| `x=0` | `5.0 < ∞` ✓ | 写 A |
| `x=1` | `5.0 < 2.0` ✗ | **丢弃** |
| `x=2` | `5.0 < 2.0` ✗ | **丢弃** |

**结果完全一样** ✓ —— **这就是 z-buffer 的核心性质：与绘制顺序无关。**

#### 🔧 手算 8：`1/r²` 与 `1/r` 的差别有多大

设 `r = 1` 处强度为 1：

| `r` | `1/r²` | `1/r` | 比值 |
|---|---|---|---|
| 1 | 1.000 | 1.000 | 1.0 |
| 2 | 0.250 | 0.500 | 2.0 |
| 4 | 0.0625 | 0.250 | 4.0 |
| 10 | 0.010 | 0.100 | 10.0 |
| 20 | 0.0025 | 0.050 | 20.0 |

**`r=10` 时 `1/r²` 只剩 1%，而 `1/r` 还有 10%** —— 差 10 倍。

**这解释了 P49 的抱怨**：配局部着色时，`1/r²` 让远处**迅速变黑**，而真实照片里远处是"暗但不是黑"（因为间接光）。所以很多引擎用 `1/r` 或加一个常数项。

**但做全局光照时必须用 `1/r²`** —— 否则能量不守恒，场景会越算越亮。

#### 🔧 手算 9：`p` 对高光的敏感性

取 `n·h = 0.9`（偏离镜面方向约 26°），算 `0.9^p`：

| `p` | `0.9^p` | 相对 `p=1` |
|---|---|---|
| 1 | 0.900 | 1.00 |
| 4 | 0.656 | 0.73 |
| 16 | 0.185 | 0.21 |
| 64 | 0.0012 | 0.0013 |
| 256 | 1.5×10⁻¹² | ≈0 |

**`p` 从 16 到 64，亮度掉 150 倍。** 所以：

- 调 `p` 时**要在对数尺度上试**（1, 4, 16, 64, 256），线性地调会"要么没变化、要么全没了"
- 美术工具里常把 `p` 暴露成"粗糙度"（`0..1`），内部再映射成指数 —— 因为直接给 `p` 太难调

**一个实用的映射**（近似物理）：

$$
p\approx\frac{2}{\alpha^2}-2
$$

其中 `α` 是微表面的粗糙度参数。`α=0.1` ⇒ `p≈198`；`α=0.5` ⇒ `p≈6`。

#### 🔧 手算 10：一个点的完整 Blinn-Phong

设：

| 参数 | 值 |
|---|---|
| `k_a, I_a` | `0.1, 1.0` |
| `k_d, k_s, p` | `0.6, 0.4, 32` |
| 光源 `I` | `4.0`，距离 `r = 2` |
| `n·l` | `0.8` |
| `n·h` | `0.95` |

**逐项**：

| 项 | 计算 | 值 |
|---|---|---|
| 到达强度 | `I/r² = 4/4` | `1.0` |
| 环境 | `0.1 × 1.0` | **0.10** |
| 漫反射 | `0.6 × 1.0 × 0.8` | **0.48** |
| 高光 | `0.4 × 1.0 × 0.95³²` | `0.4 × 0.194 =` **0.078** |
| **合计** | | **0.658** |

**再看一个"几乎镜面"的点**：`n·h = 0.99`，其余不变：

$$
0.99^{32}=0.725,\qquad 0.4\times0.725=0.29
$$

**合计 `0.10 + 0.48 + 0.29 = 0.87`** —— 从 0.66 涨到 0.87，**高光项涨了 3.7 倍**。

**这说明**：`n·h` 从 0.95 到 0.99 只差 0.04，但感知上从"有点亮"变成"很亮"。**所以高光边缘的梯度非常陡** —— 低面数时最容易出问题（手算 12）。

#### 🔧 手算 11：法线的逆转置变换

设变换矩阵是"横向拉伸 2 倍"：

$$
M=\begin{bmatrix}2&0\\0&1\end{bmatrix}
\qquad
M^{-T}=\begin{bmatrix}0.5&0\\0&1\end{bmatrix}
$$

**情形 1：法线 `n = (1,0)`（水平面）**

| 用 `M` | 用 `M⁻ᵀ` |
|---|---|
| `(2,0)` → 归一化 `(1,0)` | `(0.5,0)` → 归一化 `(1,0)` |

**两者一样** —— 因为法线正好沿拉伸方向。

**情形 2：法线 `n = (1,1)/√2`（斜 45°）**

| 用 `M` | 用 `M⁻ᵀ` |
|---|---|
| `M n = (2,1)/√2` → 归一化 `(0.894, 0.447)` | `M⁻ᵀ n = (0.5,1)/√2` → 归一化 `(0.447, 0.894)` |

**差得很远**：一个更偏 `x`（0.894），一个更偏 `y`（0.894）。

**哪个对**？表面被横向拉伸 2 倍后，斜 45° 的面会变得**更平缓**（坡度减半），所以法线应该**更偏向 `y`** ⇒ **`M⁻ᵀ` 正确** ✓

**验证方法**：取切向 `t = (1,−1)/√2`（与 `n` 垂直）。变换后 `t' = M t = (2,−1)/√2`。

- 用 `M n`：`(2,1)·(2,−1)/2 = (4−1)/2 = 1.5 ≠ 0` **不垂直** ✗
- 用 `M⁻ᵀ n`：`(0.5,1)·(2,−1)/2 = (1−1)/2 = 0` **垂直** ✓

**这就是"法线用逆转置"的数值证据。**

#### 🔧 手算 12：三种着色频率的代价

设一个模型有 `V = 10,000` 个顶点、`F = 20,000` 个三角形，屏幕覆盖 `P = 500,000` 个像素。

| 方法 | 光照计算次数 | 相对代价 |
|---|---|---|
| **Flat**（逐面） | `F = 20,000` | 1× |
| **Gouraud**（逐顶点） | `V = 10,000` | 0.5× |
| **Phong**（逐像素） | `P = 500,000` | **25×** |

**所以逐像素着色贵 25 倍**（按光照计算次数算）。

**但注意**：实际 GPU 上差距没这么大，因为：

- 光照计算里 `n·l`、`n·h` 是几次乘加，很便宜
- 真正贵的是**纹理采样**（第 6 讲），三种频率下次数一样
- 现代 GPU 的 ALU 吞吐远高于固定功能单元

**所以实践中的结论是**：**能用 Phong 就用 Phong**。逐顶点着色省下的那点算力，换来的视觉损失（高光消失/糊掉）不值得。

> **📌 什么时候确实需要 Gouraud**
>
> - **极低端硬件**（老手机、WebGL 1 时代的低端设备）
> - **顶点数远小于像素数**（比如远处的物体，`V` 小但 `P` 也小）
> - **想省电**（移动端 VR）
>
> 除此之外，现代引擎默认都是逐像素。

## 14. 实现坑

| 坑 | 症状 | 正解 |
|---|---|---|
| **`z` 的符号搞反** | 看到"背面"或全黑 | 观察空间看向 `−z`，所以"更近"是 `z` 更大；或用正的"距离" |
| **深度缓冲初始化为 0** | 什么都不显示（全部被拒） | 初始化为 `+∞`（或最大深度值） |
| **`n·l` 没裁剪** | 背光面出现黑斑（负光照吃掉其他项） | `max(0, n·l)`，shader 里用 `saturate()` |
| **法线没归一化** | 亮度随位置漂移 | `normalize()`，尤其是插值后 |
| **`p` 用整数** | 高光边缘有阶梯 | 用 `float`；`p` 是连续量 |
| **光源距离没算** | 远近一样亮 | `I/r²`；平行光才不需要 |
| **高光溢出 255** | 亮斑变成一片死白 | HDR + tone mapping（本课不涉及，但要知道） |
| **透明物体用 z-buffer** | 后面的东西消失 | 先画不透明、再画透明（第 3 节） |
| **阴影贴图没加 bias** | 表面出现条纹噪点 | 法线偏移 + 斜率缩放 bias |
| **bias 太大** | 阴影飘离物体 | 随入射角缩放，不要用固定值 |
| **顶点法线平均没归一化** | 光照强度错 | `N_v = ΣwᵢNᵢ / ‖ΣwᵢNᵢ‖` |
| **尖锐边也做了平均** | 倒角被磨圆 | split vertex + 自定义法线 |

### 14.1 一个可用的调试检查表

| 现象 | 先查什么 | 再查什么 |
|---|---|---|
| **全黑** | 光源方向是否反了？`n·l < 0`？ | `k_a` 是否为 0（没有环境光） |
| **全白** | 光照强度是否过大？`1/r²` 里 `r` 太小？ | 是否忘了裁剪到 `[0,1]` |
| **有黑斑** | `n·l` 没裁剪 | 法线朝向错（绕序反了） |
| **明暗方向反了** | `l` 的方向（surface→light 还是 light→surface） | `n` 的方向 |
| **高光位置不对** | `h = normalize(v + l)` 的 `v` 是哪个方向 | `v` 应指向**眼睛** |
| **高光太大/太小** | `p` 的量级（应该在 1~1000） | `k_s` 是否过大 |
| **阴影有条纹** | bias 太小 | 深度图精度（16 vs 24 bit） |
| **阴影飘** | bias 太大 | 是否用了斜率缩放 |
| **物体互相穿透** | 深度测试方向 | `z` 的符号约定 |
| **画面有锯齿** | 没做 MSAA（L03） | 分辨率是否够 |

## 15. 跨讲连接

这一讲是**全课的"总装车间"** —— 前面每一讲都在造零件，这一讲把零件装成一台机器。

| 本讲用到的 | 来自哪讲 | 具体在哪 |
|---|---|---|
| 三角形覆盖判定 | **L02** 光栅化 | 光栅化阶段 |
| 深度与采样 | **L03** 采样 | z-buffer 是"每个样本一个深度" |
| 变换与投影 | **L04–05** 变换 | 顶点处理阶段 |
| 透视除法与 `w` | **L04–05** 变换 | 属性插值要用 `1/w` |
| 纹理采样 | **L06–07** 纹理 | fragment shader 里查表 |
| 重心坐标插值 | **L06** 重心坐标 | `varying` 的插值 |
| 法线变换 `M⁻ᵀ` | **L08–09** 本讲 | 顶点处理阶段 |
| 光线与三角形的可见性 | **L13** 光线追踪 | 同一个"谁挡住谁"问题的另一种解法 |

**三条"回头看才明白"**：

1. **L04–05 的透视除法在这里才"用上"** —— 当时只是"把 `w` 除掉了"，这一讲才发现：**除法之后属性就不能直接线性插值了**（手算 7 的 `u=0.5` vs `0.2`）。**透视除法是"挤扁"现象的根源。**

2. **L06 的重心坐标在这里是"硬件做的事"** —— 讲纹理时我们手算重心坐标，这一讲才知道**那是光栅化器的固定功能**：它把顶点上的 `varying` 插值到每个片段。

3. **光栅化和 L13 的光线追踪是同一个问题的两个方向** —— 一个"三角形 → 像素"，一个"像素 → 三角形"。**而 z-buffer 是"正向"路线的可见性答案，光线求交是"反向"路线的答案。**

**这一讲给下游留的包袱**：

- **几何细节不够**（表面表示）→ L10–12 曲线曲面与网格
- **光照不物理**（局部模型）→ L16–17 全局光照
- **阴影贴图有失真**（分辨率、bias）→ 工业界用级联阴影贴图、PCSS 等
- **透明需要排序** → 工业界用 OIT（顺序无关透明）

## 16. 收尾

#### P126　Things to Remember

![P126 · 要记住的东西](images/p126.png)

讲义的三段式总结：

**Visibility**
- 画家算法 与 z-buffer 算法

**Simple Shading Model**
- 关键几何：光照方向、观察方向、法线
- 环境、漫反射、高光三种反射函数
- 着色频率：三角形 / 顶点 / 片段

**Graphics Rasterization Pipeline**
- 变换、光栅化、着色、纹理、可见性分别发生在哪一步？
- GPU = 实现图形管线的并行处理器

#### P127　Acknowledgments

![P127 · 致谢](images/p127.png)

课件由 **Ren Ng** 与 **James O'Brien** 开发，另有 Kayvon Fatahalian、David Forsyth、Pat Hanrahan、Angjoo Kanazawa、Steve Marschner、Mark Pauly 等贡献。

### 16.1 这一讲留下了什么

**一个值得对照的问题：z-buffer 和光线追踪各自的代价**

| | z-buffer（本讲） | 光线追踪（L13） |
|---|---|---|
| 复杂度 | `O(三角形数)` | `O(像素数 × log 三角形数)` |
| 与分辨率的关系 | **无关** | **成正比** |
| 全局效果 | 要额外 pass（shadow map、SSR） | **天然支持** |
| 4K 场景 | 便宜（三角形数不变） | 贵（像素 ×4） |

**所以现代渲染是混合的**：先用光栅化 + z-buffer 拿到第一遍可见性，再对**需要光线追踪的像素**（反射、阴影）发射光线。**这就是 RTX 的"混合渲染"思路。**

**三条反直觉但重要的结论**：

1. **z-buffer 不需要排序，反而比"排序再画"更快**。直觉上"先排好序再画"更合理，但排序是 `O(n log n)` 且可能无解；**逐像素比较是 `O(n)` 且永远有解**。这是一个"放弃全局最优、换局部简单"的经典胜利。

2. **环境光项没有任何物理依据，却是必需的**。它唯一的作用是"让阴影不要黑得那么假"。**这提醒我们：实时渲染里的很多项都是"补丁"，不是物理** —— 而补丁只要视觉上过关就是合理的。

3. **逐像素着色比逐顶点贵 25 倍（手算 12），但工业界毫不犹豫地选了它**。因为**贵的是算力，而算力在涨；损失的是画质，而画质不会自己回来**。这条经验在很多地方都成立（分辨率、采样数、阴影分辨率）。

**带走的六句话：**

1. **画家算法要求全局顺序，而遮挡不是全局关系** —— 所以它必然出局。
2. **z-buffer 把"全局排序"变成"逐像素比较"**，复杂度 `O(n)`，是硬件实现的可见性标准。
3. **Blinn-Phong = 环境 + 漫反射 + 高光**，三项都不是物理推导，而是**对观察现象的手工拟合**。
4. **高光用半角向量 `h` 代替反射方向 `r`**：便宜且好看，这是 Blinn 的关键技巧。
5. **着色频率决定插值什么**：flat 不插、Gouraud 插颜色、Phong 插法线；病灶各不相同（假边缘 / C1 断带 / 多边形轮廓）。
6. **法线必须用 `M⁻ᵀ` 变换**，且插值后必须归一化 —— 两个都容易被忘记。

**还差什么：**

| 这一讲没解决 | 谁来解决 |
|---|---|
| 曲线曲面怎么表示（硬边太贵） | L09–11 Bézier / B 样条 |
| 网格怎么简化、重网格化 | L11–12 几何处理 |
| 真实的光传输（全局光照） | L16–17 路径追踪 |
| 材质物理模型（微表面、能量守恒） | L16–17 及后续 |
| HDR 与 tone mapping | 工业和后续课程 |
| 硬件抗锯齿（MSAA）与 TAA | 第 3 讲的工程延伸 |

> **📌 下次课的第一句话**
>
> 这一讲最后提到"几何细节极其复杂"（P11）。**用三角形去描述一个光滑曲面，永远是在近似** —— 而且三角形越多，z-buffer 和着色就越贵。
>
> 下一讲换一条路：**用数学函数（多项式）直接描述曲线和曲面**。这就是 Bézier 曲线与 B 样条（L09–11）。

---

### 16.2 一张图记住整讲

```
要画一个 3D 场景
   ├─ 谁挡住谁？
   │    ├─ 画家算法（要排序，循环遮挡时无解）
   │    ├─ z-buffer（逐像素比较，O(n)，与顺序无关）← 赢家
   │    └─ 阴影贴图（从光源渲染深度，复用 z-buffer）
   ├─ 表面多亮？
   │    ├─ 环境光（常数，补间接光）
   │    ├─ 漫反射（k_d · max(0, n·l) · I/r²）
   │    └─ 高光（k_s · max(0, n·h)^p · I/r²）
   ├─ 在哪里算？
   │    ├─ Flat（每面一次，有假边缘）
   │    ├─ Gouraud（每顶点一次，高光会消失）
   │    └─ Phong（每像素一次，贵但正确）← 现代默认
   └─ 怎么装起来？
        顶点处理 → 三角形装配 → 光栅化 → 片元处理 → 帧缓冲
```

**读法**：每一层都是一个"分叉"，**每个分叉都对应一次取舍**（排序 vs 比较、常数 vs 物理、便宜 vs 正确）。**如果你能说出每个分叉"为什么选了右边"，这一讲就掌握了。**

## 附录 A · 公式速查

| 对象 | 公式 | 备注 |
|---|---|---|
| **z-buffer 测试** | `if (z < zbuffer[x,y]) { 写颜色; zbuffer = z; }` | 与绘制顺序无关 |
| 深度初始化 | `zbuffer = +∞` | 0 会导致全被拒 |
| **Lambert 漫反射** | `L_d = k_d (I/r²) max(0, n·l)` | `max` 不能省 |
| **Blinn-Phong 高光** | `L_s = k_s (I/r²) max(0, n·h)^p` | `h = normalize(v+l)` |
| 半角向量 | `h = (v+l)/‖v+l‖` | 比算反射 `r` 便宜 |
| **环境光** | `L_a = k_a I_a` | 常数，无方向 |
| **三项求和** | `L = L_a + Σ(L_d + L_s)` | 多光源时逐光累加 |
| 光强衰减 | `I/r²`（物理）/ `I/r`（折中） | 全局光照必须 `1/r²` |
| `p` 与粗糙度 | `p ≈ 2/α² − 2` | `α` 是微表面粗糙度 |
| 余弦定律 | `E = E₀ cos θ = E₀ (l·n)` | 60° 时减半 |
| **法线变换** | `n' = normalize(M⁻ᵀ n)` | 非均匀缩放时 `M` 是错的 |
| 顶点法线 | `N_v = ΣwᵢNᵢ / ‖ΣwᵢNᵢ‖` | 平均后必须归一化 |
| 透视校正插值 | 插 `u/w`、`1/w`，再相除 | 否则"挤扁" |
| 阴影贴图判据 | `d > depth_map` ⇒ 阴影 | `d` = 到光源距离 |
| bias | `bias ∝ tan θ`（斜率缩放） | 固定 bias 会 peter-pan |
| 着色代价 | flat `F` / Gouraud `V` / Phong `P` | `P ≫ V`，但现代 GPU 不在乎 |

## 附录 B · 127 页索引

| 页码 | 主题 | 为什么在这儿 |
|---|---|---|
| P1 | Section 6: The Rasterization Pipeline | 封面 |
| P2 | 已覆盖的五步 | 前七讲成果清单 |
| P3–P8 | 旋转立方体（六帧） | 目前能做到的水平 |
| P9–P10 | 照片级渲染 | 差距在哪 |
| P11 | **三个缺口**：几何 / 光照材质 / 相机 | 后续几讲地图 |
| P12 | 课程地图 | 今日：可见性 + 着色 + 管线 |
| P13 | Visibility | 分节 |
| P14–P23 | **画家算法**（从后往前画） | 最直观的策略 |
| P24 | 画家算法的两个问题 | 排序 + 无解；BSP 树的提示 |
| P25–P31 | **z-buffer 的思路** | 每样本记最小 z；额外缓冲 16–32 bit |
| P32 | z-buffer 示例 | 渲染图 vs 深度图 |
| P33 | **z-buffer 伪代码** | 四行核心；Z vs −Z 的坑 |
| P34 | 深度测试图示 | 两个三角形的掩码合并 |
| P35 | 复杂度 O(n)；地位；问题 | overdraw / transparency |
| P36 | 透明需要部分排序 | 先不透明后透明；Good/Not Good |
| P37 | Deep Alpha Buffer | 每像素存 RGB-Z 链表 |
| P38 | **阴影贴图四步** | 复用 z-buffer |
| P39 | 阴影效果 | Stamminger & Drettakis 2002 |
| P40 | 深阴影贴图 | 半透明遮挡物 |
| P41 | 签到（visibility，Lecture 8） | 讲次确认 |
| P42 | Simple Shading（Blinn-Phong） | 分节 |
| P43 | 今天的 vs 后面的 | 局部模型 vs 物理模型 |
| P44 | **三处感知观察** | 高光 / 漫反射 / 环境光 |
| P45 | 局部着色的输入 | `v, n, l` + 参数；必须归一化 |
| P46–P48 | 光强衰减 `1/r²` | 平方反比 |
| P49 | 衰减的取舍 | 局部模型配 `1/r²` 会难看 |
| P50 | **Lambert 余弦定律** | 60° 恰好一半 |
| P51 | **兰伯特公式** | `k_d (I/r²) max(0, n·l)` |
| P52 | 哑光效果 | `k_d` 递增 |
| P53 | 高光观察 | 小而亮、随视角移动 |
| P54 | 高光取决于视角 | 只在镜面方向附近亮 |
| P55 | **半角向量 `h`** | `(v+l)/‖v+l‖`；Blinn 的技巧 |
| P56 | 余弦幂曲线 | `p` 越大越窄 |
| P57 | `p = 1…256` 的球 | 光滑度可视化 |
| P58 | 同时变 `k_s` 与 `p` | 两个参数的作用 |
| P59 | 点光源 vs 平行光 | `l` 是否随位置变化 |
| P60 | 聚光灯、负光源 | 实用效果 |
| P61–P62 | "Ugly...." | 没有环境光时阴影纯黑 |
| P63–P64 | **环境光** `L_a = k_a I_a` | 承认失败的项 |
| P65–P66 | **三项求和** | 多光源要累加 |
| P67–P73 | Ashikhmin-Shirley BRDF | 各向异性 + 菲涅耳 + 能量守恒 |
| P74 | **BRDF 定义** | Blinn-Phong 是一个特例 |
| P75–P76 | 超越 BRDF | 次表面散射、跨频率 |
| P77 | 测量 BRDF 的装置 | Levoy 的机械臂 |
| P78–P81 | 实测 BRDF（四种涂料） | 用数据代替公式 |
| P82 | Gooch 着色 | 非真实感渲染 |
| P83 | Shading Triangle Meshes | 分节 |
| P84 | **三种着色频率** | flat / Gouraud / Phong |
| P85 | 面数 × 频率矩阵 | 加密 vs 提频率 |
| P86–P88 | 三种方法的病灶 | 假边缘 / C1 断带 / 多边形轮廓 |
| P89–P94 | 管线各阶段结果 | z-buffer → flat → Gouraud → 逐像素 |
| P95–P98 | **顶点法线平均** | `ΣwᵢNᵢ/Σwᵢ`；权重怎么选 |
| P99–P100 | 三种法线；平滑边 vs 尖锐边 | split vertex |
| P101 | 平滑着色 | 硬边软边共存 |
| P102–P103 | 法线插值；**长度问题** | 插值后必须归一化 |
| P104–P106 | 法线变换：`M` 是错的 | 法线跟着错切 |
| P107 | **`M⁻ᵀ` 的推导** | `tᵀn = 0` → `X = M⁻ᵀ` |
| P108 | Rasterization Pipeline | 分节 |
| P109–P114 | **五个阶段全貌** | 顶点流 → 三角形流 → 片段流 → 像素 |
| P115–P117 | **GLSL 片元 shader** | 七行代码串起前三讲 |
| P118 | 木纹 shader（Marschner） | shader 表达复杂材质 |
| P119 | Unreal Kite demo | 实时渲染的极限 |
| P120 | 独显 vs 集显 | 专用处理器 |
| P121–P124 | CPU vs GPU | 架构差异 |
| P125 | **异构多核** | 可编程 TFLOPs vs 固定功能 Tera-Ops |
| P126 | Things to Remember | 三段式总结 |
| P127 | 致谢 | Ren Ng / James O'Brien 等 |

## 附录 C · 自测 30 题

1. 前七讲已经能画出带纹理的立方体，那还缺哪三样东西？
2. 画家算法的两个致命问题是什么？
3. 什么叫"循环遮挡"？为什么它让排序无解？
4. z-buffer 为什么能做到 `O(n)` 而不需要排序？
5. z-buffer 的 `if (z < zbuffer)` 里，`z` 越大是越近还是越远？这个方向为什么容易搞错？
6. 为什么深度缓冲可以省掉符号位？
7. 半透明物体为什么不能用 z-buffer？两种解法各有什么问题？
8. 阴影贴图的四个步骤是什么？它在复用哪个算法？
9. 深度阴影贴图解决什么问题？和透明度的哪个问题同构？
10. Blinn-Phong 为什么叫"基于感知"而不是"基于物理"？
11. 局部着色模型的"局部"具体指什么？它漏掉了什么？
12. 为什么公式里的 `n, l, v` 必须归一化？不归一化会怎样？
13. 写出 Lambert 余弦定律，并解释 `max(0, ·)` 为什么不能省。
14. 60° 倾斜的板收到多少比例的光？为什么？
15. `1/r²` 衰减在局部着色里为什么"看起来难看"？全局光照为什么必须用它？
16. 半角向量 `h` 怎么算？为什么用它代替反射方向 `r`？
17. `p = 16` 和 `p = 64`，在 `n·h = 0.9` 处的亮度差多少倍？
18. 点光源和平行光在视觉上有什么区别？为什么性能不同？
19. 环境光项有物理依据吗？它在补什么？
20. flat / Gouraud / Phong 三种着色，各自插值什么？各自的典型病灶是什么？
21. 为什么高光落在三角形内部时，Gouraud 会让它"消失"？
22. 顶点法线怎么算？"split vertex" 用来解决什么？
23. 法线插值后为什么必须归一化？什么情况下会出零向量？
24. 证明法线要用 `M⁻ᵀ` 变换；为什么纯旋转时"用 `M` 也对"？

27. 手算：`p=16` 与 `p=64`，在 `n·h=0.9` 处的亮度差多少倍？
28. 手算：`M = diag(2,1)`，法线 `(1,1)/√2`，分别用 `M` 和 `M⁻ᵀ` 变换，哪个保持垂直？
29. 手算：`V=10000`、`P=500000`，flat/Gouraud/Phong 的光照计算次数各是多少？
30. 阴影贴图的 bias 为什么不能是固定值？"斜率缩放"解决什么问题？

## 附录 D · 术语表

| English | 中文 | 一句话 |
|---|---|---|
| visibility / hidden surface removal | 可见性 / 隐面消除 | 决定哪个表面被看到 |
| painter's algorithm | 画家算法 | 从远到近画并覆盖 |
| depth buffer / z-buffer | 深度缓冲 | 每样本存最小深度 |
| overdraw | 过度绘制 | 被遮挡的像素也跑了着色 |
| early-Z | 提前深度测试 | 着色前先测深度，省带宽 |
| transparency | 透明度 | 需要混合，不能覆盖 |
| deep alpha buffer | 深透明缓冲 | 每像素存 RGB-Z 链表 |
| shadow map | 阴影贴图 | 从光源渲染深度再比较 |
| shadow acne | 自阴影痤疮 | 深度误差导致自遮挡 |
| bias | 偏移 | 缓解 shadow acne |
| deep shadow map | 深阴影贴图 | 存透射率函数 |
| shading model | 着色模型 | 决定表面多亮的公式 |
| local illumination | 局部光照 | 只看本点的光照 |
| Blinn-Phong | 布林-冯模型 | 环境 + 漫反射 + 高光 |
| ambient | 环境光 | 常数值，补间接光 |
| diffuse / Lambertian | 漫反射 / 兰伯特 | 与视角无关 |
| Lambert's cosine law | 余弦定律 | 斜着收光少，`cos θ` |
| specular | 高光 | 与视角强相关 |
| half vector | 半角向量 | `(v+l)/‖v+l‖` |
| specular exponent | 高光指数 `p` | 控制叶瓣宽度 |
| falloff | 衰减 | `1/r²` 或 `1/r` |
| point light / directional light | 点光源 / 平行光 | `l` 是否随位置变 |
| spot light | 聚光灯 | 带锥角的光源 |
| BRDF | 双向反射分布函数 | 四维的方向函数 |
| BSSRDF | 次表面散射 | 光进材料内部再出 |
| anisotropic | 各向异性 | 高光呈长条 |
| Fresnel | 菲涅耳 | 掠射角反射变强 |
| energy conserving | 能量守恒 | 反射不能超过入射 |
| shading frequency | 着色频率 | 逐面 / 逐顶点 / 逐像素 |
| flat shading | 平直着色 | 每个面一个法线 |
| Gouraud shading | 古洛着色 | 顶点算光照，插颜色 |
| Phong shading | 冯着色（逐像素） | 插法线，逐像素算光照 |
| per-vertex normal | 顶点法线 | 面法线的加权平均 |
| split vertex | 拆点 | 尖锐边处存多个法线 |
| inverse transpose | 逆转置 `M⁻ᵀ` | 法线的正确变换 |
| rasterization pipeline | 光栅化管线 | 五个阶段 |
| fragment | 片段 | 被覆盖的样本 + 插值属性 |
| shader | 着色器 | 跑在 GPU 上的程序 |
| varying | 插值变量 | 由光栅化器插值 |
| uniform | 统一变量 | CPU 传入的常量 |
| fixed-function | 固定功能 | 不可编程的专用电路 |
| early-Z | 提前深度测试 | 着色前先测深度，省带宽 |
| z-fighting | 深度冲突 | 远处两表面精度不够导致闪烁 |
| overdraw | 过度绘制 | 同一像素被画多次 |
| peter-panning | 阴影悬浮 | bias 过大导致阴影脱离物体 |
| shadow acne | 自遮挡痤疮 | bias 过小导致表面自阴影 |
| microsurface | 微表面 | BRDF 的物理模型 |
| Fresnel | 菲涅耳 | 掠射角反射变强 |
| GGX | 一种法线分布 | 现代 PBR 的默认 D 项 |
| PBR | 基于物理的渲染 | 能量守恒的材质体系 |

## 附录 E · 与作业的对应

这一讲对应 CS184 的 **HW1 后半 + HW2 前半（光栅化 + 着色）**。

| 作业任务 | 本讲对应 | 关键要点 |
|---|---|---|
| **z-buffer** | §3 | 初始化 `+∞`；`z` 的符号约定 |
| **Barycentric 插值** | §6（L06） | `varying` 的插值是硬件做的 |
| **Blinn-Phong 着色** | §5–§8 | `max(0, n·l)`、`normalize` |
| **顶点法线** | §11 | 面法线加权平均后归一化 |
| **逐像素法线** | §10 | 插值后 `normalize` |
| **法线变换**（若有） | §11 | `M⁻ᵀ` 而不是 `M` |

### 常见的作业扣分点

| 扣分点 | 后果 | 检查方法 |
|---|---|---|
| z-buffer 初始化为 0 | 什么都不显示 | 打印第一次比较的 `z` 和缓冲值 |
| `z` 符号搞反 | 看到背面 | 用一个"前大后小"的立方体测试 |
| `n·l` 没裁剪 | 背光面黑斑 | 检查 `n·l < 0` 的像素颜色 |
| 法线没归一化 | 亮度漂移 | 断言向量长度 ≈ 1 |
| `l` 方向反了 | 明暗颠倒 | 把光源放在 `+x`，看哪边亮 |
| `v` 方向反了 | 高光位置错 | `v` 应指向眼睛（不是从眼睛指出去） |
| 高光用 `r·v` 但算了 `n·h` | 高光偏大 | 确认用的是同一个量 |
| 颜色没裁剪到 `[0,1]` | 溢出成奇怪的颜色 | 最后 `clamp` |

### 建议的调试顺序

1. **先只画深度图**（把 `z` 映射成灰度），确认深度正确
2. 加 z-buffer 测试，用两个相交的三角形验证遮挡
3. 加 Lambert 漫反射，**把光源绕物体转一圈**，看明暗是否跟着转
4. 加高光，**把 `p` 设为 4 和 64 对比**，确认亮斑大小变化
5. 最后加阴影贴图，先用很大的 bias 看到明显阴影，再逐步调小

**第 3 步是最有效的自检** —— 如果光源转的时候明暗不跟着转，说明 `l` 或 `n` 的方向错了。

## 附录 F · 数值答案（自测对照）

自测里的手算题答案，方便自查：

| 题号 | 答案 |
|---|---|
| 6（立方体 `V−E+F`） | `6 − 12 + 8 = 2` ✓ |
| 8（`1/r²` at `r=10`） | `0.01` —— 只剩 1% |
| 11（60° 的余弦） | `cos 60° = 0.5`，一半 |
| 16（`p=16` vs `64`，`n·h=0.9`） | `0.9¹⁶ = 0.185`，`0.9⁶⁴ = 0.0012`，**差 154 倍** |
| 17（`1/r²` 与 `1/r` 在 `r=10`） | `0.01` vs `0.1`，**差 10 倍** |
| 18（法线 `M` vs `M⁻ᵀ`） | `M` 给 `(0.894,0.447)`（错），`M⁻ᵀ` 给 `(0.447,0.894)`（对） |
| 19（flat/Gouraud/Phong 次数） | `20000 / 10000 / 500000`，Phong 是 flat 的 **25 倍** |
| 20（`z` 初始化） | 必须是 `+∞`（或最大深度），`0` 会导致全部被拒 |

**说明**：这里只列"能算成具体数字"的题；概念题没有唯一答案，请对照正文相应小节。

## 附录 G · 待生成图（提示词占位）
以下两张需要真实渲染质感，matplotlib 做不了，留提示词：

> **〔P1〕`diagrams/d17-earlyz-benchmark.png`**
> 用途：第 3 节「overdraw」的说明
> 提示词：*A false-color visualization of GPU overdraw: a 3D scene of overlapping glass panels and foliage rendered so that each pixel's color encodes how many times it was shaded (blue = 1, green = 2, yellow = 4, red = 8+). Flat lighting, no textures, 1600×900.*
> 建议：附图例，与 `d04-zbuffer.png` 相邻。

> **〔P2〕`diagrams/d18-shadow-acne.png`**
> 用途：第 4 节「shadow acne」的直观证据
> 提示词：*Close-up of a 3D rendered sphere casting a shadow on a flat plane, showing classic shadow acne: stripey self-shadowing moiré bands on the lit surface instead of clean lighting. Neutral gray materials, single directional light, 1600×900.*
> 建议：旁边放一张加 bias 后的干净版本作为对照。
