# -*- coding: utf-8 -*-
"""CS184 课程笔记 · L10（Bézier 曲线与曲面）原创图解

风格遵循 scripts/cs184-notes-standard.md。
颜色语义：teal=主链路，orange=本讲焦点，purple=控制点/数据，red=错误/异常，灰=说明
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
                                    "notes", "cs184-10-bezier-curves-surfaces", "diagrams"))
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


def box(ax, x, y, w, h, text, fc=FILL, ec=STROKE, tc=INK, fs=9.4, lw=1.4,
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


def bez(pts, t):
    """de Casteljau：任意阶 Bézier 求值。"""
    pts = np.asarray(pts, dtype=float)
    while len(pts) > 1:
        pts = (1 - t) * pts[:-1] + t * pts[1:]
    return pts[0]


def bez_curve(pts, n=200):
    ts = np.linspace(0, 1, n)
    return np.array([bez(pts, t) for t in ts])


def ctrl(ax, pts, color=PURPLE, ms=5, lw=1.0, ls=(0, (4, 3)), labels=None):
    pts = np.asarray(pts, dtype=float)
    ax.plot(pts[:, 0], pts[:, 1], ls=ls, color=color, lw=lw, zorder=2)
    ax.plot(pts[:, 0], pts[:, 1], "o", ms=ms, color=color, zorder=6,
            markerfacecolor="white", markeredgewidth=1.6)
    if labels:
        for p, lab in zip(pts, labels):
            ax.text(p[0] + 0.05, p[1] + 0.06, lab, fontsize=8.0, color=color)


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=DPI, bbox_inches="tight",
                facecolor="white", pad_inches=0.12)
    plt.close(fig)
    print("  ", name)


# ------------------------------------------------- d01 显式 vs 隐式
def d01():
    fig, ax = canvas(9.8, 3.4, (0, 9.8), (0, 3.4))
    ax.text(0.30, 3.14, "同一份几何，两种完全不同的表示方式", fontsize=10.4, color=INK,
            fontweight="bold")
    ax.text(1.55, 2.82, "显式 explicit", fontsize=9.6, color=TEAL, ha="center",
            fontweight="bold")
    th = np.linspace(0, 2 * np.pi, 200)
    ax.plot(1.55 + 0.80 * np.cos(th), 1.55 + 0.80 * np.sin(th), color="#cbd5e1", lw=1.0)
    for k in range(22):
        a = 2 * np.pi * k / 22
        ax.plot(1.55 + 0.80 * np.cos(a), 1.55 + 0.80 * np.sin(a), "o", ms=3.2, color=TEAL)
    ax.text(1.55, 0.62, "圆 = 一堆点（点云 / 多边形 / 样条）", fontsize=8.6, color=MUTED,
            ha="center")
    ax.text(1.55, 0.30, "「它由哪些点组成」", fontsize=8.6, color=TEAL, ha="center")

    ax.text(4.95, 2.82, "隐式 implicit", fontsize=9.6, color=ORANGE, ha="center",
            fontweight="bold")
    ax.plot(4.95 + 0.80 * np.cos(th), 1.55 + 0.80 * np.sin(th), color="#cbd5e1", lw=1.0)
    for r in (0.45, 0.62):
        ax.plot(4.95 + r * np.cos(th), 1.55 + r * np.sin(th), color="#fdba74", lw=0.9,
                ls=(0, (3, 3)))
    ax.text(4.95, 0.62, "$f(x,y)=x^2+y^2-R^2=0$", fontsize=8.8, color=ORANGE, ha="center")
    ax.text(4.95, 0.30, "「哪些点满足这个条件」", fontsize=8.6, color=ORANGE, ha="center")

    box(ax, 6.55, 1.35, 3.00, 1.35,
        "显式：便于「沿曲线走」\n（渲染、动画、字体）\n\n"
        "隐式：便于「判断内外」\n（求交、布尔运算、体积）",
        fs=8.4, fc=FILL, ec=STROKE)
    ax.text(0.30, 0.05, "讲义 P11：每种表示都最适合某类任务 —— 没有一种「通用最优」",
            fontsize=8.8, color=MUTED)
    save(fig, "d01-explicit-implicit.png")


# ------------------------------------------------- d02 参数化不唯一
def d02():
    fig, ax = canvas(9.6, 3.2, (0, 9.6), (0, 3.2))
    ax.text(0.30, 2.94, "同一条线段可以有无数种参数化 —— 点的「疏密」完全不同", fontsize=10.2,
            color=INK, fontweight="bold")
    for i, (fn, lab, sub) in enumerate([
            (lambda u: u, r"$x(u)=[u,\ u]$", "参数均匀 → 点等距"),
            (lambda u: u ** 3, r"$x(u)=[u^3,\ u^3]$", "参数 $u^3$ → 点先挤后松")]):
        ox = 0.55 + i * 2.60
        ax.plot([ox, ox + 2.05], [0.95, 1.85], color=TEAL, lw=2.2)
        for k in range(6):
            u = k / 5
            s = fn(u)
            ax.plot(ox + 2.05 * s, 0.95 + 0.90 * s, "o", ms=5.0, color=PURPLE, zorder=6)
            ax.text(ox + 2.05 * s, 0.72, f"{u:.1f}", fontsize=7.0, color=MUTED,
                    ha="center")
        ax.text(ox + 1.02, 2.12, f"参数化 {i+1}", fontsize=8.8, color=MUTED, ha="center")
        ax.text(ox + 1.02, 0.42, sub, fontsize=8.2, color=MUTED, ha="center")
    ax.text(5.80, 2.40, "两条曲线的**点集完全一样**", fontsize=9.2, color=INK)
    ax.text(5.80, 2.05, "但参数 u 到弧长的映射不同：", fontsize=9.2, color=INK)
    ax.text(5.80, 1.65, "• 左：等参数 → 等距 → 「匀速」", fontsize=8.8, color=MUTED)
    ax.text(5.80, 1.32, "• 右：$u^3$ → 先慢后快 → 「加速」", fontsize=8.8, color=MUTED)
    ax.text(5.80, 0.85, "实际影响：", fontsize=8.8, color=ORANGE)
    ax.text(5.80, 0.55, "动画沿曲线运动的速度、纹理沿曲线的拉伸，", fontsize=8.4, color=MUTED)
    ax.text(5.80, 0.28, "全都取决于参数化，而不是曲线本身", fontsize=8.4, color=MUTED)
    save(fig, "d02-param-nonunique.png")

# ------------------------------------------------- d03 插值质量
def d03():
    fig, ax = canvas(9.8, 4.2, (0, 9.8), (0, 4.2), eq=False)
    ax.text(0.30, 3.96, "从「连起来」到「光滑」：三种插值的差别在连续性", fontsize=10.2,
            color=INK, fontweight="bold")
    xs = [0.55, 1.85, 3.15]
    ys = [0.30, 0.72, 0.42]
    rows = [("最近邻：值不连续", 0.65, "nearest", "#6b7280"),
            ("线性：导数不连续", 1.85, "linear", ORANGE),
            ("三次：C1 连续", 3.05, "smooth", GREEN)]
    for name, y0, mode, c in rows:
        if mode == "nearest":
            for k in range(2):
                ax.plot([xs[k], xs[k + 1]], [y0 + ys[k]] * 2, color=c, lw=2.2)
                ax.plot([xs[k + 1]] * 2, [y0 + ys[k], y0 + ys[k + 1]], color=c, lw=2.2,
                        ls=(0, (2, 2)))
        elif mode == "linear":
            ax.plot(xs, [y0 + y for y in ys], color=c, lw=2.2)
        else:
            ts = np.linspace(0, 1, 80)
            for k in range(2):
                p0 = np.array([xs[k], y0 + ys[k]])
                p1 = np.array([xs[k + 1], y0 + ys[k + 1]])
                slope = 0.0 if k == 0 else 0.0
                d0 = 0.55 * (1 if k == 0 else 0.55)
                d1 = 0.55 * (1 if k == 0 else 0.55)
                h00 = 2 * ts ** 3 - 3 * ts ** 2 + 1
                h10 = ts ** 3 - 2 * ts ** 2 + ts
                h01 = -2 * ts ** 3 + 3 * ts ** 2
                h11 = ts ** 3 - ts ** 2
                px = p0[0] + (p1[0] - p0[0]) * ts
                py = h00 * p0[1] + h01 * p1[1] + (h10 * d0 + h11 * d1) * (p1[0] - p0[0])
                ax.plot(px, py, color=c, lw=2.2)
        for x, y in zip(xs, ys):
            ax.plot(x, y0 + y, "o", ms=4.6, color=INK, zorder=6)
        ax.text(3.35, y0 + 0.30, name, fontsize=8.8, color=c, va="center")
    ax.text(6.00, 2.75, "为什么不用一个高阶多项式直接插所有点？", fontsize=9.2, color=INK)
    ax.text(6.00, 2.40, "• 高阶会剧烈振荡（Runge 现象）", fontsize=8.6, color=RED)
    ax.text(6.00, 2.10, "• 改一个点，整条曲线都变（无局部性）", fontsize=8.6, color=RED)
    ax.text(6.00, 1.80, "• 数值不稳定、求值也贵", fontsize=8.6, color=RED)
    ax.text(6.00, 1.35, "所以工业界一律「分段低阶 + 保证连续」：", fontsize=8.8, color=TEAL)
    ax.text(6.00, 1.05, "Hermite：给端点值和导数", fontsize=8.4, color=MUTED)
    ax.text(6.00, 0.80, "Catmull-Rom：只给点，导数算出来", fontsize=8.4, color=MUTED)
    ax.text(6.00, 0.55, "Bézier：用控制点间接给切线", fontsize=8.4, color=MUTED)
    save(fig, "d03-interp-quality.png")

# ------------------------------------------------- d04 Hermite 基函数
def d04():
    fig, ax = canvas(9.2, 3.4, (0, 9.2), (0, 3.4), eq=False)
    ax.text(0.30, 3.14, "四个 Hermite 基函数：每个负责一个「输入」", fontsize=10.2,
            color=INK, fontweight="bold")
    t = np.linspace(0, 1, 400)
    H0 = 2 * t ** 3 - 3 * t ** 2 + 1
    H1 = -2 * t ** 3 + 3 * t ** 2
    H2 = t ** 3 - 2 * t ** 2 + t
    H3 = t ** 3 - t ** 2
    for ys, c, lab in [(H0, TEAL, "$H_0$"), (H1, ORANGE, "$H_1$"),
                       (H2, PURPLE, "$H_2$"), (H3, "#9ca3af", "$H_3$")]:
        ax.plot(0.75 + 3.4 * t, 1.35 + 1.25 * ys, color=c, lw=2.0)
    ax.text(4.55, 2.72, "$H_0$ 管 $P(0)$：在 0 处为 1，在 1 处为 0", fontsize=8.8, color=TEAL)
    ax.text(4.55, 2.40, "$H_1$ 管 $P(1)$：在 1 处为 1，在 0 处为 0", fontsize=8.8, color=ORANGE)
    ax.text(4.55, 2.08, "$H_2$ 管 $P'(0)$：0 处斜率为 1，两端值都为 0", fontsize=8.8,
            color=PURPLE)
    ax.text(4.55, 1.76, "$H_3$ 管 $P'(1)$：1 处斜率为 1，两端值都为 0", fontsize=8.8,
            color=MUTED)
    ax.text(0.75, 0.62, "$P(t)=h_0H_0(t)+h_1H_1(t)+h_2H_2(t)+h_3H_3(t)$", fontsize=10.5,
            color=INK)
    ax.text(0.75, 0.24, "四个基函数都只在 [0,1] 内非零 —— 这就是「局部性」的雏形",
            fontsize=8.8, color=MUTED)
    save(fig, "d04-hermite-basis.png")


# ------------------------------------------------- d05 ease
def d05():
    fig, ax = canvas(9.0, 3.2, (0, 9.0), (0, 3.2), eq=False)
    ax.text(0.30, 2.94, "一个意外收获：$H_1(t)$ 就是动画里的「缓动」曲线", fontsize=10.2,
            color=INK, fontweight="bold")
    t = np.linspace(0, 1, 400)
    H1 = t ** 2 * (3 - 2 * t)
    ax.plot(0.80 + 3.2 * t, 0.55 + 1.90 * H1, color=ORANGE, lw=2.4)
    ax.plot([0.80, 4.00], [0.55, 0.55], color=MUTED, lw=1.0)
    ax.plot([0.80, 0.80], [0.55, 2.55], color=MUTED, lw=1.0)
    ax.text(2.40, 0.28, "时间 $t$", fontsize=8.6, color=MUTED, ha="center")
    ax.text(0.55, 1.60, "进度", fontsize=8.6, color=MUTED, rotation=90, va="center")
    ax.text(4.10, 2.05, "$H_1(t)=t^2(3-2t)$", fontsize=10.5, color=ORANGE)
    ax.text(4.10, 1.55, "两端斜率都是 0：", fontsize=9.0, color=INK)
    ax.text(4.10, 1.25, "起手慢、收尾慢 → 「缓入缓出」", fontsize=9.0, color=INK)
    ax.text(4.10, 0.80, "这就是动画曲线编辑器里 ease-in-out 的来历", fontsize=8.8,
            color=MUTED)
    ax.text(4.10, 0.45, "（同一族函数的 $H_0$ 还能做 bounce 等变体）", fontsize=8.4,
            color=MUTED)
    save(fig, "d05-ease.png")


# ------------------------------------------------- d06 Catmull-Rom
def d06():
    fig, ax = canvas(9.6, 3.4, (0, 9.6), (0, 3.4))
    ax.text(0.30, 3.14, "Catmull-Rom：只给点，斜率由相邻点算出来", fontsize=10.2,
            color=INK, fontweight="bold")
    P = np.array([[0.65, 1.05], [1.85, 2.05], [3.05, 1.15], [4.25, 2.15]])
    ax.plot(P[:, 0], P[:, 1], ls=(0, (4, 3)), color="#cbd5e1", lw=1.0)
    for i, p in enumerate(P):
        ax.plot(*p, "o", ms=6, color=PURPLE, zorder=6)
        ax.text(p[0] - 0.04, p[1] - 0.26, f"$p_{i}$", fontsize=9.0, color=PURPLE)
    # 中间段的切线
    m1 = 0.5 * (P[2] - P[0])
    m2 = 0.5 * (P[3] - P[1])
    arrow(ax, tuple(P[1] - 0.30 * m1 / np.linalg.norm(m1)),
          tuple(P[1] + 0.42 * m1 / np.linalg.norm(m1)), color=TEAL, lw=1.8)
    arrow(ax, tuple(P[2] - 0.30 * m2 / np.linalg.norm(m2)),
          tuple(P[2] + 0.42 * m2 / np.linalg.norm(m2)), color=TEAL, lw=1.8)
    # 段内曲线
    ts = np.linspace(0, 1, 100)
    p0, p1, p2, p3 = P[0], P[1], P[2], P[3]
    h0, h1 = p1, p2
    h2, h3 = 0.5 * (p2 - p0), 0.5 * (p3 - p1)
    H0 = 2 * ts ** 3 - 3 * ts ** 2 + 1
    H1 = -2 * ts ** 3 + 3 * ts ** 2
    H2 = ts ** 3 - 2 * ts ** 2 + ts
    H3 = ts ** 3 - ts ** 2
    x = H0[:, None] * h0 + H1[:, None] * h1 + H2[:, None] * h2 + H3[:, None] * h3
    ax.plot(x[:, 0], x[:, 1], color=TEAL, lw=2.4)

    ax.text(4.75, 2.65, "切线规则（对每个点）：", fontsize=9.2, color=INK)
    ax.text(4.75, 2.28, r"$m_i=\dfrac{1}{2}(p_{i+1}-p_{i-1})$", fontsize=11, color=TEAL)
    ax.text(4.75, 1.70, "也就是「前后两点的差」的一半 —— 中心差分", fontsize=8.8, color=MUTED)
    ax.text(4.75, 1.35, "拿到点和切线后，直接套 Hermite 公式", fontsize=8.8, color=INK)
    ax.text(4.75, 0.95, "好处：用户只需给点，不用给切线", fontsize=8.6, color=GREEN)
    ax.text(4.75, 0.65, "代价：C1 连续但 C2 不连续（加速度会跳）", fontsize=8.6, color=RED)
    ax.text(4.75, 0.30, "用途：相机路径、动画关键帧 —— 手工调切线太麻烦", fontsize=8.6,
            color=MUTED)
    save(fig, "d06-catmull-rom.png")


# ------------------------------------------------- d07 Bernstein
def d07():
    fig, ax = canvas(9.4, 3.4, (0, 9.4), (0, 3.4), eq=False)
    ax.text(0.30, 3.14, "三次 Bernstein 基函数：加起来恒等于 1，且都不为负", fontsize=10.2,
            color=INK, fontweight="bold")
    t = np.linspace(0, 1, 400)
    B = [ (1-t)**3, 3*t*(1-t)**2, 3*t**2*(1-t), t**3 ]
    cols = [TEAL, ORANGE, PURPLE, "#9ca3af"]
    for ys, c, lab in zip(B, cols, ["$B_0$", "$B_1$", "$B_2$", "$B_3$"]):
        ax.plot(0.75 + 3.3 * t, 0.55 + 1.75 * ys, color=c, lw=2.0)
        ax.text(0.75 + 3.3 * 0.5, 0.55 + 1.75 * float(np.interp(0.5, t, ys)) + 0.12,
                lab, fontsize=8.6, color=c, ha="center")
    ax.plot([0.75, 4.05], [0.55, 0.55], color=MUTED, lw=1.0)
    ax.text(4.25, 2.55, r"$B_i^n(t)=\binom{n}{i}t^i(1-t)^{n-i}$", fontsize=10.5, color=INK)
    ax.text(4.25, 1.95, "两条性质决定了它的「好脾气」：", fontsize=9.0, color=INK)
    ax.text(4.25, 1.62, r"① $\sum_i B_i(t)=1$  → 仿射组合", fontsize=8.8, color=TEAL)
    ax.text(4.25, 1.30, r"② $B_i(t)\geq 0$  → 不会「插飞」", fontsize=8.8, color=TEAL)
    ax.text(4.25, 0.85, "两条合起来 = 凸包性质（曲线必在控制多边形的凸包内）", fontsize=8.8,
            color=ORANGE)
    ax.text(4.25, 0.45, "对照 Hermite：它的基函数有负值，所以曲线可能跑出控制点的凸包",
            fontsize=8.4, color=MUTED)
    save(fig, "d07-bernstein.png")


# ------------------------------------------------- d08 de Casteljau（二次）
def d08():
    fig, ax = canvas(9.2, 3.6, (0, 9.2), (0, 3.6))
    ax.text(0.30, 3.34, "de Casteljau：反复做线性插值（二次 Bézier，t=0.4）", fontsize=10.2,
            color=INK, fontweight="bold")
    P = np.array([[0.60, 1.00], [1.95, 2.75], [3.30, 1.00]])
    t = 0.4
    ax.plot(P[:, 0], P[:, 1], ls=(0, (4, 3)), color="#cbd5e1", lw=1.0)
    for p, lab in zip(P, ["$b_0$", "$b_1$", "$b_2$"]):
        ax.plot(*p, "o", ms=6, color=PURPLE, zorder=7)
        ax.text(p[0] - 0.05, p[1] - 0.24, lab, fontsize=9.2, color=PURPLE)
    b10 = (1 - t) * P[0] + t * P[1]
    b11 = (1 - t) * P[1] + t * P[2]
    ax.plot(*b10, "o", ms=5.5, color=TEAL, zorder=7)
    ax.plot(*b11, "o", ms=5.5, color=TEAL, zorder=7)
    ax.text(b10[0] - 0.30, b10[1] + 0.10, "$b_0^1$", fontsize=8.6, color=TEAL)
    ax.text(b11[0] + 0.08, b11[1] + 0.10, "$b_1^1$", fontsize=8.6, color=TEAL)
    ax.plot([b10[0], b11[0]], [b10[1], b11[1]], color=TEAL, lw=1.2, ls=(0, (3, 3)))
    b20 = (1 - t) * b10 + t * b11
    ax.plot(*b20, "o", ms=6.5, color=RED, zorder=8)
    ax.text(b20[0] + 0.10, b20[1] - 0.22, "$b_0^2$ = 曲线上的点", fontsize=8.8, color=RED)
    ts = np.linspace(0, 1, 120)
    curve = np.array([bez(P, s) for s in ts])
    ax.plot(curve[:, 0], curve[:, 1], color=ORANGE, lw=2.2, zorder=5)
    ax.text(4.10, 2.55, "每一层就是一次 lerp：", fontsize=9.2, color=INK)
    ax.text(4.10, 2.18, r"$b_i^{k}=(1-t)\,b_i^{k-1}+t\,b_{i+1}^{k-1}$", fontsize=10.5,
            color=TEAL)
    ax.text(4.10, 1.62, "n+1 个点 → n 个 → n-1 个 → … → 1 个", fontsize=8.8, color=MUTED)
    ax.text(4.10, 1.28, "最后一层的那个点就是曲线上的 $x(t)$", fontsize=8.8, color=RED)
    ax.text(4.10, 0.80, "这个算法只需要加法乘法和 lerp，不需要任何多项式", fontsize=8.6,
            color=GREEN)
    ax.text(4.10, 0.48, "——所以它在硬件和字体渲染里极其常用", fontsize=8.6, color=MUTED)
    save(fig, "d08-de-casteljau.png")


# ------------------------------------------------- d09 三次 de Casteljau 金字塔
def d09():
    fig, ax = canvas(9.4, 3.6, (0, 9.4), (0, 3.6), eq=False)
    ax.text(0.30, 3.34, "三次的情况：一个「系数金字塔」", fontsize=10.2, color=INK,
            fontweight="bold")
    rows = [["$b_0$", "$b_1$", "$b_2$", "$b_3$"],
            ["$b_0^1$", "$b_1^1$", "$b_2^1$"],
            ["$b_0^2$", "$b_1^2$"],
            ["$b_0^3=x(t)$"]]
    xs0, dx, dy = 0.75, 1.55, 0.72
    for r, row in enumerate(rows):
        y = 2.55 - r * dy
        x0 = xs0 + r * dx / 2
        for i, lab in enumerate(row):
            x = x0 + i * dx
            c = [PURPLE, TEAL, BLUE, RED][r]
            ax.text(x, y, lab, fontsize=9.2, color=c, ha="center", va="center")
            if r < 3 and i < len(rows[r + 1]):
                for tgt in (x, x + dx):
                    arrow(ax, (x, y - 0.16), (tgt, y - dy + 0.20), color="#cbd5e1",
                          lw=0.9, ms=8)
    ax.text(6.30, 2.75, "每条向下的箭头都是一次 lerp", fontsize=9.0, color=INK)
    ax.text(6.30, 2.40, "向右下 = 乘 $t$", fontsize=9.0, color=ORANGE)
    ax.text(6.30, 2.08, "向左下 = 乘 $(1-t)$", fontsize=9.0, color=TEAL)
    ax.text(6.30, 1.55, "所以最后那个点其实是", fontsize=9.0, color=INK)
    ax.text(6.30, 1.20, "所有 $(1-t)$ 与 $t$ 的组合的加权和", fontsize=8.8, color=MUTED)
    ax.text(6.30, 0.72, "把它写开，就得到 Bernstein 形式", fontsize=9.2, color=ORANGE)
    ax.text(0.75, 0.22, "金字塔的层数 = 多项式次数；节点数 = 控制点数", fontsize=8.8,
            color=MUTED)
    save(fig, "d09-pyramid.png")


# ------------------------------------------------- d10 凸包性质
def d10():
    fig, ax = canvas(9.2, 3.6, (0, 9.2), (0, 3.6))
    ax.text(0.30, 3.34, "凸包性质：曲线一定在控制多边形的凸包内", fontsize=10.2,
            color=INK, fontweight="bold")
    P = np.array([[0.70, 1.00], [1.55, 2.85], [3.05, 2.55], [3.75, 1.05]])
    # 凸包（这里控制多边形本身就是凸的，画填充）
    ax.add_patch(Polygon(P, closed=True, facecolor="#f3e8ff", ec=PURPLE, lw=1.2,
                         alpha=0.6))
    ax.plot(np.append(P[:, 0], P[0, 0]), np.append(P[:, 1], P[0, 1]),
            ls=(0, (4, 3)), color=PURPLE, lw=1.0)
    for p, lab in zip(P, ["$b_0$", "$b_1$", "$b_2$", "$b_3$"]):
        ax.plot(*p, "o", ms=6, color=PURPLE, zorder=7)
        ax.text(p[0] - 0.05, p[1] - 0.26, lab, fontsize=9.0, color=PURPLE)
    curve = bez_curve(P)
    ax.plot(curve[:, 0], curve[:, 1], color=ORANGE, lw=2.4, zorder=5)
    ax.text(4.35, 2.45, "为什么有用：", fontsize=9.2, color=INK)
    ax.text(4.35, 2.10, "① 范围可预测（做裁剪/求交时先测凸包）", fontsize=8.6, color=MUTED)
    ax.text(4.35, 1.78, "② 控制点不会「失控」带出奇怪的曲线", fontsize=8.6, color=MUTED)
    ax.text(4.35, 1.42, "③ 求交时可以先用凸包做剔除", fontsize=8.6, color=MUTED)
    ax.text(4.35, 0.95, "条件（讲义 P101）：", fontsize=8.8, color=ORANGE)
    ax.text(4.35, 0.62, r"$\sum_i b_i(u)=1$ 且 $b_i(u)\geq 0$", fontsize=9.4, color=TEAL)
    ax.text(4.35, 0.25, "这两条恰好就是 Bernstein 基函数的性质", fontsize=8.6, color=MUTED)
    save(fig, "d10-convex-hull.png")


# ------------------------------------------------- d11 细分
def d11():
    fig, ax = canvas(9.6, 3.4, (0, 9.6), (0, 3.4))
    ax.text(0.30, 3.14, "细分：在 $u=1/2$ 处切开，两半各自还是 Bézier", fontsize=10.2,
            color=INK, fontweight="bold")
    P = np.array([[0.70, 1.05], [1.45, 2.75], [3.05, 2.45], [3.75, 1.00]])
    ax.plot(np.append(P[:, 0], P[0, 0]), np.append(P[:, 1], P[0, 1]), ls=(0, (4, 3)),
            color="#cbd5e1", lw=1.0)
    for p in P:
        ax.plot(*p, "o", ms=5, color=PURPLE, zorder=7)
    curve = bez_curve(P)
    ax.plot(curve[:, 0], curve[:, 1], color=ORANGE, lw=2.2)
    # 在 t=1/2 处细分
    t = 0.5
    b01 = (1 - t) * P[0] + t * P[1]
    b11 = (1 - t) * P[1] + t * P[2]
    b21 = (1 - t) * P[2] + t * P[3]
    b02 = (1 - t) * b01 + t * b11
    b12 = (1 - t) * b11 + t * b21
    b03 = (1 - t) * b02 + t * b12
    left = np.array([P[0], b01, b02, b03])
    right = np.array([b03, b12, b21, P[3]])
    for seg, c in [(left, TEAL), (right, BLUE)]:
        ax.plot(np.append(seg[:, 0], seg[0, 0]), np.append(seg[:, 1], seg[0, 1]),
                ls=(0, (2, 2)), color=c, lw=1.0)
        for p in seg:
            ax.plot(*p, "o", ms=4.2, color=c, zorder=8)
    ax.plot(*b03, "o", ms=7, color=RED, zorder=9)
    ax.text(b03[0] + 0.10, b03[1] + 0.12, "切点", fontsize=8.4, color=RED)

    ax.text(4.35, 2.60, "关键结论：", fontsize=9.2, color=INK)
    ax.text(4.35, 2.25, "切开后的两段，各自的控制点", fontsize=8.8, color=MUTED)
    ax.text(4.35, 1.95, "可以由原来四个点线性组合得到", fontsize=8.8, color=MUTED)
    ax.text(4.35, 1.55, r"$P_1=H_{Z1}P,\quad P_2=H_{Z2}P$", fontsize=9.6, color=TEAL)
    ax.text(4.35, 1.10, "而 $H_{Z}$ 的每行和为 1 且非负", fontsize=8.8, color=ORANGE)
    ax.text(4.35, 0.78, "⇒ 新控制点仍在原控制点的凸包内", fontsize=8.8, color=ORANGE)
    ax.text(4.35, 0.42, "⇒ 反复细分，控制多边形收敛到曲线本身", fontsize=8.8, color=GREEN)
    save(fig, "d11-subdivision.png")


# ------------------------------------------------- d12 连续性
def d12():
    fig, ax = canvas(10.0, 3.4, (0, 10.0), (0, 3.4))
    ax.text(0.30, 3.14, "拼接两段曲线：C0 / C1 / C2 的差别在「连接处有多顺」", fontsize=10.2,
            color=INK, fontweight="bold")
    cases = [("$C^0$：位置连续", "两段端点相接", 0.55, TEAL),
             ("$C^1$：一阶连续", "切线方向一致，且长度比 1:1", 3.65, ORANGE),
             ("$C^2$：二阶连续", "再加二阶参数导数向量相等", 6.75, PURPLE)]
    for name, note, ox, c in cases:
        # All panels use quadratic segments, each parameterized on [0, 1].
        A = np.array([[ox, 1.45], [ox + 0.55, 2.00], [ox + 1.15, 2.15]])
        B = np.array([A[2], [ox + 1.75, 1.45], [ox + 2.40, 1.30]])
        if name.startswith("$C^1"):
            B[1] = 2 * A[2] - A[1]
        if name.startswith("$C^2"):
            B[1] = 2 * A[2] - A[1]
            B[2] = 2 * B[1] - B[0] + A[2] - 2 * A[1] + A[0]
        assert np.allclose(A[2], B[0])
        if not name.startswith("$C^0"):
            assert np.allclose(A[2] - A[1], B[1] - B[0])
        if name.startswith("$C^2"):
            assert np.allclose(A[2] - 2*A[1] + A[0], B[2] - 2*B[1] + B[0])
        for seg in (A, B):
            ax.plot(seg[:, 0], seg[:, 1],
                    ls=(0, (3, 2)), color="#cbd5e1", lw=0.9)
            ax.plot(bez_curve(seg)[:, 0], bez_curve(seg)[:, 1], color=c, lw=2.0)
        ax.text(ox + 1.15, 0.72, name, fontsize=8.8, color=c, ha="center",
                fontweight="bold")
        ax.text(ox + 1.15, 0.42, note, fontsize=7.6, color=MUTED, ha="center")
    ax.text(0.30, 0.08, "C1 的条件：$a_n=b_0=\\frac{1}{2}(a_{n-1}+b_1)$ —— "
                        "（同次数、同参数区间）；三点共线且等距",
            fontsize=8.6, color=MUTED)
    save(fig, "d12-continuity.png")


# ------------------------------------------------- d13 双三次曲面片
def d13():
    fig, ax = canvas(9.4, 3.8, (0, 9.4), (0, 3.8), eq=False)
    ax.text(0.30, 3.54, "双三次 Bézier 面片：4×4 控制点，两个方向各三次", fontsize=10.2,
            color=INK, fontweight="bold")
    # 4x4 控制点网格（斜投影）
    def proj(i, j, z=0.0):
        return np.array([1.10 + i * 0.52 + j * 0.26, 1.10 + j * 0.42 + z])
    for i in range(4):
        for j in range(4):
            p = proj(i, j)
            ax.plot(*p, "o", ms=4.2, color=PURPLE, zorder=6)
    for i in range(4):
        pts = [proj(i, j) for j in range(4)]
        ax.plot([p[0] for p in pts], [p[1] for p in pts], ls=(0, (2, 2)),
                color="#cbd5e1", lw=0.8)
    for j in range(4):
        pts = [proj(i, j) for i in range(4)]
        ax.plot([p[0] for p in pts], [p[1] for p in pts], ls=(0, (2, 2)),
                color="#cbd5e1", lw=0.8)
    # 高亮一行（一条 u 曲线）
    jj = 2
    pts = [proj(i, jj, 0.0) for i in range(4)]
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color=ORANGE, lw=2.2, zorder=7)
    ax.text(proj(3, jj)[0] + 0.16, proj(3, jj)[1] + 0.06, "一条 u 曲线", fontsize=8.4,
            color=ORANGE)

    ax.text(4.75, 3.00, "构造思路（P171）：", fontsize=9.2, color=INK)
    ax.text(4.75, 2.65, "① 每行 4 个控制点 → 一条 u 方向 Bézier 曲线", fontsize=8.6,
            color=MUTED)
    ax.text(4.75, 2.35, "② 四条曲线上「同参数」的点 → 4 个新控制点", fontsize=8.6,
            color=MUTED)
    ax.text(4.75, 2.05, "③ 这 4 个点定义一条 v 方向的「移动曲线」", fontsize=8.6, color=MUTED)
    ax.text(4.75, 1.75, "④ 移动曲线扫过整个面片", fontsize=8.6, color=MUTED)
    ax.text(4.75, 1.30, "所以求值可以「分离」成两次一维：", fontsize=9.0, color=ORANGE)
    ax.text(4.75, 0.95, r"$x(u,v)=\mathcal{P}_3(u)\,\beta_Z\,P\,\beta_Z^{T}\,\mathcal{P}_3(v)^{T}$",
            fontsize=10.5, color=TEAL)
    ax.text(4.75, 0.45, "先按 u 求值（每行一次），再按 v 求值 —— 这就是「可分离」", fontsize=8.4,
            color=MUTED)
    ax.text(0.30, 0.10, "代价：16 个控制点。工程上常用「面片拼起来」覆盖大曲面（Catmull 的 Gumbo 模型、Utah Teapot 都是这么做的）",
            fontsize=8.4, color=MUTED)
    save(fig, "d13-bezier-patch.png")


# ------------------------------------------------- d14 高阶振荡
def d14():
    fig, ax = canvas(9.4, 3.2, (0, 9.4), (0, 3.2), eq=False)
    ax.text(0.30, 2.94, "为什么不用一个高阶多项式直接插所有点", fontsize=10.2, color=INK,
            fontweight="bold")
    n = 11
    xs = np.linspace(0, 1, n)
    ys = np.array([0.5, 0.75, 0.55, 0.85, 0.45, 0.9, 0.5, 0.8, 0.55, 0.75, 0.5])
    ax.plot(0.70 + 3.3 * xs, 0.55 + 1.45 * (ys - 0.4) / 0.6, "o", ms=4.5, color=PURPLE,
            zorder=6)
    # 拉格朗日插值的高阶振荡（用 np.polyfit 近似演示）
    coef = np.polyfit(xs, ys, n - 1)
    tt = np.linspace(0, 1, 800)
    yy = np.polyval(coef, tt)
    ax.plot(0.70 + 3.3 * tt, 0.55 + 1.45 * (yy - 0.4) / 0.6, color=RED, lw=1.6)
    ax.text(4.35, 2.55, "高阶多项式插值在端点附近剧烈振荡", fontsize=9.2, color=RED)
    ax.text(4.35, 2.20, "（Runge 现象）", fontsize=8.6, color=MUTED)
    ax.text(4.35, 1.75, "三个实际问题：", fontsize=9.0, color=INK)
    ax.text(4.35, 1.45, "• 不稳定（数值误差被放大）", fontsize=8.6, color=MUTED)
    ax.text(4.35, 1.15, "• 无局部性（改一个点整条变）", fontsize=8.6, color=MUTED)
    ax.text(4.35, 0.85, "• 求值贵（高次幂）", fontsize=8.6, color=MUTED)
    ax.text(4.35, 0.42, "⇒ 分段三次：每段只需 4 个控制，且 C1/C2 可以拼出来", fontsize=8.8,
            color=TEAL)
    save(fig, "d14-high-order.png")


# ------------------------------------------------- d15 端点性质
def d15():
    fig, ax = canvas(9.0, 3.4, (0, 9.0), (0, 3.4))
    ax.text(0.30, 3.14, "Bézier 的两个端点性质：过端点、且切线可控", fontsize=10.2,
            color=INK, fontweight="bold")
    P = np.array([[0.70, 1.05], [1.60, 2.60], [2.90, 2.55], [3.80, 1.00]])
    curve = bez_curve(P)
    ax.plot(curve[:, 0], curve[:, 1], color=ORANGE, lw=2.4)
    ax.plot(np.append(P[:, 0], P[0, 0]), np.append(P[:, 1], P[0, 1]), ls=(0, (4, 3)),
            color="#cbd5e1", lw=1.0)
    for p, lab in zip(P, ["$b_0$", "$b_1$", "$b_2$", "$b_3$"]):
        ax.plot(*p, "o", ms=6, color=PURPLE, zorder=7)
        ax.text(p[0] - 0.05, p[1] - 0.26, lab, fontsize=9.0, color=PURPLE)
    arrow(ax, tuple(P[0]), tuple(P[0] + 0.85 * (P[1] - P[0]) / np.linalg.norm(P[1] - P[0])),
          color=TEAL, lw=2.0)
    arrow(ax, tuple(P[3]), tuple(P[3] + 0.85 * (P[2] - P[3]) / np.linalg.norm(P[2] - P[3])),
          color=TEAL, lw=2.0)
    ax.text(4.25, 2.55, r"$b(0)=b_0,\quad b(1)=b_3$", fontsize=10, color=INK)
    ax.text(4.25, 2.00, r"$b'(0)=3(b_1-b_0)$", fontsize=10, color=TEAL)
    ax.text(4.25, 1.55, r"$b'(1)=3(b_3-b_2)$", fontsize=10, color=TEAL)
    ax.text(4.25, 1.05, "所以「控制点的连线」就是端点切线方向", fontsize=8.8, color=ORANGE)
    ax.text(4.25, 0.70, "这就是 Bézier 相比 Hermite 的便利：", fontsize=8.8, color=INK)
    ax.text(4.25, 0.40, "用户只放点，不用输入切向量（切线由点的位置暗示）", fontsize=8.6,
            color=MUTED)
    save(fig, "d15-endpoint.png")


# ------------------------------------------------- d16 变换不变性
def d16():
    fig, ax = canvas(9.6, 3.4, (0, 9.6), (0, 3.4))
    ax.text(0.30, 3.14, "仿射不变性：先变换控制点、再求曲线 = 先求曲线、再变换", fontsize=10.2,
            color=INK, fontweight="bold")
    P = np.array([[0.65, 1.00], [1.45, 2.55], [2.75, 2.35], [3.45, 1.00]])
    curve = bez_curve(P)
    ax.plot(curve[:, 0], curve[:, 1], color=TEAL, lw=2.2)
    for p in P:
        ax.plot(*p, "o", ms=4.5, color=PURPLE, zorder=6)
    ax.text(2.05, 0.70, "原曲线", fontsize=8.6, color=TEAL, ha="center")

    # 变换后的曲线
    M = np.array([[1.0, 0.45], [0.0, 1.0]])
    Q = P @ M.T + np.array([3.55, 0.15])
    curve2 = curve @ M.T + np.array([3.55, 0.15])
    ax.plot(curve2[:, 0], curve2[:, 1], color=ORANGE, lw=2.2)
    for p in Q:
        ax.plot(*p, "o", ms=4.5, color=PURPLE, zorder=6)
    ax.text(5.20, 0.62, "错切后的曲线", fontsize=8.6, color=ORANGE, ha="center")

    ax.text(4.45, 2.70, "两条路等价（仿射变换）：", fontsize=9.0, color=INK)
    ax.text(4.45, 2.35, "① 变换所有控制点 → 求值", fontsize=8.6, color=TEAL)
    ax.text(4.45, 2.05, "② 求值 → 变换曲线", fontsize=8.6, color=ORANGE)
    box(ax, 6.85, 1.75, 2.55, 0.95, "但**透视**变换下不等价\n（Bézier 不保透视；NURBS 才保）",
        fs=8.2, fc="#fff7ed", ec=ORANGE, tc="#7c3a00")
    ax.text(0.30, 0.28, "实用意义：GPU 里只变换控制点（4 个点）就够了，不用细分整条曲线再变换",
            fontsize=8.8, color=GREEN)
    save(fig, "d16-affine-invariance.png")


if __name__ == "__main__":
    print("generating ->", OUT)
    for fn in [d01, d02, d03, d04, d05, d06, d07, d08,
               d09, d10, d11, d12, d13, d14, d15, d16]:
        fn()
    print("done: 16 diagrams")
