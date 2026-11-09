---
title: "8829：稀疏抓拍怎样拼成路面？联合优化为什么也会把几何调坏？"
date: 2026-11-09
summary: "从当前实验首页与旧全线浏览器分层讲起，解释记录清理、相机几何、高度场、曝光、纹理交替优化、留出对应和真实局部结果。"
tags: ["实习", "路面拼接", "联合优化"]
series: "internship"
order: 11
shortTitle: "8829：稀疏抓拍与路面优化"
---

## 0. 当前首页与原全线浏览器不是同一个结果

2026-11-09 读取的首页标题为“8829 · 路面重建最新成果”，入口文件链接到 `viewer_full_route_1015045141.html` 保留原全线浏览器。当前首页展示局部实验、输入问题与几何诊断；不能把其中一处清晰样例说成整条路线已经通过几何验收。

该分支主要使用 1012 平台稀疏前后摄抓拍。它与 8828 连续录像底图的采样和时间问题不同，也与 8827 的三维高斯优化不同。

## 1. 输入为什么要先清理，再谈模型？

![8829 现有原始网格照片组](/notes/internship/media/8829-raw_grid_rows.jpg)

*这组已保存照片用于观察真实重复结构和采样关系。它不是合成纹理，也不是优化后的表面。*

平台 CSV 的一行不一定代表一次新的曝光：可能出现重复图像、重复位置、时间回退或旧定位复用。若把这些行一概当作不同相机观测，系统会被要求“相同照片来自不同位置”，这与真实成像过程矛盾。

`prepare_clean_inputs.py`、`clean_duplicate_images.py`、`clean_time_regressions.py` 以及 `run_clean_pipeline.py` 把这些检查放到独立运行目录。驱动程序冻结源 CSV 与代码哈希，避免旧中间结果和新输入混用。清理记录必须保留源行号和排除原因，不能只交付一个更漂亮的成功子集。

![8829 数据到验证的流程](/notes/internship/figures/8829.png)

## 2. 最终想求的表面是什么？

`p13_joint.py` 的主要表示是道路高度场：对每个东、北位置 $(E,N)$，只允许一个高度 $z(E,N)$。这适合局部道路，不适合立交上下两层共用同一平面位置，也不能表示垂直建筑立面。

高度在较粗的控制网格上存储，再用双线性插值取得采样位置的高度。纹理在更细的路面网格上表示。当前脚本默认参数中纹理分辨率为 0.04 m，高度控制网格为 0.25 m；实际历史实验可能覆盖这些默认值，必须看运行参数。

这与三维高斯不同：没有为每个纹理像素放一个自由旋转椭球，主要是把一个表面投影回各张照片取颜色。

## 3. 逆向采样：一个地面格子怎样找到多张照片？

给定地面格子中心 $\mathbf X=(E,N,z(E,N))$，用各相机位姿和内参投影出像素 $\pi_i(\mathbf X)$，再从照片双线性取样 $I_i(\pi_i(\mathbf X))$。只保留在图内、位于有效道路区域、距离符合要求的观测。

$$
C_i(\mathbf X)=I_i\bigl(\pi(K_iT_{wc,i}\mathbf X)\bigr).
$$

投影位置随相机与高度改变，所以照片采样也随之改变。只要采样操作可微，颜色误差就能反传给位姿和高度。这是联合优化可以调整几何的原因，也是它可能用错误几何解释外观变化的原因。

![现有局部实验的一张较清楚来源结果](/notes/internship/media/8829-best_resolved_source.jpg)

*“较清楚来源”强调选图和投影后的可见纹理，不等于独立测量已确认几何正确。来源见素材清单。*

## 4. 曝光、暗角与阴影怎样进入模型？

同一地面格子在不同照片中可能因为自动曝光、眩光或本车阴影而亮度不同。代码用每帧通道增益 $a$、偏置 $b$、相机暗角场 $V$ 和阴影项解释这些差异。概念关系为：

$$
I_{i,c}=a_{i,c}\,T_c\,V_{cam}(u,v)
\exp\bigl(s_{i,c}M_{shadow}(u,v)\bigr)+b_{i,c}.
$$

$T$ 是希望恢复的地面纹理。增益处理整体比例，偏置处理加性的亮度偏移，暗角描述相机画面位置相关的衰减，阴影掩膜指定局部阴影区域。

假如不解释曝光，优化器可能通过移动相机，把一个暗像素对到另一块暗地面来减小损失；反过来，曝光模型太自由，也可能吸收真正的错位，令训练损失看起来很好。因此几何和外观必须分别检查。

## 5. 为什么交替求纹理与几何？

固定几何和外观校正时，同一个格子的多个颜色观测可以直接加权平均得到纹理。固定纹理后，再对高度、位姿和曝光做若干步 Adam。这样重复交替，而不是一开始把所有变量完全自由地一起更新。

$$
T(\mathbf X)=\frac{\sum_i w_i(\mathbf X)\,\widetilde C_i(\mathbf X)}
{\sum_iw_i(\mathbf X)+\epsilon}.
$$

$\widetilde C_i$ 是按当前外观参数校正后的颜色。距离权重含 $(3/d)^2$ 形式：距离 3 m 时权重 1，6 m 时为 0.25。这偏好近处分辨率更好的观测，但不是近处永远更可信；近处若有车身阴影或标定问题仍会出错。

![相同局部实验的等权融合结果](/notes/internship/media/8829-equal_weight_blend.jpg)

*与较清楚来源图一起读：平均会抑制噪声，也会把不一致纹理混成重影。颜色更平滑不能证明位姿更准确。*

## 6. 鲁棒损失和平滑项，各自限制哪一种自由度？

光度项使用 Charbonnier 一类平滑绝对值：

$$
\rho(r)=\sqrt{r^2+\epsilon^2}.
$$

大残差相对平方误差不会增长得那么快，减少阴影或坏匹配的影响。高度平滑项则限制相邻控制点高度变化，避免用锯齿表面逐像素拟合噪声；高度先验把弱观测区拉回初始道路模型；位姿正则限制相机偏离可靠初值。

这些项需要合理权重。如果把高度锁死，真实坡道无法表达；如果放得太松，表面可能扭曲去解释曝光或时钟错误。`p13` 有冻结几何、关闭曝光、关闭高度等开关，正适合做明确的消融实验，但脚本支持某选项并不证明某历史结果使用了它。

## 7. 一个具体陷阱：绕世界原点旋转相机

正确的小旋转通常希望改变相机朝向，而不让相机中心绕远处世界原点转一圈。脚本保留 `--rot_world` 旧约定作为对照，并注明默认绕相机中心。

**手算。** 场景距原点 1300 m，旋转 $10^{-4}$ rad 若绕世界原点发生，会引入约 $1300\times10^{-4}=0.13$ m 的位置移动。角度极小，平移却达到 13 cm。这说明变换作用点与旋转矩阵同样重要。

## 8. 留出几何为什么比训练拼图更有说服力？

![已保存的留出交点诊断](/notes/internship/media/8829-heldout_intersections.jpg)

![已保存的对应点审查图](/notes/internship/media/8829-correspondence_review.jpg)

训练图参与参数拟合，因此可能被过拟合。选未用于求解的标线交点或人工对应，检查投影是否一致，才更能区分“把训练颜色抹平”与“几何解释更可靠”。若所谓留出点仍参与了上游相机估计，应说明信息复用范围。

还要同时检查覆盖：只保留最容易的几张图可以变清楚，但失去很多道路。展示质量、覆盖和几何误差应并列记录。

![已有局部覆盖比较](/notes/internship/media/8829-coverage_comparison.jpg)

*这张图用于说明覆盖需要单独检查。本文没有把它外推为全路线覆盖已验收。*

## 9. 代码存在、实验跑过、当前上线，是三件事

`p13_joint.py` 的头部解释了高度场思路，但仓库中还有多个版本和许多诊断脚本；不能串成一条从未实际运行过的“最终流程”。当前首页、保留的全线浏览器和独立清理运行目录，应各自拥有结果清单与哈希。

本篇讲清了这份优化器的机制，并用已有局部结果解释观察方法。本次没有运行清理驱动、训练或覆盖线上数据。下一步真正验收，应固定输入、相机与留出对应，再逐项开关高度、位姿、曝光，观察误差与覆盖如何同时变化。

<details>
<summary>为什么让每张图自由形变，可能让拼图变清楚却削弱三维意义？</summary>

形变可以直接把相同纹理拉到一起，绕过真实相机和表面的几何约束。若不限制幅度并用独立对应检验，它可能只是二维拼接补偿，不能证明恢复了正确三维道路。

</details>

## 源码课：从公式回到真实文件

下面是可离线阅读的带行号代码快照。项目调用代码采集于2026-11-09；模型与历史补充文件单独标注日期。源码注释也可能包含旧判断，应与本文核验和实际语句一起读。

| 文件 | 原路径 / 快照 | 长度 |
|---|---|---|
| [p13_joint.py](/notes/internship/code/8829-p13_joint.py.html) | `/home/yjl/crack/snap1012/build/p13_joint.py` | 619 行 |
| [p14_render.py](/notes/internship/code/8829-p14_render.py.html) | `/home/yjl/crack/snap1012/build/p14_render.py` | 425 行 |
| [prepare_clean_inputs.py](/notes/internship/code/8829-prepare_clean_inputs.py.html) | `/home/yjl/crack/snap1012/build/prepare_clean_inputs.py` | 64 行 |
| [run_clean_pipeline.py](/notes/internship/code/8829-run_clean_pipeline.py.html) | `/home/yjl/crack/snap1012/build/run_clean_pipeline.py` | 168 行 |

### 关键片段逐句读

固定当前几何与外观参数后，这一函数重新估计路面纹理。读代码时追踪每个格子的颜色和权重累加，再看分母；它与随后对几何执行Adam是交替步骤。

原文件定位：[p13_joint.py 第 434 行](/notes/internship/code/8829-p13_joint.py.html#L434)。以下为真实节选，依赖所在文件上下文，不是独立可运行程序。

```python
def update_T():
    with torch.no_grad():
        acc = torch.zeros((NT, 3), device=dev); ws = torch.zeros(NT, device=dev)
        for vi in range(NV):
            ii, w = samp[vi]
            pred, ok = observe(vi, ii)
            ww = w * ok
            acc.index_add_(0, ii, pred * ww[:, None]); ws.index_add_(0, ii, ww)
        return acc / ws.clamp_min(1e-6)[:, None], ws


if args.init:
    J = np.load(f"{OUT}/joint_{args.init}.npz")
    with torch.no_grad():
        tt = lambda k: torch.tensor(J[k], device=dev)
        omega.copy_(tt("omega")); delta.copy_(tt("delta")); rear_d.copy_(tt("rear_d") - rinit)
        rc_old = bool(J["rot_center"]) if "rot_center" in J.files else False
        if rc_old != (not args.rot_world):   # 约定不同：保持同一个相机位姿，换算平移量
            for fi_ in range(NF):
                S_ = so3(omega[fi_]); t0_ = W0_t[fi_, :3, 3]
                tf_ = (S_ @ t0_ if rc_old else t0_) + delta[fi_]
                delta[fi_] = tf_ - (t0_ if args.rot_world else S_ @ t0_)
            log(f"init: rotation convention converted ({'center' if rc_old else 'world'} -> {'world' if args.rot_world else 'center'})")
        loga.copy_(tt("loga")); bb.copy_(tt("bb")); vig.copy_(tt("vig")); shad.copy_(tt("shad"))
        dZ.copy_(tt("Zg") - Zg0_t)
        if "rs" in J.files: rs.copy_(tt("rs"))
        if "rext_w" in J.files: rext_w.copy_(tt("rext_w")); rext_t.copy_(tt("rext_t"))
        if "bgrid" in J.files: bgrid.copy_(tt("bgrid"))
```

[返回专栏总览](/notes/internship-00-overview/) · [下载可编辑图解](/notes/internship/editable-diagrams.zip)
