---
title: "8830：人工标注怎样成为可复查的评估数据？"
date: 2026-11-09
summary: "按真实 HTTP 接口解释检测框、裂缝折线、预测连通块、VOC/PNG/JSON 保存和盲核对抽样；用真实照片与坐标算例讲清像素、线宽与统计分母。"
tags: ["实习", "标注工具", "评估"]
series: "internship"
order: 12
shortTitle: "8830：病害标注与核对"
---

## 0. 它不是重建器，而是证据生产工具

8830 当前运行 `/home/yjl/crack/annot_tool/server.py`。它让人修正检测框、检查裂缝分割，并完成独立核对队列。它会保存评估集，因此浏览器里的“保存”是数据写入；本次写笔记只读取列表、样例与代码，没有提交答案或触发评估。

![当前评估集中一张真实原始照片](/notes/internship/media/8830-observation.jpg)

*样例 `p_00057_1788762762844`，1280×720。读取时该样例的检测和分割完成标记均为 0，不能将其预标注当人工真值。*

## 1. 一个样本有哪些文件？

![8830 数据读写流程](/notes/internship/figures/8830.png)

| 文件 | 表示的内容 | 谁使用 |
|---|---|---|
| `images/<name>.jpg` | 原始照片 | 页面与评估输入 |
| `pred/` | 原始预测 | 提供预标注参照，不能等同于答案 |
| `det_xml/<name>.xml` | VOC 检测框 | 检测评估 |
| `seg_png/<name>.png` | 离散类别彩图 | 分割评估 |
| `annot/<name>.json` | 框、删除连通块、改类、手画折线 | 恢复完整编辑状态 |
| `notes.csv` | 是否完成、可用性、备注 | 决定评估范围 |
| `annot/_log.jsonl` | 历次保存状态 | 追溯修改 |

为什么 JSON 与 XML/PNG 都要保存？JSON 保留人的编辑意图，例如“删除第 12 个预测连通块”；XML/PNG 是现有评估脚本需要的最终表示。只存 PNG，就难以恢复这条编辑意图。

## 2. 页面打开后，服务器实际返回什么？

`GET /api/list` 返回样本清单和完成状态；`GET /api/item/<name>` 返回框、分割编辑状态与元信息；`GET /img/<name>.jpg` 返回照片。分割连通块另由 `/segmap/` 编码提供。

当前读到的样例有一个 `road_box_d` 预标注框：左上 $(428,270)$，右下 $(474,295)$，`origin="model"`、分数约 0.2572。这是预测记录，不是本文确认它正确。

**手算。** 按连续坐标差的约定，该框宽 46 px、高 25 px，中心为 $(451,282.5)$。若前端把图缩成 640×360 显示，显示位置减半；保存时必须乘回原图比例，不能把屏幕坐标直接写进原始分辨率的 XML。

## 3. 人手画的裂缝线，怎样变成类别图？

`render_seg()` 先复制预测标签，按照 `removed` 将指定连通块置背景，再按 `recls` 改类别，最后把手画折线栅格化。核心调用是：

```python
pts = np.round(np.array(ln['pts'], float)).astype(np.int32)
cv2.polylines(lab, [pts.reshape(-1, 1, 2)], False,
              int(ln['cls']), thickness=max(1, int(ln.get('w', 4))),
              lineType=cv2.LINE_8)
```

`False` 表示不自动闭合；`w` 是像素线宽，默认 4。它并不是裂缝真实物理宽度。相机距离不同，4 px 对应的地面长度不同；评估时还要明确标注的是中心线带还是实际可见边界。

输出数组先存离散标签，再按调色板映射到 BGR 彩图。颜色只是类别编码，不应把抗锯齿混合色误当成新类别。

## 4. 保存请求怎样同步各文件？

`POST /api/save/<name>` 进入 `save_state()`。程序验证类别，排序框两端坐标，把线与连通块编辑整理成统一格式，然后在进程锁中写 JSON、追加日志、写 XML、重画 PNG，并更新 `notes.csv`。

`notes.csv` 使用临时文件再 `os.replace`；但不能因此声称所有文件作为一个事务原子保存。若进程在多文件写入中途退出，仍需要根据日志与状态核查各格式是否一致。

启动时有原预标注备份逻辑，但备份文件存在不意味着每次保存都自动生成完整快照。实际恢复需要查看对应备份、JSON 与追加日志。

## 5. 为什么“未完成”不能当作“没有病害”？

空标注可能有三种含义：图中没有病害、标注员还没处理、图像不可用。`done_det`、`done_seg` 和 `usable` 分开记录，正是为了避免把它们混成背景样本。

检测精确率与召回率分别是：

$$
P=\frac{TP}{TP+FP},\qquad R=\frac{TP}{TP+FN}.
$$

未完成图像若被当成全背景，正确预测会被算成 FP；漏标目标又会让真实 FN 消失。数据状态会直接改变指标，因此“标注平台能画框”只是第一步，完成状态和协议同样重要。

## 6. IoU 怎样计算，为什么细裂缝特别敏感？

两个区域的交并比是：

$$
\operatorname{IoU}(A,B)=\frac{|A\cap B|}{|A\cup B|}.
$$

教学例子：两条同长、宽 4 px 的带横向错 2 px，忽略端点后交集宽2、并集宽6，IoU约1/3。肉眼可能认为两条线指向同一裂缝，但像素 IoU 已明显降低。若目标是中心线定位，还需考虑容许距离或骨架指标；本页不把这些建议说成现有评估脚本已实现。

## 7. 核对队列为什么要隐藏模型分数？

`build_verify_queue.py` 按分数段与类别组分层抽样，固定随机种子，并保存每层总体数与抽样数到元信息。页面不显示模型分数和另一趟是否复现，是为了减少评判时的暗示。

如果每层抽同样多，但真实总体中各层大小不同，简单平均样本正确率不代表总体正确率。设第 $h$ 层总体数 $N_h$、抽样数 $n_h$，抽到样本的估计权重为 $N_h/n_h$：

$$
\hat p=\frac{\sum_h(N_h/n_h)\sum_{i\in h}y_i}{\sum_hN_h}.
$$

这是解释如何从分层样本估计总体比例的公式，不是声称平台已经自动算好了全部加权指标。缺失答案、无效图和重复物理实例还要单独处理。

## 8. 标注与算法改进应该怎样衔接？

先明确标注单位是一次检测还是物理病害；再规定模糊、遮挡与不可判断的处理；保存完成状态后，冻结一份评估集。之后比较模型时使用同一冻结版本。若边看结果边改答案，比较对象就随算法一起变化，指标失去可解释性。

当前类别中文名称的源码注释还写着“按英文类名字面意思写，尚未经算法侧确认”。笔记保留这个事实，不把名称当成已完成业务标准核验。

<details>
<summary>为什么本次没有点击“跑评估”？</summary>

本任务是解释实现和展示已有证据，不是新增评估或写入结果。服务器的 `/api/eval` 会启动评估子进程，读取页面与读取代码已经足够解释其接口，未调用该执行入口。

</details>

## 源码课：从公式回到真实文件

下面是可离线阅读的带行号代码快照。项目调用代码采集于2026-11-09；模型与历史补充文件单独标注日期。源码注释也可能包含旧判断，应与本文核验和实际语句一起读。

| 文件 | 原路径 / 快照 | 长度 |
|---|---|---|
| [server.py](/notes/internship/code/8830-server.py.html) | `/home/yjl/crack/annot_tool/server.py` | 421 行 |
| [build_verify_queue.py](/notes/internship/code/8830-build_verify_queue.py.html) | `/home/yjl/crack/annot_tool/build_verify_queue.py` | 91 行 |

### 关键片段逐句读

先复制预测，删除指定连通块，再改类别，最后画人的折线。顺序决定最终标签；保存的是类别编码而非叠加展示颜色。

原文件定位：[server.py 第 157 行](/notes/internship/code/8830-server.py.html#L157)。以下为真实节选，依赖所在文件上下文，不是独立可运行程序。

```python
def render_seg(name, seg):
    c = comps(name)
    if c is None:
        return False
    lab0, ids, _ = c
    lab = lab0.copy()
    removed = [int(v) for v in seg.get('removed', [])]
    if removed:
        lab[np.isin(ids, removed)] = 0
    for k, v in (seg.get('recls') or {}).items():
        lab[ids == int(k)] = int(v)
    for ln in seg.get('lines', []):
        pts = np.round(np.array(ln['pts'], float)).astype(np.int32).reshape(-1, 1, 2)
        if len(pts) >= 2:
            cv2.polylines(lab, [pts], False, int(ln['cls']), thickness=max(1, int(ln.get('w', 4))), lineType=cv2.LINE_8)
    pal = np.array([PAL[k] for k in range(4)], np.uint8)
    cv2.imwrite(S('seg_png', name + '.png'), pal[lab])
    return True


def get_state(name, it):
```

[返回专栏总览](/notes/internship-00-overview/) · [下载可编辑图解](/notes/internship/editable-diagrams.zip)
