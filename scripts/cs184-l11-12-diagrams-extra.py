# -*- coding: utf-8 -*-
"""CS184 · L11–12 追加图解（d17–d22），按 v2 标准补齐到 22 张。

风格：一图一关系、无坐标轴、颜色语义固定
（teal=主链路，orange=焦点，purple=数据，red=错误，灰=说明）。
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
                                    "notes", "cs184-11-12-meshes-geometry", "diagrams"))
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


def box(ax, x, y, w, h, text, fc=FILL, ec=STROKE, tc=INK, fs=8.8, lw=1.4,
        pad=0.07, rad=0.13):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle=f"round,pad={pad},rounding_size={rad}",
                                facecolor=fc, edgecolor=ec, linewidth=lw, zorder=3))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            color=tc, zorder=4, linespacing=1.5)


def arrow(ax, p, q, color=TEAL, lw=1.6, ls="-", z=5, ms=12, rad=0.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=ms, color=color,
                                 lw=lw, linestyle=ls, zorder=z,
                                 connectionstyle=f"arc3,rad={rad}",
                                 shrinkA=1, shrinkB=1))


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=DPI, bbox_inches="tight",
                facecolor="white", pad_inches=0.12)
    plt.close(fig)
    print("  ", name)


# ------------------------------------------------- d17 Euler 与亏格
def d17():
    fig, ax = canvas(10.2, 3.2, (0, 10.2), (0, 3.2))
    ax.text(0.30, 2.94, "Euler 示性数 V−E+F = 2−2g：亏格就是洞的个数", fontsize=10.2,
            color=INK, fontweight="bold")
    # 球
    c = (1.45, 1.55)
    ax.add_patch(Circle(c, 0.72, facecolor="#e6f7f4", ec=TEAL, lw=1.5))
    ax.plot([c[0] - 0.55, c[0] + 0.55], [c[1], c[1]], color=TEAL, lw=1.0)
    th = np.linspace(0, np.pi, 40)
    ax.plot(c[0] + 0.72 * np.cos(th), c[1] + 0.72 * np.sin(th) * 0.35, color=TEAL, lw=0.8)
    ax.text(c[0], 0.55, "球面  $g=0$", fontsize=9.0, color=TEAL, ha="center")
    ax.text(c[0], 0.22, "$V-E+F = 2$", fontsize=9.2, color=TEAL, ha="center")

    # 环面
    cx, cy = 4.90, 1.55
    for r, w in [(0.85, 1.6), (0.42, 1.4)]:
        th = np.linspace(0, 2 * np.pi, 100)
        ax.plot(cx + r * np.cos(th), cy + r * 0.45 * np.sin(th), color=ORANGE, lw=w)
    ax.text(cx, 0.55, "环面  $g=1$", fontsize=9.0, color=ORANGE, ha="center")
    ax.text(cx, 0.22, "$V-E+F = 0$", fontsize=9.2, color=ORANGE, ha="center")

    # 双环面
    dx, dy = 8.35, 1.55
    for off in (-0.42, 0.42):
        for r, w in [(0.62, 1.5), (0.28, 1.2)]:
            th = np.linspace(0, 2 * np.pi, 100)
            ax.plot(dx + off + r * np.cos(th), dy + r * 0.5 * np.sin(th),
                    color=PURPLE, lw=w)
    ax.text(dx, 0.55, "双环面  $g=2$", fontsize=9.0, color=PURPLE, ha="center")
    ax.text(dx, 0.22, "$V-E+F = -2$", fontsize=9.2, color=PURPLE, ha="center")

    ax.text(0.30, 0.02, "用途：加载网格后算一次 V−E+F。不等于 2−2g 就说明有洞 / 重复面 / 非流形 —— "
                        "这是加载器里最常见的一行自检", fontsize=8.4, color=MUTED)
    save(fig, "d17-euler-genus.png")


# ------------------------------------------------- d18 翻边时的指针重排
def d18():
    fig, ax = canvas(10.0, 3.6, (0, 10.0), (0, 3.6))
    ax.text(0.30, 3.34, "翻边（flip）：几何上换一条对角线，代码上要改 6 个指针", fontsize=10.2,
            color=INK, fontweight="bold")
    # 左：之前
    A, B, Cc, D = (1.10, 1.05), (3.10, 1.05), (2.10, 2.55), (2.10, 1.05)
    tri(ax, [A, Cc, D], fc="#e0f2fe", ec=BLUE, lw=1.1)
    tri(ax, [Cc, B, D], fc="#f3e8ff", ec=PURPLE, lw=1.1)
    for p, lab in [(A, "a"), (B, "b"), (Cc, "c"), (D, "d")]:
        ax.plot(*p, "o", ms=4.5, color=INK, zorder=8)
        ax.text(p[0] - 0.16, p[1] + 0.10, lab, fontsize=8.4, color=INK)
    ax.plot([Cc[0], D[0]], [Cc[1], D[1]], color=RED, lw=2.2, zorder=6)
    ax.text(2.10, 0.72, "公共边 c–d", fontsize=7.8, color=RED, ha="center")
    ax.text(1.45, 2.85, "翻转前：两个三角形", fontsize=8.2, color=MUTED, ha="center")

    arrow(ax, (3.40, 1.80), (4.05, 1.80), color=MUTED, lw=1.4)
    ax.text(3.72, 2.02, "flip", fontsize=8.2, color=MUTED, ha="center")

    # 右：之后
    ox = 4.35
    A2, B2, C2, D2 = (ox + 0.55, 1.05), (ox + 2.55, 1.05), (ox + 1.55, 2.55), (ox + 1.55, 1.05)
    tri(ax, [A2, D2, C2], fc="#e6f7f4", ec=TEAL, lw=1.1)
    tri(ax, [D2, B2, C2], fc="#fff7ed", ec=ORANGE, lw=1.1)
    for p, lab in [(A2, "a"), (B2, "b"), (C2, "c"), (D2, "d")]:
        ax.plot(*p, "o", ms=4.5, color=INK, zorder=8)
        ax.text(p[0] - 0.16, p[1] + 0.10, lab, fontsize=8.4, color=INK)
    ax.plot([A2[0], B2[0]], [A2[1], B2[1]], color=RED, lw=2.2, zorder=6)
    ax.text(ox + 1.55, 0.72, "新公共边 a–b", fontsize=7.8, color=RED, ha="center")
    ax.text(ox + 1.55, 2.85, "翻转后：同样的四个顶点", fontsize=8.2, color=MUTED, ha="center")

    ax.text(7.55, 2.60, "要改的指针：", fontsize=8.8, color=INK)
    for i, s in enumerate(["① 两条半边的 vertex",
                           "② 两条半边的 twin",
                           "③ 四条外圈的 next",
                           "④ 两个面的 halfedge",
                           "⑤ 两个三角形的 v[]",
                           "⑥ 两条边的 halfedge"]):
        ax.text(7.75, 2.30 - i * 0.27, s, fontsize=7.6, color=MUTED)
    box(ax, 7.55, 0.50, 2.30, 0.55, "顶点/边/面的总数不变", fs=7.8, fc="#e6f7f4",
        ec=TEAL, tc=TEAL)
    save(fig, "d18-halfedge-flip.png")


def tri(ax, pts, fc="#dbeafe", ec=BLUE, lw=1.2, z=2):
    ax.add_patch(Polygon(pts, closed=True, facecolor=fc, edgecolor=ec, linewidth=lw,
                         zorder=z))


# ------------------------------------------------- d19 QEM 的最优位置
def d19():
    fig, ax = canvas(9.8, 3.4, (0, 9.8), (0, 3.4))
    ax.text(0.30, 3.14, "QEM 不只是「合并到中点」—— 它还能解出最优位置", fontsize=10.2,
            color=INK, fontweight="bold")
    # 两个平面 + 等值线
    ax.plot([0.55, 3.55], [1.30, 1.85], color=BLUE, lw=1.6)
    ax.plot([0.55, 3.55], [2.35, 1.55], color=PURPLE, lw=1.6)
    ax.text(3.60, 1.86, "平面 1", fontsize=7.6, color=BLUE)
    ax.text(3.60, 1.36, "平面 2", fontsize=7.6, color=PURPLE)
    # 二次型等值线（椭圆）
    cx, cy = 2.30, 1.72
    for k, r in enumerate([0.18, 0.36, 0.54]):
        th = np.linspace(0, 2 * np.pi, 100)
        ax.plot(cx + r * np.cos(th) * 1.15, cy + r * np.sin(th) * 0.75,
                color="#fdba74", lw=0.8, ls=(0, (3, 3)))
    ax.plot(cx, cy, "o", ms=6.5, color=GREEN, zorder=8)
    ax.text(cx + 0.10, cy + 0.16, "最优点", fontsize=7.8, color=GREEN)
    # 边的两个端点 + 中点
    p1, p2 = np.array([1.10, 1.28]), np.array([3.45, 2.32])
    ax.plot(*p1, "o", ms=5, color=INK, zorder=8)
    ax.plot(*p2, "o", ms=5, color=INK, zorder=8)
    m = (p1 + p2) / 2
    ax.plot(*m, "o", ms=5.5, color=RED, zorder=8)
    ax.text(m[0] + 0.06, m[1] - 0.26, "边中点", fontsize=7.6, color=RED)

    ax.text(4.85, 2.65, "三种选新位置的方式（由差到好）：", fontsize=8.8, color=INK)
    ax.text(5.05, 2.32, "① 两个端点之一 —— 最省，但形状退化", fontsize=7.8, color=MUTED)
    ax.text(5.05, 2.04, "② 边中点 —— 折中，够用", fontsize=7.8, color=MUTED)
    ax.text(5.05, 1.76, "③ 解 $\\partial D/\\partial v=0$ —— 最准", fontsize=7.8, color=GREEN)
    ax.text(4.85, 1.35, "最优解就是一个 3×3 线性方程组：", fontsize=8.4, color=INK)
    ax.text(5.05, 1.02, r"$q_{11}v_x+q_{12}v_y+q_{13}v_z=-q_{14}$", fontsize=8.0, color=TEAL)
    ax.text(5.05, 0.78, r"$q_{12}v_x+q_{22}v_y+q_{23}v_z=-q_{24}$", fontsize=8.0, color=TEAL)
    ax.text(5.05, 0.54, r"$q_{13}v_x+q_{23}v_y+q_{33}v_z=-q_{34}$", fontsize=8.0, color=TEAL)
    ax.text(4.85, 0.20, "矩阵奇异（近似共面）时退回中点", fontsize=7.6, color=RED)
    save(fig, "d19-qem-optimal.png")


# ------------------------------------------------- d20 三类点的位置
def d20():
    fig, ax = canvas(9.8, 3.4, (0, 9.8), (0, 3.4))
    ax.text(0.30, 3.14, "Loop vs Catmull-Clark：同样的「三类新点」，不同的网格", fontsize=10.2,
            color=INK, fontweight="bold")
    # Loop（三角形）
    ax.text(1.75, 2.85, "Loop：三角形网格", fontsize=8.6, color=TEAL, ha="center")
    A, B, Cc = (0.70, 1.05), (2.80, 1.05), (1.75, 2.45)
    tri(ax, [A, B, Cc], fc="#e6f7f4", ec=TEAL, lw=1.2)
    for p in (A, B, Cc):
        ax.plot(*p, "o", ms=4.5, color=TEAL, zorder=8)
    M = [((A[0]+B[0])/2, (A[1]+B[1])/2), ((B[0]+Cc[0])/2, (B[1]+Cc[1])/2),
         ((Cc[0]+A[0])/2, (Cc[1]+A[1])/2)]
    for p in M:
        ax.plot(*p, "o", ms=4.2, color=ORANGE, zorder=8)
    G = ((A[0]+B[0]+Cc[0])/3, (A[1]+B[1]+Cc[1])/3)
    ax.plot(*G, "o", ms=5, color=PURPLE, zorder=8)
    ax.text(G[0] + 0.10, G[1] - 0.22, "只切不加中心点", fontsize=7.2, color=PURPLE)
    ax.text(1.75, 0.62, "4 个三角形；边中点各加一个点", fontsize=7.6, color=MUTED,
            ha="center")

    # Catmull-Clark（四边形）
    ox = 4.55
    ax.text(ox + 1.35, 2.85, "Catmull-Clark：四边形网格", fontsize=8.6, color=ORANGE,
            ha="center")
    Q = [(ox + 0.30, 1.05), (ox + 2.40, 1.05), (ox + 2.40, 2.45), (ox + 0.30, 2.45)]
    ax.add_patch(Polygon(Q, closed=True, facecolor="#fff7ed", ec=ORANGE, lw=1.2))
    for p in Q:
        ax.plot(*p, "o", ms=4.5, color=ORANGE, zorder=8)
    for i in range(4):
        m = ((Q[i][0] + Q[(i+1) % 4][0]) / 2, (Q[i][1] + Q[(i+1) % 4][1]) / 2)
        ax.plot(*m, "o", ms=4.2, color=TEAL, zorder=8)
    Fc = (ox + 1.35, 1.75)
    ax.plot(*Fc, "o", ms=5.5, color=PURPLE, zorder=8)
    ax.text(Fc[0] + 0.10, Fc[1] + 0.10, "新增面心点", fontsize=7.2, color=PURPLE)
    ax.text(ox + 1.35, 0.62, "4 个四边形；面心 + 边中点都加", fontsize=7.6, color=MUTED,
            ha="center")

    ax.text(7.55, 2.55, "关键差别：", fontsize=8.8, color=INK)
    ax.text(7.55, 2.22, "Loop 不加面心点，", fontsize=7.8, color=MUTED)
    ax.text(7.55, 1.95, "所以一个三角形 → 4 个三角形；", fontsize=7.8, color=MUTED)
    ax.text(7.55, 1.55, "CC 加面心点，", fontsize=7.8, color=MUTED)
    ax.text(7.55, 1.28, "所以一个 n 边形 → n 个四边形。", fontsize=7.8, color=MUTED)
    box(ax, 7.55, 0.55, 2.10, 0.55, "CC 会把网格「四边形化」", fs=7.6, fc="#fff7ed",
        ec=ORANGE, tc="#7c3a00")
    save(fig, "d20-loop-vs-cc.png")


# ------------------------------------------------- d21 渐进网格
def d21():
    fig, ax = canvas(10.0, 3.2, (0, 10.0), (0, 3.2))
    ax.text(0.30, 2.94, "渐进网格：一次简化一整条链，任意精度随取随用", fontsize=10.2,
            color=INK, fontweight="bold")
    stages = [("30k", 9, TEAL), ("3k", 7, TEAL), ("300", 5, ORANGE), ("30", 3, RED)]
    for k, (lab, n, c) in enumerate(stages):
        ox = 0.55 + k * 2.40
        cx, cy, R = ox + 0.85, 1.55, 0.78
        for i in range(n):
            th0 = 2 * np.pi * i / n
            th1 = 2 * np.pi * (i + 1) / n
            ax.plot([cx, cx + R * np.cos(th0)], [cy, cy + R * np.sin(th0)],
                    color=c, lw=0.9, alpha=0.8)
            ax.plot([cx + R * np.cos(th0), cx + R * np.cos(th1)],
                    [cy + R * np.sin(th0), cy + R * np.sin(th1)], color=c, lw=1.1)
        ax.text(cx, 0.55, lab + " 三角形", fontsize=8.4, color=c, ha="center",
                fontweight="bold")
        if k < 3:
            arrow(ax, (ox + 1.80, 1.55), (ox + 2.28, 1.55), color=MUTED, lw=1.2, ms=10)
    ax.text(0.30, 0.22, "每一对相邻 LOD 之间差一组「边收缩」记录 —— 存下来就是渐进网格（progressive mesh），"
                        "可以无损地反向恢复细节", fontsize=8.4, color=INK)
    save(fig, "d21-progressive-mesh.png")


# ------------------------------------------------- d22 半边 vs 索引三角形
def d22():
    fig, ax = canvas(10.0, 3.4, (0, 10.0), (0, 3.4), eq=False)
    ax.text(0.30, 3.14, "为什么需要半边：同一个查询，两种结构的代价", fontsize=10.2,
            color=INK, fontweight="bold")
    rows = [("找 v 的一个邻面", "O(n) 扫描整个三角形数组", "O(1)：v->halfedge->face"),
            ("绕 v 走一圈邻居", "O(n) 每步都要全扫", "O(deg(v))"),
            ("找某条边的两个面", "O(n)", "O(1)：h->face, h->twin->face"),
            ("改一个顶点的位置", "要同步所有副本", "只改一处"),
            ("内存", "小（3 个下标/面）", "大（5 个指针/半边）")]
    ax.text(0.55, 2.80, "查询", fontsize=8.4, color=INK, fontweight="bold")
    ax.text(4.05, 2.80, "索引三角形", fontsize=8.4, color=PURPLE, fontweight="bold")
    ax.text(7.05, 2.80, "半边结构", fontsize=8.4, color=TEAL, fontweight="bold")
    for i, (a, b, c) in enumerate(rows):
        y = 2.48 - i * 0.42
        ax.text(0.55, y, a, fontsize=7.8, color=INK)
        ax.text(4.05, y, b, fontsize=7.6, color="#6b21a8")
        ax.text(7.05, y, c, fontsize=7.6, color="#0b4f4a")
    ax.text(0.30, 0.55, "结论：用空间换时间。几百万三角形时，O(n) 的邻域查询是不可接受的 —— "
                        "所以编辑/细分类算法必须用半边（或类似结构）。", fontsize=8.4, color=INK)
    ax.text(0.30, 0.25, "但纯渲染不需要半边：GPU 只要顶点缓冲 + 索引缓冲就够了，"
                        "因为它从不做「查邻居」这种操作。", fontsize=8.4, color=MUTED)
    save(fig, "d22-halfedge-vs-indexed.png")


if __name__ == "__main__":
    print("generating ->", OUT)
    for fn in [d17, d18, d19, d20, d21, d22]:
        fn()
    print("done: 6 extra diagrams")
