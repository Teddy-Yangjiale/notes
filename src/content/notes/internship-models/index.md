---
title: "模型拆解课：ABot、SAM 3、DA3 分别从照片里算出了什么？"
date: 2026-11-09
summary: "从 Patch、注意力、稠密预测头讲到 ABot 局部点图、SAM 语义掩膜与 DA3 Nested 尺度；解释模型能力如何经过项目代码变成实际数据。"
tags: ["实习", "视觉模型", "三维重建"]
series: "internship"
order: 16
shortTitle: "模型原理与调用边界"
---

## 0. 不要把三个模型合成一句“提取特征”

老师讲模型时，第一步应画清输入与输出。ABot 提供逐像素几何及位姿能力；SAM 3 提供语义对象的掩膜；DA3 提供深度与相机相关预测。项目随后对这些输出做尺度修正、坐标转换与掩膜处理，才成为高斯训练数据。

![视觉模型到几何接口的解释图](/notes/internship/figures/models.png)

本篇模型内部根据 2026-11-07 已保存的真实源码审查快照解释；项目调用点另用 2026-11-09 快照核对。模型默认配置、某次运行覆盖参数和论文推荐配置可能不同，文中分别说明。

## 1. 图像如何变成 Transformer 能处理的序列？

图像本来是 $H\times W\times3$ 的像素。Patch embedding 把它划成小块，再用可学习投影把每块变成一个长度为 $d$ 的向量。它的作用是把局部颜色和纹理变成后续可以比较与交换的信息。

若小块边长为 $P$，且尺寸能整除，图像 token 数为：

$$
N=\frac{H}{P}\frac{W}{P}.
$$

**手算。** 420×756 图像使用14×14 patch，得到30×54=1620个图像token，此外可能还有寄存器或相机token。这里一个token覆盖14×14像素，不是一个token直接对应一个三维高斯。

输入缩放与居中裁剪决定token实际看到原图哪一块。几何预测输出回到原图时，必须逆转这个预处理；只知道输出数组大小还不够。

## 2. 注意力究竟计算什么？

将token矩阵记为 $X$，分别线性变换得到查询、键和值：$Q=XW_Q$、$K=XW_K$、$V=XW_V$。注意力是：

$$
\operatorname{Attention}(Q,K,V)
=\operatorname{softmax}\left(\frac{QK^T}{\sqrt d}+M\right)V.
$$

第 $i$ 个查询与第 $j$ 个键的点积，表示当前任务下“第 $i$ 个位置应该从第 $j$ 个位置取多少信息”；softmax把权重归一化；最后加权求和值向量。$M$ 可以屏蔽不允许访问的位置，例如未来帧或窗口外的帧。

**手算。** 假设某个查询对两个位置给出softmax后权重0.8、0.2，它们的值分别为 $(1,0)$ 和 $(0,2)$，输出为 $(0.8,0.4)$。它没有复制一个像素，而是在特征空间混合信息。几何模型随后学习把这些组合解释为对应、深度或位姿。

多头注意力让不同子空间学习不同关系；位置编码说明token在图上或序列中的位置。不能只说“注意力融合全局信息”，还应问：允许访问哪些帧、哪些token，以及是否缓存历史特征。

## 3. ABot：图像特征如何生成点图？

审查的 `abot_pi3.py` 使用 DINOv2 ViT-L/14 编码器。large解码配置为1024维、16头、36层；代码同时支持其他配置和覆盖参数，所以这是所审查配置的结构描述，不能外推到所有同名权重。

编码器首先提取每张图的空间特征；解码部分让允许范围内的观测交换信息；点预测头再把patch特征还原为密集像素预测。`point_head` 输出的三通道被解释为两个方向分量与对数深度，而不是直接把三个无约束数当XYZ。

设预测为 $(a,b,\ell)$，代码通过正值变换得到深度：

$$
z=\exp(\min(\ell,\ell_{max})),
\qquad \mathbf P=(az,bz,z).
$$

这种参数化保证前向深度为正，$a,b$ 类似归一化成像坐标，随 $z$ 一起生成横纵位置。实际稳定性还依赖深度上限、权重和训练分布。

`local_points` 与 `global_points` 的区别是坐标系：局部点属于当前相机，全球点还要经过位姿组合。项目 `t04` 又以自己的标定射线和轨迹重放这些深度，因此浏览器点云不是未经处理的原始模型输出。

## 4. ABot 的“流式”为什么不是无限记忆？

所审查配置默认局部窗口12帧。模型设计通过有限局部上下文和缓存处理长序列，逐步组合相邻相机关系：

$$
T_{0\leftarrow i}=T_{0\leftarrow i-1}T_{i-1\leftarrow i}.
$$

每次只更新局部预测，内存不必随历史帧数无限增长。但组合会积累相对位姿误差：每步都有很小角度偏差，长距离之后仍可显著漂移。项目用外部轨迹和尺度约束重组点云，正是在利用不同来源的几何信息。

模型README的流式能力不能替代历史命令记录。某次0903重建究竟使用了何种窗口、采样率和输入分辨率，应看该次日志与元数据；不能用当前默认12帧反推旧运行的全部配置。

## 5. SAM 3：语义提示如何成为像素标签？

可以把它拆成图像编码、提示编码、对象查询与掩膜预测。图像特征提供哪里有什么局部外观；语义提示告诉模型要找哪类概念；候选对象输出类别相关分数和像素掩膜。

审查的 `sam3_processor.py` 关键处理是：

```python
out_probs = out_logits.sigmoid()
presence_score = outputs['presence_logit_dec'].sigmoid().unsqueeze(1)
out_probs = (out_probs * presence_score).squeeze(-1)
keep = out_probs > self.confidence_threshold
```

候选分数与“该概念存在”的分数相乘，再筛选实例。随后对mask logits插值到原图并做sigmoid、阈值化。项目的道路/车辆/天空提示与优先覆盖逻辑把这些实例变成一个标签图。

![SAM 输出经过项目合并后的标签可视化](/notes/internship/media/3540-labels.jpg)

输出结果告诉我们哪些像素暂时适合道路平面、哪些应排除静态训练。它不直接告诉车辆速度，也不保留跨帧对象身份。要重建动态车，需要在此之外增加跟踪与对象运动模型。

## 6. DA3：为什么多视模型之外还套一层 metric 模型？

`da3_nested_config.yaml` 指向 `NestedDepthAnything3Net`，any-view分支为giant，metric分支为large。前者利用多观测一致性，后者提供度量深度参照；Nested实现把两者的结果做尺度对齐，而不是简单平均两张深度图。官方代码和接口见 [DA3 仓库](https://github.com/ByteDance-Seed/Depth-Anything-3)与[API 文档](https://github.com/ByteDance-Seed/Depth-Anything-3/blob/main/docs/API.md)。

审查的网络包含DINOv2骨干和稠密预测头。DPT类预测头把不同层或尺度的token特征恢复为空间特征图，再逐步上采样，产生深度与置信。粗特征提供大范围关系，细特征补边界；输出分辨率不代表每个像素都有独立可信的几何测量。

Nested内部选择非天空和适当置信的像素，解一个标量尺度问题。设any-view深度为 $d_i$，metric参照为 $m_i$：

$$
\min_s\sum_i(sd_i-m_i)^2
\quad\Rightarrow\quad
s=\frac{\sum_i d_i m_i}{\sum_i d_i^2}.
$$

这来自求导 $2\sum_i d_i(sd_i-m_i)=0$。代码随后同时缩放深度和外参平移，以保持长度尺度一致。

**手算。** $d=(2,4)$、$m=(3,6)$，$s=(6+24)/(4+16)=1.5$，缩放后精确对应。若两者局部形状不同，一个标量无法同时消除全部误差。

## 7. 为什么项目还要再做一次道路尺度修正？

模型的metric先验来自学习，项目需要与自己的相机高度、轨迹单位一致。因此 `e03` 又使用道路平面估计组尺度。这是两个不同层次：模型内部让any-view分支接近metric分支，模型外部让输出接近项目道路尺度。

若模型metric分支正确而道路平面假设错误，外部修正反而可能引入偏差。必须保存修正前后深度、比例统计与参与像素，才能判断是哪种情况。只保存最终NPZ会降低诊断能力。

![DA3 已保存深度可视化](/notes/internship/media/3540-depth.jpg)

## 8. 置信字段为何不能看到名字就直接当概率？

一个名叫confidence的数，可能是概率、精度、经过指数变换的正值，或仅与正确程度单调相关的分数。是否落在0–1、是否校准、越大是否越好，都要查预测头和后处理。

当前审查路径中正值置信经 `clip(0,1)` 可能全部变成1，具体问题已在[8827第6节](/notes/internship-8827/)解释。正确处理应先统计分布，再与跨帧误差或人工几何检查作关系分析，最后确定权重函数。若高分像素并不更可靠，归一化也不能凭空制造可靠性。

## 9. 为什么 SR 与修补模型不能替代三维证据？

照片分支还有超分辨率与去车修补。超分辨率可以提高视觉锐度，但新细节未必来自真实观测；修补可以填满被车遮住的颜色，但不能证明填充处的几何正确。

如果将修补像素用于三维训练，必须给它们单独标签和较低证据地位。真实未遮挡照片仍应是主监督。对于用户优先的自由视角展示，锐利的输入只是条件之一，稳定的多视几何和正确遮挡更关键。

## 10. 三个模型的接口总结

| 模型 | 我们真正消费的量 | 项目额外操作 | 最容易误说的地方 |
|---|---|---|---|
| ABot | 点图深度与几何信息 | 重新标定射线、道路定尺度、项目轨迹、过滤 | “直接用模型全球点云” |
| SAM 3 | 道路/动态/天空掩膜 | 筛分数、合实例、覆盖优先级、膨胀 | “已经跟踪并重建车辆” |
| DA3 Nested | 深度、置信、内参 | 分组择中、道路尺度、道路深度替换 | “已有置信概率和唯一真表面” |

<details>
<summary>为什么网络越强，仍然可能在错误标定下重建失败？</summary>

网络输出必须经过像素映射、尺度和位姿才能进入世界坐标。错误接口可以把合理的相机深度放到错误方向或距离。模型能力与项目几何接口共同决定最终结果，不能只靠更换权重修复坐标错误。

</details>

## 源码课：从公式回到真实文件

下面是可离线阅读的带行号代码快照。项目调用代码采集于2026-11-09；模型与历史补充文件单独标注日期。源码注释也可能包含旧判断，应与本文核验和实际语句一起读。

| 文件 | 原路径 / 快照 | 长度 |
|---|---|---|
| [abot_pi3.py](/notes/internship/code/models-abot_pi3.py.html) | `2026-11-07 model audit snapshot` | 730 行 |
| [abot_config.json](/notes/internship/code/models-abot_config.json.html) | `2026-11-07 model audit snapshot` | 10 行 |
| [abot_preprocessing.py](/notes/internship/code/models-abot_preprocessing.py.html) | `2026-11-07 model audit snapshot` | 117 行 |
| [da3_model.py](/notes/internship/code/models-da3_model.py.html) | `2026-11-07 model audit snapshot` | 442 行 |
| [da3_nested_config.yaml](/notes/internship/code/models-da3_nested_config.yaml.html) | `2026-11-07 model audit snapshot` | 10 行 |
| [sam3_processor.py](/notes/internship/code/models-sam3_processor.py.html) | `2026-11-07 model audit snapshot` | 223 行 |

### 关键片段逐句读

先把logit变成候选分数，再乘presence分数，最后按阈值筛选。这个实例级筛选与随后像素掩膜阈值是两层不同判断。

原文件定位：[sam3_processor.py 第 195 行](/notes/internship/code/models-sam3_processor.py.html#L195)。以下为真实节选，依赖所在文件上下文，不是独立可运行程序。

```python
        out_probs = out_logits.sigmoid()
        presence_score = outputs["presence_logit_dec"].sigmoid().unsqueeze(1)
        out_probs = (out_probs * presence_score).squeeze(-1)

        keep = out_probs > self.confidence_threshold
        out_probs = out_probs[keep]
        out_masks = out_masks[keep]
        out_bbox = out_bbox[keep]

```

[返回专栏总览](/notes/internship-00-overview/) · [下载可编辑图解](/notes/internship/editable-diagrams.zip)
