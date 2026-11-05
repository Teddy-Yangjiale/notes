# -*- coding: utf-8 -*-
"""CS184 课程笔记 · L11–12（网格与几何处理）原创图解

风格遵循 scripts/cs184-notes-standard.md。
颜色语义：teal=主链路，orange=本讲焦点，purple=数据/元素，red=错误/异常，灰=说明
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


def tri(ax, pts, fc="#dbeafe", ec=BLUE, lw=1.2, z=2):
    ax.add_patch(Polygon(pts, closed=True, facecolor=fc, edgecolor=ec, linewidth=lw,
                         zorder=z))


def dot(ax, p, c=INK, ms=5, z=6, face="white"):
    ax.plot(p[0], p[1], "o", ms=ms, color=c, zorder=z, markerfacecolor=face,
            markeredgewidth=1.5)


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=DPI, bbox_inches="tight",
                facecolor="white", pad_inches=0.12)
    plt.close(fig)
    print("  ", name)


# ------------------------------------------------- d01 网格的规模
def d01():
    fig, ax = canvas(10.0, 3.2, (0, 10.0), (0, 3.2), eq=False)
    ax.text(0.30, 2.94, "网格的规模跨了十几个数量级", fontsize=10.4, color=INK,
            fontweight="bold")
    items = [("8 顶点 / 12 三角形\n入门示例", 1.55, TEAL),
             ("2818 万顶点\n5623 万三角形\n「大卫」扫描", 4.55, ORANGE),
             ("万亿级三角形\nGoogle Earth\n航拍重建", 7.75, PURPLE)]
    for text, x, c in items:
        # 用逐渐变密的三角形示意
        n = [2, 6, 10][items.index((text, x, c))]
        for i in range(n):
            for j in range(n - i):
                p = [(x - 0.85) + (i + j) * 0.24, 0.95 + i * 0.17]
                tri(ax, [p, [p[0] + 0.24, p[1]], [p[0] + 0.12, p[1] + 0.17]],
                    fc="white", ec=c, lw=0.5)
        ax.text(x, 0.55, text, fontsize=7.8, color=MUTED, ha="center", linespacing=1.5,
                va="top")
    ax.text(0.30, 2.30, "为什么关心规模：", fontsize=9.2, color=INK)
    ax.text(0.30, 2.00, "• 渲染要光栅化每一个三角形（第 2 讲）", fontsize=8.4, color=MUTED)
    ax.text(0.30, 1.72, "• 存储与传输是真实瓶颈（一个扫描 1 GB+）", fontsize=8.4, color=MUTED)
    ax.text(0.30, 1.44, "• 所以需要「增加/减少/规整」三类操作", fontsize=8.4, color=TEAL)
    save(fig, "d01-mesh-scale.png")


# ------------------------------------------------- d02 索引 vs 列表
def d02():
    fig, ax = canvas(9.8, 3.4, (0, 9.8), (0, 3.4), eq=False)
    ax.text(0.30, 3.14, "同样的网格，两种存法：冗余 vs 共享", fontsize=10.2, color=INK,
            fontweight="bold")
    ax.text(0.60, 2.80, "① 三角形列表（每面存三个坐标）", fontsize=8.8, color=MUTED)
    for k in range(3):
        y = 2.45 - k * 0.42
        ax.text(0.60, y, f"T{k}: (1.0,0.0) (0.0,1.0) (0.0,0.0)", fontsize=7.6,
                color=INK, family="monospace")
    ax.text(0.60, 1.05, "顶点坐标重复存了 3 次", fontsize=8.2, color=RED)
    ax.text(0.60, 0.75, "改一个顶点要改所有用到它的三角形", fontsize=8.2, color=RED)

    ax.text(4.55, 2.80, "② 索引三角形（点表 + 索引表）", fontsize=8.8, color=MUTED)
    for k, s in enumerate(["V0: (1.0,0.0)", "V1: (0.0,1.0)", "V2: (0.0,0.0)"]):
        ax.text(4.55, 2.45 - k * 0.30, s, fontsize=7.6, color=TEAL, family="monospace")
    for k, s in enumerate(["T0: 0 1 2", "T1: 0 2 3", "T2: 1 2 4"]):
        ax.text(6.55, 2.45 - k * 0.30, s, fontsize=7.6, color=PURPLE, family="monospace")
    ax.text(4.55, 1.05, "省内存（顶点只存一次）+ 保证完整性", fontsize=8.2, color=GREEN)
    ax.text(4.55, 0.75, "代价：多了索引这一层间接寻址", fontsize=8.2, color=MUTED)
    ax.text(0.30, 0.22, "GPU 的顶点缓冲（VBO）+ 索引缓冲（IBO）就是这个结构 —— "
                        "也是「顶点着色只跑一次、结果被多个三角形复用」的前提",
            fontsize=8.6, color=INK)
    save(fig, "d02-indexed-vs-list.png")


# ------------------------------------------------- d03 拓扑 vs 几何
def d03():
    fig, ax = canvas(10.4, 3.6, (0, 10.4), (0, 3.6))
    ax.text(0.30, 3.34, "拓扑（谁连谁）与几何（点在哪）是两个独立的东西", fontsize=10.2,
            color=INK, fontweight="bold")

    # ---- 左：同拓扑 / 不同几何（两个三角形并排，连接方式完全一样）
    ax.text(2.10, 3.02, "同拓扑 / 不同几何", fontsize=8.8, color=TEAL, ha="center")
    base = [(0.55, 1.05), (2.05, 1.05), (1.30, 2.20)]
    warp = [(3.05, 1.05), (4.55, 1.05), (4.05, 2.20)]
    for pts, lab in [(base, "原形状"), (warp, "只挪顶点")]:
        tri(ax, pts, fc="#e6f7f4", ec=TEAL, lw=1.4)
        for k, p in enumerate(pts):
            dot(ax, p, TEAL, ms=4.6)
            ax.text(p[0] - 0.16, p[1] + 0.10, f"v{k}", fontsize=7.4, color=TEAL)
    ax.text(1.30, 0.72, "v0-v1-v2", fontsize=7.6, color=MUTED, ha="center")
    ax.text(3.80, 0.72, "v0-v1-v2（同一套）", fontsize=7.6, color=MUTED, ha="center")

    # ---- 右：同几何 / 不同拓扑（同一个四边形，两条不同对角线）
    ax.text(7.55, 3.02, "同几何 / 不同拓扑", fontsize=8.8, color=ORANGE, ha="center")
    for k, diag in enumerate([((0, 2), "对角线 a-c"), ((1, 3), "对角线 b-d")]):
        ox = 5.55 + k * 2.15
        Q = [np.array([ox, 1.05]), np.array([ox + 1.20, 1.05]),
             np.array([ox + 1.20, 2.15]), np.array([ox, 2.15])]
        for a, b in [(0, 1), (1, 2), (2, 3), (3, 0)]:
            ax.plot([Q[a][0], Q[b][0]], [Q[a][1], Q[b][1]], color=ORANGE, lw=1.3)
        i, j = diag[0]
        ax.plot([Q[i][0], Q[j][0]], [Q[i][1], Q[j][1]], color=RED, lw=1.5)
        ax.add_patch(Polygon([Q[0], Q[1], Q[2], Q[3]], closed=True, facecolor="#fff7ed",
                             alpha=0.5, ec="none", zorder=1))
        for p in Q:
            dot(ax, p, ORANGE, ms=4.0)
        ax.text(ox + 0.60, 0.72, diag[1], fontsize=7.4, color=MUTED, ha="center")

    ax.text(0.30, 0.30, "同拓扑才能「逐顶点插值」（做变形动画）；但线性插值不一定语义正确 —— "
                        "旋转 180° 的中间值会「塌成一点」，所以工业界用四元数插值",
            fontsize=8.6, color=INK)
    ax.text(0.30, 0.02, "同几何不同拓扑则影响：法线平均（哪些面算邻居）、细分结果、简化顺序",
            fontsize=8.4, color=MUTED)
    save(fig, "d03-topology-geometry.png")

# ------------------------------------------------- d04 流形
def d04():
    fig, ax = canvas(9.8, 3.4, (0, 9.8), (0, 3.4))
    ax.text(0.30, 3.14, "流形：任何一点附近都「长得像一张平面」", fontsize=10.2, color=INK,
            fontweight="bold")
    # 流形
    ax.text(1.45, 2.85, "流形（manifold）", fontsize=8.8, color=GREEN, ha="center")
    A, B, C, D = (0.70, 1.10), (2.20, 1.10), (1.45, 2.25), (1.45, 1.10)
    tri(ax, [A, C, D], fc="#e6f7f4", ec=TEAL, lw=1.2)
    tri(ax, [C, B, D], fc="#e6f7f4", ec=TEAL, lw=1.2)
    for p in (A, B, C, D):
        dot(ax, p, TEAL)
    ax.text(1.45, 0.72, "每条边恰好 2 个面", fontsize=8.0, color=MUTED, ha="center")

    # 非流形：一条边三个面
    ax.text(4.55, 2.85, "非流形：一条边三个面", fontsize=8.8, color=RED, ha="center")
    P, Q = np.array([4.55, 1.05]), np.array([4.55, 2.15])
    for ang in (20, 160, 265):
        r = np.radians(ang)
        R = np.array([np.cos(r), np.sin(r)]) * 1.0
        tri(ax, [P, Q, Q + R], fc="#fde8e8", ec=RED, lw=1.0)
    ax.plot([P[0], Q[0]], [P[1], Q[1]], color=RED, lw=2.4, zorder=5)
    ax.text(4.55, 0.72, "中间那条边被 3 个面共用", fontsize=8.0, color=MUTED, ha="center")

    # 非流形：两个锥共点
    ax.text(7.55, 2.85, "非流形：顶点处两个锥", fontsize=8.8, color=RED, ha="center")
    for y0 in (1.15, 1.95):
        R = 0.55
        th = np.linspace(0, 2 * np.pi, 40)
        ax.plot(7.55 + R * np.cos(th) * 0.5, y0 + R * np.sin(th) * 0.22,
                color=RED, lw=1.0)
        for k in range(6):
            a = 2 * np.pi * k / 6
            ax.plot([7.55, 7.55 + R * np.cos(a) * 0.5], [1.55 if y0 < 1.5 else 1.55,
                                                          y0 + R * np.sin(a) * 0.22],
                    color=RED, lw=0.8)
    dot(ax, (7.55, 1.55), RED, ms=6)
    ax.text(7.55, 0.72, "共用顶点处「捏」出两个锥", fontsize=8.0, color=MUTED, ha="center")

    ax.text(0.30, 0.30, "判据（讲义 P22）：用任意小球去切表面，切出来的必须是一块「圆盘」。有三个面的边、或两个锥共用的点，都切不出圆盘。",
            fontsize=8.4, color=INK)
    save(fig, "d04-manifold.png")


# ------------------------------------------------- d05 Euler 公式
def d05():
    fig, ax = canvas(9.6, 3.4, (0, 9.6), (0, 3.4))
    ax.text(0.30, 3.14, "Euler 公式：流形网格的拓扑不变量", fontsize=10.2, color=INK,
            fontweight="bold")
    # 立方体
    v = [(0.70, 1.05), (2.35, 1.05), (2.35, 2.55), (0.70, 2.55),
         (1.05, 0.72), (2.70, 0.72), (2.70, 2.22), (1.05, 2.22)]
    E = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4),
         (0, 4), (1, 5), (2, 6), (3, 7)]
    F = [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6),
         (3, 0, 4, 7)]
    for f in F:
        ax.add_patch(Polygon([v[i] for i in f], closed=True, facecolor="#e0f2fe",
                             edgecolor=BLUE, lw=0.8, alpha=0.55, zorder=1))
    for a, b in E:
        ax.plot([v[a][0], v[b][0]], [v[a][1], v[b][1]], color=BLUE, lw=1.2, zorder=3)
    for p in v:
        dot(ax, p, BLUE, ms=4.0)

    ax.text(4.05, 2.55, "#f − #e + #v = 2", fontsize=13, color=INK)
    ax.text(4.05, 1.95, "立方体验算：", fontsize=9.2, color=INK)
    for k, s in enumerate(["面 #f = 6", "边 #e = 12", "顶点 #v = 8"]):
        ax.text(4.35, 1.62 - k * 0.32, s, fontsize=9.0, color=MUTED)
    ax.text(4.35, 0.50, r"$6-12+8=2$", fontsize=11, color=GREEN)
    ax.text(4.05, 0.12, "对「拓扑上等价于球面」的封闭网格成立", fontsize=8.2, color=MUTED)

    box(ax, 6.30, 1.30, 3.10, 1.35,
        "为什么是 2？\n$V-E+F = 2-2g$\n$g$ = 亏格（洞的个数）\n"
        "球 g=0 → 2；环 g=1 → 0",
        fs=8.4, fc="#fff7ed", ec=ORANGE, tc="#7c3a00")
    ax.text(0.30, 0.10, "实用价值：可以用它检查网格是否有拓扑错误（比如漏了一个面、或多了一条边）—— 算出来不等于 2 就说明坏了",
            fontsize=8.4, color=TEAL)
    save(fig, "d05-euler.png")


# ------------------------------------------------- d06 半边结构
def d06():
    fig, ax = canvas(9.4, 3.6, (0, 9.4), (0, 3.6))
    ax.text(0.30, 3.34, "半边结构：每条边拆成两条有向半边，各归属一个面", fontsize=10.2,
            color=INK, fontweight="bold")
    # 两个三角形
    A, B, C, D = (1.10, 1.15), (3.25, 1.15), (2.20, 2.65), (2.20, 1.15)
    tri(ax, [A, B, C], fc="#e0f2fe", ec=BLUE, lw=1.2)
    tri(ax, [A, B, D], fc="#f3e8ff", ec=PURPLE, lw=1.2)
    for p, lab, off in [(A, "v0", (-0.28, -0.05)), (B, "v1", (0.10, -0.05)),
                        (C, "v2", (-0.05, 0.12)), (D, "v3", (-0.05, -0.22))]:
        dot(ax, p, INK, ms=4.5)
        ax.text(p[0] + off[0], p[1] + off[1], lab, fontsize=8.2, color=INK)
    # 上半边（属于上面三角形）
    arrow(ax, (A[0] + 0.10, A[1] + 0.06), (B[0] - 0.10, B[1] + 0.06), color=BLUE,
          lw=1.6, ms=10)
    ax.text((A[0] + B[0]) / 2, A[1] + 0.16, "h", fontsize=8.6, color=BLUE)
    arrow(ax, (B[0] - 0.10, B[1] - 0.06), (A[0] + 0.10, A[1] - 0.06), color=PURPLE,
          lw=1.6, ms=10)
    ax.text((A[0] + B[0]) / 2 + 0.30, A[1] - 0.24, "twin(h)", fontsize=8.2, color=PURPLE)

    ax.text(4.35, 2.75, "每个半边存：", fontsize=9.2, color=INK)
    for k, s in enumerate(["twin：反向的那条半边",
                           "next：同一面内下一条半边",
                           "vertex：指向的顶点",
                           "edge：所属的边",
                           "face：所属的面"]):
        ax.text(4.55, 2.42 - k * 0.30, "• " + s, fontsize=8.4, color=MUTED)
    ax.text(4.35, 0.80, "每个顶点 / 边 / 面只存**一个**半边指针", fontsize=8.6, color=TEAL)
    ax.text(4.35, 0.48, "（图上标 ★ 的那个），其余靠遍历得到", fontsize=8.2, color=MUTED)
    ax.text(0.60, 0.45, "关键设计：", fontsize=8.8, color=ORANGE)
    ax.text(0.60, 0.15, "两条半边互为 twin，就像「胶水」把相邻两个面粘起来", fontsize=8.4,
            color=INK)
    save(fig, "d06-halfedge.png")


# ------------------------------------------------- d07 半边遍历
def d07():
    fig, ax = canvas(9.8, 3.4, (0, 9.8), (0, 3.4))
    ax.text(0.30, 3.14, "半边让「绕着一个面」和「绕着一个点」都变成几行代码", fontsize=10.2,
            color=INK, fontweight="bold")
    # 左：绕面
    A, B, C = (0.65, 1.00), (2.05, 1.00), (1.35, 2.30)
    tri(ax, [A, B, C], fc="#e0f2fe", ec=BLUE, lw=1.3)
    for p0, p1 in [(A, B), (B, C), (C, A)]:
        d = np.array(p1) - np.array(p0)
        d = d / np.linalg.norm(d)
        n = np.array([-d[1], d[0]]) * 0.0
        arrow(ax, tuple(np.array(p0) + d * 0.18), tuple(np.array(p1) - d * 0.18),
              color=TEAL, lw=1.6, ms=10)
    for p in (A, B, C):
        dot(ax, p, INK, ms=4.5)
    ax.text(1.35, 0.72, "绕面：h = h->next", fontsize=8.4, color=TEAL, ha="center")
    ax.text(1.35, 2.52, "例 1：一个面的所有边", fontsize=8.6, color=INK, ha="center")

    # 右：绕点（六边形）
    cx, cy, R = 5.60, 1.55, 0.85
    ring = [(cx + R * np.cos(np.radians(90 + k * 60)),
             cy + R * np.sin(np.radians(90 + k * 60))) for k in range(6)]
    for k in range(6):
        tri(ax, [(cx, cy), ring[k], ring[(k + 1) % 6]], fc="#f3e8ff", ec=PURPLE, lw=0.9)
    for k in range(6):
        ax.plot([cx, ring[k][0]], [cy, ring[k][1]], color=RED, lw=1.6, zorder=5)
        dot(ax, ring[k], PURPLE, ms=3.6)
    dot(ax, (cx, cy), RED, ms=5.5)
    ax.text(cx, 0.55, "绕点：h = h->twin->next", fontsize=8.4, color=RED, ha="center")
    ax.text(cx, 2.62, "例 2：一个顶点的所有邻边", fontsize=8.6, color=INK, ha="center")

    ax.text(7.05, 2.45, "两条遍历规则：", fontsize=9.0, color=INK)
    ax.text(7.05, 2.10, "面内前进：next", fontsize=8.6, color=TEAL)
    ax.text(7.05, 1.78, "跨到隔壁面：twin->next", fontsize=8.6, color=RED)
    ax.text(7.05, 1.30, "组合起来就得到了", fontsize=8.4, color=MUTED)
    ax.text(7.05, 1.00, "「一圈邻域」的常数时间访问", fontsize=8.4, color=MUTED)
    ax.text(7.05, 0.55, "这就是第 6 讲法线平均、", fontsize=8.0, color=MUTED)
    ax.text(7.05, 0.30, "第 10 讲细分需要的操作", fontsize=8.0, color=MUTED)
    save(fig, "d07-halfedge-traversal.png")


# ------------------------------------------------- d08 三种局部操作
def d08():
    fig, ax = canvas(10.0, 3.4, (0, 10.0), (0, 3.4))
    ax.text(0.30, 3.14, "三种局部操作：翻边、加点、收边", fontsize=10.2, color=INK,
            fontweight="bold")
    cases = [("flip（翻边）", "把对角线换一个方向", 0.45, TEAL, "元素数量不变"),
             ("split（加点）", "在边上插一个顶点", 3.60, ORANGE, "面数 +1"),
             ("collapse（收边）", "把一条边缩成一个点", 6.75, PURPLE, "面数 −1")]
    for name, note, ox, c, tally in cases:
        A = np.array([ox + 0.15, 1.20])
        B = np.array([ox + 1.30, 0.85])
        Cc = np.array([ox + 1.30, 2.20])
        D = np.array([ox + 2.45, 1.20])
        if name.startswith("flip"):
            tri(ax, [A, Cc, B], fc="#e6f7f4", ec=c, lw=1.0)
            tri(ax, [Cc, D, B], fc="#e6f7f4", ec=c, lw=1.0)
            ax.plot([A[0], D[0]], [A[1], D[1]], color=c, lw=1.8)
            for p in (A, B, Cc, D):
                dot(ax, p, c, ms=4.0)
            ax.plot([B[0], Cc[0]], [B[1], Cc[1]], color=RED, lw=1.0, ls=(0, (3, 3)))
            ax.text((B[0] + Cc[0]) / 2 + 0.10, (B[1] + Cc[1]) / 2, "换掉", fontsize=7.4,
                    color=RED)
        elif name.startswith("split"):
            M = (B + Cc) / 2
            tri(ax, [A, Cc, M], fc="#fff7ed", ec=c, lw=1.0)
            tri(ax, [A, M, B], fc="#fff7ed", ec=c, lw=1.0)
            tri(ax, [Cc, D, M], fc="#fff7ed", ec=c, lw=1.0)
            tri(ax, [M, D, B], fc="#fff7ed", ec=c, lw=1.0)
            for p in (A, B, Cc, D):
                dot(ax, p, c, ms=4.0)
            dot(ax, M, RED, ms=5.0)
            ax.text(M[0] + 0.08, M[1] + 0.10, "新点", fontsize=7.4, color=RED)
        else:
            tri(ax, [A, Cc, B], fc="#f3e8ff", ec=c, lw=1.0)
            tri(ax, [Cc, D, B], fc="#f3e8ff", ec=c, lw=1.0)
            M = (B + Cc) / 2
            ax.plot([B[0], Cc[0]], [B[1], Cc[1]], color=c, lw=2.2)
            dot(ax, M, RED, ms=5.0)
            for p in (A, D):
                dot(ax, p, c, ms=4.0)
            for p in (B, Cc):
                dot(ax, p, c, ms=3.0, face="#e5e7eb")
            ax.text(M[0] + 0.10, M[1] - 0.05, "合并成一个点", fontsize=7.4, color=RED)
        ax.text(ox + 1.30, 0.55, name, fontsize=8.8, color=c, ha="center",
                fontweight="bold")
        ax.text(ox + 1.30, 0.25, note, fontsize=7.6, color=MUTED, ha="center")
        ax.text(ox + 1.30, 2.48, tally, fontsize=7.6, color=ORANGE, ha="center")
    ax.text(0.30, 0.02, "所有全局操作（细分、简化、规整）都是这三种基本操作的组合 —— "
                        "而且每次操作后都要重新维护 half-edge 指针",
            fontsize=8.6, color=INK)
    save(fig, "d08-edge-ops.png")


# ------------------------------------------------- d09 Loop 权重
def d09():
    fig, ax = canvas(9.8, 3.6, (0, 9.8), (0, 3.6))
    ax.text(0.30, 3.34, "Loop 细分（三角形网格）：两类顶点各有一套权重", fontsize=10.2,
            color=INK, fontweight="bold")
    # 左：新边点
    ax.text(1.55, 3.00, "① 新边点 = 四个点的加权", fontsize=8.8, color=TEAL, ha="center")
    P = np.array([0.55, 1.45]); Q = np.array([2.55, 1.45])
    R = np.array([0.55, 2.50]); S = np.array([2.55, 2.50])
    ax.plot([P[0], Q[0]], [P[1], Q[1]], color=INK, lw=1.6)
    ax.plot([R[0], S[0]], [R[1], S[1]], color=INK, lw=1.0, ls=(0, (3, 3)))
    M = (P + Q) / 2
    dot(ax, P, INK, ms=4.5); dot(ax, Q, INK, ms=4.5)
    dot(ax, R, INK, ms=4.5); dot(ax, S, INK, ms=4.5)
    dot(ax, M, RED, ms=6.0)
    ax.text(M[0] - 0.05, M[1] - 0.30, "新点", fontsize=7.8, color=RED)
    ax.text(P[0] - 0.10, P[1] - 0.28, "3/8", fontsize=8.2, color=TEAL)
    ax.text(Q[0] - 0.20, Q[1] - 0.28, "3/8", fontsize=8.2, color=TEAL)
    ax.text(R[0] - 0.10, R[1] + 0.10, "1/8", fontsize=8.2, color=MUTED)
    ax.text(S[0] - 0.20, S[1] + 0.10, "1/8", fontsize=8.2, color=MUTED)
    ax.text(1.55, 0.95, "边两端各 3/8，对顶点各 1/8", fontsize=8.2, color=MUTED, ha="center")

    # 右：老顶点
    ax.text(6.55, 3.00, "② 老顶点 = (1−n·u)·自己 + u·每个邻居", fontsize=8.8,
            color=ORANGE, ha="center")
    cx, cy, Rr = 6.55, 1.55, 0.80
    n = 6
    ring = [(cx + Rr * np.cos(np.radians(90 + k * 60)),
             cy + Rr * np.sin(np.radians(90 + k * 60))) for k in range(n)]
    for k in range(n):
        tri(ax, [(cx, cy), ring[k], ring[(k + 1) % n]], fc="#fff7ed", ec="#fdba74", lw=0.8)
    for p in ring:
        ax.plot([cx, p[0]], [cy, p[1]], color=ORANGE, lw=0.9)
        dot(ax, p, ORANGE, ms=3.4)
        ax.text(p[0] + (p[0] - cx) * 0.20, p[1] + (p[1] - cy) * 0.20, "1/16",
                fontsize=6.6, color=MUTED, ha="center")
    dot(ax, (cx, cy), RED, ms=6.0)
    ax.text(cx, cy - 0.34, "10/16", fontsize=8.2, color=RED, ha="center")
    ax.text(cx, 0.55, "度 n=6 时：自己 10/16，六个邻居各 1/16", fontsize=8.2, color=MUTED,
            ha="center")
    ax.text(0.55, 0.42, "u 的取值：", fontsize=8.6, color=INK)
    ax.text(1.55, 0.42, r"$u=\dfrac{3}{16}$（n=3）", fontsize=8.6, color=TEAL)
    ax.text(3.20, 0.42, r"$u=\dfrac{3}{8n}$（n>3）", fontsize=8.6, color=TEAL)
    ax.text(5.00, 0.42, r"$1-nu$ 是「自己」的权重", fontsize=8.4, color=MUTED)
    save(fig, "d09-loop-weights.png")


# ------------------------------------------------- d10 Loop = split + flip
def d10():
    fig, ax = canvas(9.8, 3.2, (0, 9.8), (0, 3.2))
    ax.text(0.30, 2.94, "Loop 细分的实现：一次 split，再一次 flip", fontsize=10.2,
            color=INK, fontweight="bold")
    A, B, C = np.array([0.65, 0.95]), np.array([2.65, 0.95]), np.array([1.65, 2.45])
    stages = [("原始三角形", 0), ("每条边 split", 1), ("中间三条边 flip", 2)]
    for k in range(3):
        ox = k * 2.65
        Aa = A + [ox, 0]; Bb = B + [ox, 0]; Cc = C + [ox, 0]
        if k == 0:
            tri(ax, [Aa, Bb, Cc], fc="#e0f2fe", ec=BLUE, lw=1.2)
            for p in (Aa, Bb, Cc):
                dot(ax, p, BLUE, ms=4.5)
        elif k == 1:
            M = [(Aa + Bb) / 2, (Bb + Cc) / 2, (Cc + Aa) / 2]
            for i in range(3):
                tri(ax, [[Aa, Bb, Cc][i], M[i], M[(i + 2) % 3]], fc="#e6f7f4",
                    ec=TEAL, lw=1.0)
            tri(ax, M, fc="#fff7ed", ec=ORANGE, lw=1.0)
            for p in (Aa, Bb, Cc):
                dot(ax, p, BLUE, ms=4.5)
            for p in M:
                dot(ax, p, ORANGE, ms=4.0)
        else:
            M = [(Aa + Bb) / 2, (Bb + Cc) / 2, (Cc + Aa) / 2]
            G = (Aa + Bb + Cc) / 3
            for i in range(3):
                tri(ax, [G, M[i], M[(i + 1) % 3]], fc="#f3e8ff", ec=PURPLE, lw=1.0)
            for i in range(3):
                tri(ax, [[Aa, Bb, Cc][i], M[i], M[(i + 2) % 3]], fc="#e6f7f4",
                    ec=TEAL, lw=1.0)
            for p in list(M) + [G] + [Aa, Bb, Cc]:
                dot(ax, p, PURPLE, ms=3.6)
        ax.text(1.65 + ox, 0.55, stages[k][0], fontsize=8.4, color=MUTED, ha="center")
    ax.text(0.30, 0.22, "4 个三角形每个再分成 4 个 → 一次细分后面数 ×4。"
                        "「split 后 flip」是 Loop 的标准实现路线（P55）", fontsize=8.6,
            color=INK)
    save(fig, "d10-loop-split-flip.png")


# ------------------------------------------------- d11 B 样条的 hump
def d11():
    fig, ax = canvas(9.4, 3.2, (0, 9.4), (0, 3.2), eq=False)
    ax.text(0.30, 2.94, "B 样条：把「基函数」平移叠加，自动得到 C2", fontsize=10.2,
            color=INK, fontweight="bold")
    t = np.linspace(0, 1, 200)

    def hump(x):
        return np.where((x >= 0) & (x < 1), (3 * x ** 3 - 6 * x ** 2 + 4) / 6, 0.0)

    xs = np.linspace(-1, 3, 800)
    for k in range(4):
        y = hump(xs - k + 0.5)
        ax.plot(0.70 + 2.05 * xs, 0.55 + 1.55 * y, lw=1.6,
                color=[TEAL, ORANGE, PURPLE, "#9ca3af"][k])
    ax.text(4.35, 2.55, "每个控制点对应一个「小山包」", fontsize=9.0, color=INK)
    ax.text(4.35, 2.22, "曲线 = 这些山包的加权和", fontsize=9.0, color=INK)
    ax.text(4.35, 1.80, "关键区别（对比 Bézier / L10）：", fontsize=8.8, color=ORANGE)
    ax.text(4.35, 1.50, "• 每个基函数只覆盖局部（4 段）", fontsize=8.4, color=MUTED)
    ax.text(4.35, 1.22, "• 重叠部分自动保证 C2 连续", fontsize=8.4, color=MUTED)
    ax.text(4.35, 0.94, "• 曲线**不经过**控制点（逼近而非插值）", fontsize=8.4, color=MUTED)
    ax.text(4.35, 0.50, "这就是「放弃插值、换取连续性和局部性」的交易", fontsize=8.8,
            color=TEAL)
    save(fig, "d11-bspline-humps.png")


# ------------------------------------------------- d12 Catmull-Clark 规则
def d12():
    fig, ax = canvas(10.0, 3.6, (0, 10.0), (0, 3.6))
    ax.text(0.30, 3.34, "Catmull-Clark（四边形网格）：一步细分产生三类新点", fontsize=10.2,
            color=INK, fontweight="bold")
    # 一个四边形及其邻居
    Q = np.array([[1.10, 1.10], [2.60, 1.10], [2.60, 2.60], [1.10, 2.60]])
    ax.add_patch(Polygon(Q, closed=True, facecolor="#e0f2fe", ec=BLUE, lw=1.6))
    # 邻居面（简化为外侧点）
    nb = [(0.35, 1.85), (1.85, 0.35), (3.35, 1.85), (1.85, 3.35)]
    for p in nb:
        ax.plot([p[0], (Q[0][0] + Q[3][0]) / 2 if p[0] < 1 else p[0]],
                [p[1], p[1]], color="#cbd5e1", lw=0.8)

    F = Q.mean(axis=0)
    dot(ax, F, RED, ms=6.5)
    ax.text(F[0] + 0.10, F[1] + 0.10, "face point", fontsize=8.0, color=RED)

    for i in range(4):
        M = (Q[i] + Q[(i + 1) % 4]) / 2
        dot(ax, M, ORANGE, ms=5.5)
        ax.text(M[0] + 0.06, M[1] - 0.24, "edge", fontsize=7.4, color=ORANGE)
    for i in range(4):
        dot(ax, Q[i], PURPLE, ms=5.0)
        ax.text(Q[i][0] - 0.10, Q[i][1] + 0.10, "v", fontsize=7.6, color=PURPLE)

    ax.text(4.35, 2.70, "① face point = 面的重心", fontsize=8.8, color=RED)
    ax.text(4.35, 2.35, "② edge point = 边两端 + 两侧面心的平均", fontsize=8.8, color=ORANGE)
    ax.text(4.35, 2.00, "③ vertex point = 邻域面上的平均", fontsize=8.8, color=PURPLE)
    ax.text(4.35, 1.55, "然后把每个 n 边形拆成 n 个四边形：", fontsize=8.8, color=INK)
    ax.text(4.35, 1.25, "（v, edge, face, edge）四点连成一个四边面", fontsize=8.4,
            color=MUTED)
    ax.text(4.35, 0.80, "结果：**全部变成四边形**，", fontsize=8.8, color=TEAL)
    ax.text(4.35, 0.50, "而且非四边形和异常点都被「稀释」了", fontsize=8.4, color=MUTED)
    ax.text(0.30, 0.08, "对比 Loop（三角形网格）：Catmull-Clark 处理任意多边形，一次细分后面数 ×4、"
                        "但「四边形化」是它的关键副作用", fontsize=8.4, color=MUTED)
    save(fig, "d12-cc-rules.png")


# ------------------------------------------------- d13 异常点被稀释
def d13():
    fig, ax = canvas(9.8, 3.2, (0, 9.8), (0, 3.2), eq=False)
    ax.text(0.30, 2.94, "为什么细分能「修好」网格：异常点的数量不增加", fontsize=10.2,
            color=INK, fontweight="bold")
    # 三个级别的网格示意
    for k, (n, lab) in enumerate([(3, "原始：有三角形面\n和 5 度顶点"), (6, "一次细分后"),
                                  (12, "两次细分后")]):
        ox = 0.55 + k * 2.55
        ax.add_patch(Rectangle((ox, 1.00), 1.95, 1.55, facecolor="#f8fafc", ec=MUTED,
                               lw=0.8))
        for i in range(n):
            for j in range(n):
                ax.plot([ox + 0.06 + i * 1.83 / n, ox + 0.06 + i * 1.83 / n],
                        [1.06, 2.49], color="#e5e7eb", lw=0.4)
                ax.plot([ox + 0.06, ox + 1.89],
                        [1.06 + j * 1.43 / n, 1.06 + j * 1.43 / n], color="#e5e7eb",
                        lw=0.4)
        if k == 0:
            ax.plot([ox + 1.30, ox + 1.80], [1.06, 2.49], color=RED, lw=1.2)
            ax.plot([ox + 0.06, ox + 1.89], [1.06, 1.95], color=RED, lw=1.2)
            ax.plot(ox + 1.30, 1.90, "o", ms=5, color=ORANGE, zorder=8)
        ax.text(ox + 0.98, 0.62, lab, fontsize=7.8, color=MUTED, ha="center",
                linespacing=1.5, va="top")

    ax.text(7.95, 2.45, "关键结论（P48–P54）：", fontsize=8.8, color=INK)
    ax.text(7.95, 2.10, "细分不会制造新的异常点", fontsize=8.4, color=TEAL)
    ax.text(7.95, 1.78, "只会把它们「稀释」到", fontsize=8.4, color=MUTED)
    ax.text(7.95, 1.48, "越来越大的网格里", fontsize=8.4, color=MUTED)
    ax.text(7.95, 1.05, "所以大部分区域都是正则的", fontsize=8.4, color=ORANGE)
    ax.text(7.95, 0.75, "（度 6 / 度 4）", fontsize=8.2, color=MUTED)
    ax.text(7.95, 0.42, "只有在异常点附近才需要特殊规则", fontsize=8.2, color=MUTED)
    save(fig, "d13-extraordinary.png")


# ------------------------------------------------- d14 二次误差
def d14():
    fig, ax = canvas(9.6, 3.4, (0, 9.6), (0, 3.4))
    ax.text(0.30, 3.14, "二次误差度量：每个顶点记一个 4×4 矩阵，代表「周围的平面」", fontsize=10.2,
            color=INK, fontweight="bold")
    # 两个面片 + 平面
    ax.add_patch(Polygon([[0.55, 1.15], [2.15, 0.80], [2.85, 1.75], [1.25, 2.10]],
                         closed=True, facecolor="#e0f2fe", ec=BLUE, lw=1.2))
    ax.plot([0.55, 2.85], [1.15, 1.75], color=BLUE, lw=1.0, ls=(0, (3, 3)))
    P = np.array([1.95, 2.55])
    dot(ax, P, RED, ms=6)
    ax.text(P[0] + 0.10, P[1] + 0.06, "候选新位置 $v$", fontsize=8.2, color=RED)
    for q in [(1.25, 2.10), (1.25, 1.30)]:
        ax.plot([P[0], q[0]], [P[1], q[1]], color=RED, lw=1.0, ls=(0, (2, 2)))

    ax.text(3.35, 2.60, "平面写成 $n^Tv+d=0$，", fontsize=9.0, color=INK)
    ax.text(3.35, 2.25, "点到平面的距离平方：", fontsize=9.0, color=INK)
    ax.text(3.35, 1.85, r"$D(v)=v^T(nn^T)v+2d\,n^Tv+d^2$", fontsize=9.6, color=TEAL)
    ax.text(3.35, 1.35, "把它写成齐次形式：", fontsize=8.6, color=MUTED)
    ax.text(3.35, 0.95, r"$D(v)=\tilde{v}^{T}Q\tilde{v}$，其中 $\tilde{v}=[v_x,v_y,v_z,1]^T$",
            fontsize=9.2, color=ORANGE)
    box(ax, 6.95, 1.45, 2.45, 1.35,
        "Q 是 4×4 对称矩阵\n只需存 10 个数\n（不是 16 个）",
        fs=8.4, fc="#fff7ed", ec=ORANGE, tc="#7c3a00")
    ax.text(0.30, 0.42, "为什么用「到平面的距离」：它同时度量了位置误差和形状误差 —— "
                        "一个点偏离原来的表面多远，就等于它把形状破坏了多少",
            fontsize=8.6, color=INK)
    ax.text(0.30, 0.12, "每个顶点的 Q 是「它周围所有面」的 Q 之和；两个顶点合并时，Q 也相加",
            fontsize=8.6, color=TEAL)
    save(fig, "d14-quadric.png")


# ------------------------------------------------- d15 QEM 简化循环
def d15():
    fig, ax = canvas(9.8, 3.4, (0, 9.8), (0, 3.4), eq=False)
    ax.text(0.30, 3.14, "QEM 简化：把所有边排进优先队列，反复收掉「最便宜」的那条", fontsize=10.2,
            color=INK, fontweight="bold")
    steps = [("① 给每条边算代价", "collapse 后 $v^TQv$", TEAL),
             ("② 放进优先队列", "按代价排序", ORANGE),
             ("③ 收掉最小的一条", "更新受影响边的代价", PURPLE),
             ("④ 重复到目标面数", "O(n log n)", GREEN)]
    for i, (t1, t2, c) in enumerate(steps):
        x = 0.40 + i * 2.40
        box(ax, x, 1.55, 2.05, 1.05, t1, fs=8.6, fc=FILL, ec=c, tc=c)
        ax.text(x + 1.02, 1.20, t2, fontsize=7.8, color=MUTED, ha="center")
        if i < 3:
            arrow(ax, (x + 2.12, 2.07), (x + 2.36, 2.07), color=MUTED, lw=1.3, ms=10)
    ax.text(0.40, 0.72, "关键：只重算「与刚合并的点相邻」的那些边 —— 所以整体是局部更新，不是每次全局重算",
            fontsize=8.8, color=INK)
    ax.text(0.40, 0.40, "结果：30,000 → 3,000 → 300 → 30 个三角形，形状基本保持（P113–P118 的骷髅）",
            fontsize=8.8, color=TEAL)
    ax.text(0.40, 0.10, "注意：边 collapse 可能翻面 / 破坏流形，需要额外检查（link condition）",
            fontsize=8.4, color=RED)
    save(fig, "d15-qem.png")


# ------------------------------------------------- d16 等向重网格
def d16():
    fig, ax = canvas(9.8, 3.4, (0, 9.8), (0, 3.4))
    ax.text(0.30, 3.14, "等向重网格：四步循环，让三角形「大小均匀、形状接近正三角」", fontsize=10.2,
            color=INK, fontweight="bold")
    labels = [("① split", "边 > 4/3·均值"), ("② collapse", "边 < 4/5·均值"),
              ("③ flip", "改善顶点度数"), ("④ 切向平移到重心", "改善三角形形状")]
    for i, (a, b) in enumerate(labels):
        x = 0.55 + i * 2.35
        ax.add_patch(Circle((x + 0.95, 1.95), 0.62, facecolor="#e6f7f4", ec=TEAL, lw=1.2))
        ax.text(x + 0.95, 1.98, a, fontsize=8.0, color=TEAL, ha="center", va="center")
        ax.text(x + 0.95, 1.05, b, fontsize=7.6, color=MUTED, ha="center")
        if i < 3:
            arrow(ax, (x + 1.62, 1.95), (x + 2.28, 1.95), color=MUTED, lw=1.3, ms=10)
    arrow(ax, (8.75, 1.30), (2.20, 0.72), color=TEAL, lw=1.2, ls=(0, (4, 3)), rad=0.25)
    ax.text(5.30, 0.55, "重复直到收敛", fontsize=8.2, color=TEAL, ha="center")
    ax.text(0.30, 0.22, "为什么是 4/3 和 4/5：这两个阈值让边长的分布收敛到「均值附近」，"
                        "同时避免抖动（上界 4/3、下界 4/5 是经验值，来自 Botsch & Kobbelt）",
            fontsize=8.4, color=INK)
    save(fig, "d16-remeshing.png")


if __name__ == "__main__":
    print("generating ->", OUT)
    for fn in [d01, d02, d03, d04, d05, d06, d07, d08,
               d09, d10, d11, d12, d13, d14, d15, d16]:
        fn()
    print("done: 16 diagrams")
