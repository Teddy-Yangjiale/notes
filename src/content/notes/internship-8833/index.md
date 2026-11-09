---
title: "8833：算法讲解站如何把代码、公式与真实结果组织在一起？"
date: 2026-11-09
summary: "解释独立重建讲解站的静态构建、阶段切换、数学渲染、搜索导航、素材来源和服务边界；说明它展示已有结果，并不训练场景。"
tags: ["实习", "技术讲解", "可视化"]
series: "internship"
order: 15
shortTitle: "8833：算法讲解站"
---

## 0. 先说明它与这一套笔记的关系

8833 是此前搭建的独立重建说明站，服务位于 `/vdata/yjl/recon8833`，监听 Tailscale 地址 `100.105.132.36:8833`。它以8825的展示风格组织原图、标签、深度、流程、公式和代码入口。本次用户要求的是更深入的老师式解释，因此这套实习笔记重新撰写正文，补上推导、算例和失败原因。

8833 本身不运行 SAM、DA3 或高斯训练；它读取已有媒体和说明。下面讲它的实现，避免把“在网页里切换步骤”误认为在线执行了步骤。

## 1. 构建时与访问时，各发生什么？

![8833 构建与阅读流程](/notes/internship/figures/8833.png)

| 时刻 | 实际动作 | 结果 |
|---|---|---|
| 整理证据 | 读取代码、日志和既有结果 | 可追溯的说明材料 |
| 准备媒体 | 对已有标签、深度数组做可视化 | JPEG 与来源清单 |
| 构建页面 | 写 HTML、样式、交互数据，准备公式资源 | 静态站点目录 |
| 浏览器打开 | 下载这些文件 | 展示已有内容 |
| 用户切换阶段 | 更新本地 DOM 与图片引用 | 改变阅读内容，不调用训练 |

对应本地工作文件包括 `build_site.py`、`prepare_media.py`、`app.js`、`site.css`、`serve.py`。部署产物与生成脚本应分别记录；修改脚本后未重新构建，页面不会自动变化。

## 2. 一张标签图怎样变成读者看得懂的配图？

原始标签是每像素一个小整数，直接打开可能全黑。可视化时把不同类别映射为颜色，再与原片混合，形成叠加：

$$
C_{show}=(1-\alpha)C_{photo}+\alpha C_{label}.
$$

$\alpha$ 只是展示透明度，不是模型分数。颜色表必须固定，并配图注说明语义。原始标签 PNG 与叠加 JPEG 用途不同，定量分析应回到原始标签。

![已有标签叠加图](/notes/internship/media/3540-labels.jpg)

*叠加图让类别边界容易观察，但模型预测仍可能错误。它没有被人工逐像素确认。*

## 3. 深度色彩为什么要解释范围与变换？

道路近处与远处的深度跨度很大，直接线性映射会使近处颜色变化不明显。已有媒体采用一定范围内的对数映射，概念上可以写成：

$$
x=\frac{\log D-\log D_{min}}{\log D_{max}-\log D_{min}}.
$$

再把 $x$ 裁到0–1并送入颜色表。因此相邻颜色不是相差固定一米。超出范围被裁剪的地方，也不表示所有点深度相同。

![已有深度可视化](/notes/internship/media/3540-depth.jpg)

**手算。** 范围若为1到100 m，对数中点对应10 m，而非50.5 m。读深度图时忽略色标，会把颜色距离错误地理解成物理距离。

## 4. 数学公式怎样才能稳定显示？

公式文本使用 LaTeX 语法，由 KaTeX 转成浏览器可排版的 HTML/MathML。公式源码、字体与 CSS 缺一不可；把 `\\`、反斜线或美元符号经过多次字符串转义时，还可能损坏结构。

这套 Astro 笔记使用 `remark-math` 和 `rehype-katex`。正文的块级公式单独使用一行 `$$` 开始、另一行 `$$` 结束，避免公式解析把后面章节吞进去。验收除了查有没有红色错误，还要核对构建后标题、图片和正文是否仍完整。

公式正确渲染只是排版条件。教学还必须先解释每个符号与单位，再给公式；仅仅展示一个矩阵不代表读者知道为什么乘它。

## 5. 阶段切换与搜索，如何保证读者不迷路？

阶段面板的数据嵌在 `app.js` 中，点击后直接同步更新标题、说明和图片，避免依赖额外异步文件才显示内容。章节搜索控制哪些章可见，深链接则打开指定章。

两者组合有一个细节：搜索可能把深链接目标隐藏。因此打开 hash 目标时，要先清理冲突的过滤状态，再展开目标。否则 URL 看起来正确，读者却找不到那一章。

图片采用保持宽高比的布局。把深度图和原图强行拉成固定高度，会让道路透视形状变形，影响读者对几何的判断。

## 6. 服务器职责与访问范围

静态 `serve.py` 负责文件、缓存和必要的 Range 请求。当前服务绑定Tailscale地址，所以读者需要能访问该网络。页面与资源的成功加载应分别检查，首页200不能替代所有图片检查。

已有部署记录使用用户级systemd服务，但用户会话、linger和开机条件会影响启动行为。不能只看“enabled”就承诺任何重启后都必然可用。本篇只确认本次进程与HTTP响应，不改动现有服务。

## 7. 为什么讲解站需要“来源清单”？

每张真实图至少记录源路径、帧号或场景ID、生成方式与哈希。这样未来替换深度模型时，可以知道图是否仍对应旧输出。历史诊断图还需说明是否保留训练母版、相机是否更新。

在实习笔记中，这些信息由[素材来源清单](/notes/internship/media-provenance.json)、[本次读取的素材](/notes/internship/live-media-provenance.json)和[代码索引](/notes/internship/source-index.json)提供。数学示意与教学数字明确标为解释工具，不冒充实验。

<details>
<summary>页面把 RGB、标签、深度三个按钮做出来，能否说明三步算法都已正确？</summary>

不能。它只证明三个资源可以展示。算法正确性还需要核对原始数据、输出定义、版本和独立检查。交互是帮助读者检查证据的工具，不是精度证明。

</details>

## 源码课：从公式回到真实文件

下面是可离线阅读的带行号代码快照。项目调用代码采集于2026-11-09；模型与历史补充文件单独标注日期。源码注释也可能包含旧判断，应与本文核验和实际语句一起读。

| 文件 | 原路径 / 快照 | 长度 |
|---|---|---|
| [app.js](/notes/internship/code/8833-app.js.html) | `2026-11-08 local deployment source` | 17 行 |
| [serve.py](/notes/internship/code/8833-serve.py.html) | `2026-11-08 local deployment source` | 73 行 |

### 关键片段逐句读

这个服务文件负责HTTP资源交付。算法阶段已经离线生成文件，读取页面不会回调SAM、DA3或高斯训练。

原文件定位：[serve.py 第 11 行](/notes/internship/code/8833-serve.py.html#L11)。以下为真实节选，依赖所在文件上下文，不是独立可运行程序。

```python
class Handler(http.server.SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    timeout = 75
    extensions_map = dict(http.server.SimpleHTTPRequestHandler.extensions_map, **{
        ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8", ".js": "text/javascript; charset=utf-8",
        ".json": "application/json; charset=utf-8", ".mp4": "video/mp4", ".webp": "image/webp", ".svg": "image/svg+xml"})

    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def end_headers(self):
        self.send_header("Accept-Ranges", "bytes")
```

[返回专栏总览](/notes/internship-00-overview/) · [下载可编辑图解](/notes/internship/editable-diagrams.zip)
