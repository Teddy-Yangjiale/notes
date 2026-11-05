# -*- coding: utf-8 -*-
"""CS184 课程笔记 · L08–09（可见性 / 着色 / 管线）原创图解

风格遵循 scripts/cs184-notes-standard.md。
颜色语义：teal=主链路，orange=本讲焦点，purple=数据/材质，red=错误/异常，灰=说明
含 LaTeX 的字符串一律用 r"" 原始字符串。
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Polygon, Circle

plt.rcParams["font.family"] = ["Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

OUT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "src", "content",
                                    "notes", "cs184-08-09-rasterization-shading", "diagrams"))
os.makedirs(OUT, exist_ok=True)
DPI = 200

INK, MUTED = "#16202c", "#5b6b7c"
FILL, STROKE = "#f4f6f9", "#c3ccd6"
TEAL, ORANGE, PURPLE = "#0f766e", "#b45309", "#5b21b6"
BLUE, RED, GREEN = "#1d4ed8", "#b91c1c", "#15803d"


def canvas(w, h, xlim, ylim, eq=True):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim); ax.set_ylim(*ylim)
    ax.axis("off")
    if eq:
        ax.set_aspect("equal")
    return fig, ax


def box(ax, x, y, w, h, text, fc=FILL, ec=STROKE, tc=INK, fs=9.6, lw=1.4,
        pad=0.07, rad=0.13):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle=f"round,pad={pad},rounding_size={rad}",
                                facecolor=fc, edgecolor=ec, linewidth=lw, zorder=3))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            color=tc, zorder=4, linespacing=1.5)


def arrow(ax, p, q, color=TEAL, lw=1.8, ls="-", z=2, ms=13, rad=0.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=ms, color=color,
                                 lw=lw, linestyle=ls, zorder=z,
                                 connectionstyle=f"arc3,rad={rad}",
                                 shrinkA=1, shrinkB=1))


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=DPI, bbox_inches="tight",
                facecolor="white", pad_inches=0.12)
    plt.close(fig)
    print("  ", name)


def sphere(ax, cx, cy, r, base, ka=0.0, kd=1.0, ks=0.0, p=16, ldir=(-0.6, 0.8),
           vdir=(0.0, 1.0), quant=0, blocks=0):
    """局部 Blinn-Phong 上色的球。

    quant>0  把法线方向量化到 quant 段（模拟 flat shading 的逐面法线）
    blocks>0 把着色结果按 blocks×blocks 分块平均（模拟 Gouraud 的逐顶点插值）
    """
    n = 200
    xs = np.linspace(-1, 1, n)
    X, Y = np.meshgrid(xs, xs)
    R2 = X ** 2 + Y ** 2
    inside = R2 <= 1.0
    Z = np.sqrt(np.clip(1 - R2, 0, 1))
    Nx, Ny, Nz = X.copy(), Y.copy(), Z.copy()
    if quant:
        q = 2.0 / quant
        Nx = np.round(Nx / q) * q
        Ny = np.round(Ny / q) * q
        Nz = np.round(Nz / q) * q
        nn = np.sqrt(Nx ** 2 + Ny ** 2 + Nz ** 2) + 1e-9
        Nx, Ny, Nz = Nx / nn, Ny / nn, Nz / nn
    L = np.array([ldir[0], ldir[1], 0.55]); L /= np.linalg.norm(L)
    V = np.array([vdir[0], vdir[1], 0.55]); V /= np.linalg.norm(V)
    H = L + V; H /= np.linalg.norm(H)
    NdL = np.clip(Nx * L[0] + Ny * L[1] + Nz * L[2], 0, None)
    NdH = np.clip(Nx * H[0] + Ny * H[1] + Nz * H[2], 0, None)
    shade = np.clip(ka + kd * NdL + ks * NdH ** p, 0, 1.0)
    if blocks:
        k = max(1, n // blocks)
        for i in range(0, n, k):
            for j in range(0, n, k):
                m = shade[i:i + k, j:j + k]
                shade[i:i + k, j:j + k] = m.mean()
    rgb = np.dstack([base[0] * shade, base[1] * shade, base[2] * shade])
    rgb = np.clip(rgb, 0, 1)
    rgb[~inside] = 1.0
    ax.imshow(rgb, extent=(cx - r, cx + r, cy - r, cy + r), origin="lower", zorder=3)


# ------------------------------------------------- d01 五个阶段
def d01():
    fig, ax = canvas(11.2, 3.4, (0, 11.2), (0, 3.4), eq=False)
    ax.text(0.30, 3.10, "光栅化管线：五个阶段，两种加工对象（顶点 / 片段）", fontsize=10.4,
            color=INK, fontweight="bold")
    stages = [("① Vertex\nProcessing", "顶点", "MVP 变换\n法线变换"),
              ("② Triangle\nProcessing", "三角形", "装配、剔除\n裁剪"),
              ("③ Rasterization", "片段", "覆盖判定\n插值属性"),
              ("④ Fragment\nProcessing", "片段", "纹理查找\n着色计算"),
              ("⑤ Framebuffer\nOperations", "像素", "深度测试\n混合")]
    for i, (name, typ, work) in enumerate(stages):
        x = 0.30 + i * 2.18
        fc = "#fff7ed" if i in (2, 3) else FILL
        box(ax, x, 1.35, 1.85, 1.05, name, fs=9.2, fc=fc, ec=ORANGE if i in (2, 3) else STROKE)
        ax.text(x + 0.92, 1.10, f"对象：{typ}", fontsize=8.4, color=MUTED, ha="center")
        ax.text(x + 0.92, 0.72, work, fontsize=8.2, color=MUTED, ha="center",
                va="top", linespacing=1.5)
        if i < 4:
            arrow(ax, (x + 1.90, 1.88), (x + 2.16, 1.88), color=MUTED, lw=1.3, ms=11)
    ax.text(0.30, 0.22, "前两段加工「顶点/三角形」，后三段加工「片段/像素」—— "
                        "中间那道栅格化就是第 2 讲的采样", fontsize=9.0, color=INK)
    save(fig, "d01-five-stages.png")


# ------------------------------------------------- d02 画家算法
def d02():
    fig, ax = canvas(9.8, 3.4, (0, 9.8), (0, 3.4))
    ax.text(0.30, 3.12, "画家算法：从远到近画，后画的盖住先画的", fontsize=10.4, color=INK,
            fontweight="bold")
    # 三个深度不同的方块，从远到近依次覆盖
    for i, (x, y, s, c, lab) in enumerate([(0.75, 1.55, 1.15, "#cbd5e1", "远景"),
                                           (1.55, 1.30, 1.15, "#94a3b8", "中景"),
                                           (2.45, 1.05, 1.15, "#475569", "近景")]):
        ax.add_patch(Rectangle((x, y), s, s, facecolor=c, ec=INK, lw=1.2, zorder=2 + i))
        ax.text(x + s / 2, y - 0.22, lab, fontsize=8.4, color=MUTED, ha="center")
    for i in range(2):
        arrow(ax, (1.95 + i * 0.85, 0.55), (2.35 + i * 0.85, 0.55), color=MUTED,
              lw=1.2, ms=10)
    ax.text(2.55, 0.28, "绘制顺序", fontsize=8.4, color=MUTED, ha="center")

    box(ax, 4.55, 1.35, 4.85, 1.45,
        "两个问题：\n"
        "① 排序要 O(n log n)，而且 n 有几百万时很贵\n"
        "② 存在「无法排序」的三角形环（下一张图）",
        fs=8.8, fc="#fff7ed", ec=ORANGE, tc="#7c3a00")
    ax.text(4.55, 1.05, "画家算法在图形学里基本只作为「教学对照」存在", fontsize=9.0,
            color=MUTED)
    ax.text(4.55, 0.65, "真正赢的是 z-buffer：O(n)、无序、硬件实现", fontsize=9.0, color=TEAL)
    save(fig, "d02-painter.png")


# ------------------------------------------------- d03 无法排序的循环遮挡
def d03():
    fig, ax = canvas(9.4, 3.6, (0, 9.4), (0, 3.6))
    ax.text(0.30, 3.34, "循环遮挡：三个三角形两两互相遮挡，任何顺序都错", fontsize=10.4,
            color=INK, fontweight="bold")
    A = np.array([[0.55, 0.70], [2.55, 1.35], [1.15, 2.55]])
    B = np.array([[2.15, 0.65], [3.75, 2.05], [2.05, 2.65]])
    C = np.array([[1.10, 1.45], [2.85, 1.05], [2.20, 2.95]])
    for tri, col, lab, pos in [(A, TEAL, "A", (0.95, 0.95)),
                               (B, ORANGE, "B", (3.45, 0.95)),
                               (C, PURPLE, "C", (2.35, 2.20))]:
        ax.add_patch(Polygon(tri, closed=True, facecolor=col, alpha=0.22, ec=col, lw=1.6))
        ax.text(pos[0], pos[1], lab, fontsize=11, color=col, fontweight="bold",
                ha="center")
    ax.text(4.55, 2.55, "遮挡关系：", fontsize=9.6, color=INK)
    ax.text(4.55, 2.15, "A 挡住 B 的一部分", fontsize=9.0, color=MUTED)
    ax.text(4.55, 1.80, "B 挡住 C 的一部分", fontsize=9.0, color=MUTED)
    ax.text(4.55, 1.45, "C 挡住 A 的一部分", fontsize=9.0, color=MUTED)
    ax.text(4.55, 0.95, "⇒ 不是全序，排序无解", fontsize=9.6, color=RED, fontweight="bold")
    ax.text(4.55, 0.50, "解法：z-buffer（逐像素记最小深度，不需要任何全局顺序）；\n"
                        "或者 BSP 树（递归切分空间，得到一个可用的顺序）",
            fontsize=8.8, color=INK, va="top", linespacing=1.6)
    save(fig, "d03-cyclic-overlap.png")


# ------------------------------------------------- d04 z-buffer
def d04():
    fig, ax = canvas(10.0, 4.2, (0, 10.0), (0, 4.2), eq=False)
    ax.text(0.30, 3.94, "z-buffer：逐像素记住「目前最近的那个深度」", fontsize=10.4,
            color=INK, fontweight="bold")
    # 左：两个三角形
    ax.add_patch(Polygon([[0.50, 2.60], [2.85, 2.60], [0.50, 1.05]], closed=True,
                         facecolor=TEAL, alpha=0.28, ec=TEAL, lw=1.5))
    ax.add_patch(Polygon([[1.35, 2.05], [3.55, 2.05], [3.55, 1.05], [1.35, 1.05]],
                         closed=True, facecolor=ORANGE, alpha=0.24, ec=ORANGE, lw=1.5))
    ax.text(1.20, 2.72, "三角形 A（远处，z=5）", fontsize=8.6, color=TEAL)
    ax.text(2.05, 0.82, "三角形 B（近处，z=2）", fontsize=8.6, color=ORANGE)
    for i in range(6):
        for j in range(4):
            ax.add_patch(Rectangle((0.50 + i * 0.42, 1.05 + j * 0.34), 0.42, 0.34,
                                   fill=False, ec="#cbd5e1", lw=0.6))

    # 右：深度缓冲两张表
    ax.text(4.35, 3.05, "先画 A（z=5）", fontsize=9.0, color=TEAL)
    ax.text(6.75, 3.05, "再画 B（z=2）", fontsize=9.0, color=ORANGE)
    for k, x0 in enumerate((4.35, 6.75)):
        for i in range(3):
            for j in range(2):
                ax.add_patch(Rectangle((x0 + i * 0.72, 1.55 + j * 0.62), 0.72, 0.62,
                                       facecolor="white", ec=MUTED, lw=0.9))
        for (i, j, val) in [(0, 0, "5"), (1, 0, "5"), (0, 1, "5"),
                            (1, 1, "2" if k else "5"), (2, 1, "2" if k else "∞")]:
            ax.text(x0 + i * 0.72 + 0.36, 1.55 + j * 0.62 + 0.31, val, fontsize=9.0,
                    color=(ORANGE if (k and val == "2") else INK), ha="center", va="center")
    ax.text(4.35, 1.25, "无覆盖处保持 ∞", fontsize=7.8, color=MUTED)
    box(ax, 4.35, 0.35, 5.30, 0.65,
        "测试：if (z < zbuffer[x,y]) { 写颜色; zbuffer = z; } else 丢弃",
        fs=8.8, fc="#e6f7f4", ec=TEAL, tc=TEAL)
    ax.text(0.30, 0.55, "关键是：这个算法", fontsize=9.0, color=INK)
    ax.text(0.30, 0.22, "不需要任何三角形排序", fontsize=9.6, color=RED, fontweight="bold")
    save(fig, "d04-zbuffer.png")


# ------------------------------------------------- d05 三个分量
def d05():
    fig, ax = canvas(10.2, 3.0, (0, 10.2), (0, 3.0), eq=False)
    ax.text(0.30, 2.76, "Blinn-Phong 把「看到的光」拆成三项：环境 + 漫反射 + 高光",
            fontsize=10.2, color=INK, fontweight="bold")
    base = (0.35, 0.55, 0.95)
    sphere(ax, 1.05, 1.30, 0.72, base, ka=0.35, kd=0.0, ks=0.0)
    ax.text(1.05, 0.35, "环境 $k_a I_a$", fontsize=8.6, color=MUTED, ha="center")
    ax.text(1.70, 1.30, "+", fontsize=16, color=MUTED, ha="center", va="center")

    sphere(ax, 3.05, 1.30, 0.72, base, ka=0.0, kd=1.0, ks=0.0)
    ax.text(3.05, 0.35, "漫反射 $k_d(I/r^2)\\max(0,n\\cdot l)$", fontsize=8.6,
            color=MUTED, ha="center")
    ax.text(3.70, 1.30, "+", fontsize=16, color=MUTED, ha="center", va="center")

    sphere(ax, 5.05, 1.30, 0.72, (1.0, 1.0, 1.0), ka=0.0, kd=0.0, ks=1.0, p=40)
    ax.text(5.05, 0.35, "高光 $k_s(I/r^2)\\max(0,n\\cdot h)^p$", fontsize=8.6,
            color=MUTED, ha="center")
    ax.text(5.70, 1.30, "=", fontsize=16, color=MUTED, ha="center", va="center")

    sphere(ax, 7.05, 1.30, 0.72, base, ka=0.3, kd=0.85, ks=0.8, p=40)
    ax.text(7.05, 0.35, "合起来 = 材质外观", fontsize=8.6, color=INK, ha="center",
            fontweight="bold")
    ax.text(8.25, 1.85, "三项都是「局部」的", fontsize=9.4, color=INK)
    ax.text(8.25, 1.50, "• 只看这一点的 $n,l,v$", fontsize=8.6, color=MUTED)
    ax.text(8.25, 1.18, "• 不考虑别的物体挡光", fontsize=8.6, color=MUTED)
    ax.text(8.25, 0.86, "• 不考虑别的物体反光", fontsize=8.6, color=MUTED)
    ax.text(8.25, 0.45, "所以叫「局部着色模型」", fontsize=9.0, color=RED)
    save(fig, "d05-three-components.png")


# ------------------------------------------------- d06 Lambert
def d06():
    fig, ax = canvas(9.6, 3.4, (0, 9.6), (0, 3.4))
    ax.text(0.30, 3.12, "Lambert 余弦定律：入射光按 $\\cos\\theta$ 摊到更大的面积上",
            fontsize=10.4, color=INK, fontweight="bold")
    # 左：正对
    for k in range(6):
        ax.plot([0.70 + k * 0.20, 0.70 + k * 0.20], [2.45, 1.80], color=ORANGE, lw=1.4)
    ax.add_patch(Rectangle((0.62, 1.15), 1.10, 0.62, facecolor="#dbeafe", ec=BLUE, lw=1.3))
    ax.text(1.17, 0.92, "正对：全部接住", fontsize=8.8, color=MUTED, ha="center")
    ax.text(1.17, 2.62, "$\\theta = 0$", fontsize=9.2, color=ORANGE, ha="center")

    # 中：倾斜 60°
    ang = np.radians(60)
    for k in range(6):
        ax.plot([3.10 + k * 0.20, 3.10 + k * 0.20], [2.45, 1.80], color=ORANGE, lw=1.4)
    cx, cy, w, h = 3.62, 1.46, 1.10, 0.62
    c, s = np.cos(ang), np.sin(ang)
    R = np.array([[c, -s], [s, c]])
    corners = np.array([[-w / 2, -h / 2], [w / 2, -h / 2], [w / 2, h / 2], [-w / 2, h / 2]])
    ax.add_patch(Polygon(corners @ R.T + [cx, cy], closed=True, facecolor="#dbeafe",
                         ec=BLUE, lw=1.3))
    # 只画落在板上的那部分光线
    for k in range(3):
        ax.plot([3.10 + k * 0.20, 3.10 + k * 0.20], [2.45, 1.80], color=ORANGE, lw=1.4)
    ax.text(3.62, 0.92, "倾斜 60°：只接住一半", fontsize=8.8, color=MUTED, ha="center")
    ax.text(3.62, 2.62, "$\\theta = 60°$", fontsize=9.2, color=ORANGE, ha="center")

    ax.text(5.55, 2.30, "照到板上的光通量恒定，但板被「照亮」的强度是", fontsize=9.0,
            color=INK)
    ax.text(5.55, 1.85, r"$E = E_0 \cos\theta = E_0\,(l\cdot n)$", fontsize=11, color=TEAL)
    ax.text(5.55, 1.30, "所以斜着放，单位面积收到的光只剩一半", fontsize=9.0, color=MUTED)
    box(ax, 5.55, 0.55, 3.75, 0.62, "这就是 max(0, n·l) 的来源", fs=9.0,
        fc="#e6f7f4", ec=TEAL, tc=TEAL)
    save(fig, "d06-lambert.png")


# ------------------------------------------------- d07 半角向量
def d07():
    fig, ax = canvas(9.4, 3.6, (0, 9.4), (0, 3.6))
    ax.text(0.30, 3.34, "为什么用半角向量 h：镜面反射方向不好算，h 好算", fontsize=10.4,
            color=INK, fontweight="bold")
    P = np.array([1.55, 1.05])
    N = np.array([0.0, 1.0])
    L = np.array([-0.72, 0.69]); L /= np.linalg.norm(L)
    V = np.array([0.55, 0.83]); V /= np.linalg.norm(V)
    H = L + V; H /= np.linalg.norm(H)
    R = 2 * (L @ N) * N - L
    ax.plot([0.35, 2.85], [1.05, 1.05], color=INK, lw=1.4)
    arrow(ax, tuple(P), tuple(P + N * 1.1), color=INK, lw=1.6)
    ax.text(*(P + N * 1.16), "$n$", fontsize=10, color=INK, ha="center")
    arrow(ax, tuple(P), tuple(P + L * 1.15), color=ORANGE, lw=1.8)
    ax.text(*(P + L * 1.22), "$l$（指向光源）", fontsize=9.0, color=ORANGE)
    arrow(ax, tuple(P), tuple(P + V * 1.15), color=TEAL, lw=1.8)
    ax.text(*(P + V * 1.22), "$v$（指向眼睛）", fontsize=9.0, color=TEAL)
    arrow(ax, tuple(P), tuple(P + H * 1.15), color=RED, lw=2.0, ls=(0, (4, 2)))
    ax.text(*(P + H * 1.20), "$h$", fontsize=10, color=RED, fontweight="bold")
    arrow(ax, tuple(P), tuple(P + R * 1.0), color="#94a3b8", lw=1.3, ls=(0, (3, 3)))
    ax.text(*(P + R * 1.05), "$r$（镜面反射）", fontsize=8.6, color=MUTED)

    ax.text(4.45, 2.75, r"$h = \dfrac{v+l}{\|v+l\|}$", fontsize=12, color=RED)
    ax.text(4.45, 2.10, "h 是 v 与 l 的角平分线方向", fontsize=9.0, color=INK)
    ax.text(4.45, 1.70, "镜面反射成立 ⟺ r 与 v 重合 ⟺ h 与 n 重合", fontsize=9.0,
            color=INK)
    ax.text(4.45, 1.20, r"所以用 $\max(0, n\cdot h)^p$ 代替 $\max(0, r\cdot v)^p$", fontsize=9.6,
            color=TEAL)
    ax.text(4.45, 0.72, "好处：h 只要一次向量加法 + 归一化，不用算反射方向 r", fontsize=8.8,
            color=MUTED)
    ax.text(4.45, 0.36, "代价：h·n 与 r·v 不完全等价（掠射角误差变大）—— 这就是 Blinn 对 Phong 的改进",
            fontsize=8.6, color=ORANGE)
    save(fig, "d07-half-vector.png")


# ------------------------------------------------- d08 高光叶瓣
def d08():
    fig, ax = canvas(9.8, 3.2, (0, 9.8), (0, 3.2), eq=False)
    ax.text(0.30, 2.96, "$p$ 越大，高光叶瓣越窄（高光越「锐」）", fontsize=10.4, color=INK,
            fontweight="bold")
    th = np.linspace(-np.pi / 2, np.pi / 2, 500)
    for p, c, dy in [(1, "#94a3b8", 0.0), (4, TEAL, 0.0), (16, ORANGE, 0.0),
                     (64, PURPLE, 0.0)]:
        y = np.clip(np.cos(th), 0, None) ** p
        ax.plot(0.95 + 2.05 * (th / (np.pi / 2)), 0.75 + 1.55 * y, color=c, lw=1.8)
        ax.text(3.12, 0.75 + 1.55 * float(np.clip(np.cos(0), 0, 1) ** 0) + dy,
                "", fontsize=1)
    for p, c, yy in [(1, "#94a3b8", 2.30), (4, TEAL, 1.95), (16, ORANGE, 1.60),
                     (64, PURPLE, 1.25)]:
        ax.text(3.20, yy, f"$p={p}$", fontsize=8.8, color=c, va="center")
    ax.text(1.98, 0.46, "角度 α（$n$ 与 $h$ 的夹角）", fontsize=8.6, color=MUTED, ha="center")
    ax.text(1.98, 2.52, "$\\cos^p\\alpha$", fontsize=10.5, color=INK, ha="center")
    ax.text(4.05, 2.85, "p 的物理意义：材质「光滑程度」", fontsize=9.2, color=INK)
    ax.text(4.05, 2.42, "p 小（1~4）：粗糙哑光，高光一大片", fontsize=8.8, color=MUTED)
    ax.text(4.05, 2.10, "p 大（100+）：光滑金属，高光是个点", fontsize=8.8, color=MUTED)
    ax.text(4.05, 1.55, "$p$ 与粗糙度非线性：$p \\approx 2/\\alpha^2$ 更接近物理模型",
            fontsize=9.0, color=ORANGE)
    ax.text(4.05, 1.05, "实际渲染里 p 常取 1~1000，", fontsize=8.8, color=MUTED)
    ax.text(4.05, 0.75, "也可以做成一张纹理（第 6 讲的粗糙度贴图）", fontsize=8.8, color=MUTED)
    save(fig, "d08-specular-lobe.png")


# ------------------------------------------------- d09 光强衰减
def d09():
    fig, ax = canvas(9.4, 3.2, (0, 9.4), (0, 3.2), eq=False)
    ax.text(0.30, 2.96, "光强随距离衰减：物理上是 $1/r^2$，工程上常用 $1/r$", fontsize=10.4,
            color=INK, fontweight="bold")
    r = np.linspace(0.6, 4.0, 400)
    ax.plot(0.9 + 1.55 * r, 0.75 + 1.55 / r ** 2, color=ORANGE, lw=2.0)
    ax.plot(0.9 + 1.55 * r, 0.75 + 1.55 / r, color=TEAL, lw=2.0)
    ax.text(4.05, 1.55, "$1/r^2$（物理正确）", fontsize=9.0, color=ORANGE)
    ax.text(4.05, 1.15, "$1/r$（折中）", fontsize=9.0, color=TEAL)
    ax.text(2.55, 0.45, "距离 r", fontsize=8.6, color=MUTED, ha="center")
    ax.text(2.55, 2.70, "强度", fontsize=8.6, color=MUTED, ha="center")
    ax.text(4.35, 2.30, "为什么 $1/r^2$ 配局部着色会难看", fontsize=9.4, color=INK)
    ax.text(4.35, 1.95, "• 近处过曝（$r\\to 0$ 时炸到无穷）", fontsize=8.8, color=MUTED)
    ax.text(4.35, 1.62, "• 远处立刻全黑，看不出环境反射", fontsize=8.8, color=MUTED)
    ax.text(4.35, 1.28, "• 而真实的「远处不黑」来自间接光 —— 局部模型没有", fontsize=8.8,
            color=MUTED)
    ax.text(4.35, 0.75, "所以局部着色里常改用 $1/r$、或加常数项、或干脆用平行光", fontsize=9.0,
            color=TEAL)
    ax.text(4.35, 0.38, "但做全局光照（L16–17）时必须回到 $1/r^2$，否则能量不守恒", fontsize=8.8,
            color=RED)
    save(fig, "d09-falloff.png")


# ------------------------------------------------- d10 着色频率
def d10():
    fig, ax = canvas(10.4, 3.6, (0, 10.4), (0, 3.6), eq=False)
    ax.text(0.30, 3.32, "三种着色频率：差别在「每一步插值的是什么」", fontsize=10.4,
            color=INK, fontweight="bold")
    rows = [("Flat（逐面）", "每个三角形一个法线", "$n$：不变，整个面同色", "#cbd5e1"),
            ("Gouraud（逐顶点）", "顶点算法线光照，插颜色", "$c$：插颜色，法线不插", TEAL),
            ("Phong（逐像素）", "插法线，每个像素重算光照", "$n$：插法线，再算光照", ORANGE)]
    for i, (name, how, what, c) in enumerate(rows):
        y = 2.55 - i * 0.85
        ax.text(0.30, y, name, fontsize=9.6, color=c if c != "#cbd5e1" else INK,
                fontweight="bold")
        ax.text(2.45, y, how, fontsize=8.8, color=MUTED)
        ax.text(6.55, y, what, fontsize=8.8, color=INK)
    # 右边：三条插值示意
    for k, (yy, col) in enumerate([(2.55, "#94a3b8"), (1.70, TEAL), (0.85, ORANGE)]):
        xs = np.linspace(8.55, 10.05, 60)
        if k == 0:
            ax.plot(xs, np.full_like(xs, yy), color=col, lw=2.4)
        elif k == 1:
            ax.plot(xs, yy + 0.16 * np.sin((xs - 8.55) / 1.5 * np.pi), color=col, lw=2.4)
        else:
            ax.plot(xs, yy + 0.16 * np.sin((xs - 8.55) / 1.5 * np.pi * 2), color=col, lw=2.4)
    ax.text(0.30, 0.42, "注意命名陷阱：这里的 Phong 指「逐像素着色」（Phong shading），"
                        "和反射模型里的 Phong（= Blinn-Phong 的前身）不是一回事", fontsize=8.8,
            color=RED)
    ax.text(0.30, 0.12, "三者代价递增：flat 最便宜（每面一次），Phong 最贵（每像素一次光照计算）",
            fontsize=8.8, color=MUTED)
    save(fig, "d10-shading-frequency.png")


# ------------------------------------------------- d11 粗网格上的高光
def d11():
    fig, ax = canvas(10.2, 3.4, (0, 10.2), (0, 3.4), eq=False)
    ax.text(0.30, 3.12, "同一个低面数球：平直/顶点/像素三种着色频率", fontsize=10.2,
            color=INK, fontweight="bold")
    base = (0.92, 0.92, 0.95)
    sphere(ax, 1.45, 1.55, 0.85, base, ka=0.15, kd=0.75, ks=0.9, p=60, quant=6)
    sphere(ax, 4.10, 1.55, 0.85, base, ka=0.15, kd=0.75, ks=0.9, p=60, blocks=26)
    sphere(ax, 6.75, 1.55, 0.85, base, ka=0.15, kd=0.75, ks=0.9, p=60)
    for x, name, col, note in [(1.45, "Flat", "#6b7280", "每个面一个法线\n高光整块亮或整块没有"),
                               (4.10, "Gouraud", TEAL, "顶点算法线再插颜色\n高光被摊平"),
                               (6.75, "Phong", ORANGE, "插法线再逐像素算\n高光是圆的")]:
        ax.text(x, 0.55, name, fontsize=9.6, color=col, ha="center", fontweight="bold")
        ax.text(x, 0.22, note, fontsize=7.8, color=MUTED, ha="center", linespacing=1.5,
                va="top")
    ax.text(8.35, 2.10, "差别最大的是", fontsize=9.0, color=INK)
    ax.text(8.35, 1.80, "高光的形状", fontsize=9.4, color=RED, fontweight="bold")
    ax.text(8.35, 1.35, "低面数时 flat\n整块面全白，\nGouraud 糊成一片", fontsize=8.2,
            color=MUTED, va="top", linespacing=1.5)
    save(fig, "d11-shading-artifact.png")


# ------------------------------------------------- d12 顶点法线平均
def d12():
    fig, ax = canvas(9.6, 3.4, (0, 9.6), (0, 3.4))
    ax.text(0.30, 3.12, "顶点法线：把相邻面的法线加权平均", fontsize=10.4, color=INK,
            fontweight="bold")
    # 左：一个顶点 + 四个面
    P = np.array([1.62, 1.42])
    angs = [0, 65, 130, 200, 265]
    for i in range(4):
        a0, a1 = np.radians(angs[i]), np.radians(angs[i + 1])
        ax.add_patch(Polygon([P,
                              P + 0.95 * np.array([np.cos(a0), np.sin(a0)]),
                              P + 1.15 * np.array([np.cos((a0 + a1) / 2), np.sin((a0 + a1) / 2)]),
                              P + 0.95 * np.array([np.cos(a1), np.sin(a1)])],
                             closed=True, facecolor="#e0f2fe", ec=BLUE, lw=1.0))
        arrow(ax, tuple(P), tuple(P + 0.72 * np.array([np.cos((a0 + a1) / 2),
                                                       np.sin((a0 + a1) / 2)])),
              color=BLUE, lw=1.2, ms=9)
    arrow(ax, tuple(P), tuple(P + np.array([0.0, 0.95])), color=RED, lw=2.2)
    ax.plot(*P, "o", ms=5, color=INK, zorder=6)
    ax.text(P[0] + 0.05, P[1] + 1.02, "平均后的 $N_v$", fontsize=9.0, color=RED)
    ax.text(1.62, 0.42, "四个面法线加权平均", fontsize=8.8, color=MUTED, ha="center")

    ax.text(3.60, 2.60, r"$N_v = \dfrac{\sum_i w_i N_i}{\sum_i w_i}$", fontsize=12,
            color=INK)
    ax.text(3.60, 1.95, "权重的常见选择：", fontsize=9.2, color=INK)
    ax.text(3.60, 1.62, "• 等权 $w_i = 1$：最简单，但大面占优不够", fontsize=8.8, color=MUTED)
    ax.text(3.60, 1.30, "• 按面积、或按夹角：更符合几何", fontsize=8.8, color=MUTED)
    ax.text(3.60, 0.90, "更好的做法：直接从底层几何（如球面参数）取法线，", fontsize=9.0,
            color=TEAL)
    ax.text(3.60, 0.58, "而不是从三角面反推 —— 这样才真正「光滑」", fontsize=9.0, color=TEAL)
    box(ax, 7.10, 1.35, 2.30, 1.25, "尖锐的边（sharp edge）\n不要平均！\n否则倒角会被抹圆",
        fs=8.6, fc="#fff7ed", ec=ORANGE, tc="#7c3a00")
    save(fig, "d12-vertex-normal.png")


# ------------------------------------------------- d13 法线变换
def d13():
    fig, ax = canvas(9.8, 3.6, (0, 9.8), (0, 3.6))
    ax.text(0.30, 3.34, "法线不能用 $M$ 变换，要用 $M^{-T}$（逆转置）", fontsize=10.4,
            color=INK, fontweight="bold")
    # 原始：正方形 + 法线
    for k, (ox, label, shear, col) in enumerate([(0.45, "原始", 0.0, MUTED),
                                                 (3.15, "用 $M$ 变换法线", 0.9, RED),
                                                 (6.20, "用 $M^{-T}$", 0.9, GREEN)]):
        h = 0.70
        w = 0.95
        pts = np.array([[0, 0], [w, 0], [w + shear * h, h], [shear * h, h]])
        ax.add_patch(Polygon(pts + [ox, 1.30], closed=True, facecolor="#e2e8f0",
                             ec=MUTED, lw=1.3))
        if k == 0:
            arrow(ax, (ox + w / 2, 1.30 + h), (ox + w / 2, 2.45), color=col, lw=1.8)
            ax.text(ox + w / 2 + 0.10, 2.52, "法线", fontsize=8.4, color=col)
        elif k == 1:
            # 用 M 变换：法线跟着错切，不再垂直于面
            arrow(ax, (ox + w / 2 + shear * h, 1.30 + h),
                  (ox + w / 2 + shear * h + 0.62, 2.45), color=col, lw=1.8)
            ax.text(ox + w / 2 + shear * h + 0.68, 2.40, "偏了", fontsize=8.6, color=col)
        else:
            arrow(ax, (ox + w / 2 + shear * h, 1.30 + h),
                  (ox + w / 2 + shear * h - 0.52, 2.45), color=col, lw=1.8)
            ax.text(ox + w / 2 + shear * h - 0.92, 2.40, "正确", fontsize=8.6, color=col)
        ax.text(ox + 0.55, 0.95, label, fontsize=9.0, color=col, ha="center")
    ax.text(0.45, 0.52, "为什么：法线是「垂直于切平面的余向量」，不是普通向量。"
                        "切向 $t$ 用 $M$ 变换后，$n$ 必须用 $M^{-T}$ 才能继续保持 $t\\cdot n = 0$",
            fontsize=8.8, color=INK)
    ax.text(0.45, 0.22, "常见触发条件：非均匀缩放、错切。纯旋转时 $M^{-T} = M$，所以很多 demo 里看不出问题",
            fontsize=8.8, color=RED)
    save(fig, "d13-normal-transform.png")


# ------------------------------------------------- d14 透明排序
def d14():
    fig, ax = canvas(10.0, 3.2, (0, 10.0), (0, 3.2))
    ax.text(0.30, 2.94, "透明度必须「从远到近」混，否则结果错", fontsize=10.4, color=INK,
            fontweight="bold")
    for i, (ox, order, ok) in enumerate([(0.55, ["opaque", "opaque", "alpha"], True),
                                         (5.15, ["alpha", "opaque", "opaque"], False)]):
        for k in range(3):
            ax.add_patch(Rectangle((ox + k * 0.85, 1.10), 0.75, 1.10,
                                   facecolor=(TEAL if order[k] == "opaque" else ORANGE),
                                   alpha=(1.0 if order[k] == "opaque" else 0.45),
                                   ec=INK, lw=1.0, zorder=2 + k))
        ax.text(ox + 1.20, 2.35, "从远到近" if ok else "从近到远", fontsize=8.8,
                color=GREEN if ok else RED, ha="center")
        ax.text(ox + 1.20, 0.82, "✓ 正确" if ok else "✗ 错误（半透明盖不住后面的）",
                fontsize=8.8, color=GREEN if ok else RED, ha="center")
        for k, lbl in enumerate(order):
            ax.text(ox + k * 0.85 + 0.37, 0.55, lbl[:5], fontsize=7.4, color=MUTED,
                    ha="center")
    ax.text(0.30, 0.22, "z-buffer 只能留下「最近的一个」，而半透明需要「把沿途所有颜色按权重累加」—— "
                        "所以要么排序，要么用深度剥离 / A-buffer", fontsize=8.8, color=MUTED)
    save(fig, "d14-transparency.png")


# ------------------------------------------------- d15 shadow map
def d15():
    fig, ax = canvas(10.0, 3.4, (0, 10.0), (0, 3.4), eq=False)
    ax.text(0.30, 3.14, "阴影贴图：从光源视角先存一张深度图，再从相机视角比较", fontsize=10.4,
            color=INK, fontweight="bold")
    ax.text(0.30, 2.68, "① 从光源渲染，只留深度", fontsize=9.2, color=ORANGE)
    box(ax, 0.45, 1.55, 2.35, 0.95, "光源视角\n深度图（shadow buffer）", fs=8.8,
        fc="#fff7ed", ec=ORANGE, tc="#7c3a00")
    arrow(ax, (2.95, 2.02), (3.55, 2.02), color=MUTED, lw=1.4)
    ax.text(3.25, 2.22, "复用", fontsize=8.0, color=MUTED, ha="center")
    ax.text(3.68, 2.68, "② 从相机渲染，逐像素比较", fontsize=9.2, color=TEAL)
    box(ax, 3.68, 1.55, 2.55, 0.95, "相机视角\n该点到光源的距离 $d$", fs=8.8,
        fc="#e6f7f4", ec=TEAL, tc=TEAL)
    ax.text(6.45, 2.15, "$d >$ 深度图里的值 ⇒ 被挡 ⇒ 阴影", fontsize=9.0, color=INK)
    ax.text(6.45, 1.75, "$d \\leq$ 深度图里的值 ⇒ 可见 ⇒ 加光照", fontsize=9.0, color=INK)
    ax.text(6.45, 1.20, "经典问题：自阴影痤疮（shadow acne）", fontsize=8.8, color=RED)
    ax.text(6.45, 0.88, "因为离散深度有误差，表面会自己遮住自己，", fontsize=8.4, color=MUTED)
    ax.text(6.45, 0.62, "解法：加偏移（bias）、法线偏移、或用斜率缩放", fontsize=8.4, color=MUTED)
    ax.text(0.45, 1.15, "本质：shadow map 是「把可见性问题再算一遍」，", fontsize=8.8, color=MUTED)
    ax.text(0.45, 0.85, "只不过换成「从光源看谁在前」", fontsize=8.8, color=MUTED)
    ax.text(0.45, 0.42, "所以 z-buffer 那一套能直接复用 —— 这是本讲最漂亮的复用", fontsize=9.0,
            color=TEAL)
    save(fig, "d15-shadow-map.png")


# ------------------------------------------------- d16 BRDF
def d16():
    fig, ax = canvas(9.6, 3.4, (0, 9.6), (0, 3.4))
    ax.text(0.30, 3.14, "BRDF：给定入射方向和出射方向，返回「多少光被反射过去」", fontsize=10.4,
            color=INK, fontweight="bold")
    P = np.array([1.70, 1.05])
    ax.plot([0.45, 2.95], [1.05, 1.05], color=INK, lw=1.4)
    arrow(ax, tuple(P), tuple(P + np.array([0.0, 1.15])), color=INK, lw=1.5)
    ax.text(P[0] + 0.06, P[1] + 1.20, "$n$", fontsize=9.6, color=INK)
    for k in range(7):
        a = np.radians(150 - k * 20)
        c = TEAL if k % 2 == 0 else "#94a3b8"
        arrow(ax, tuple(P), tuple(P + 1.05 * np.array([np.cos(a), np.sin(a)])),
              color=c, lw=1.2, ms=9)
    ax.text(0.55, 2.15, "入射方向 $l$（可来自半球任意方向）", fontsize=8.6, color=TEAL)
    for k in range(7):
        a = np.radians(35 + k * 17)
        arrow(ax, tuple(P), tuple(P + 0.85 * np.array([np.cos(a), np.sin(a)])),
              color=ORANGE, lw=1.0, ms=8)
    ax.text(2.55, 1.70, "出射方向 $v$", fontsize=8.6, color=ORANGE)
    ax.plot(*P, "o", ms=5, color=INK, zorder=6)
    ax.text(1.70, 0.62, "着色点", fontsize=8.6, color=MUTED, ha="center")

    ax.text(4.35, 2.55, r"$\rho(v, l, n)$", fontsize=13, color=INK)
    ax.text(4.35, 1.95, "它是一个四维函数（两个方向各二维）", fontsize=9.0, color=INK)
    ax.text(4.35, 1.62, "Blinn-Phong 就是其中一个「手工设计」的 BRDF", fontsize=9.0,
            color=TEAL)
    ax.text(4.35, 1.20, "更真实的模型要考虑：", fontsize=9.0, color=INK)
    ax.text(4.35, 0.92, "• 各向异性（拉丝金属）• 菲涅耳（掠射变亮）", fontsize=8.4, color=MUTED)
    ax.text(4.35, 0.64, "• 能量守恒 • 次表面散射（BRDF 描述不了）", fontsize=8.4, color=MUTED)
    ax.text(4.35, 0.28, "所以讲义引了 Ashikhmin-Shirley 和实测 BRDF —— 这条线一直通到 L16–17",
            fontsize=8.6, color=ORANGE)
    save(fig, "d16-brdf.png")


if __name__ == "__main__":
    print("generating ->", OUT)
    for fn in [d01, d02, d03, d04, d05, d06, d07, d08,
               d09, d10, d11, d12, d13, d14, d15, d16]:
        fn()
    print("done: 16 diagrams")
