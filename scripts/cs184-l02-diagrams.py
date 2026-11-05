# -*- coding: utf-8 -*-
"""CS184 课程笔记 · 原创图解生成器

风格约定（对齐 camera-calibration 那篇的图解语言）
--------------------------------------------------
1. 一个概念一张图；图里不放坐标轴、刻度、图例框、标题
2. 用圆角矩形 + 箭头 + 少量象形元素表达"关系"，而不是画数据
3. 颜色只做分组：teal=主链路/内侧，orange=本讲焦点，purple=数据形态，red=异常/错误
4. 图注写在正文里（斜体），不画进图

用法
----
    python cs184-l02-diagrams.py            # 生成 L02 的 14 张图
输出目录：src/content/notes/cs184-02-drawing-triangles/diagrams/
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import (FancyBboxPatch, FancyArrowPatch, Rectangle,
                                Polygon, Circle)

plt.rcParams["font.family"] = ["Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

OUT = os.path.join(os.path.dirname(__file__), "..", "src", "content", "notes",
                   "cs184-02-drawing-triangles", "diagrams")
OUT = os.path.normpath(OUT)
os.makedirs(OUT, exist_ok=True)
DPI = 200

INK, MUTED = "#16202c", "#5b6b7c"
FILL, STROKE = "#f4f6f9", "#c3ccd6"
TEAL, ORANGE, PURPLE = "#0f766e", "#b45309", "#5b21b6"
BLUE, RED, GREEN = "#1d4ed8", "#b91c1c", "#15803d"


# ----------------------------------------------------------------- 公共
def canvas(w, h, xlim, ylim):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axis("off")
    ax.set_aspect("equal")
    return fig, ax


def box(ax, x, y, w, h, text, fc=FILL, ec=STROKE, tc=INK, fs=11,
        lw=1.4, pad=0.10, rad=0.16):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle=f"round,pad={pad},rounding_size={rad}",
                                facecolor=fc, edgecolor=ec, linewidth=lw, zorder=3))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            color=tc, zorder=4)


def arrow(ax, p, q, color=TEAL, lw=1.9, rad=0.0, ls="-", z=2, ms=14):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=ms,
                                 color=color, lw=lw, linestyle=ls, zorder=z,
                                 connectionstyle=f"arc3,rad={rad}",
                                 shrinkA=1, shrinkB=1))


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=DPI, bbox_inches="tight",
                facecolor="white", pad_inches=0.12)
    plt.close(fig)
    print("  ", name)


# ------------------------------------------------- 01 图形管线（两排：全链路 + 本讲）
def d01():
    fig, ax = canvas(10.6, 5.4, (0, 10.6), (0, 5.4))
    y, W, H = 3.62, 1.55, 0.92
    items = [("顶点\n(3D)", 0.25, PURPLE), ("变换后顶点\n(屏幕 x,y)", 2.10, PURPLE),
             ("片段\nFragments", 4.15, ORANGE), ("着色后片段", 6.20, PURPLE),
             ("像素\nPixels", 8.15, PURPLE)]
    for t, x, c in items:
        box(ax, x, y, W, H, t, tc=c)
    for i in range(4):
        arrow(ax, (items[i][1] + W + 0.02, y + H / 2),
              (items[i + 1][1] - 0.03, y + H / 2))
    ax.text(0.25, 5.02, "完整图形管线", fontsize=12, color=INK, fontweight="bold")
    for txt, xc, col in [("MVP", 1.91, TEAL), ("光栅化", 3.86, ORANGE),
                         ("着色", 5.90, TEAL), ("深度", 7.94, TEAL)]:
        ax.text(xc, y + H + 0.10, txt, fontsize=8.6, color=col, ha="center",
                va="bottom", fontweight="bold" if col == ORANGE else "normal", zorder=6)

    ax.text(0.25, 3.20, "本讲把橙色那一格拧开", fontsize=12, color=ORANGE,
            fontweight="bold")
    y2 = 1.20
    box(ax, 0.25, y2, 2.05, H, "屏幕上的三角形\n三个浮点顶点", tc=ORANGE, ec=ORANGE)
    box(ax, 3.30, y2, 2.05, H, "inside ∈ {0,1}\n每个像素判一次", tc=ORANGE, ec=ORANGE)
    box(ax, 6.30, y2, 2.05, H, "Image[y][x]\n写 0 或 1", tc=ORANGE, ec=ORANGE)
    arrow(ax, (2.34, y2 + H / 2), (3.26, y2 + H / 2), color=ORANGE)
    arrow(ax, (5.39, y2 + H / 2), (6.26, y2 + H / 2), color=ORANGE)
    ax.text(2.80, y2 + H + 0.10, "三个 L 判号", fontsize=8.6, color=ORANGE,
            ha="center", va="bottom")
    ax.text(5.82, y2 + H + 0.10, "像素中心采样", fontsize=8.6, color=ORANGE,
            ha="center", va="bottom")
    arrow(ax, (4.20, y - 0.02), (4.20, y2 + H + 0.04), color=STROKE, lw=1.4,
          ls=(0, (4, 3)))
    ax.text(8.75, y2 + H / 2, "颜色留给\nL06–08", fontsize=8.6, color=MUTED,
            ha="left", va="center", linespacing=1.5)
    save(fig, "d01-pipeline.png")


# ------------------------------------------------- 02 矢量 vs 光栅
def d02():
    fig, ax = canvas(10, 4.4, (0, 10), (0, 4.4))
    ax.add_patch(FancyBboxPatch((0.45, 0.85), 3.6, 2.75,
                                boxstyle="round,pad=0.06,rounding_size=0.18",
                                facecolor="#0b1220", edgecolor=STROKE, lw=1.4, zorder=2))
    t = np.linspace(0, 1, 500)
    xs = 0.75 + 3.0 * t
    ys = 2.2 + 0.85 * np.sin(2 * np.pi * 1.6 * t) * np.cos(2 * np.pi * 0.55 * t)
    ax.plot(xs, ys, color="#22d3ee", lw=2.4, zorder=3, solid_capstyle="round")
    ax.text(2.25, 3.95, "示波器 / 矢量", fontsize=11.5, color=TEAL, ha="center",
            fontweight="bold")
    ax.text(2.25, 0.45, "电子束连续偏转 · 没有像素", fontsize=9.2, color=MUTED,
            ha="center")

    ax.add_patch(FancyBboxPatch((5.95, 0.85), 3.6, 2.75,
                                boxstyle="round,pad=0.06,rounding_size=0.18",
                                facecolor="#0b1220", edgecolor=STROKE, lw=1.4, zorder=2))
    t2 = np.linspace(0, 1, 200)
    for k in range(9):
        yy = 1.05 + k * 0.29
        ax.plot([6.2, 9.3], [yy, yy], color="#7dd3fc", lw=0.9, alpha=0.55, zorder=3)
        on = (0.5 + 0.5 * np.sin(2 * np.pi * 1.4 * t2 + k * 0.6)) > 0.55
        ax.plot(6.2 + 3.1 * t2[on], np.full(on.sum(), yy), "|", color="#f59e0b",
                ms=4.5, mew=1.3, zorder=4)
    ax.text(7.75, 3.95, "CRT 光栅", fontsize=11.5, color=ORANGE, ha="center",
            fontweight="bold")
    ax.text(7.75, 0.45, "逐行扫描 · 强度调制 · 有格子", fontsize=9.2, color=MUTED,
            ha="center")

    arrow(ax, (4.30, 2.20), (5.70, 2.20), color=MUTED, lw=1.6)
    ax.text(5.0, 2.44, "离散化的代价", fontsize=9.4, color=RED, ha="center",
            fontweight="bold")
    ax.text(5.0, 1.94, "连续 → 网格", fontsize=8.8, color=MUTED, ha="center")
    save(fig, "d02-vector-vs-raster.png")


# ------------------------------------------------- 03 帧缓冲
def d03():
    fig, ax = canvas(9.6, 3.9, (0, 9.6), (0, 3.9))
    rng = np.random.default_rng(7)
    pal = ["#22c55e", "#f59e0b", "#ef4444", "#3b82f6", "#a855f7", "#14b8a6"]
    n = 8
    for i in range(n):
        for j in range(n):
            c = pal[(i * 3 + j * 5) % len(pal)] if rng.random() > 0.35 else "#1f2937"
            ax.add_patch(Rectangle((0.5 + i * 0.20, 1.15 + j * 0.20), 0.20, 0.20,
                                   facecolor=c, edgecolor="white", lw=0.7, zorder=3))
    ax.add_patch(Rectangle((0.5, 1.15), 1.6, 1.6, fill=False, ec=INK, lw=1.4, zorder=4))
    ax.text(1.3, 0.92, "帧缓冲：8×8 个数", fontsize=9.5, color=INK, ha="center")
    ax.text(1.3, 2.95, "内存", fontsize=11.5, color=PURPLE, ha="center",
            fontweight="bold")

    box(ax, 3.0, 1.62, 1.5, 0.62, "DAC", tc=MUTED, fs=10)
    ax.text(3.75, 1.32, "数字 → 模拟电压", fontsize=8.6, color=MUTED, ha="center")
    arrow(ax, (2.35, 1.95), (2.95, 1.93), color=MUTED, lw=1.5)

    ax.add_patch(FancyBboxPatch((5.0, 1.05), 2.0, 1.75,
                                boxstyle="round,pad=0.05,rounding_size=0.10",
                                facecolor="#111827", edgecolor=STROKE, lw=1.4, zorder=2))
    for i in range(n):
        for j in range(n):
            c = pal[(i * 3 + j * 5) % len(pal)] if rng.random() > 0.35 else "#0f172a"
            ax.add_patch(Rectangle((5.18 + i * 0.205, 1.22 + j * 0.20), 0.205, 0.20,
                                   facecolor=c, edgecolor="none", zorder=3))
    ax.plot([5.85, 5.85], [1.05, 0.72], color=STROKE, lw=2)
    ax.plot([5.55, 6.15], [0.72, 0.72], color=STROKE, lw=2.4)
    ax.text(6.0, 0.45, "电子束按行扫过 · 每格亮度由电压决定", fontsize=9,
            color=MUTED, ha="center")
    ax.text(6.0, 2.95, "屏幕", fontsize=11.5, color=INK, ha="center", fontweight="bold")
    arrow(ax, (4.55, 1.93), (4.95, 1.93), color=MUTED, lw=1.5)
    ax.text(8.15, 1.95, "同一件事\n两种表示", fontsize=10, color=TEAL,
            ha="center", va="center", fontweight="bold")
    save(fig, "d03-frame-buffer.png")


# ------------------------------------------------- 04 为什么是三角形
def d04():
    fig, ax = canvas(9.2, 3.9, (0, 9.2), (0, 3.9))
    ax.add_patch(Polygon([[0.6, 1.15], [3.5, 0.95], [3.2, 2.25], [0.95, 2.05]],
                         closed=True, facecolor="#eef2f7", ec=STROKE, lw=1.2, zorder=2))
    pts = [(0.6, 1.15), (3.5, 0.95), (3.2, 2.25)]
    ax.plot(*zip(*pts), "o", ms=8, color=BLUE, zorder=5)
    ax.plot(1.9, 2.95, "o", ms=9, color=RED, zorder=6)
    ax.plot([3.2, 1.9], [2.25, 2.95], ls=(0, (3, 3)), color=RED, lw=1.4, zorder=4)
    ax.text(2.0, 3.12, "第 4 点翘起来了", fontsize=9, color=RED, ha="center")
    ax.text(2.05, 0.55, "四边形：四个点可能不共面", fontsize=10, color=RED,
            ha="center", fontweight="bold")
    ax.text(2.05, 0.25, "→ 这个面「朝哪边」没有答案", fontsize=8.8, color=MUTED,
            ha="center")

    ax.add_patch(Polygon([[5.4, 1.15], [8.3, 0.95], [7.1, 2.6]],
                         closed=True, facecolor="#e8f7f4", ec=TEAL, lw=1.6, zorder=2))
    for p in [(5.4, 1.15), (8.3, 0.95), (7.1, 2.6)]:
        ax.plot(*p, "o", ms=9, color=TEAL, zorder=5)
    ax.text(6.85, 3.12, "三点必定共面", fontsize=9, color=GREEN, ha="center")
    ax.text(6.85, 0.55, "三角形：永远共面", fontsize=10, color=TEAL,
            ha="center", fontweight="bold")
    ax.text(6.85, 0.25, "→ 平面唯一，「内部」也唯一", fontsize=8.8, color=MUTED,
            ha="center")
    ax.plot([4.55, 4.55], [0.35, 3.3], color="#e5e9ef", lw=1.2)
    save(fig, "d04-triangle-why.png")


# ------------------------------------------------- 05 一维采样
def d05():
    fig, ax = canvas(8.6, 3.5, (0, 8.6), (0, 3.5))
    x = np.linspace(0.6, 8.0, 500)
    f = lambda v: 0.75 + 1.85 * np.exp(-((v - 4.3) ** 2) / 4.2) + 0.12 * np.sin(3.1 * v)
    ax.plot(x, f(x), color=BLUE, lw=2.4, zorder=3)
    xs = np.arange(0.9, 8.0, 0.72)
    ys = f(xs)
    ax.vlines(xs, 0.42, ys, color=ORANGE, lw=1.0, ls=(0, (2, 2)), alpha=0.7, zorder=2)
    ax.plot(xs, ys, "o", ms=8, color=ORANGE, zorder=5, mec="white", mew=1.2)
    ax.plot([0.6, 8.05], [0.42, 0.42], color=STROKE, lw=1.4)
    ax.text(4.3, 0.16, "采样点等间距排列（周期采样）", fontsize=9.2, color=MUTED,
            ha="center")
    a, b = xs[3], xs[4]
    ax.plot([a, b], [f(a), f(b)], color=RED, lw=1.6, ls=(0, (4, 3)), zorder=6)
    ax.text((a + b) / 2, (f(a) + f(b)) / 2 + 0.28, "中间这段\n我们不知道",
            fontsize=9, color=RED, ha="center", va="bottom")
    ax.text(0.6, 3.22, "连续函数", fontsize=10.5, color=BLUE, fontweight="bold")
    ax.text(6.35, 3.22, "● 采样值 = 唯一留下的信息", fontsize=9.2, color=ORANGE)
    save(fig, "d05-sampling.png")


# ------------------------------------------------- 06 光栅化 = 2D 采样
def d06():
    fig, ax = canvas(8.4, 4.8, (0, 8.4), (0, 4.8))
    NX, NY = 11, 8
    ox, oy, cw = 0.55, 0.60, 0.42
    tri = np.array([[1.55, 1.05], [4.05, 2.55], [3.15, 4.10]])

    def inside(px, py):
        s = 0
        for k in range(3):
            x0, y0 = tri[k]
            x1, y1 = tri[(k + 1) % 3]
            dx, dy = x1 - x0, y1 - y0
            s += (-(px - x0) * dy + (py - y0) * dx) > 0
        return s == 3

    for i in range(NX):
        for j in range(NY):
            ax.add_patch(Rectangle((ox + i * cw, oy + j * cw), cw, cw, fill=False,
                                   ec="#dfe4ea", lw=0.8, zorder=1))
    ax.add_patch(Polygon(tri, closed=True, facecolor="#fde8e8", alpha=0.85,
                         ec="#c53030", lw=2.0, zorder=2))
    for i in range(NX):
        for j in range(NY):
            px, py = ox + i * cw + cw / 2, oy + j * cw + cw / 2
            ok = inside(px, py)
            ax.plot(px, py, "o", ms=5.2 if ok else 4.6, zorder=5,
                    markerfacecolor="#c53030" if ok else "white",
                    markeredgecolor="#c53030" if ok else "#b0bcc9", markeredgewidth=1.0)

    i0, j0 = 7, 4
    px, py = ox + i0 * cw, oy + j0 * cw
    ax.add_patch(Rectangle((px, py), cw, cw, fill=False, ec=ORANGE, lw=2.2, zorder=6))
    z = 1.45
    arrow(ax, (px + cw, py + cw), (5.62, 2.05), color=ORANGE, lw=1.6)
    ax.add_patch(Rectangle((5.62, 2.05), z, z, facecolor="white", ec=ORANGE,
                           lw=2.0, zorder=4))
    ax.plot(5.62 + z / 2, 2.05 + z / 2, "o", ms=7.5, color="#c53030", zorder=6)
    ax.text(6.35, 1.72, "像素 (x,y) 的采样点\n= 格子正中心 (x+½, y+½)",
            fontsize=9, color=ORANGE, ha="center", va="top", linespacing=1.5)
    ax.text(6.35, 3.98, "每个像素只问一句话：\n「中心在三角形里吗？」",
            fontsize=9.5, color=INK, ha="center", va="center", linespacing=1.6)
    ax.text(6.35, 4.62, "结果只有 0 或 1", fontsize=10.5, color=RED,
            ha="center", fontweight="bold")
    save(fig, "d06-rasterize.png")


# ------------------------------------------------- 07 三个半平面
def d07():
    fig, ax = canvas(8.0, 6.0, (0, 8.0), (0, 6.0))
    P = np.array([[2.2, 1.65], [5.7, 2.25], [3.5, 4.55]])
    for k in range(3):
        p0, p1 = P[k], P[(k + 1) % 3]
        d = p1 - p0
        d = d / np.linalg.norm(d)
        a = p0 - d * 0.85
        b = p0 + d * (np.linalg.norm(p1 - p0) + 0.85)
        ax.plot([a[0], b[0]], [a[1], b[1]], color=INK, lw=1.3, alpha=0.5, zorder=2)
    ax.add_patch(Polygon(P, closed=True, facecolor="#fde8e8", ec="#c53030",
                         lw=2.2, zorder=3))
    cen = P.mean(axis=0)
    for k in range(3):
        p0, p1 = P[k], P[(k + 1) % 3]
        d = p1 - p0
        n = np.array([-d[1], d[0]])
        n = n / np.linalg.norm(n)
        if np.dot(cen - p0, n) < 0:
            n = -n
        mid = (p0 + p1) / 2
        arrow(ax, tuple(mid + n * 0.10), tuple(mid + n * 0.50), color=TEAL,
              lw=1.6, ms=11, z=5)
        ax.text(*(mid + n * 0.68), "+", fontsize=14, color=TEAL, ha="center",
                va="center", fontweight="bold", zorder=8)
        ax.text(*(mid - n * 0.52), f"L{k}", fontsize=10.5, color=TEAL, ha="center",
                va="center", fontweight="bold",
                bbox=dict(fc="white", ec="none", pad=1.6), zorder=8)
        ax.text(*(mid - n * 1.02), "−", fontsize=15, color=RED, ha="center",
                va="center", zorder=8)
    off = [(-0.46, -0.16), (0.18, -0.28), (0.18, 0.14)]
    for k, p in enumerate(P):
        ax.plot(*p, "o", ms=7, color=INK, zorder=6)
        ax.text(p[0] + off[k][0], p[1] + off[k][1], f"P{k}", fontsize=10, color=INK)
    ax.text(0.15, 5.70, "每条边向两侧延成一条无限长直线，把平面切成两半",
            fontsize=9.5, color=MUTED)
    ax.text(0.15, 0.30, "箭头 = 法向 N 指向内侧（+ 号侧）；三条边的内侧交集 = 三角形本身",
            fontsize=9.2, color=MUTED)
    save(fig, "d07-halfplanes.png")


# ------------------------------------------------- 08 点积判号
def d08():
    fig, ax = canvas(7.6, 5.3, (0, 7.6), (0, 5.3))
    P0 = np.array([1.15, 1.35])
    d = np.array([4.0, 1.30])
    T = d / np.linalg.norm(d)
    N = np.array([-T[1], T[0]])
    a = P0 - T * 0.85
    b = P0 + T * (np.linalg.norm(d) + 0.95)
    ax.plot([a[0], b[0]], [a[1], b[1]], color=INK, lw=1.5, zorder=2)
    far = 3.5
    ax.add_patch(Polygon([a, b, b + N * far, a + N * far], closed=True,
                         facecolor="#e6f7f4", ec="none", zorder=1))
    ax.text(5.95, 3.55, "L > 0", fontsize=13, color=TEAL, ha="center", fontweight="bold")
    ax.text(1.85, 0.72, "L < 0", fontsize=13, color=RED, ha="center", fontweight="bold")
    arrow(ax, tuple(P0), tuple(P0 + T * np.linalg.norm(d)), color=BLUE, lw=2.0)
    ax.text(3.55, 2.22, r"T = P₁ − P₀", fontsize=10, color=BLUE)
    arrow(ax, tuple(P0), tuple(P0 + N * 1.60), color=TEAL, lw=2.0)
    ax.text(0.55, 2.98, "N = Perp(T)", fontsize=10, color=TEAL, ha="center")
    Q = P0 + T * 2.5 + N * 1.85
    arrow(ax, tuple(P0), tuple(Q), color=ORANGE, lw=2.0)
    ax.plot(*Q, "o", ms=9, color=RED, zorder=6)
    ax.text(Q[0] + 0.22, Q[1] + 0.14, "P = (x, y)", fontsize=10, color=INK)
    ax.text(2.75, 2.62, "V = P − P₀", fontsize=10, color=ORANGE)
    ax.plot(*P0, "o", ms=7, color=INK, zorder=6)
    ax.text(P0[0] - 0.48, P0[1] - 0.36, "P₀", fontsize=11)
    Pe = P0 + T * np.linalg.norm(d)
    ax.plot(*Pe, "o", ms=6, color=INK, zorder=6)
    ax.text(Pe[0] + 0.10, Pe[1] + 0.24, "P₁", fontsize=11)
    ax.text(0.30, 4.92, r"L(x, y) = V · N     符号决定 P 在哪一侧", fontsize=11, color=INK)
    ax.text(0.30, 0.28, "|V·N| 正比于点到直线的距离，比例因子是边长 |T|",
            fontsize=9, color=MUTED)
    save(fig, "d08-line-equation.png")


# ------------------------------------------------- 09 增量递推
def d09():
    fig, ax = canvas(9.0, 2.9, (0, 9.0), (0, 2.9))
    vals = [3.2, 2.4, 1.6, 0.8, 0.0, -0.8]
    x0, w, h, y = 0.5, 1.28, 0.92, 1.0
    for i, v in enumerate(vals):
        ins = v > 0
        box(ax, x0 + i * (w + 0.16), y, w, h, f"L = {v:+.1f}",
            fc="#fde8e8" if ins else "#eef2f7",
            ec="#c53030" if ins else STROKE,
            tc="#7f1d1d" if ins else MUTED, fs=10.5, rad=0.12)
        if i < len(vals) - 1:
            bx = x0 + i * (w + 0.16) + w
            arrow(ax, (bx + 0.01, y + h / 2), (bx + 0.15, y + h / 2),
                  color=ORANGE, lw=1.6, ms=12)
    ax.text(0.5, 2.42, r"同一行内：L(x+1, y) = L(x, y) + A$_i$    （这里 A = −0.8）",
            fontsize=11, color=INK)
    ax.text(0.5, 0.62, "每步只要一次加法：不用乘法，也不用重新代公式",
            fontsize=9.5, color=ORANGE)
    ax.text(0.5, 0.30, "红色 = 在内，灰色 = 在外；跨过 0 的那一格就是边界",
            fontsize=9.2, color=MUTED)
    save(fig, "d09-incremental.png")


# ------------------------------------------------- 10 分块遍历
def d10():
    fig, ax = canvas(6.6, 5.5, (0, 6.6), (0, 5.5))
    N, T = 16, 4
    ox, oy, cw = 0.50, 0.85, 0.30
    tri = np.array([[2.0, 2.1], [13.4, 4.4], [6.2, 12.6]])

    def inside(px, py):
        s = 0
        for k in range(3):
            x0, y0 = tri[k]
            x1, y1 = tri[(k + 1) % 3]
            dx, dy = x1 - x0, y1 - y0
            s += (-(px - x0) * dy + (py - y0) * dx) > 0
        return s == 3

    centers = {"out": None, "in": None, "part": None}
    for ti in range(N // T):
        for tj in range(N // T):
            pts = [(ti * T + a + 0.5, tj * T + b + 0.5)
                   for a in range(T) for b in range(T)]
            cnt = sum(inside(*p) for p in pts)
            key = "out" if cnt == 0 else ("in" if cnt == T * T else "part")
            fc, ec, lw = (("#e3e9f0", "#b9c3ce", 1.1) if key == "out" else
                          ("#fbd9a5", "#b45309", 1.6) if key == "in" else
                          ("white", "#8b98a6", 1.2))
            X, Y = ox + ti * T * cw, oy + tj * T * cw
            ax.add_patch(Rectangle((X, Y), T * cw, T * cw, facecolor=fc, ec=ec,
                                   lw=lw, zorder=1))
            if centers[key] is None:
                centers[key] = (X + T * cw / 2, Y + T * cw / 2)
    for i in range(N):
        for j in range(N):
            ax.plot(ox + i * cw + cw / 2, oy + j * cw + cw / 2, ".", ms=2.0,
                    color="#aab6c2", zorder=2)
    ax.add_patch(Polygon([[ox + p[0] * cw, oy + p[1] * cw] for p in tri],
                         closed=True, fill=False, ec="#c53030", lw=2.2, zorder=3))
    for key, txt, col in [("in", "early in", "#7c3a00"),
                          ("out", "early out", "#44546a"),
                          ("part", "逐点测", "#5b6b7c")]:
        if centers[key]:
            ax.text(centers[key][0], centers[key][1], txt, fontsize=8.4, color=col,
                    ha="center", va="center", zorder=6)
    ly = 0.45
    for i, (fc, ec, t) in enumerate([("#e3e9f0", "#b9c3ce", "整块在外 → 跳过"),
                                     ("#fbd9a5", "#b45309", "整块在内 → 全填"),
                                     ("white", "#8b98a6", "含边界 → 逐点测")]):
        x = 0.55 + i * 2.05
        ax.add_patch(Rectangle((x, ly - 0.09), 0.22, 0.18, facecolor=fc, ec=ec, lw=1.2))
        ax.text(x + 0.33, ly, t, fontsize=8.8, color=MUTED, va="center")
    save(fig, "d10-tiled.png")


# ------------------------------------------------- 11 锯齿 = 采样密度
def d11():
    fig, ax = canvas(9.6, 3.5, (0, 9.6), (0, 3.5))
    for p, n in enumerate([4, 8, 16]):
        ox, oy, w = 0.55 + p * 3.15, 0.95, 2.45
        c = w / n
        for i in range(n):
            for j in range(n):
                cx, cy = (i + 0.5) / n, (j + 0.5) / n
                ok = (cx + cy) < 1.02
                ax.add_patch(Rectangle((ox + i * c, oy + j * c), c, c,
                                       facecolor="#fca5a5" if ok else "white",
                                       ec="#e2e8f0", lw=0.5 if n > 8 else 0.8, zorder=2))
        ax.plot([ox, ox + w], [oy, oy + w], color="#c53030", lw=1.4,
                ls=(0, (4, 3)), zorder=4)
        ax.text(ox + w / 2, oy + w + 0.22, f"{n} × {n} 像素", fontsize=10, color=INK,
                ha="center", fontweight="bold")
        ax.text(ox + w / 2, oy - 0.24, f"台阶数 = {n}", fontsize=8.8, color=MUTED,
                ha="center")
    ax.text(0.55, 0.28, "同一条 45° 斜边：分辨率越高，台阶越细 —— 但「台阶」这件事不会消失",
            fontsize=9.4, color=ORANGE)
    ax.text(8.1, 1.62, "第 3 讲从这里\n开始讲「为什么」", fontsize=9, color=RED,
            ha="center", va="center", linespacing=1.5)
    save(fig, "d11-jaggies.png")


# ------------------------------------------------- 12 超采样
def d12():
    fig, ax = canvas(9.4, 3.4, (0, 9.4), (0, 3.4))
    ox, oy, w = 0.55, 0.95, 2.1
    ax.add_patch(Rectangle((ox, oy), w, w, facecolor="white", ec=INK, lw=1.6, zorder=2))
    ax.add_patch(Polygon([[ox, oy], [ox + w, oy], [ox, oy + w * 0.82]], closed=True,
                         facecolor="#fca5a5", alpha=0.75, ec="#c53030", lw=1.4, zorder=3))
    hit = 0
    for i in range(4):
        for j in range(4):
            cx, cy = ox + (i + 0.5) * w / 4, oy + (j + 0.5) * w / 4
            ok = (cx - ox) / w + (cy - oy) / w < 0.82
            hit += ok
            ax.plot(cx, cy, "o", ms=6.0, zorder=5,
                    markerfacecolor="#c53030" if ok else "white",
                    markeredgecolor="#c53030" if ok else "#9aa7b4", markeredgewidth=1.1)
    ax.text(ox + w / 2, oy - 0.26, "像素内取 4×4 = 16 个子样本", fontsize=9,
            color=MUTED, ha="center")
    arrow(ax, (ox + w + 0.12, oy + w / 2), (3.05, oy + w / 2), color=MUTED, lw=1.6)
    ax.text(2.86, oy + w / 2 + 0.30, "数一数", fontsize=9, color=MUTED, ha="center")
    box(ax, 3.2, 1.28, 1.75, 1.44, f"{hit}/16\n= {hit/16:.3f}", fs=13,
        fc="#fde8e8", ec="#c53030", tc="#7f1d1d", rad=0.18)
    ax.text(4.08, oy - 0.26, "覆盖率 → 像素值", fontsize=9, color=MUTED, ha="center")
    arrow(ax, (5.05, oy + w / 2), (5.85, oy + w / 2), color=MUTED, lw=1.6)
    levels = 17
    bx, bw = 5.95, 0.19
    for k in range(levels):
        g = 1.0 - k / (levels - 1) * 0.82
        ax.add_patch(Rectangle((bx + k * bw, 1.55), bw, 0.85,
                               facecolor=(g, g * 0.72 + 0.05, g * 0.72 + 0.05),
                               ec="white", lw=1.0, zorder=3))
    ax.text(bx + levels * bw / 2, 2.62, "0 → 1 共 17 级（含两端）", fontsize=9,
            color=MUTED, ha="center")
    ax.text(bx + levels * bw / 2, oy - 0.26, "比 0/1 两档多了 15 级过渡",
            fontsize=9, color=ORANGE, ha="center")
    ax.text(8.95, 1.98, "边缘不再是\n硬台阶", fontsize=9, color=RED, ha="center",
            va="center", linespacing=1.5)
    save(fig, "d12-supersample.png")


# ------------------------------------------------- 13 摩尔纹
def d13():
    fig, ax = canvas(9.4, 3.6, (0, 9.4), (0, 3.6))
    cx, cy, R = 2.05, 1.85, 1.35
    for k in range(64):
        a0 = 2 * np.pi * k / 64
        ax.plot([cx + 0.42 * np.cos(a0), cx + R * np.cos(a0)],
                [cy + 0.42 * np.sin(a0), cy + R * np.sin(a0)],
                color="#c53030", lw=0.55, alpha=0.85, zorder=2)
    ax.add_patch(Circle((cx, cy), 0.42, facecolor="#fde047", ec="#f59e0b",
                        lw=1.2, zorder=3))
    ax.text(cx, cy - R - 0.30, "真实图案：64 条等角度辐条", fontsize=9, color=MUTED,
            ha="center")
    ax.text(cx, 3.34, "连续（未采样）", fontsize=10, color=INK, ha="center",
            fontweight="bold")

    arrow(ax, (3.62, 1.85), (4.55, 1.85), color=MUTED, lw=1.7)
    ax.text(4.08, 2.12, "低分辨率光栅化", fontsize=8.8, color=RED, ha="center")

    cx2, cy2, N = 5.75, 1.85, 42
    for k in range(N):
        a0 = 2 * np.pi * k / N
        rr = R * (0.62 + 0.38 * abs(np.sin(3.1 * a0) ** 3))
        ax.plot([cx2 + 0.42 * np.cos(a0), cx2 + rr * np.cos(a0)],
                [cy2 + 0.42 * np.sin(a0), cy2 + rr * np.sin(a0)],
                color="#c53030", lw=0.8, alpha=0.9, zorder=2)
    ax.add_patch(Circle((cx2, cy2), 0.42, facecolor="#fde047", ec="#f59e0b",
                        lw=1.2, zorder=3))
    ax.text(cx2, cy2 - R - 0.30, "像素化后：辐条长度忽长忽短", fontsize=9,
            color=MUTED, ha="center")
    ax.text(cx2, 3.34, "采样之后", fontsize=10, color=INK, ha="center",
            fontweight="bold")
    ax.text(7.55, 2.45, "尖刺的长短\n原本不存在", fontsize=9.5, color=RED,
            ha="center", va="center", linespacing=1.5)
    ax.text(7.55, 1.15, "这叫摩尔纹 / 混叠\n（讲义 p27、p95 那张「太阳」）",
            fontsize=9, color=MUTED, ha="center", va="center", linespacing=1.5)
    save(fig, "d13-moire.png")


# ------------------------------------------------- 14 边缘归属
def d14():
    fig, ax = canvas(7.4, 4.4, (0, 7.4), (0, 4.4))
    A = [[1.5, 3.0], [5.3, 3.0], [3.4, 0.75]]
    B = [[1.5, 3.0], [5.3, 3.0], [3.4, 4.05]]
    ax.add_patch(Polygon(A, closed=True, facecolor="#dbeafe", ec=BLUE, lw=1.8, zorder=2))
    ax.add_patch(Polygon(B, closed=True, facecolor="#fde8e8", ec="#c53030",
                         lw=1.8, zorder=2))
    ax.plot([1.5, 5.3], [3.0, 3.0], color="#14532d", lw=4.2, alpha=0.42,
            solid_capstyle="round", zorder=4)
    for x in [2.2, 2.95, 3.7, 4.45]:
        ax.plot(x, 3.0, "o", ms=8, markerfacecolor="white", markeredgecolor=ORANGE,
                markeredgewidth=2.0, zorder=6)
    ax.text(3.4, 2.45, "三角形 A", fontsize=10.5, color=BLUE, ha="center",
            fontweight="bold")
    ax.text(3.4, 3.55, "三角形 B", fontsize=10.5, color="#c53030", ha="center",
            fontweight="bold")
    ax.text(3.4, 3.0, "共享边", fontsize=8.6, color="#14532d", ha="center",
            va="center", bbox=dict(fc="white", ec="none", pad=1.2), zorder=7)
    ax.text(0.25, 4.18, "对 A：水平且在 A 所有边之上 → top edge → 算在内",
            fontsize=9, color=TEAL)
    ax.text(0.25, 0.28, "对 B：水平的底边，既非 top 也非 left → 算在外。结果：恰好画一次",
            fontsize=9, color=MUTED)
    save(fig, "d14-edge-rule.png")


if __name__ == "__main__":
    print("generating ->", OUT)
    for fn in [d01, d02, d03, d04, d05, d06, d07, d08, d09, d10, d11, d12, d13, d14]:
        fn()
    print("done: 14 diagrams")
