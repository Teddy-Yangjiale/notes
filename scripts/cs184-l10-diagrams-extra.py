# -*- coding: utf-8 -*-
"""CS184 · L10 追加图解（d17–d22），按 v2 标准补齐到 22 张。"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Polygon, Circle

plt.rcParams["font.family"] = ["Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

OUT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "src", "content",
                                    "notes", "cs184-10-bezier-curves-surfaces",
                                    "diagrams"))
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


def box(ax, x, y, w, h, text, fc=FILL, ec=STROKE, tc=INK, fs=8.6, lw=1.3,
        pad=0.07, rad=0.12):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle=f"round,pad={pad},rounding_size={rad}",
                                facecolor=fc, edgecolor=ec, linewidth=lw, zorder=3))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            color=tc, zorder=4, linespacing=1.5)


def arrow(ax, p, q, color=TEAL, lw=1.5, ls="-", z=5, ms=11, rad=0.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=ms, color=color,
                                 lw=lw, linestyle=ls, zorder=z,
                                 connectionstyle=f"arc3,rad={rad}",
                                 shrinkA=1, shrinkB=1))


def bez(pts, t):
    pts = np.asarray(pts, dtype=float)
    while len(pts) > 1:
        pts = (1 - t) * pts[:-1] + t * pts[1:]
    return pts[0]


def bez_curve(pts, n=200):
    return np.array([bez(pts, t) for t in np.linspace(0, 1, n)])


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=DPI, bbox_inches="tight",
                facecolor="white", pad_inches=0.12)
    plt.close(fig)
    print("  ", name)


# ------------------------------------------------- d17 Bernstein 权重
def d17():
    fig, ax = canvas(9.6, 3.4, (0, 9.6), (0, 3.4), eq=False)
    ax.text(0.30, 3.14, "Bernstein 权重就是帕斯卡三角的第 n 行除以 2ⁿ", fontsize=10.2,
            color=INK, fontweight="bold")
    rows = [(1, [1]),
            (2, [1, 1]),
            (3, [1, 2, 1]),
            (4, [1, 3, 3, 1]),
            (5, [1, 4, 6, 4, 1])]
    for r, (n, row) in enumerate(rows):
        y = 2.70 - r * 0.46
        ax.text(0.55, y, f"n={n-1}", fontsize=7.8, color=MUTED)
        for c, v in enumerate(row):
            x = 1.45 + (c + (len(rows[-1][1]) - len(row)) / 2) * 0.62
            col = TEAL if n == 4 else "#94a3b8"
            ax.text(x, y, str(v), fontsize=9.0, color=col, ha="center",
                    fontweight="bold" if n == 4 else "normal")
    ax.text(5.05, 2.70, "n=3（三次）时：", fontsize=9.0, color=INK)
    ax.text(5.05, 2.35, "权重 $=(1,3,3,1)/8$", fontsize=9.6, color=TEAL)
    ax.text(5.05, 1.95, r"$=(0.125,\ 0.375,\ 0.375,\ 0.125)$", fontsize=9.0, color=TEAL)
    ax.text(5.05, 1.45, "为什么除以 8：", fontsize=8.6, color=ORANGE)
    ax.text(5.25, 1.15, "$t=\\frac{1}{2}$ 时 $t^k(1-t)^{n-k}=\\frac{1}{2^n}$", fontsize=8.6,
            color=MUTED)
    ax.text(5.05, 0.65, "所以任意 `n` 的权重**必然和为 1**", fontsize=8.6, color=GREEN)
    ax.text(5.05, 0.32, "（这就是「仿射组合」的离散版）", fontsize=8.0, color=MUTED)
    save(fig, "d17-bernstein-pascal.png")


# ------------------------------------------------- d18 de Casteljau 数值
def d18():
    fig, ax = canvas(9.8, 3.8, (0, 9.8), (0, 3.8))
    ax.text(0.30, 3.56, "de Casteljau 走一遍：每一层都是「按 0.6 / 0.4 分点」", fontsize=10.2,
            color=INK, fontweight="bold")
    t = 0.4
    P = [np.array([0.55, 1.05]), np.array([1.75, 2.85]),
         np.array([3.05, 2.65]), np.array([3.95, 1.05])]
    ax.plot([p[0] for p in P], [p[1] for p in P], ls=(0, (4, 3)), color="#cbd5e1", lw=1.0)
    for p, lab in zip(P, ["$b_0$", "$b_1$", "$b_2$", "$b_3$"]):
        ax.plot(*p, "o", ms=5.5, color=PURPLE, zorder=8)
        ax.text(p[0] - 0.10, p[1] - 0.26, lab, fontsize=8.6, color=PURPLE)
    # 第一层
    L1 = [(1 - t) * P[i] + t * P[i + 1] for i in range(3)]
    for p in L1:
        ax.plot(*p, "o", ms=5.0, color=TEAL, zorder=8)
    ax.plot([p[0] for p in L1], [p[1] for p in L1], color=TEAL, lw=1.0, ls=(0, (3, 3)))
    for p, lab, off in [(L1[0], "$b_0^1$", (-0.34, 0.10)), (L1[1], "$b_1^1$", (0.06, 0.16)),
                        (L1[2], "$b_2^1$", (0.10, 0.06))]:
        ax.text(p[0] + off[0], p[1] + off[1], lab, fontsize=8.0, color=TEAL)
    # 第二层
    L2 = [(1 - t) * L1[i] + t * L1[i + 1] for i in range(2)]
    for p in L2:
        ax.plot(*p, "o", ms=5.5, color=BLUE, zorder=8)
    for p, lab in [(L2[0], "$b_0^2$"), (L2[1], "$b_1^2$")]:
        ax.text(p[0] - 0.10, p[1] - 0.26, lab, fontsize=8.0, color=BLUE)
    # 第三层
    L3 = (1 - t) * L2[0] + t * L2[1]
    ax.plot(*L3, "o", ms=6.5, color=RED, zorder=9)
    ax.text(L3[0] + 0.14, L3[1] - 0.30, "$b_0^3=x(0.4)$", fontsize=8.4, color=RED)
    curve = bez_curve(P)
    ax.plot(curve[:, 0], curve[:, 1], color=ORANGE, lw=1.8, zorder=4)

    ax.text(4.45, 2.95, "每一层的坐标（t = 0.4）：", fontsize=8.8, color=INK)
    rows = [("$b_0^1$", "0.6·(0,0) + 0.4·(1,2) = (0.40, 0.80)", TEAL),
            ("$b_1^1$", "0.6·(1,2) + 0.4·(3,2) = (1.80, 2.00)", TEAL),
            ("$b_2^1$", "0.6·(3,2) + 0.4·(4,0) = (3.40, 1.20)", TEAL),
            ("$b_0^2$", "0.6·(0.40,0.80) + 0.4·(1.80,2.00) = (0.96, 1.28)", BLUE),
            ("$b_1^2$", "0.6·(1.80,2.00) + 0.4·(3.40,1.20) = (2.44, 1.68)", BLUE),
            ("$b_0^3$", "0.6·(0.96,1.28) + 0.4·(2.44,1.68) = (1.55, 1.44)", RED)]
    for i, (lab, expr, c) in enumerate(rows):
        ax.text(4.55, 2.62 - i * 0.30, lab, fontsize=7.6, color=c)
        ax.text(5.15, 2.62 - i * 0.30, expr, fontsize=7.0, color=MUTED)
    box(ax, 4.45, 0.45, 5.15, 0.50, "只有加法和乘法 —— 没有任何求幂、没有多项式展开",
        fs=8.0, fc="#e6f7f4", ec=TEAL, tc=TEAL)
    ax.text(0.30, 0.18, "这正是它比 Bernstein 形式更快、更稳的原因（下一张图对比）", fontsize=8.2,
            color=MUTED)
    save(fig, "d18-de-casteljau-numeric.png")


# ------------------------------------------------- d19 导数的控制点
def d19():
    fig, ax = canvas(9.8, 3.4, (0, 9.8), (0, 3.4))
    ax.text(0.30, 3.14, "曲线的导数也是一条 Bézier 曲线（次数低一阶）", fontsize=10.2,
            color=INK, fontweight="bold")
    P = [np.array([0.55, 1.05]), np.array([1.70, 2.70]),
         np.array([2.95, 2.55]), np.array([3.85, 1.05])]
    curve = bez_curve(P, 120)
    ax.plot(curve[:, 0], curve[:, 1], color=TEAL, lw=2.0)
    for p in P:
        ax.plot(*p, "o", ms=4.5, color=PURPLE, zorder=8)
    ax.text(2.20, 0.72, "原曲线（三次，4 个控制点）", fontsize=8.0, color=TEAL, ha="center")

    # 导数控制点（放大显示）
    D = [3 * (P[i + 1] - P[i]) for i in range(3)]
    ox, oy, sc = 5.30, 1.55, 0.42
    Dp = [np.array([ox + d[0] * sc, oy + d[1] * sc]) for d in D]
    dc = bez_curve(Dp, 120)
    ax.plot(dc[:, 0], dc[:, 1], color=ORANGE, lw=2.0)
    for p in Dp:
        ax.plot(*p, "o", ms=4.5, color=ORANGE, zorder=8)
    ax.text(ox + 0.55, 0.72, "导数曲线（二次，3 个控制点）", fontsize=8.0, color=ORANGE,
            ha="center")

    ax.text(3.85, 2.85, "导数的控制点：", fontsize=8.8, color=INK)
    for i in range(3):
        ax.text(4.05, 2.52 - i * 0.28,
                f"$d_{i}$ = 3($b_{i+1}$ − $b_{i}$)", fontsize=8.0, color=ORANGE)
    ax.text(3.85, 1.55, "那个因子 3：", fontsize=8.4, color=RED)
    ax.text(4.05, 1.25, "来自 $n=3$ 的求导", fontsize=8.0, color=MUTED)
    ax.text(3.85, 0.85, "端点切线：", fontsize=8.4, color=INK)
    ax.text(4.05, 0.55, "$b'(0)=3(b_1-b_0)=d_0$", fontsize=8.0, color=TEAL)
    ax.text(4.05, 0.28, "$b'(1)=3(b_3-b_2)=d_2$", fontsize=8.0, color=TEAL)
    save(fig, "d19-hodograph.png")


# ------------------------------------------------- d20 细分矩阵
def d20():
    fig, ax = canvas(9.8, 3.6, (0, 9.8), (0, 3.6), eq=False)
    ax.text(0.30, 3.34, "细分 = 一次矩阵乘法：左半和右半各一个稀疏矩阵", fontsize=10.2,
            color=INK, fontweight="bold")
    ax.text(0.55, 2.95, "左半（$t \\in [0,\\frac{1}{2}]$）的新控制点：", fontsize=8.6, color=TEAL)
    ax.text(0.75, 2.30, "  [ 1    0    0    0 ]", fontsize=8.0, color=INK, family="monospace")
    ax.text(0.75, 2.02, "  [ 1/2  1/2  0    0 ]", fontsize=8.0, color=INK, family="monospace")
    ax.text(0.75, 1.74, "  [ 1/4  2/4  1/4  0 ]", fontsize=8.0, color=INK, family="monospace")
    ax.text(0.75, 1.46, "  [ 1/8  3/8  3/8  1/8]", fontsize=8.0, color=TEAL,
            family="monospace")
    ax.text(3.55, 2.05, "×", fontsize=12, color=MUTED, ha="center", va="center")
    ax.text(3.95, 2.05, "[ b₀ b₁ b₂ b₃ ]ᵀ", fontsize=8.4, color=PURPLE)

    ax.text(5.05, 2.95, "右半（$t \\in [\\frac{1}{2},1]$）：", fontsize=8.6, color=ORANGE)
    ax.text(5.25, 2.30, "  [ 1/8  3/8  3/8  1/8]", fontsize=8.0, color=ORANGE,
            family="monospace")
    ax.text(5.25, 2.02, "  [ 0    1/4  2/4  1/4]", fontsize=8.0, color=INK,
            family="monospace")
    ax.text(5.25, 1.74, "  [ 0    0    1/2  1/2]", fontsize=8.0, color=INK,
            family="monospace")
    ax.text(5.25, 1.46, "  [ 0    0    0    1  ]", fontsize=8.0, color=INK,
            family="monospace")

    ax.text(0.55, 1.00, "注意到什么：", fontsize=8.6, color=INK)
    ax.text(0.75, 0.70, "① 两行是「反向的」—— 右半矩阵是左半的上下翻转", fontsize=8.0,
            color=MUTED)
    ax.text(0.75, 0.44, "② 两行中间那一行相同（1/8, 3/8, 3/8, 1/8）= 切点", fontsize=8.0,
            color=MUTED)
    ax.text(0.75, 0.18, "③ 每行和都是 1 —— 所以新控制点仍在凸包内", fontsize=8.0, color=GREEN)
    save(fig, "d20-subdivision-matrix.png")


# ------------------------------------------------- d21 G1 vs C1
def d21():
    fig, ax = canvas(9.8, 3.4, (0, 9.8), (0, 3.4))
    ax.text(0.30, 3.14, "C1 要求「等长」，G1 只要求「共线」—— 差别在速度连续性", fontsize=10.2,
            color=INK, fontweight="bold")
    # G1：共线但不等长
    A = np.array([0.55, 1.10]); J = np.array([2.35, 1.90])
    B2 = np.array([3.05, 2.45])
    ax.plot([0.95, 1.75], [1.28, 1.60], color=TEAL, lw=2.0)
    ax.plot([1.75, 2.95], [1.60, 2.38], color=ORANGE, lw=2.0)
    ax.plot(*J, "o", ms=5.5, color=RED, zorder=8)
    arrow(ax, tuple(J), tuple(J + (J - np.array([1.75, 1.60])) * 1.9), color=TEAL,
          lw=1.4, ls=(0, (3, 2)))
    arrow(ax, tuple(J), tuple(J + np.array([0.62, 0.50])), color=ORANGE, lw=1.4,
          ls=(0, (3, 2)))
    ax.text(2.45, 2.55, "G1：切线方向一致，长度不等", fontsize=8.2, color=ORANGE)
    ax.text(1.80, 0.80, "两段在接缝处「方向」对齐", fontsize=7.8, color=MUTED, ha="center")
    ax.text(2.20, 3.05, "① 几何连续（G1）", fontsize=8.6, color=ORANGE, ha="center")

    # C1：等长
    ox = 5.10
    ax.plot([ox - 0.10, ox + 0.90], [1.28, 1.60], color=TEAL, lw=2.0)
    ax.plot([ox + 0.90, ox + 1.90], [1.60, 2.10], color=GREEN, lw=2.0)
    J2 = np.array([ox + 0.90, 1.60])
    ax.plot(*J2, "o", ms=5.5, color=RED, zorder=8)
    arrow(ax, tuple(J2 - np.array([0.50, 0.20])), tuple(J2), color=TEAL, lw=1.4)
    arrow(ax, tuple(J2), tuple(J2 + np.array([0.50, 0.20])), color=GREEN, lw=1.4)
    ax.text(ox + 0.55, 2.55, "C1：方向一致且长度相等", fontsize=8.2, color=GREEN)
    ax.text(ox + 0.90, 0.80, "导数完全相等", fontsize=7.8, color=MUTED, ha="center")
    ax.text(ox + 0.90, 3.05, "② 参数连续（C1）", fontsize=8.6, color=GREEN, ha="center")

    box(ax, 7.60, 1.30, 2.05, 1.25, "动画里：\nG1 看起来光滑，\n但速度会突变\n（有「顿」一下）", fs=7.4,
        fc="#fff7ed", ec=ORANGE, tc="#7c3a00")
    ax.text(0.30, 0.20, "数学差别：C1 要求 $b'(t)$ 在两段相等（向量相等）；G1 只要求方向平行"
                        "（$b'(t)$ 差一个正数倍）。", fontsize=8.2, color=INK)
    save(fig, "d21-g1-vs-c1.png")


# ------------------------------------------------- d22 两条求值路线
def d22():
    fig, ax = canvas(10.2, 3.2, (0, 10.2), (0, 3.2), eq=False)
    ax.text(0.30, 2.94, "同一个点，两条算法：几何路线 vs 代数路线", fontsize=10.2,
            color=INK, fontweight="bold")
    ax.text(0.55, 2.60, "① 几何：de Casteljau", fontsize=8.8, color=TEAL)
    for i, s in enumerate(["反复做 lerp（层数 = 次数）", "只用加法乘法", "数值稳定（凸组合）",
                           "天然支持细分", "不需要求幂"]):
        ax.text(0.75, 2.28 - i * 0.26, "• " + s, fontsize=7.6, color=MUTED)
    ax.text(5.35, 2.60, "② 代数：Bernstein", fontsize=8.8, color=ORANGE)
    for i, s in enumerate(["直接算 $t^k(1-t)^{n-k}$", "要算组合数和幂", "高次时数值误差大",
                           "便于求导/分析性质", "便于写成矩阵"]):
        ax.text(5.55, 2.28 - i * 0.26, "• " + s, fontsize=7.6, color=MUTED)
    box(ax, 2.55, 0.30, 5.15, 0.50, "两者结果完全相等（手算 3 与手算 4 已验证）", fs=8.2,
        fc="#e6f7f4", ec=TEAL, tc=TEAL)
    ax.text(0.30, 0.02, "实践建议：求值用 de Casteljau，分析用 Bernstein。渲染器、字体引擎都用前者；"
                        "论文推导和性质证明用后者。", fontsize=8.2, color=INK)
    save(fig, "d22-two-routes.png")


if __name__ == "__main__":
    print("generating ->", OUT)
    for fn in [d17, d18, d19, d20, d21, d22]:
        fn()
    print("done: 6 extra diagrams")
