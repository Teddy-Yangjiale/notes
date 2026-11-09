---
title: "8825：把重建结果做成可核对的项目展示，而不是重新运行算法"
date: 2026-11-09
summary: "区分离线结果生成、对照视频编码、静态 HTTP 服务与页面交互，解释展示页中的每种画面能证明什么，以及如何避免拿不同相机画面做方法比较。"
tags: ["实习", "结果展示", "可复现性"]
series: "internship"
order: 7
shortTitle: "8825：项目展示页面"
---

## 0. 文件夹叫 show8821，服务为什么在 8825？

文件夹名称记录项目历史，监听端口由启动参数决定。当前进程为 `python3 /home/yjl/crack/show8821/serve.py --port 8825`。它是项目说明与结果展示入口，不是另一个训练服务。

这一区分对初学者很重要：点击“播放高斯结果”，通常只是读取已经编码好的视频；点击三维入口，才进入能够根据当前相机重新渲染的查看器；二者都不意味着重新训练了场景。

## 1. 从离线产物到浏览器，要经过哪些步骤？

![8825 结果发布流程](/notes/internship/figures/8825.png)

| 阶段 | 做什么 | 判断是否成功 |
|---|---|---|
| 选取已有场景 | 选择同一位置的点云、道路、高斯或照片 | 场景身份与版本清楚 |
| 生成对照画面 | 固定相机轨迹或截图相机 | 两边视野、位置和时间可对应 |
| 编码媒体 | 把帧序列写成可播放文件 | 时长、帧数、画面尺寸正确 |
| 编排 HTML/JS | 标题、图片、说明、展开项、入口 | 每个结论紧跟证据 |
| HTTP 发送 | `serve.py` 返回页面与媒体 | 资源路径、状态码、Range 请求正确 |

本地已有 `r04_hd.py`、`r06_compare8826.py`、`r07_gaussian8826.py`、`r08_encode_gaussian.py` 等审查副本，可用于追踪已有展示材料的生成过程。它们是历史生成代码，不能因为存在就推断当前网页引用了其中每一个版本。

## 2. 展示三种场景时，应先解释表示差异

照片是一张固定观察位置的像素数组；点云是一组带颜色的三维点；三维高斯是在点附近放置具有方向、大小、透明度与颜色参数的椭球。不同表示的画质和交互条件不同。

![已有高斯留出视角对照拼图](/notes/internship/media/g1_00-sheet_hold.jpg)

*这张图是历史 g1_00 的诊断拼图，用来解释怎样展示对照；不是宣称 8825 当前首页正在使用这张图。历史训练母版缺失且后来位姿更新，不能当作当前版本的真值精度评测。*

如果点云截图看起来稀疏，高斯截图看起来连续，差异可能来自表示与光栅化，也可能来自训练数据、相机、尺度或渲染分辨率。展示页必须给比较条件，不能只写“效果更好”。

## 3. 同一相机为什么是对照的必要条件？

针孔投影为 $u=f_xX/Z+c_x$。同一物体，如果改变焦距、相机位置或裁剪范围，占据的像素就会改变。把近景截图与远景截图并排，会让细节密度产生误导。

对于严格的 A/B 对照，应固定以下元组：

$$
\mathcal C=(T_{cw},K,W,H,\text{crop},\text{time}).
$$

这里 $T_{cw}$ 是相机位姿，$K$ 是内参，$W,H$ 是输出尺寸，`crop` 是裁剪区域，`time` 是所对应观测时刻。模型文件版本另外记录。任何一项变化，都应在图注中说明。

**手算。** 原始宽度 1920 px 的视频显示成 960 px，屏幕上的裂缝宽度减半。这是显示缩放，不是模型失去了二分之一分辨率。因此比较应尽量使用原图裁剪，并注明最终显示尺度。

## 4. 视频编码和三维重建，分别损失什么？

视频编码减少空间和时间冗余，可能模糊细线、产生块效应。它改变的是展示像素；三维重建误差则会随视角变化表现为漂浮、拉伸、重影或遮挡错误。

一个实用检查是同时保留单帧 PNG 与编码视频对应帧。若静态 PNG 清楚而视频模糊，先检查码率、缩放和编码；若二者在侧移视角都出现两层栏杆，才追踪几何、透明度与训练监督。

![同一历史场景的偏移视角诊断拼图](/notes/internship/media/g1_00-sheet_novel.jpg)

*偏移视角没有对应真实相机照片时，只能观察几何症状，不能计算有意义的真值 PSNR。该拼图与上一张不是已控制所有条件的当前线上 A/B 实验。*

## 5. HTTP Range 为什么影响拖动视频？

浏览器跳到视频后半段时，不一定要重新下载整个文件，它会请求一个字节区间。支持 Range 的服务应返回部分内容以及正确范围；页面上的播放失败也可能只是资源传输问题。

这属于交付链而非重建算法。首页返回 200 只说明 HTML 能取到，不说明视频、贴图或 PLY 都完整。验收应分别检查页面、媒体和跳转入口。

## 6. 这类展示页应该怎样写说明？

每幅结果图下至少回答四件事：原始数据是哪一趟、当前画面是哪种表示、用了哪个相机或帧号、这张图能支持哪个结论。若展示的是历史结果，日期与限制也要写在图旁。

这次实习笔记借用了 8825 清楚的章节与配图组织，但正文重新按原理、公式、代码和结果撰写。展示页是一种阅读形式，不能替代算法解释。

<details>
<summary>为什么播放流畅不能证明三维场景能够实时自由浏览？</summary>

预编码视频已经把每一帧算好，播放只需解码。自由视角则需要根据用户此刻的位置实时投影、排序与合成场景。两个任务的计算量和可观察范围都不同。

</details>

## 源码课：从公式回到真实文件

下面是可离线阅读的带行号代码快照。项目调用代码采集于2026-11-09；模型与历史补充文件单独标注日期。源码注释也可能包含旧判断，应与本文核验和实际语句一起读。

| 文件 | 原路径 / 快照 | 长度 |
|---|---|---|
| [serve.py](/notes/internship/code/8825-serve.py.html) | `/home/yjl/crack/show8821/serve.py` | 73 行 |
| [index.html](/notes/internship/code/8825-index.html.html) | `/home/yjl/crack/show8821/site/index.html` | 334 行 |

### 关键片段逐句读

Range 是浏览器请求的字节范围。程序先验证文件与区间，再返回206和内容长度。此处只传已有文件，没有任何模型推理调用。

原文件定位：[serve.py 第 29 行](/notes/internship/code/8825-serve.py.html#L29)。以下为真实节选，依赖所在文件上下文，不是独立可运行程序。

```python
    def send_head(self):
        self._range = None
        rng = self.headers.get("Range"); path = self.translate_path(self.path)
        if not rng or not os.path.isfile(path): return super().send_head()
        m = RANGE.match(rng.strip())
        if not m or (m.group(1) == "" and m.group(2) == ""): return super().send_head()
        try: f = open(path, "rb")
        except OSError: self.send_error(404, "Not found"); return None
        st = os.fstat(f.fileno()); size = st.st_size
        if m.group(1) == "": start, end = max(0, size - int(m.group(2))), size - 1          # 末尾 N 个字节
        else: start = int(m.group(1)); end = min(int(m.group(2)), size - 1) if m.group(2) else size - 1
        if start >= size or start > end:
            f.close(); self.send_response(416); self.send_header("Content-Range", "bytes */%d" % size); self.send_header("Content-Length", "0"); self.end_headers(); return None
        self.send_response(206); self.send_header("Content-Type", self.guess_type(path)); self.send_header("Content-Range", "bytes %d-%d/%d" % (start, end, size))
        self.send_header("Content-Length", str(end - start + 1)); self.send_header("Last-Modified", self.date_time_string(st.st_mtime)); self.end_headers()
        f.seek(start); self._range = end - start + 1; return f

```

[返回专栏总览](/notes/internship-00-overview/) · [下载可编辑图解](/notes/internship/editable-diagrams.zip)
