---
title: "CS184 第 11–12 讲：网格与几何处理"
date: 2026-11-05
summary: "上一讲用数学函数描述曲面，但渲染时最终还是要变成三角形。这一讲处理这个「三角形集合」：怎么存（半边结构）、怎么改（翻边/加点/收边）、怎么变多（Loop 与 Catmull-Clark 细分）、怎么变少（QEM 简化）、怎么变均匀（等向重网格）。配 16 张原创图解、9 个手算、139 页全索引。"
tags: ["计算机图形学", "网格", "细分曲面", "半边结构", "CS184"]
series: "cs184"
order: 11
shortTitle: "L11–12 · 网格与几何处理"
---

> UC Berkeley · CS184/284A Computer Graphics and Imaging · Fall 2026 · Lecture 11–12

上一讲（L10）用参数多项式描述曲面。但**渲染管线只认三角形** —— 所以曲面最后还是要变成网格。而一旦变成了网格，就出现了新的问题：**怎么存、怎么改、怎么变密、怎么变稀**。

这就是"几何处理"（geometry processing）。

```
网格 = 顶点 + 三角形
   ↓ 怎么存
两种：三角形列表（冗余）/ 索引三角形（共享）
   ↓ 相邻关系怎么快速查
拓扑结构：半边（half-edge）—— 每条边拆成两条有向半边
   ↓ 想改网格
三种局部操作：flip / split / collapse
   ↓ 三种全局任务都是它们的组合
① 变密 → 细分（Loop 三角形 / Catmull-Clark 四边形）
② 变稀 → 简化（二次误差度量 QEM）
③ 变匀 → 等向重网格（split/collapse/flip/居中 四步循环）
```

![三种局部操作](diagrams/d08-edge-ops.png)

*翻边（换对角线）、加点（边上插顶点）、收边（边缩成点）。**后面所有全局操作都是这三种的组合** —— 细分主要是 split、简化主要是 collapse、规整三者都用。*

*139 页 · 77 张关键页截图 · 16 张原创图解 · 9 个手算 · 26 道自测*

> **💡 这一讲的位置**
>
> 前面十讲都在**用**网格（光栅化、纹理、着色）。这一讲第一次**把网格本身当作研究对象** —— 关心它的**拓扑、数据结构、编辑操作**。
>
> 这是全课里最"数据结构和算法"的一讲，和第 10 讲的"连续数学"正好互补。

## 1. 网格的规模与三类任务

#### P3　Mesh Examples

![P3 · 网格的例子](images/p003.png)

*网格的例子遍布各类资产：扫描、建模、程序生成。**它们的共同点是"用三角形逼近一个形状"，差别只在分辨率和质量**。*

#### P4　A Small Triangle Mesh

*8 vertices, 12 triangles*

![P4 · 小网格](images/p004.png)

一个最简单的封闭网格：**8 个顶点、12 个三角形**（就是立方体）。

#### P5　A Large Triangle Mesh

*David · Digital Michelangelo Project · 28,184,526 vertices · 56,230,343 triangles*

![P5 · 大卫像扫描](images/p005.png)

**2818 万顶点、5623 万三角形。** 这是斯坦福的 Digital Michelangelo 项目对米开朗基罗《大卫》的 3D 扫描结果。

**这个数字很值得体会**：`5623 万`个三角形，如果每个三角形存 3 个 `float3` 坐标，就是 `56M × 3 × 12 字节 ≈ 2 GB` —— 还没算索引和法线。

#### P6　A Very Large Triangle Mesh

*Google Earth · Meshes reconstructed from satellite and aerial photography · Trillions of triangles*

![P6 · Google Earth](images/p006.png)

**万亿级三角形**（trillions）。这个规模已经**不可能全部放进显存**，必须按视锥和 LOD（细节层次）流式加载。

![网格规模跨了十几个数量级](diagrams/d01-mesh-scale.png)

*从 12 个三角形到万亿级 —— **规模差 11 个数量级**。这就是为什么需要"变密/变稀/变匀"这三类操作：没有一个固定的分辨率能通吃所有场景。*

#### P7–P8　Digital Geometry Processing

*3D Scanning · 3D Printing*

![P7 · 3D 扫描](images/p007.png)

![P8 · 3D 打印](images/p008.png)

**为什么"几何处理"成了一门学科**：

| 应用 | 为什么需要处理网格 |
|---|---|
| **3D 扫描** | 扫出来的原始网格有**噪声、孔洞、几十万冗余三角形** |
| **3D 打印** | 必须**封闭、流形、无自交**，否则打印机会算出错误的内外 |
| 游戏/VR | 需要**多级 LOD** 和**规整**的网格做形变 |

#### P9–P12　Geometry Processing: Tasks

*Three examples*

![P10 · 网格上采样（细分）](images/p010.png)

![P11 · 网格下采样（简化）](images/p011.png)

![P12 · 网格规整](images/p012.png)

讲义给出三类任务（这三个词贯穿全讲）：

| 任务 | 做什么 | 对应算法 |
|---|---|---|
| **Upsampling（细分）** | 增加分辨率，但**保持形状** | Loop、Catmull-Clark |
| **Downsampling（简化）** | 减少三角形，**尽量保形** | QEM 边收缩 |
| **Regularization（规整）** | **改变采样分布**，提高质量 | 等向重网格 |

**注意三者的目标不同**：细分和简化改变**数目**，规整**不改变数目**（或只微调），只改善**三角形形状**。

## 2. 网格表示

#### P13–P15　List of Triangles / Indexed Triangle

![P14 · 三角形列表](images/p014.png)

![P15 · 索引三角形](images/p015.png)

**两种最基础的存法**：

```c
// ① 三角形列表：每个三角形存三个点
struct Triangle { Vec3 v[3]; };
Triangle tris[12];   // 12 * 3 * 12 字节

// ② 索引三角形：点表 + 索引表
Vec3  verts[8];      // 8 个顶点
int   idx[12][3];    // 每个三角形存三个下标
```

![索引 vs 列表](diagrams/d02-indexed-vs-list.png)

*左边的三角形列表把顶点坐标重复存了很多次；右边的索引三角形只存一份顶点，三角形里存下标。*

#### P16　Comparison

*Triangles: + Simple, − Redundant information · Points + Triangles: + Sharing vertices reduces memory usage, + Ensure integrity of the mesh*

![P16 · 两种存法的对比](images/p016.png)

**讲义列了四条**：

| 存法 | 优点 | 缺点 |
|---|---|---|
| **纯三角形列表** | **简单**（不用管索引） | **信息冗余**（一个顶点被 6 个三角形各存一遍） |
| **点 + 索引** | **省内存** | 多一层间接寻址 |
| | **保证完整性** | 改一个顶点，所有用到它的三角形自动跟着变 |

**"Ensure integrity" 这条最容易被低估**：如果是纯三角形列表，你把一个顶点挪了位置，但忘了改某个三角形里的副本 → **网格出现裂缝**。索引结构从根上避免了这个问题。

## 3. 拓扑：流形与 Euler 公式

#### P17–P20　Topology vs Geometry
![P18 · 同拓扑的插值](images/p018.png)

*两个同拓扑的模型之间做逐顶点插值。**这就是形变动画** —— 只要顶点能一一对应，中间帧就是加权平均。*

*Same geometry, different mesh topology · Same mesh topology, different geometry*

![P17 · 拓扑 vs 几何](images/p017.png)

![P19 · 同拓扑可插值](images/p019.png)

**这是全讲最重要的一个区分**：

| | 拓扑（topology） | 几何（geometry） |
|---|---|---|
| 问什么 | **谁和谁相连** | **点在空间的哪个位置** |
| 由什么决定 | 顶点/边/面的邻接关系 | 顶点的坐标 |

![拓扑与几何是独立的](diagrams/d03-topology-geometry.png)

*左边：同一套连接关系（v0-v1-v2），只挪顶点位置 → **同拓扑不同几何**。右边：同一个四边形，两条不同的对角线 → **同几何不同拓扑**。*

**为什么这个区分有用**（P19–P20）：

> 同拓扑的网格之间可以**逐顶点线性插值**：`V_new = αV_1 + (1−α)V_2`

这是**形变动画**（morphing）的基础。

**但讲义立刻给了一个警告**：

> *"Note that basic linear interpolation may not be semantically correct."*

**例子**：把一个物体旋转 180° 再取中间帧。逐顶点线性插值会让物体**塌缩成一点**（所有顶点都往中心移动），而不是"转 90°"。

**正解**：对**变换**插值（用四元数或对偶四元数），而不是对**顶点**插值。

#### P21　Topological Mesh Information

*Applications: Constant time access to neighbors（e.g. surface normal calculation, subdivision）· Editing the geometry（e.g. adding/removing vertices, faces, edges）*

![P21 · 为什么需要拓扑信息](images/p021.png)

**两个需求**：

| 需求 | 例子 |
|---|---|
| **常数时间访问邻居** | 算法线（要遍历一圈邻面）、细分（要取一圈邻点） |
| **编辑几何** | 加/删顶点、面、边（就是 P31 的局部操作） |

**如果只有索引三角形**：找一个顶点的所有邻面要**扫描整个三角形数组**（`O(n)`）。**几百万三角形时不可接受**。

**所以需要专门的数据结构** —— 就是半边缘。

#### P22–P23　Topological Validity: Manifold

*Definition: a 2D manifold is a surface that when cut with a small sphere always yields a disk.*

![P22 · 流形的定义](images/p022.png)

**流形的定义（几何版）**：用任意小球去切表面，切出来的**必须是一块圆盘**。

**推论（组合版）**，讲义列了五条：

| 性质 | 含义 |
|---|---|
| 一条边**恰好**连接两个面 | 不能有"三个面共用一条边" |
| 一条边恰好连接两个顶点 | 不能有"自环" |
| 一个面是一圈边和顶点 | 面要闭合 |
| 一个顶点是一圈边和面 | 顶点的邻域是一圈（不能是两个锥） |
| **Euler 公式** `#f − #e + #v = 2` | 对拓扑等价于球面的封闭网格 |

![流形与非流形](diagrams/d04-manifold.png)

*左：正常流形（每条边 2 个面）。中：一条边被 3 个面共用 —— 切不出圆盘。右：一个顶点处捏出两个锥 —— 切出来是两块圆盘，也不是流形。*

#### P24　Topological Validity: Orientation Consistency

*Non-orientable · Both facing front · Inconsistent orientations*

![P24 · 朝向一致性](images/p024.png)

**朝向一致性**：相邻两个面必须"同向"（共享边在两个面里的方向相反）。

图上是 `A B C D` 四个顶点，两种三角形拆分方式，其中一种的**朝向不一致**（一个面朝前、一个面朝后）。

**为什么重要**：法线方向、背面剔除（backface culling）、光照全依赖朝向。**朝向不一致的网格，渲染出来会有"黑块"**。

## 4. Euler 公式

#### P22 附：Euler's Polyhedron Formula

![Euler 公式](diagrams/d05-euler.png)

$$
\#f-\#e+\#v=2
$$

**🔧 手算 1：在立方体上验算**

| 量 | 值 |
|---|---|
| 面 `#f` | 6 |
| 边 `#e` | 12 |
| 顶点 `#v` | 8 |

$$
6-12+8=2\ \checkmark
$$

**推广形式**（图上右下角）：

$$
V-E+F=2-2g
$$

其中 `g` 是**亏格**（genus，洞的个数）：

| 形状 | `g` | `V−E+F` |
|---|---|---|
| 球面 | 0 | **2** |
| 环面（甜甜圈） | 1 | **0** |
| 双环面 | 2 | **−2** |

**🔧 手算 2：验算一个环面网格**

取一个 `4×4` 的环形网格（每圈 4 段，共 4 圈）：

| 量 | 计算 | 值 |
|---|---|---|
| 顶点 `V` | `4 × 4` | 16 |
| 面 `F` | `4 × 4` | 16 |
| 边 `E` | 每条边被 2 个面共用：`4F/2` | 32 |

$$
V-E+F=16-32+16=0\ \checkmark
$$

**正好是 `2−2×1 = 0`** ✓

> **📌 这个公式的实际用途：检查网格是否损坏**
>
> 加载一个扫描得到的网格，算一下 `V−E+F`：
> - 如果等于 2（或 `2−2g`）→ 拓扑正常
> - 如果**不等于** → 网格有洞、有重复面、或非流形
>
> **这是加载器里最常见的一行自检代码。**

## 5. 半边结构

#### P25–P27　Triangle-Neighbor Data Structure

![P26 · 三角形-邻居结构](images/p026.png)

```c
struct Tri {
  Vert *v[3];    // 三个顶点
  Tri  *t[3];    // 三条边对面的三角形（邻居）
};
struct Vert {
  Point pt;
  Tri   *t[];    // 所有相邻的三角形
};
```

**思路很直接**：每个三角形记三个顶点 + 三个邻居。

**P27 的遍历代码**展示了怎么"绕顶点转一圈"：

```c
Tri *tccwvt(Vert *v, Tri *t)   // next triangle CCW around vertex v
{
  if (v == t->v[0]) return t->t[0];
  if (v == t->v[1]) return t->t[1];
  if (v == t->v[2]) return t->t[2];
}
```

**问题**：`Vert` 里的 `Tri *t[]` 是**变长数组** —— 每个顶点的度数不同，不好存。而且每次查询要判断"`v` 是第几个顶点"。

#### P28　Half-Edge Data Structure

*Key idea: two half-edges act as "glue" between mesh elements*

![P28 · 半边结构](images/p028.png)

**核心思路**：**把每条边拆成两条有向的"半边"**，每条半边归属一个面。

```c
struct Halfedge {
  Halfedge *twin;    // 反向的那条半边
  Halfedge *next;    // 同一面内的下一条半边
  Vertex   *vertex;  // 指向的顶点
  Edge     *edge;    // 所属的边
  Face     *face;    // 所属的面
};
```

**每个顶点/边/面只存一个半边指针**（图上标 ★ 的 "one-halfedge"），其余靠遍历得到。

![半边结构：两条半边互为 twin](diagrams/d06-halfedge.png)

*两个相邻三角形共享一条边，这条边在左边三角形里是 `h`（一个方向），在右边是 `twin(h)`（反方向）。**两条半边就像"胶水"把两个面粘起来**。*

**为什么这个设计好**：

| 问题 | 索引三角形 | 半边 |
|---|---|---|
| 找 `v` 的一个邻面 | `O(n)` 扫描 | **`O(1)`**（`v->halfedge->face`） |
| 绕 `v` 转一圈 | 难 | **`O(deg(v))`** |
| 存一个顶点的邻面列表 | 变长数组 | **不需要**（遍历得到） |
| 内存 | 小 | 大（每半边 5 个指针） |

**"用时间换空间"的经典权衡**：半边多存了指针，但省掉了变长数组、也让所有邻域查询变成常数时间。

#### P29–P30　Half-Edge Facilitates Mesh Traversal

![P29 · 遍历例 1：绕面](images/p029.png)

![P30 · 遍历例 2：绕点](images/p030.png)

**两条遍历规则，各只要一行**：

```c
// 例 1：绕一个面（所有边）
Halfedge *h = f->halfedge;
do { process(h->vertex); h = h->next; } while (h != f->halfedge);

// 例 2：绕一个顶点（所有邻边）
Halfedge *h = v->halfedge;
do { process(h->edge); h = h->twin->next; } while (h != v->halfedge);
```

![两条遍历规则](diagrams/d07-halfedge-traversal.png)

*绕面用 `next`，绕点用 `twin->next`。**组合这两条，就得到了"一圈邻域"的常数时间访问** —— 这正是第 6 讲法线平均、第 10 讲细分所需要的操作。*

**P30 那张立方体图**把"绕顶点的一圈"高亮成红色环 —— 六条边围绕一个顶点。

## 6. 局部操作

#### P31–P36　Local Mesh Operations

*Basic operations for linked list: insert, delete · Basic ops for half-edge mesh: flip, split, collapse edges*

![P32 · 三种局部操作](images/p032.png)

![P33 · 翻边](images/p033.png)

**三种基本操作，讲义逐一给出**：

| 操作 | 做什么 | 元素数量变化 | 页 |
|---|---|---|---|
| **flip（翻边）** | 两个三角形共享的边换成另一条对角线 | **不变** | P33 |
| **split（加点）** | 在边上插一个顶点，把边一分为二 | **面 +1** | P34 |
| **collapse（收边）** | 把一条边缩成一个点（两个顶点合并） | **面 −1** | P35 |

**P33 的原文**：

> *Triangles `(a,b,c)`, `(b,d,c)` become `(a,d,c)`, `(a,b,d)`.*
> *Long list of pointer reassignments. However, no elements created/destroyed.*

**"Long list of pointer reassignments"（一长串指针重排）** 是这节最诚实的描述 —— **数学上很简单，实现上很啰嗦**，而且是 bug 高发区。

**P32 末尾的警告**：

> *(Care needed to preserve mesh manifold property)*

**每次操作后都必须检查网格是否还是流形**。比如 collapse 一条边时，如果两个顶点的邻域有"额外的公共邻居"，合并后会产生非流形结构。

#### P36　Composite Operations

![P36 · 复合操作](images/p036.png)

**复合操作**：把基本操作组合成更复杂的编辑。

图上展示的是 `cut`（切分）：把一个大三角形沿一条线切开，需要先 `split` 两次、再重新连接。

## 7. 细分曲面

#### P37–P38　Global Mesh Operations

![P38 · 三类全局操作](images/p038.png)

讲义重申三类全局任务（P38 配了一头牛的 LOD 序列图：从粗糙控制网到精细网格）：

| 操作 | 方向 | 算法 |
|---|---|---|
| **Mesh subdivision** | 变密 | Loop / Catmull-Clark |
| **Mesh simplification** | 变稀 | QEM |
| **Mesh regularization** | 变匀 | 等向重网格 |

#### P39–P41　Subdivision Surfaces

*Start with coarse polygon mesh ("control cage") · Subdivide each element · Update vertices via local averaging · Many possible rules: Catmull-Clark (quads), Loop (triangles) · Common issues: interpolating or approximating? continuity at vertices?*

![P40 · 细分曲面](images/p040.png)

**这是本节的核心思想**，图上有一个"控制笼"（control cage）被逐级细分成光滑表面的序列。

**基本流程（三步）**：

| 步骤 | 做什么 |
|---|---|
| ① | 从一个**粗糙的多边形网格**（控制笼）开始 |
| ② | 把每个元素**细分**（加点） |
| ③ | 用**局部平均**更新顶点位置 |

**两个"common issues"值得注意**：

> - **interpolating or approximating?**（插值还是逼近？）
> - **continuity at vertices?**（顶点处的连续性？）

**这两个问题就是整个细分曲面领域的核心**：
- Loop 和 Catmull-Clark 都是**逼近**（曲线不过控制点）
- 连续性在**正则区域**很好（C2），但在**异常点**附近会降到 C1

#### P41　Core Idea: Let Subdivision Define The Surface

*In Bezier curves, we saw: Evaluation by subdivision (de Casteljau algorithm) · Or evaluation by algebra (Bernstein polynomials) · Insight that leads to subdivision surfaces: Free ourselves from the algebraic evaluation · Let subdivision fully define the surface*

![P41 · 核心思想](images/p041.png)

**这一页把 L10 和 L11 接上了**：

> 在 Bézier 曲线里我们看到两种求值方式：**用细分求值**（de Casteljau）或**用代数求值**（Bernstein 多项式）。
>
> **启示**：干脆**抛弃代数**，让"细分规则"本身来定义曲面。

**这个思想转变很深刻**：

| 视角 | 曲面是什么 |
|---|---|
| **传统（Bézier/NURBS）** | 一个解析式，细分只是求值手段 |
| **细分曲面** | **一条无穷细分过程的极限**，没有解析式 |

**好处**：可以处理**任意拓扑**的网格（Bézier 面片只适合规则四边形网格）。

**代价**：没有解析式，所以求值只能靠细分（或近似），连续性的证明变得很难。

> **📌 这句话是全讲的转折点**
>
> 前半讲（数据结构、局部操作）都是"怎么摆弄三角形"。从这里开始，**三角形不再只是三角形，而是一个无穷过程的第 0 层**。
>
> 这个视角也解释了为什么细分能"自动"光滑：**极限曲面本身是光滑的，网格只是它的近似**。

## 8. Loop 细分

#### P42–P44　Loop Subdivision

*Common subdivision rule for triangle meshes · "C2" smoothness away from irregular vertices · Approximating, not interpolating · Generalization of Box Splines*

![P42 · Loop 细分](images/p042.png)

![P44 · 逼近而非插值](images/p044.png)

**Loop 细分**（Charles Loop, 1987）是**三角形网格**的标准细分规则。

三条性质：

| 性质 | 说明 |
|---|---|
| **C2 光滑（在正则区域）** | 远离异常点处是 C2 |
| **逼近，不插值** | 新曲面**不经过**原来的顶点（除非特殊处理） |
| **Box 样条的推广** | 图上小字：*"Basis functions are projections of hypercubes!"* |

**P44 的三张图**是同一个二十面体被细分 0/1/2 次 —— 可以看到它逐渐变成球。

#### P45–P47　Loop Subdivision Algorithm

*Split each triangle into four · Assign new vertex positions according to weights*

![P45 · 算法两步](images/p045.png)

![P46 · 度 6 的例子](images/p046.png)

**算法只有两步**：

| 步骤 | 做什么 |
|---|---|
| ① | 把每个三角形**分成四个**（每条边取中点） |
| ② | 按权重**重新分配**新顶点和老顶点的位置 |

**注意第 ② 步才是"Loop"的部分** —— 第 ① 步只是拓扑，任何细分都这么做。

#### 新顶点的权重（边中点）

![Loop 的两套权重](diagrams/d09-loop-weights.png)

*左边：新边点 = 边两端各 3/8 + 两侧对顶点各 1/8。右边：老顶点 = 自己占 (1−n·u)，每个邻居占 u。*

$$
\text{新边点}=\frac{3}{8}(v_1+v_2)+\frac{1}{8}(v_3+v_4)
$$

其中 `v_1, v_2` 是边的两个端点，`v_3, v_4` 是**两侧三角形的对顶点**。

**四个权重之和**：`3/8 + 3/8 + 1/8 + 1/8 = 1` ✓（仿射组合，不会插飞）

#### 老顶点的权重

$$
\text{老顶点}=(1-n\cdot u)\,v + u\sum_{i=1}^{n}v_i
$$

其中：

$$
u=\begin{cases}\dfrac{3}{16} & n=3\\[6pt]\dfrac{3}{8n} & n>3\end{cases}
$$

`n` 是顶点的**度数**（相邻顶点个数）。

**🔧 手算 3：算一个新边点**

取一条边的两个端点 `v₁=(0,0)`、`v₂=(2,0)`，两侧对顶点 `v₃=(1,1)`、`v₄=(1,−1)`。

$$
\begin{aligned}
\text{新点}&=\frac{3}{8}(0,0)+\frac{3}{8}(2,0)+\frac{1}{8}(1,1)+\frac{1}{8}(1,-1)\\
&=(0,0)+(0.75,0)+(0.125,0.125)+(0.125,-0.125)\\
&=(1.0,\ 0)
\end{aligned}
$$

**结果 `(1,0)` 正是边的中点** —— 因为这个例子的 `v₃, v₄` 关于 `x` 轴对称，它们的贡献互相抵消。

**如果对顶点不对称**（比如 `v₃=(1,2)`、`v₄=(1,0)`）：

$$
\text{新点}=(0.75+0.125+0.125,\ 0+0.25+0)=(1.0,\ 0.25)
$$

**新点被"拉"向对顶点密集的那一侧** —— 这就是细分的**平滑作用**：它把尖锐的起伏平均掉。

**🔧 手算 4：算一个度 6 的老顶点**

取一个度数为 6 的顶点，`v=(0,0)`，六个邻居在单位圆上均匀分布（正六边形）。

**权重**：`n=6 > 3`，所以 `u = 3/(8×6) = 3/48 = 1/16`。

**自己**占 `1 − 6×(1/16) = 1 − 6/16 = 10/16`。

**邻居的贡献**：六个邻居**关于原点对称**，所以求和为 `(0,0)`。

$$
\text{新位置}=\frac{10}{16}(0,0)+\frac{1}{16}\sum \vec{v_i}=(0,0)
$$

**位置不变** ✓ —— 这是正确的：**正六边形网格是 Loop 细分的"正则情形"，顶点不该移动**（否则平面会被细分得起伏）。

**🔧 手算 5：算一个度 3 的老顶点**

`n=3`，所以 `u = 3/16`。自己占 `1 − 3×(3/16) = 1 − 9/16 = 7/16`。

设邻居为 `(1,0)`、`(−0.5, 0.866)`、`(−0.5, −0.866)`（正三角形，和为 `(0,0)`）：

$$
\text{新位置}=\frac{7}{16}v+\frac{3}{16}(0,0)=\frac{7}{16}v
$$

**顶点向原点收缩了 `7/16`！**

> **⚠️ 为什么 `n=3` 要单独处理**
>
> 如果用通式 `u = 3/(8n) = 3/24 = 1/8`，那么自己占 `1 − 3/8 = 5/8`，收缩得更厉害。
>
> `n=3` 用 `3/16` 是**为了让边界和角点的行为正确**（这个特殊值来自 Loop 原始论文的推导）。**度 3 的顶点在封闭网格里对应"最尖的角"**，规则必须区别对待。

#### P48　Semi-Regular Meshes
![P49 · 异常点数量的推导](images/p049.png)

*讲义用几页推导"为什么球面网格必须有异常点"：假设全是度 6，则 `V−E+F = 0`，与球面的 `2` 矛盾。*

*Most of the mesh has vertices with degree 6 · But if the mesh is topologically equivalent to a sphere, then not all the vertices can have degree 6 · Must have a few extraordinary points (degree not equal to 6)*

![P48 · 半正则网格](images/p048.png)

**这段推理很重要，是理解细分曲面的关键**：

| 步骤 | 结论 |
|---|---|
| ① | 三角形网格里"正则"的度数是 **6**（六个正三角形围一点） |
| ② | 但**拓扑上等价于球面的网格不可能全是度 6** |
| ③ | 所以**必然存在少量"异常点"**（度 ≠ 6） |

**第 ② 步的证明**（讲义 P49–P54，很好的一道题）：

**🔧 手算 6：证明球面网格必有异常点**

设一个三角形网格全是度 6 的顶点，`V` 个顶点、`E` 条边、`F` 个面。

**由"每个面 3 条边、每条边 2 个面"**：

$$
3F=2E \quad\Longrightarrow\quad F=\frac{2E}{3}
$$

**由"每个顶点度 6、每条边 2 个端点"**：

$$
6V=2E \quad\Longrightarrow\quad E=3V,\quad F=2V
$$

**代入 Euler 公式**：

$$
V-E+F=V-3V+2V=0
$$

**得到 `0`，但球面应该是 `2`** —— **矛盾！**

**所以"全是度 6"的三角形网格的 Euler 示性数必然是 0**（对应环面，`g=1`），不可能是球面。

**结论**：球面网格**必有异常点**，而且数量由 `Σ(6−deg(v)) = 12` 约束（这是 Euler 公式的另一种写法）。

![异常点被稀释](diagrams/d13-extraordinary.png)

*细分不会"消灭"异常点，只会把它们**稀释**到越来越大的网格里 —— 所以极限曲面上异常点仍然存在（只是周围越来越光滑）。*

#### P55　Loop via Edge Operations

![P55 · 用边操作实现 Loop](images/p055.png)

**实现路线**：**先 split 每条边，再 flip 中间那三条边**。

![split 再 flip](diagrams/d10-loop-split-flip.png)

*原始三角形 → 每条边 split（得到 4 个小三角形 + 中间一个）→ 把中间那个三角形的三条边 flip → 得到标准的 Loop 细分拓扑。*

**为什么这样绕一圈**：因为半边结构里 `split` 和 `flip` 是**已经实现好的、经过测试的**基本操作。**复用它们比自己写一套"一次分成四份"的代码更不容易出 bug。**

#### P56–P57　Loop 的连续性

![P56 · 连续性说明](images/p056.png)

![P57 · 细分结果](images/p057.png)

**连续性**（讲义 P56）：

- **正则区域（全度 6）**：**C2** 连续
- **异常点附近**：降到 **C1**

**为什么异常点处会掉到 C1**：因为异常点附近的**基函数结构不同**（不是规则的 Box 样条张量积）。这是所有细分方案的共同特征 —— **异常点是"连续性的瓶颈"**。

## 9. B 样条：为细分做理论准备

#### P58–P59　B-Splines

*Goal: local support · Give up interpolation · Convex hull · C2*

![P59 · B 样条](images/p059.png)

讲义用近三十页讲 B 样条（P58–P85）。**为什么在这个位置讲**：因为 **Loop 和 Catmull-Clark 的细分规则都是从 B 样条推导出来的**。

**四条设计目标**（和 Bézier 对照着看）：

| 目标 | Bézier | B 样条 |
|---|---|---|
| **局部支撑（local support）** | ✗ 单片全是全局的 | ✓ 每个控制点只影响 4 段 |
| **放弃插值** | 过首末点 | **完全不经过**控制点 |
| **凸包性质** | ✓ | ✓ |
| **C2 连续** | ✗ 拼接要手工 | ✓ **自动** |

![B 样条的"小山包"](diagrams/d11-bspline-humps.png)

*每个控制点对应一个"小山包"基函数，只在局部非零。曲线是这些山包的加权和 —— **重叠部分自动保证 C2 连续**。*

> **📌 "放弃插值"是整个交易的核心**
>
> Bézier 想"经过控制点"，所以基函数必须在端点取 1 —— 这个约束逼着它全局化（Bernstein 基在整个区间非零）。
>
> B 样条**放弃"经过"**，只要求"在控制点附近"，于是基函数可以做成**局部的**（只覆盖 4 段）。**局部性带来两个好处：局部编辑 + 自动 C2。**
>
> **这就是"用一点直觉性换取数学好性质"的经典取舍。**

#### P60–P67　B 样条的约束与例子

![P61 · 约束条件](images/p061.png)

![P66 · 带端节点的例子](images/p066.png)

讲义用**16 个约束条件**来推导 B 样条的基函数（P60–P62），然后给出带"端节点"（end knots）的例子（P63–P67）。

**"节点"（knot）是什么**：B 样条把参数轴分成若干段，每段之间用"节点"分隔。**因为节点可以任意分布，所以 B 样条是"非均匀"的**。

#### P68–P70　叠加与重复节点

![P69 · 重叠的山包](images/p069.png)

![P70 · 重复节点降低连续性](images/p070.png)

**P69 展示"重叠"**：多个山包（hump）叠在一起，形成一条光滑曲线。

**P70 讲"重复节点"**：如果把某个节点重复一次，**连续性就降低一阶**：

| 节点重数 | 连续性 |
|---|---|
| 1（简单节点） | C2 |
| 2 | C1 |
| 3 | C0 |
| 4 | C−1（断开） |

**这个性质非常实用**：想在 B 样条里做一条"锐利的边"，只要把节点重复几次即可 —— **不需要换算法**。

#### P71–P74　Cox-de Boor 与 NURBS

![P72 · Cox-de Boor 递推](images/p072.png)

**Cox-de Boor 递推**：B 样条基函数的递归定义（结构类似 de Casteljau，也是"降阶递归"）。

#### P75　NURBS

![P75 · NURBS](images/p075.png)

**NURBS**（Non-Uniform Rational B-Spline）：给每个控制点加一个**权重** `w_i`，变成有理形式：

$$
x(u)=\frac{\sum_i N_i(u)\,w_i\,b_i}{\sum_i N_i(u)\,w_i}
$$

图上的小字：*"thumb weights"* —— 讲义用"大拇指按压力度"来类比权重的含义。

**为什么需要有理形式**（呼应第 10 讲）：**只有有理形式才能精确表示圆锥曲线，并且对透视变换保持不变**。所以 CAD 系统统一用 NURBS。

**"Non-Uniform"** 指节点可以不等距；**"Rational"** 指带权重；两者合起来让 NURBS 能表示几乎所有工程曲线。

## 10. Catmull-Clark 细分

#### P76–P79　Catmull-Clark Subdivision

![P76 · Catmull-Clark](images/p076.png)

![P77 · 规则四边形网格的细分](images/p077.png)

**Catmull-Clark**（1978）是**四边形网格**（以及任意多边形网格）的标准细分规则。

**它是双三次 B 样条细分规则在任意拓扑网格上的推广** —— 所以正则区域是 C2。

#### P80　四边形网格的三类点

![P80 · 三类新点](images/p080.png)

针对**全四边形网格**，一步细分产生三类点：

| 类型 | 位置 | 规则 |
|---|---|---|
| **Face point** | 面的中心 | 该面四个顶点的平均 |
| **Edge point** | 边的中点附近 | 边两端 + 两侧面心的平均 |
| **Vertex point**（更新老顶点） | 老顶点新位置 | 邻域信息的加权平均 |

#### P86–P95　一般网格的处理
![P90 · 细分一次之后](images/p090.png)

*左边是细分前（有非四边形面 + 异常点），右边是细分后。**关键观察：非四边形面消失了**（都变成了四边形），而异常点还在，但周围被四边形包围。*

![P86 · 一般网格](images/p086.png)

![P88 · 非四边形面和异常点](images/p088.png)

![P91 · 细分后的问题](images/p091.png)

**真正的挑战是"一般网格"** —— 里面有**非四边形面**（图上标红三角）和**异常点**（度 ≠ 4，标紫圆点）。

**P91 那三个问题问得很好**：

> - 一次细分后还有多少异常点？
> - 它们的度数是多少？
> - 还有多少个非四边形面？

**答案是**：
- **非四边形面 → 0 个**（每个 n 边形被拆成 n 个四边形）
- **异常点数量不变**（不会新增）
- 但**度数会变**：原来的 n 度顶点仍 n 度；**新产生的边点度数都是 4**

**所以一次细分之后，所有"非四边形"都消失了，只剩少量异常点** —— 这就是 Catmull-Clark 的关键性质。

![Catmull-Clark 的四边形化](diagrams/d12-cc-rules.png)

*① face point = 面重心；② edge point = 边两端 + 两侧面心；③ vertex point = 邻域平均。然后把每个 n 边形拆成 n 个四边形 `(v, edge, face, edge)`。*

#### P96–P100　Catmull-Clark 顶点更新规则
![P97 · 一般网格的规则](images/p097.png)

*一般网格的规则比规则网格复杂：**要同时考虑相邻面心、相邻边中点、以及顶点度数**。讲义用几页把这个公式逐步搭出来。*

![P96 · 一般网格的顶点规则](images/p096.png)

一般网格的顶点更新规则（P96–P100）：

$$
v'=\frac{F+2R+\frac{n-3}{n}v}{n}
$$

其中：
- `F` = 相邻**面心**的平均
- `R` = 相邻**边中点**的平均
- `n` = 顶点度数

**🔧 手算 7：算一个 Catmull-Clark 新顶点**

取一个度 `n=4` 的顶点 `v=(0,0)`，周围四个面都是正方形，相邻边中点：

$$
R_1=(1,0),\ R_2=(0,1),\ R_3=(-1,0),\ R_4=(0,-1)
$$

面心（四个象限的中心）：

$$
F_1=(0.5,0.5),\ F_2=(-0.5,0.5),\ F_3=(-0.5,-0.5),\ F_4=(0.5,-0.5)
$$

**平均**：

$$
\bar{F}=(0,0),\qquad \bar{R}=(0,0)
$$

**代入公式**（`n=4`，`(n−3)/n = 1/4`）：

$$
v'=\frac{(0,0)+2(0,0)+\frac{1}{4}(0,0)}{4}=(0,0)
$$

**位置不变** ✓ —— 规则网格上的顶点不动，这正是"细分不该改变平面"的要求。

**换成不对称的例子**：设 `R̄=(0.2,0)`、`F̄=(0.4,0)`、`v=(0,0)`：

$$
v'=\frac{(0.4,0)+2(0.2,0)+0.25\times(0,0)}{4}=\frac{(0.8,0)}{4}=(0.2,\ 0)
$$

**新位置被拉向邻域的中心** —— 这就是细分的平滑作用。

#### P101–P109　连续性与锐边
![P104 · 锐边的规则](images/p104.png)

*锐边的做法：**细分时这条边不参与平均**，所以它保持原来的位置和方向。图上把锐边涂成蓝色，可以看到细分后它仍然是直线。*

![P101 · 连续性](images/p101.png)

![P109 · Geri's Game 中的锐边](images/p109.png)

**连续性**：

- **正则区域（全度 4）**：**C2**
- **异常点附近**：**C1**

**P102–P108 讲"锐边"（sharp creases）** —— 这是 Catmull-Clark 最实用的扩展：

| 做法 | 效果 |
|---|---|
| 把某条边**标记为 crease** | 细分时这条边**不参与平均**，保持锐利 |
| 部分锐化（partial sharpness） | 用"半锐"的权重，在锐与圆之间插值 |
| 顶点角点（corner） | 完全固定不动 |

**P109 是《Geri's Game》的剧照** —— 皮克斯 1997 年的短片，**第一个大量使用细分曲面做角色**的作品。老头的脸部皱纹、衣服褶皱都靠 crease 控制。

> **📌 为什么"锐边"是必需的**
>
> 纯细分会把**所有**棱角都磨圆 —— 但现实物体有大量需要保持锐利的地方（桌沿、门框、指甲盖）。
>
> 所以工业界的细分曲面系统**必须**提供 crease 机制。这也是"细分"从数学玩具变成生产工具的关键一步。

## 11. 网格简化

#### P110–P112　Mesh Simplification

*Goal: reduce number of mesh elements while maintaining overall shape*

![P111 · 简化](images/p111.png)

![P112 · 局部操作回顾](images/p112.png)

**目标**：减少元素数量，但**保持整体形状**。

**P112 把三种局部操作和三种全局任务对应起来**：

| 局部操作 | 对应的全局任务 |
|---|---|
| **Edge split** | 局部**上采样** |
| **Edge collapse** | 局部**下采样** |
| **Edge flip** | 局部**规整** |

**小字总结**：*"Still need to intelligently decide which edges to modify!"* —— **关键不是"能不能改"，而是"改哪一条"。**

#### P113–P118　简化的效果

![P114 · 30000 → 3000](images/p114.png)

![P116 · 30000 → 30](images/p116.png)

![P118 · 四级 LOD](images/p118.png)

**一个骷髅从 30,000 个三角形逐级简化到 3,000 → 300 → 30**。

**P118 的加粗问题**：***"How to compute?"***（怎么算？）—— 引出下面的误差度量。

**观察这几张图**：
- 3,000 时几乎看不出差别
- 300 时轮廓开始有棱角
- **30 时已经完全认不出** —— 这给出了"简化到什么程度"的直观边界

#### P119–P120　Estimate: Error Introduced by Collapsing An Edge?

![P119 · 收缩一条边的误差](images/p119.png)

![P120 · 二次误差](images/p120.png)

**问题**：收缩一条边会引入多少几何误差？

**朴素的答案**：算"新顶点到原来那条边的距离"。**但这是错的** —— 因为它没有考虑**周围的形状**。

**正确思路（QEM）**：一个顶点"偏离原来的表面多远"——**用"到周围所有平面的距离平方和"来度量**。

#### P121–P125　Quadric Error Metric

*Garland & Heckbert, 1997*

![P121 · QEM](images/p121.png)

![P123 · 推导](images/p123.png)

![P124 · 顶点处的 Q](images/p124.png)

**这是网格简化里最著名的算法**（Garland & Heckbert, SIGGRAPH '97）。

![二次误差：到平面的距离](diagrams/d14-quadric.png)

*每个顶点记一个 4×4 矩阵 `Q`，它编码了"这个点周围有哪些平面"。候选新位置 `v` 的代价就是 `ṽᵀQṽ`（`ṽ = [v,1]`）。*

**推导（三步）**：

**① 一个平面的二次型**

平面写成 `nᵀv + d = 0`（`n` 是单位法向）。点到平面的距离平方：

$$
D(v)=\big(n^Tv+d\big)^2=v^T(nn^T)v+2d\,n^Tv+d^2
$$

**② 写成齐次形式**

令 `ṽ = [v_x, v_y, v_z, 1]ᵀ`，则：

$$
D(v)=\tilde{v}^TQ\,\tilde{v},
\qquad
Q=\begin{bmatrix}nn^T & dn\\ d n^T & d^2\end{bmatrix}
$$

**③ 一个顶点的 Q 是它周围所有面的 Q 之和**

$$
Q_v=\sum_{\text{faces }f}Q_f
$$

**🔧 手算 8：算一个点的二次误差**

设一个平面 `z = 0`，法向 `n = (0,0,1)`、`d = 0`。取点 `v = (1, 2, 3)`。

**距离平方**应该是 `3² = 9`。用公式验证：

$$
Q=\begin{bmatrix}0&0&0&0\\0&0&0&0\\0&0&1&0\\0&0&0&0\end{bmatrix}
$$

$$
\tilde{v}^TQ\tilde{v}=v_z^2=3^2=9\ \checkmark
$$

**再把两个平面加起来**：加一个平面 `z = 2`（`n=(0,0,1)`、`d=−2`）。

`Q_2` 的 `d²` 项是 `4`，`dn` 项是 `−2·(0,0,1)`。

$$
D_{\text{total}}(v)=v_z^2+(v_z-2)^2=9+1=10
$$

**这就是"到一个点集的所有平面距离平方和"** —— 正是 QEM 的定义。

#### P126–P127　算法与结果

![P126 · QEM 算法](images/p126.png)

![P127 · 结果](images/p127.png)

![QEM 简化循环](diagrams/d15-qem.png)

*四步循环：给每条边算代价 → 放进优先队列 → 收掉最便宜的 → 更新受影响边的代价 → 重复。*

**算法细节**：

| 步骤 | 说明 |
|---|---|
| ① 给每条边算 collapse 代价 | 把 `Q₁ + Q₂` 相加，最小化 `ṽᵀ(Q₁+Q₂)ṽ` |
| ② 优先队列 | 按代价排序 |
| ③ 反复取最小 | 收掉，**只重算相邻边**的代价 |
| ④ 直到目标面数 | 复杂度 `O(n log n)` |

**新位置的选取**：最优解是解线性方程组 `∂D/∂v = 0`（`Q` 左上 3×3 部分可逆时）。不可逆就退化到"边中点"或"两个端点里代价小的那个"。

> **⚠️ 边收缩的两个陷阱**
>
> **① 拓扑破坏（link condition）**
> 收缩一条边时，如果两个顶点有"额外的公共邻居"，合并后会产生**非流形结构**（比如两个面变成同一个面）。所以要检查 **link condition**。
>
> **② 翻面（normal flip）**
> 收缩后相邻三角形的**法向可能反过来**（因为顶点移动太多）。也必须检查。
>
> 这两个检查让 QEM 的实际实现比论文描述要长得多。

## 12. 网格规整

#### P128–P132　Mesh Regularization
![P130 · 规整的目标](images/p130.png)

*规整不改变形状，只改变"采样点在表面上的分布"。**左图是原始不均匀的网格，右图是规整后** —— 轮廓完全一样，但三角形质量差很多。*

![P129 · 规整](images/p129.png)

![P131 · 三角形形状](images/p131.png)

**目标**：**不改变形状**，只改善**三角形的质量**。

**两个质量指标**：

| 指标 | 目标 |
|---|---|
| **三角形形状** | 接近**正三角形**（不要细长的"针"） |
| **顶点度数** | 接近 **6**（三角形网格的正则度数） |

**为什么要规整**：

- **细长三角形**在光栅化时覆盖判定不准、插值误差大
- **度数不均**会让细分、简化、形变都出问题
- **有限元分析**（FEA）对网格质量极其敏感

#### P133–P137　Delaunay 与度数
![P134 · 度数分布](images/p134.png)

*顶点度数的可视化：颜色表示度数偏离 6 的程度。**规整的目标就是让这张图尽量均匀**。*

![P133 · Delaunay 三角化](images/p133.png)

![P135 · 顶点度数](images/p135.png)

![P137 · 把顶点移到重心](images/p137.png)

**Delaunay 三角化**：最大化最小角（避免"针"形三角形）。

**但讲义提醒**（P137）：*"Delaunay doesn't mean equilateral triangles"* —— **Delaunay 只保证"没有过小的角"，不保证"接近正三角形"**。

**更好的做法**：**把顶点移到邻域的重心**（centroid），同时**约束在切平面上**（否则会改变形状）。

![把顶点移到切平面上的重心](diagrams/d16-remeshing.png)

*四步循环：split 长边、collapse 短边、flip 改善度数、把顶点切向平移到重心。*

#### P138　Isotropic Remeshing Algorithm

*Repeat four steps: Split edges over 4/3rds mean edge length · Collapse edges less than 4/5ths mean edge length · Flip edges to improve vertex degree · Center vertices tangentially*

![P138 · 等向重网格算法](images/p138.png)

**四步循环**（Botsch & Kobbelt, 2004）：

| 步骤 | 阈值 | 用哪个局部操作 |
|---|---|---|
| ① **split** | 边 > `4/3 × 平均边长` | split |
| ② **collapse** | 边 < `4/5 × 平均边长` | collapse |
| ③ **flip** | 改善顶点度数（趋向 6） | flip |
| ④ **切向平移到重心** | — | 移动顶点（不改变拓扑） |

**🔧 手算 9：算一下阈值区间**

设平均边长 `L̄ = 1.0`：

| 判据 | 阈值 | 动作 |
|---|---|---|
| 边 > `4/3 × 1 = 1.333` | 太长 | split |
| 边 < `4/5 × 1 = 0.8` | 太短 | collapse |
| `0.8 ≤ 边 ≤ 1.333` | 合格 | 不动 |

**注意两个阈值不对称**：上界 `1.333`、下界 `0.8`，中间留了一个"缓冲区"。

**为什么要留缓冲区**：如果上界和下界相等（比如都是 1.0），那么 split 一次会让边变成 0.5（触发 collapse），collapse 又让边变回 1.0（触发 split）—— **无限抖动**。

**`4/3` 和 `4/5` 的比值是 `5/3 ≈ 1.67`**，足够宽，能保证收敛。

> **📌 这就是"用局部规则实现全局目标"的范例**
>
> 你没法直接说"我要每个三角形都是正三角" —— 那是个**全局优化**问题，很难解。
>
> 但你可以说"边太长就切、太短就合、度数不对就翻、位置偏了就挪" —— **四个纯局部规则，反复迭代，就收敛到接近最优的全局状态**。
>
> 这和 QEM（局部边收缩 → 全局简化）、细分（局部平均 → 全局光滑）是同一个套路：**局部规则 + 迭代 = 全局行为**。

## 13. 收尾

#### P139　Acknowledgments

![P139 · 致谢](images/p139.png)

课件由 **Ren Ng** 与 **James O'Brien** 开发，另有 Kayvon Fatahalian、David Forsyth、Pat Hanrahan、Angjoo Kanazawa、Steve Marschner、Mark Pauly 等贡献。

### 13.1 这一讲留下了什么

**带走的八句话：**

1. **网格 = 拓扑 + 几何**，两者独立；同拓扑才能插值，但线性插值不一定语义正确。
2. **索引三角形**（点表 + 索引）比纯三角形列表省内存，而且保证完整性。
3. **流形**要求每条边恰好 2 个面；**Euler 公式** `V−E+F = 2−2g` 可以检查拓扑是否损坏。
4. **半边结构**把每条边拆成两条有向半边，`twin` 当胶水；绕面用 `next`、绕点用 `twin->next`，都是常数时间。
5. **三种局部操作**：flip / split / collapse —— 一切全局操作的积木。
6. **细分曲面**放弃解析式，让"无穷细分过程的极限"定义曲面；Loop 处理三角形、Catmull-Clark 处理任意多边形。
7. **异常点是连续性的瓶颈**：正则区域 C2，异常点处降到 C1；而且球面网格**必然**有异常点。
8. **简化用 QEM**（到周围平面距离平方和），**规整用四步循环**；两者都是"局部规则 + 迭代 = 全局行为"。

**还差什么：**

| 这一讲没解决 | 谁来解决 |
|---|---|
| 网格怎么变成像素（光栅化） | L02 + L08 |
| 光线怎么和这些网格求交、怎么加速 | **L13 光线追踪** |
| 参数化 / UV 展开（网格 ↔ 纹理） | L06–07 讲过问题，解法属 CAD 方向 |
| 动画 / 蒙皮（骨骼与网格的关系） | 不在本课（角色动画方向） |
| 网格压缩、流式传输 | 工业界（Draco 等） |

> **📌 下次课的第一句话**
>
> 这一讲最后说"网格是三角形集合"。**渲染它们有两条路**：光栅化（L02，逐三角形投影到屏幕）和**光线追踪**（逐像素发射光线去问"打到哪个三角形"）。
>
> 光栅化的代价与三角形数量**线性相关**；而光线追踪如果逐三角形暴力测试，代价是 `像素数 × 三角形数` —— **完全不可行**。
>
> **所以 L13 的核心不是"怎么求交"，而是"怎么加速求交"**：包围盒层次（BVH）、空间划分、以及采样与降噪。

---

## 附录 A · 公式速查

| 对象 | 公式 | 备注 |
|---|---|---|
| **Euler 公式** | `V − E + F = 2 − 2g` | 球面 `g=0` → 2；环面 `g=1` → 0 |
| 三角网格关系 | `3F = 2E`，`6V = 2E`（全度 6 时） | 推出 `V−E+F = 0` |
| **Loop 新边点** | `⅜(v₁+v₂) + ⅛(v₃+v₄)` | `v₃,v₄` 是两侧对顶点 |
| **Loop 老顶点** | `(1−nu)v + u·Σvᵢ` | `u = 3/16`（n=3）或 `3/(8n)`（n>3） |
| **Loop 度数约束** | `Σ(6 − deg(v)) = 12` | 球面必有异常点 |
| **Catmull-Clark 顶点** | `v' = (F̄ + 2R̄ + (n−3)/n·v) / n` | `F̄` 面心均值，`R̄` 边中点均值 |
| **B 样条有理形式** | `x(u) = ΣNᵢwᵢbᵢ / ΣNᵢwᵢ` | NURBS；保透视、能表圆锥 |
| 节点重数与连续性 | 重数 `k` → `C^(2−k)` | 重 4 次就断开 |
| **QEM 代价** | `D(v) = ṽᵀQṽ`，`ṽ=[v,1]` | `Q` 4×4 对称，存 10 个数 |
| 平面二次型 | `Q = [[nnᵀ, dn],[dnᵀ, d²]]` | 点到平面距离平方 |
| 顶点 Q | `Q_v = Σ_f Q_f` | 合并时 `Q₁+Q₂` |
| **重网格阈值** | 长边 `> 4/3·L̄`，短边 `< 4/5·L̄` | 比值 5/3，避免抖动 |

## 附录 B · 139 页索引

| 页码 | 主题 | 为什么在这儿 |
|---|---|---|
| P1–P2 | 封面 | — |
| P3 | Mesh Examples | 引入 |
| P4 | 小网格（8 顶点 12 面） | 最小封闭网格 |
| P5 | **大卫像**（2818 万顶点） | 规模震撼 |
| P6 | Google Earth（万亿级） | 规模上限 |
| P7–P8 | 3D 扫描 / 3D 打印 | 为什么要做几何处理 |
| P9–P12 | **三类任务**：细分 / 简化 / 规整 | 全讲地图 |
| P13 | Mesh Representations | 分节 |
| P14–P15 | 三角形列表 / 索引三角形 | 两种基础存法 |
| P16 | 对比：冗余 vs 共享 | 取舍 |
| P17 | **拓扑 vs 几何** | 核心区分 |
| P18–P20 | 同拓扑可插值；语义警告 | 形变动画 |
| P21 | 为什么需要拓扑信息 | `O(1)` 邻域访问 |
| P22–P23 | **流形**的五条性质 | 有效性判据 |
| P24 | 朝向一致性 | 法线/剔除的基础 |
| P25 | Mesh Data Structures | 分节 |
| P26 | 三角形-邻居结构 | 第一版方案 |
| P27 | 绕顶点遍历的代码 | 变长数组问题 |
| P28 | **半边结构** | twin 当胶水 |
| P29–P30 | 两条遍历规则 | `next` / `twin->next` |
| P31 | Local Mesh Operations | 分节 |
| P32 | 三种操作总览 | 元素数量变化 |
| P33 | **flip** | 数量不变，指针重排 |
| P34 | **split** | 面 +1 |
| P35 | **collapse** | 面 −1 |
| P36 | 复合操作（cut） | 组合基本操作 |
| P37–P38 | Global Mesh Operations | 三类任务再现 |
| P39 | Subdivision Surfaces | 分节 |
| P40 | 控制笼 → 细分 | 插值 vs 逼近 |
| P41 | **核心思想：让细分定义曲面** | 抛弃解析式 |
| P42–P44 | Loop：C2 / 逼近 / Box 样条推广 | 三角形网格规则 |
| P45–P47 | **Loop 两步 + 权重** | 新边点 / 老顶点 |
| P48 | **半正则网格** | 球面必有异常点 |
| P49–P54 | 异常点必然存在的证明 | `V−E+F = 0` 矛盾 |
| P55 | Loop = split + flip | 复用基本操作 |
| P56–P57 | 连续性 C1/C2；结果 | 异常点是瓶颈 |
| P58–P59 | **B 样条的目标** | 局部支撑 + C2 |
| P60–P62 | 16 个约束条件 | 推导基函数 |
| P63–P67 | 带端节点的例子 | 非均匀 |
| P68–P70 | 重叠山包；**重复节点降连续** | 做锐边的原理 |
| P71–P74 | Cox-de Boor 递推 | 递归定义 |
| P75 | **NURBS** | 权重、保透视 |
| P76–P79 | **Catmull-Clark** 引入 | 四边形网格 |
| P80 | 三类新点（规则网格） | face/edge/vertex |
| P81–P85 | 规则细分结果；同基矩阵思路 | 与 Bézier 对照 |
| P86–P89 | 一般网格：非四边形面 + 异常点 | 真正的挑战 |
| P90–P95 | 细分一次后的三个问题 | 四边形化、异常点不增 |
| P96–P100 | **一般网格的顶点更新规则** | `(F+2R+(n−3)/n·v)/n` |
| P101 | 连续性 C1/C2 | — |
| P102–P108 | **锐边（crease）** | 保持棱角 |
| P109 | Geri's Game | 首个大量用细分的角色 |
| P110 | Mesh Simplification | 分节 |
| P111–P112 | 简化目标；三种局部操作对应 | 关键在"选哪条边" |
| P113–P118 | 骷髅 30000 → 30 | 简化的极限 |
| P119–P120 | 收缩误差怎么估 | 引出 QEM |
| P121–P125 | **QEM**（Garland & Heckbert '97） | 4×4 矩阵、10 个系数 |
| P126 | 算法流程 | 优先队列 + 局部更新 |
| P127 | 简化结果 | — |
| P128 | Mesh Regularization | 分节 |
| P129–P132 | 规整的目标 | 不改变形状 |
| P133–P134 | Delaunay 三角化 | 最大化最小角 |
| P135–P136 | 顶点度数；flip 改善 | 趋向 6 |
| P137 | Delaunay ≠ 正三角；居中 | 切向移动 |
| P138 | **等向重网格四步** | 4/3 与 4/5 |
| P139 | 致谢 | Ren Ng / James O'Brien 等 |

## 附录 C · 自测 26 题

1. 一个 5623 万三角形的网格，光存顶点坐标要多少内存？为什么这决定了必须做简化？
2. 三角形列表和索引三角形各有什么优缺点？"保证完整性"具体指什么？
3. 什么是拓扑？什么是几何？举一个"同拓扑不同几何"和"同几何不同拓扑"的例子。
4. 为什么同拓扑的网格才能做形变插值？为什么线性插值可能"语义不正确"？
5. 流形的定义（用小球切）是什么？列出它的五条组合性质。
6. 举出两种非流形结构，并说明它们为什么切不出圆盘。
7. 立方体的 `V−E+F` 是多少？环面呢？给出通式。
8. 怎么用 Euler 公式检查一个网格有没有坏？
9. 半边结构里存了哪五个指针？为什么每个元素只存一个半边就够？
10. 绕一个面遍历用哪个指针？绕一个顶点呢？
11. 半边相比"三角形-邻居"结构，主要解决了什么问题？
12. flip / split / collapse 各让元素数量怎么变？
13. 为什么每次局部操作后都要检查流形性？举一个 collapse 破坏拓扑的例子。
14. 细分曲面的"核心思想"是什么？为什么说它"放弃了代数求值"？
15. Loop 细分分两步，哪一步是"Loop"的部分？另一部分是什么？
16. 写出 Loop 的新边点公式，并验证四个权重和为 1。
17. 手算：两端点 `(0,0),(2,0)`、对顶点 `(1,2),(1,0)`，新边点在哪？
18. Loop 的老顶点公式里 `u` 为什么对 `n=3` 要特殊处理？
19. 证明"全度 6 的三角形网格的 `V−E+F` 必然是 0"。这说明了什么？
20. 为什么球面网格必然有异常点？异常点的数量受什么约束？
21. B 样条相比 Bézier 放弃了什么、换来了什么？"局部支撑"带来哪些好处？
22. 重复一个节点两次，连续性怎么变？这个性质有什么用？
23. Catmull-Clark 三类新点分别怎么算？为什么它能把任意多边形变成全四边形？
24. Catmull-Clark 的顶点更新公式里，`F`、`R`、`n` 各是什么？
25. QEM 的 `Q` 矩阵为什么只需存 10 个数？两个顶点合并时 `Q` 怎么处理？
26. 等向重网格的四个步骤和阈值是什么？为什么阈值要留缓冲区？

## 附录 D · 术语表

| English | 中文 | 一句话 |
|---|---|---|
| mesh | 网格 | 顶点 + 面 |
| indexed triangle | 索引三角形 | 点表 + 索引表 |
| topology | 拓扑 | 谁和谁相连 |
| geometry | 几何 | 点在哪 |
| manifold | 流形 | 每点邻域像平面 |
| non-manifold | 非流形 | 切不出圆盘 |
| orientation | 朝向 | 相邻面方向一致 |
| Euler's formula | Euler 公式 | `V−E+F = 2−2g` |
| genus | 亏格 | 洞的个数 |
| half-edge | 半边 | 有向的边，twin 配对 |
| twin | 对偶半边 | 反向的那条 |
| traversal | 遍历 | 沿指针走一圈 |
| edge flip | 翻边 | 换对角线 |
| edge split | 加点 | 边上插顶点 |
| edge collapse | 收边 | 边缩成点 |
| link condition | 连接条件 | 判 collapse 是否破坏拓扑 |
| subdivision surface | 细分曲面 | 无穷细分的极限 |
| control cage | 控制笼 | 粗糙的多边形网格 |
| Loop subdivision | Loop 细分 | 三角形网格规则 |
| Catmull-Clark | — | 任意多边形网格规则 |
| extraordinary vertex | 异常点 | 度不等于正则值 |
| regular vertex | 正则顶点 | 三角形：度 6；四边形：度 4 |
| semi-regular mesh | 半正则网格 | 少量异常点 + 大量正则 |
| approximating | 逼近 | 不经过控制点 |
| interpolating | 插值 | 经过控制点 |
| B-spline | B 样条 | 局部支撑、自动 C2 |
| knot | 节点 | 参数轴上的分界点 |
| knot multiplicity | 节点重数 | 重数↑ → 连续性↓ |
| NURBS | 非均匀有理 B 样条 | 带权重、保透视 |
| Cox-de Boor | — | B 样条的递推定义 |
| crease | 锐边 | 细分时保持锐利的边 |
| sharpness | 锐度 | 部分锐化的程度 |
| simplification | 简化 | 减少三角形 |
| QEM | 二次误差度量 | 到平面距离平方和 |
| quadric | 二次型 | 4×4 对称矩阵 |
| priority queue | 优先队列 | 按代价取最小 |
| LOD | 细节层次 | 多级分辨率 |
| regularization | 规整 | 改善三角形质量 |
| Delaunay | Delaunay 三角化 | 最大化最小角 |
| valence / degree | 度数 | 顶点邻居个数 |
| isotropic remeshing | 等向重网格 | 四步循环 |
| tangential smoothing | 切向平滑 | 只沿切平面移动 |

## 附录 E · 待生成图（提示词占位）

以下两张需要真实渲染质感，matplotlib 做不了，留提示词：

> **〔P1〕`diagrams/d17-lod-skull.png`**
> 用途：第 11 节「简化的极限」
> 提示词：*Four renders of the same human skull model side by side on white background, at 30000, 3000, 300 and 30 triangles respectively. Same camera and lighting. The last one (30 triangles) should look clearly faceted and barely recognizable as a skull. Flat matte blue-gray material, 1600×600.*
> 建议：下方标注面数，与 `d15-qem.png` 相邻。

> **〔P2〕`diagrams/d18-crease-comparison.png`**
> 用途：第 10 节「锐边（crease）」
> 提示词：*Two side-by-side renders of the same subdivision-surface cube-like shape. Left: uniform Catmull-Clark, all edges rounded into soft pillows. Right: same shape with all 12 edges marked as sharp creases, edges remain crisp and corners stay tight. Neutral gray material, studio lighting, 1600×900.*
> 建议：标注 `smooth` / `creased`，说明"纯细分会把所有棱角磨圆"。
