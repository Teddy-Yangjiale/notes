---
title: "8832：同一份高斯模型，为什么换个浏览器渲染路径就变样？"
date: 2026-11-09
summary: "按 Gaussian Lab 的真实实现讲解共享模型字节、相机同步、Spark/Radix、packed/ext 精度、坐标系、透明度排序与帧间隔统计。"
tags: ["实习", "高斯渲染", "数值精度"]
series: "internship"
order: 14
shortTitle: "8832：Gaussian Lab"
---

## 0. 先确认现在这个端口是什么

当前 8832 运行 `/home/yjl/crack/radix8832/serve.py`，核心页面位于 `site/radix-compare`。它对同一个已有高斯模型比较浏览器渲染路径。旧 `snap1012/p11_raw.py` 注释曾把 8832 分给标定消融，但那不是当前监听服务。

本篇的重点是：**上游模型是否正确**与**浏览器是否忠实显示了模型**必须分开检查。换渲染器可能修复坐标精度或透明度处理，却不能补上录像从未观察到的建筑背面。

## 1. 怎样保证两边真的看同一个模型？

![8832 渲染比较流程](/notes/internship/figures/8832.png)

父页面读取配置、下载场景文件，将同一份文件字节与同步相机状态发送给两个子页面。`viewer.js` 使用 `postMessage` 接收初始化与状态，检查来源是同源父页面。Spark 和 Radix 都从传入的字节解码，而不是各自随便寻找一个同名模型。

配置中的 g1_00 部署记录有 950059 个高斯，模型哈希可回查。文件名相同不够，哈希才检查字节是否相同；但哈希相同仍不保证两套解码后的数值类型一致。

## 2. 相机为什么用完整内参，而不只设置 FOV？

`viewer.js` 从 $f_x,f_y,c_x,c_y$ 构造透视投影矩阵，近面为0.2、远面为1500。主点可能不在图像正中，只设置一个垂直视场角，会忽略偏心主点。

近平面左右上下边界为：

$$
l=-c_xn/f_x,\quad r=(W-c_x)n/f_x,
\quad t=c_yn/f_y,\quad b=-(H-c_y)n/f_y.
$$

$n$ 是近平面距离。这个公式把像素边界沿射线投到近平面，使浏览器投影与真实标定一致。当前比较器输出960×540，并设像素比为1；相机参数仍对应1920×1080的同一视野比例。

坐标变换将 ENU 变成 Three.js 使用的 $(E,U,-N)$。源码对高斯整体施加绕 x 轴 −90° 旋转。高斯朝向与方向颜色也必须使用一致变换，不能只旋转中心。

## 3. packed 与 ext 的差别，为什么会变成米级？

二进制浮点数不是对所有数值都保持同样绝对间隔。对于正规半精度数，某个二进制数量级内的间隔约为：

$$
\operatorname{ULP}(x)=2^{\lfloor\log_2|x|\rfloor-10}.
$$

在1024到2048附近，间隔约1；在2048到4096附近，约2。若坐标单位是米，绝对坐标位于几千米范围时，半精度中心无法稳定保留厘米细节。

**手算。** 2803.2 m 转成间隔2 m的表示，邻近可表示值可能是2802或2804 m，舍入误差可能接近1 m。若先减去局部原点2800 m，剩3.2 m，在这个量级的间隔约0.001953 m，数值精度就完全不同。

这说明局部原点不是美化代码的技巧，而是保护有效位数的必要设计。原点在解码前还是解码后减，也很重要：若小数已经量化丢失，后面再减原点不会恢复它。

## 4. 当前两条实现怎样配置？

Spark 使用 `WebGLRenderer` 和 `SparkRenderer`，`SplatMesh` 的 `extSplats` 由查询参数 `precision=ext` 控制。Radix 使用 `loadSplats(..., {layout:'extSplats'})` 和 `GpuArrays`，并选择 WebGPU 或实际可用的 WebGL2 回退。

因此“Radix 页面打开了”不一定表示正在使用 WebGPU，要读实际后端状态。比较画质也要固定是否采用扩展精度，否则会把数据表示差异误归因于光栅化算法。

## 5. 已有精度诊断实际测了什么？

历史只读诊断对同一 g1_00 文件的解码中心做过表示比较，半精度中心相对高精度解码中心的三维差异中位约0.519 m、95分位约0.960 m。这是**表示造成的坐标差**，不是模型相对真实道路的误差，更不是新实验测得的重建精度。

![该历史场景的偏移视角诊断](/notes/internship/media/g1_00-sheet_novel.jpg)

*这幅图帮助理解几何症状，但不是当前 Spark/Radix 同相机截图。因此不能用它直接给两者排画质名次。本次笔记没有重新跑 GPU 渲染基准。*

压缩 PLY 自己也可能引入分块量化，之后再转 packed 又是另一层表示损失。应分别检查母版→PLY、PLY→解码数组、解码数组→GPU 表示，而不是把所有误差归在“压缩”一个词里。

## 6. 排序与滤波会怎样改变细节？

高斯颜色由近到远进行 alpha 合成，顺序改变会改变遮挡。屏幕滤波还会改变小高斯覆盖范围：滤波太弱可能闪烁，太强可能显得模糊。

当前比较器将色调映射关闭、输出设为 sRGB，并显式设置部分模糊参数，是为了降低显示条件的差异。但相同参数名不必然代表两套实现完全相同的数学运算，仍需要固定场景和像素级对照。

## 7. 页面里的帧间隔，为什么不是纯 GPU 时间？

实现用动画循环相邻时间戳之差记录帧间隔，保留最多600个样本，再报告中位和95分位。这个时间包含浏览器调度、垂直同步和 CPU/GPU 交互，并非严格的 GPU kernel 计时。

若中位间隔16.7 ms，可以近似说显示循环约60 Hz，但不能推断 GPU 恰好耗时16.7 ms。不可见页面、模型仍在加载、相机切换和温度状态都可能影响统计。公平性能测试要固定分辨率、可见性、模型、相机和预热条件。

## 8. 最小诊断顺序

先确认模型字节哈希与相机；再比较 Spark packed 与 Spark ext，把渲染器不变，仅改变表示；然后用 ext 数据比较 Spark 与 Radix；最后才改滤波或投影方法。每步保存同相机截图和数值差，同时观察道路、杆件和遮挡边界。

如果 ext 明显改善近景几何，说明表示精度值得修；如果两者都出现相同漂浮，则返回 8827 检查相机、深度与训练。不要把后端切换当作上游几何修复。

<details>
<summary>把已经半精度量化的中心转换回 float32，能恢复厘米信息吗？</summary>

不能。float32 只能更精确地存储已经舍入后的数值，丢失的小数不会自行回来。必须从较高精度的源数据重新解码，并在合适阶段使用局部坐标。

</details>

## 源码课：从公式回到真实文件

下面是可离线阅读的带行号代码快照。项目调用代码采集于2026-11-09；模型与历史补充文件单独标注日期。源码注释也可能包含旧判断，应与本文核验和实际语句一起读。

| 文件 | 原路径 / 快照 | 长度 |
|---|---|---|
| [viewer.js](/notes/internship/code/8832-viewer.js.html) | `/home/yjl/crack/radix8832/site/radix-compare/viewer.js` | 14 行 |
| [compare.js](/notes/internship/code/8832-compare.js.html) | `/home/yjl/crack/radix8832/site/radix-compare/compare.js` | 22 行 |
| [config.json](/notes/internship/code/8832-config.json.html) | `/home/yjl/crack/radix8832/site/radix-compare/config.json` | 1 行 |

### 关键片段逐句读

同一个父页面状态同步相机位置、四元数与当前方法。若两边相机不一致，就无法把画面差异归因于渲染路径。

原文件定位：[viewer.js 第 4 行](/notes/internship/code/8832-viewer.js.html#L4)。以下为真实节选，依赖所在文件上下文，不是独立可运行程序。

```javascript
function apply(){if(!camera||!state)return;camera.position.fromArray(state.pose.p);camera.quaternion.fromArray(state.pose.q);camera.updateMatrixWorld(true);active=state.active;if(method!==state.method){method=state.method;intervals=[];last=0}if(splatRenderer&&!isSpark)splatRenderer.method=method;}
```

[返回专栏总览](/notes/internship-00-overview/) · [下载可编辑图解](/notes/internship/editable-diagrams.zip)
