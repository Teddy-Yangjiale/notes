---
title: "8824：交通标志在三维空间中的位置，是怎样算出来的？"
date: 2026-11-09
summary: "从检测框的锚点出发，逐步推导射线求交、多视三角化、Huber 重加权与退化检查，并解释后续时钟审计为什么改变早期结论。"
tags: ["实习", "资产定位", "三角化"]
series: "internship"
order: 6
shortTitle: "8824：道路资产三维定位"
---

## 0. 先把检测与定位分开

检测器能回答“这张照片中哪一个矩形像交通标志”，但矩形仍然是二维像素。8824 接着回答“这个标志在道路坐标系中在哪里”。该项目使用 0907 资产观测和 P0 米制位姿，当前服务是 `/home/yjl/asset8824/site/serve.py`，与 0924 裂缝查看器使用的数据不同。

![8824 资产总览的既有截图](/notes/internship/media/8824_overview.jpg)

左侧资产列表、中央三维位置和右侧观测照片分别对应三种数据：对象身份、几何位置、原始证据。不能只看三维标记，因为错误检测或错误关联也能产生一个看起来合理的三维点。

## 1. 代码如何从一条资产轨迹开始？

`a1_locate.py` 读取 `tracks`、`proposals` 和按 `frame_id` 索引的位姿。一个 track 是算法认为属于同一物体的一组检测框。脚本遍历每个 track，找到各帧的框、类别、相机矩阵，然后根据物体种类决定采用哪一种几何。

![8824 实现流程](/notes/internship/figures/8824.png)

| 物体类型 | 框内取哪个像素 | 为什么 |
|---|---|---|
| 贴地标线 | 框中心 | 想估计其地面代表位置 |
| 锥桶、施工牌等立地物 | 框底边中点 | 底边接近与道路接触的位置 |
| 悬空标志、信号灯 | 框中心 | 多张照片交会出一个代表点 |

这由 `geom.anchor_uv()` 实现。框中心不一定是稳定的同一个物理点：遮挡或框大小变化会改变中心，因此框级三角化精度受到检测框稳定性的限制。

## 2. 把框内像素变成世界射线

先用内参逆矩阵得到相机方向，再转到世界并单位化：

$$
\mathbf q_i=K^{-1}[u_i,v_i,1]^T,
\qquad \mathbf d_i=\frac{R_i^T\mathbf q_i}{\|R_i^T\mathbf q_i\|}.
$$

这里的 $R_i$ **按本分支代码表示 world-to-camera**。虽然变量名写成 `R_cw`，`ray()` 里实际使用 `R_cw.T @ r`，`reproject()` 里使用 `R_cw @ (X-C)`。这与有些其他分支的同名变量方向不同。读代码必须通过实际乘法确认，不能全项目统一按名字猜。

相机中心 $\mathbf o_i$ 是射线起点，$\mathbf d_i$ 是单位方向。现在每次观测给出一条直线上的可能位置，而不是一个确定点。

## 3. 地面资产：一条射线已经够用，但依赖平面假设

`ground_intersect()` 将局部道路高度设为相机高度减去 `CAM_HEIGHT_M`，当前这条实现使用 1.60 m。求交为：

$$
t_i=\frac{z_{road}-o_{iz}}{d_{iz}},
\qquad \mathbf X_i=\mathbf o_i+t_i\mathbf d_i.
$$

程序拒绝朝上、平行或交点在身后的射线，并检查最大距离。同一个资产在多张照片得到多个落点，`a1` 先计算逐坐标中位数，再按离中位数的距离筛点，最后对保留点求平均。

**注意具体实现的细节。** 文件中的 `scatter_m` 是各保留落点到均值的距离的标准差，不是位置协方差，也不是这些距离的 RMS。这几个统计量含义不同，不能在报告里互换名称。

![8824 标线资产的既有截图](/notes/internship/media/8824_mark.jpg)

*照片提供框与地面语境。若路面有坡度，水平平面假设会改变距离；多帧落点相近也可能共同带着同一个高度偏差。*

## 4. 悬空资产：为什么要最小化点到射线的距离？

![两台相机观察同一物体的三角化示意](/notes/internship/figures/triangulation.png)

*原生可编辑教学图。几何上真正有用的是射线夹角，而不是照片张数或车辆总里程本身。*

有噪声的多条射线通常不会精确相交。我们寻找一个点，使它离这些射线尽量近。对单位方向 $\mathbf d_i$，矩阵 $P_i=I-\mathbf d_i\mathbf d_i^T$ 会去掉向量沿射线的分量，只留下垂直分量。因此：

$$
E(\mathbf X)=\sum_i w_i\|P_i(\mathbf X-\mathbf o_i)\|^2.
$$

因为 $P_i$ 对称且 $P_i^2=P_i$，对 $\mathbf X$ 求导并令其为零，得到一个 3×3 线性系统：

$$
A\mathbf X=\mathbf b,
\qquad A=\sum_iw_iP_i,
\qquad \mathbf b=\sum_iw_iP_i\mathbf o_i.
$$

这正是 `geom.triangulate()` 中 `A += wi * P`、`b += wi * (P @ oi)` 和 `np.linalg.solve(A,b)` 的含义。它每次求一个三维点，没有训练神经网络。

![8824 交通标志的既有截图](/notes/internship/media/8824_sign.jpg)

## 5. 两个相机离得远，为什么仍可能三角化不好？

想象汽车一直朝一块正前方标志开。相机中心移动很多，但看向标志的射线方向变化很小。沿射线移动三维点，重投影变化也很小，所以距离不容易确定。

双目近似可以帮助估算敏感性：若有效横向基线为 $B$，焦距为 $f$，视差 $d=fB/Z$，则一像素视差误差带来的深度误差近似为：

$$
|\Delta Z|\approx\frac{Z^2}{fB}|\Delta d|.
$$

**手算。** $Z=30$ m、$f=1200$ px、有效横向基线 $B=1$ m，1 px 的误差约造成 0.75 m 深度误差。若有效基线只有 0.1 m，误差约为 7.5 m。这里说的是有效横向基线，不是车辆总共走了多少米。

实现检查 $A$ 的条件数，过大时拒绝求解；还记录最大射线夹角。条件数大表示某个方向几乎没有约束，小像素扰动就可能造成大坐标变化。

## 6. Huber 重加权怎样处理坏框？

第一次令全部 $w_i=1$ 求三维点，再投回每张照片，计算预测像素与框锚点的距离 $e_i$。随后更新：

$$
w_i=\begin{cases}1,&e_i\le\delta,\\\delta/e_i,&e_i>\delta.\end{cases}
$$

较大残差仍参与，但权重变小。`robust_triangulate()` 默认阈值为 8 px，并有最大迭代次数；最终 `w>0.3` 的观测用于部分汇总统计。**它并不是每轮都直接最小化完整像素重投影目标**：每轮解的是带权点到射线距离，再用像素误差更新权重。这是这份实现的具体选择。

## 7. 结果为什么还要看时钟审计？

![8824 信号灯的既有截图](/notes/internship/media/8824_light.jpg)

历史 README 先报告了重投影、点云邻近和高度合理性，后来 2026-10-08 的只读审计提出约 +1.7 s 的录像—定位时间差。以 44 km/h 做量级估算，$44/3.6\times1.7\approx20.8$ m。这解释了为什么局部相对几何可以很像，绝对位置仍整体偏移很多。

后续记录还指出高度 1.60 m 与若干几何估计约 1.50 m 不一致，以及标志关联存在重复。README 明确把相关预演写入 `preview_*`，没有把它宣称为已经应用到原结果。本篇不会把预演改进数字写成当前线上已修复。

此外，点云与资产虽然来自不同算法，仍共享位姿和标定；二者相互贴近是有用的交叉检查，但不是完全独立的绝对真值。

## 8. 新读者怎样顺着代码读完一条资产？

从 `a1_locate.py` 的 `for t in tracks.itertuples()` 开始，依次记录 track ID、参与观测框、锚点、射线、所选几何分支、剔除条件、输出坐标，再到 `a2_verify.py` 看附加检查，最后到 `a4_site.py` 看这些字段如何进入页面。

如果缺少某条资产的中间射线图，应该用其原始观测重新作只读诊断图，而不是拿另一个资产的图作结果。当前配图是已保存的真实查看器截图，未重新三角化或重写资产台账。

<details>
<summary>为什么框的类别抖动，也会改变三维资产数量？</summary>

若关联阶段以细类别严格分组，同一块标志在不同帧被分成两个类别，就可能拆成两条 track，随后各自三角化成两个资产。三维求解器并不知道它们实际上是同一块牌，问题发生在对象关联阶段。

</details>

## 源码课：从公式回到真实文件

下面是可离线阅读的带行号代码快照。项目调用代码采集于2026-11-09；模型与历史补充文件单独标注日期。源码注释也可能包含旧判断，应与本文核验和实际语句一起读。

| 文件 | 原路径 / 快照 | 长度 |
|---|---|---|
| [geom.py](/notes/internship/code/8824-geom.py.html) | `/home/yjl/asset8824/a/geom.py` | 131 行 |
| [a1_locate.py](/notes/internship/code/8824-a1_locate.py.html) | `/home/yjl/asset8824/run/a1_locate.py` | 132 行 |
| [a2_verify.py](/notes/internship/code/8824-a2_verify.py.html) | `/home/yjl/asset8824/run/a2_verify.py` | 118 行 |
| [README.md](/notes/internship/code/8824-README.md.html) | `/home/yjl/asset8824/README.md` | 113 行 |

### 关键片段逐句读

P 去掉沿射线的分量；A、b 累加每条射线的约束；cond 检查系统是否退化；solve 求三维点。逐句对应正文的正规方程。

原文件定位：[geom.py 第 57 行](/notes/internship/code/8824-geom.py.html#L57)。以下为真实节选，依赖所在文件上下文，不是独立可运行程序。

```python
def triangulate(origins, dirs, weights=None):
    """最小二乘多视三角化：min Σ wᵢ‖(I − dᵢdᵢᵀ)(X − oᵢ)‖²。

    返回 (X, 残差RMS, 条件数)。条件数大 = 几何退化（前向运动的极点附近）。
    """
    O = np.asarray(origins, float)
    D = np.asarray(dirs, float)
    w = np.ones(len(O)) if weights is None else np.asarray(weights, float)
    A = np.zeros((3, 3)); b = np.zeros(3)
    for oi, di, wi in zip(O, D, w):
        P = np.eye(3) - np.outer(di, di)
        A += wi * P
        b += wi * (P @ oi)
    cond = float(np.linalg.cond(A))
    if not np.isfinite(cond) or cond > 1e12:
        return None, np.inf, cond
    X = np.linalg.solve(A, b)
    res = np.array([np.linalg.norm((np.eye(3) - np.outer(d, d)) @ (X - o))
                    for o, d in zip(O, D)])
    return X, float(np.sqrt((res ** 2).mean())), cond


def max_pair_angle(dirs) -> float:
    """射线两两夹角的最大值（度）。前向运动下这是可解性的直接度量。"""
```

[返回专栏总览](/notes/internship-00-overview/) · [下载可编辑图解](/notes/internship/editable-diagrams.zip)
