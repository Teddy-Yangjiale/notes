# -*- coding: utf-8 -*-
"""CS184 课程笔记 · L04–05（变换）原创图解

风格遵循 scripts/cs184-notes-standard.md：
一图一关系 / 不画 matplotlib 坐标轴 / 图内无标题 / 图注写在正文 / 颜色语义固定
颜色语义：teal=主链路/内侧，orange=本讲焦点，purple=数据形态/对象，red=错误/异常，灰=说明
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
                                    "notes", "cs184-04-05-transforms", "diagrams"))
os.makedirs(OUT, exist_ok=True)
DPI = 200

INK, MUTED = "#16202c", "#5b6b7c"
FILL, STROKE = "#f4f6f9", "#c3ccd6"
TEAL, ORANGE, PURPLE = "#0f766e", "#b45309", "#5b21b6"
BLUE, RED, GREEN = "#1d4ed8", "#b91c1c", "#15803d"


def canvas(w, h, xlim, ylim, eq=True):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axis("off")
    if eq:
        ax.set_aspect("equal")
    return fig, ax


def box(ax, x, y, w, h, text, fc=FILL, ec=STROKE, tc=INK, fs=10, lw=1.4,
        pad=0.07, rad=0.13):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle=f"round,pad={pad},rounding_size={rad}",
                                facecolor=fc, edgecolor=ec, linewidth=lw, zorder=3))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            color=tc, zorder=4, linespacing=1.45)


def arrow(ax, p, q, color=TEAL, lw=1.8, ls="-", z=2, ms=13, rad=0.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=ms, color=color,
                                 lw=lw, linestyle=ls, zorder=z,
                                 connectionstyle=f"arc3,rad={rad}",
                                 shrinkA=1, shrinkB=1))


def axes2d(ax, x0, y0, L=1.0, color=MUTED, label=True, lw=1.2):
    arrow(ax, (x0, y0), (x0 + L, y0), color=color, lw=lw, ms=10)
    arrow(ax, (x0, y0), (x0, y0 + L), color=color, lw=lw, ms=10)
    if label:
        ax.text(x0 + L + 0.06, y0 - 0.02, "x", fontsize=8.6, color=color, va="center")
        ax.text(x0 - 0.04, y0 + L + 0.06, "y", fontsize=8.6, color=color, ha="center")


def house(ax, x0, y0, s=1.0, rot=0.0, color=PURPLE, alpha=0.85, lw=1.4):
    """一个不对称的小房子，用来看出旋转/镜像/错切。"""
    pts = np.array([[-0.5, -0.4], [0.5, -0.4], [0.5, 0.15], [0.0, 0.6], [-0.5, 0.15]])
    c, si = np.cos(rot), np.sin(rot)
    R = np.array([[c, -si], [si, c]])
    p = (pts @ R.T) * s + np.array([x0, y0])
    ax.add_patch(Polygon(p, closed=True, facecolor=color, alpha=alpha,
                         edgecolor=color, lw=lw, zorder=4))


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=DPI, bbox_inches="tight",
                facecolor="white", pad_inches=0.12)
    plt.close(fig)
    print("  ", name)


# ------------------------------------------------------- d01 变换 = 点上的函数
def d01():
    fig, ax = canvas(10.4, 3.4, (0, 10.4), (0, 3.4))
    # 左：函数观
    ax.text(0.30, 2.95, "变换就是「作用在点上的函数」", fontsize=10.4, color=INK,
            fontweight="bold")
    ax.plot(1.15, 1.35, "o", ms=9, color=BLUE, zorder=5)
    ax.text(0.95, 1.05, "$P$", fontsize=11, color=BLUE)
    arrow(ax, (1.28, 1.45), (2.35, 2.05), color=MUTED, lw=1.4, rad=-0.25)
    ax.text(1.75, 1.95, "$F$", fontsize=11, color=MUTED)
    ax.plot(2.50, 2.15, "o", ms=9, color=ORANGE, zorder=5)
    ax.text(2.62, 2.28, "$P'=F(P)$", fontsize=10.5, color=ORANGE)
    ax.text(1.55, 0.62, "$(x',y',z')=F(x,y,z)$", fontsize=9.6, color=MUTED,
            ha="center")

    # 右：三种基本效果
    for i, (lab, fn, c) in enumerate([("旋转", "rotate", TEAL),
                                      ("平移", "translate", ORANGE),
                                      ("缩放", "scale", PURPLE)]):
        x0 = 4.55 + i * 1.95
        axes2d(ax, x0, 1.05, L=0.75)
        if fn == "rotate":
            house(ax, x0 + 0.30, 1.45, s=0.34, color="#cbd5e1")
            house(ax, x0 + 0.30, 1.45, s=0.34, rot=np.pi / 5, color=c)
        elif fn == "translate":
            house(ax, x0 + 0.18, 1.35, s=0.30, color="#cbd5e1")
            house(ax, x0 + 0.62, 1.80, s=0.30, color=c)
        else:
            house(ax, x0 + 0.34, 1.50, s=0.44, color="#cbd5e1")
            house(ax, x0 + 0.34, 1.50, s=0.24, color=c)
        ax.text(x0 + 0.38, 0.62, lab, fontsize=9.6, color=c, ha="center",
                fontweight="bold")
    ax.plot([4.25, 4.25], [0.55, 2.75], color="#e5e9ef", lw=1.2)
    save(fig, "d01-transform-as-function.png")


# ------------------------------------------------------- d02 矩阵的列 = 新坐标轴
def d02():
    fig, ax = canvas(10.0, 4.6, (-1.7, 6.6), (-1.4, 3.2))
    sq = np.array([[0, 0], [1, 0], [1, 1], [0, 1]])
    ax.add_patch(Polygon(sq, closed=True, facecolor="#e2e8f0", ec=MUTED, lw=1.4))
    axes2d(ax, 0, 0, L=1.6)
    ax.text(1.05, -0.28, "$\hat x=(1,0)$", fontsize=8.4, color=BLUE)
    ax.text(-0.32, 1.62, "$\hat y=(0,1)$", fontsize=8.4, color=BLUE, ha="center")
    house(ax, 0.5, 0.5, s=0.42, color=PURPLE, alpha=0.5)
    ax.text(0.5, -0.92, "单位方格", fontsize=9.2, color=MUTED, ha="center")

    arrow(ax, (1.90, 0.85), (2.80, 0.85), color=MUTED, lw=1.6)
    ax.text(2.35, 1.05, "$M$", fontsize=12, color=MUTED, ha="center")

    ox = 3.10
    M = np.array([[1.5, 0.9], [0.4, 1.7]])
    par = sq @ M.T + np.array([ox, 0])
    ax.add_patch(Polygon(par, closed=True, facecolor="#fde8e8", ec=RED, lw=1.6))
    axes2d(ax, ox, 0, L=1.6)
    c1 = M.T @ np.array([1, 0])
    c2 = M.T @ np.array([0, 1])
    arrow(ax, (ox, 0), (ox + c1[0], c1[1]), color=ORANGE, lw=2.4, ms=14)
    arrow(ax, (ox, 0), (ox + c2[0], c2[1]), color=TEAL, lw=2.4, ms=14)
    ax.text(ox + c1[0] + 0.12, c1[1] - 0.30, "第 1 列 $(a,c)$", fontsize=8.8,
            color=ORANGE)
    ax.text(ox + c2[0] + 0.10, c2[1] + 0.22, "第 2 列 $(b,d)$", fontsize=8.8,
            color=TEAL)
    hp = np.array([[0.5, 0.5]]) @ M.T + np.array([ox, 0])
    house(ax, hp[0, 0], hp[0, 1], s=0.42, color=PURPLE, alpha=0.5)
    ax.text(ox + 0.5, -0.92, "变换后：两列就是两个新轴", fontsize=9.2, color=INK,
            ha="center")
    ax.text(0.0, -1.28, "M = [ a  b ]", fontsize=9.6, color=INK, family="monospace")
    ax.text(0.0, -1.62, "    [ c  d ]", fontsize=9.6, color=INK, family="monospace")
    save(fig, "d02-matrix-columns.png")

# ------------------------------------------------------- d03 线性变换搬不动原点
def d03():
    fig, ax = canvas(9.6, 3.6, (0, 9.6), (0, 3.6))
    ax.text(0.30, 3.28, "线性变换必然把原点映射到原点 —— 所以它搬不动图形", fontsize=10.4,
            color=INK, fontweight="bold")
    # 左：原点必须固定
    axes2d(ax, 1.0, 1.10, L=1.5)
    ax.plot(1.0, 1.10, "o", ms=10, color=BLUE, zorder=6)
    ax.text(0.62, 0.72, "$M\\cdot\\mathbf{0}=\\mathbf{0}$", fontsize=10.5, color=BLUE)
    house(ax, 1.55, 1.75, s=0.40, color=PURPLE, alpha=0.75)
    ax.text(1.85, 0.45, "原点被钉死", fontsize=9.0, color=MUTED, ha="center")

    ax.plot([3.40, 3.40], [0.45, 3.05], color="#e5e9ef", lw=1.2)

    # 右：要平移，就必须用更大的维度
    axes2d(ax, 4.05, 1.10, L=1.5)
    ax.plot(4.05, 1.10, "o", ms=10, color=BLUE, zorder=6)
    house(ax, 5.05, 1.85, s=0.40, color=ORANGE, alpha=0.85)
    arrow(ax, (4.75, 1.75), (5.05, 1.85), color=ORANGE, lw=1.4,
          ls=(0, (3, 3)))
    ax.text(5.05, 0.45, "要先「升一维」，才搬得动", fontsize=9.0, color=MUTED,
            ha="center")
    box(ax, 6.55, 1.55, 2.55, 1.05,
        "加一个 $w$ 坐标后\n$M\\cdot(0,0,1)=(t_x,t_y,1)$\n原点就不再被钉死了",
        fs=8.8, fc="#fff7ed", ec=ORANGE, tc="#7c3a00")
    save(fig, "d03-no-translation.png")


# ------------------------------------------------------- d04 齐次坐标的 w
def d04():
    fig, ax = canvas(10.2, 3.9, (0, 10.2), (0, 3.9))
    ax.text(0.30, 3.58, "齐次坐标里的 $w$ 记录「这个量是什么类型」", fontsize=10.4,
            color=INK, fontweight="bold")
    box(ax, 0.30, 2.30, 2.30, 0.85, "点　point\n$(x,y,1)^T$", fs=9.4, fc="#e6f7f4",
        ec=TEAL, tc=TEAL)
    box(ax, 0.30, 1.15, 2.30, 0.85, "向量　vector\n$(x,y,0)^T$", fs=9.4, fc="#f5f3ff",
        ec=PURPLE, tc=PURPLE)

    ops = [("vector + vector", "vector", "0+0=0", GREEN, True),
           ("point − point", "vector", "1−1=0", GREEN, True),
           ("point + vector", "point", "1+0=1", GREEN, True),
           ("point + point", "非法", "1+1=2", RED, False)]
    for i, (op, res, wr, col, ok) in enumerate(ops):
        y = 2.86 - i * 0.66
        ax.text(3.05, y, op, fontsize=9.4, color=INK, va="center",
                family="monospace" if False else None)
        ax.text(5.55, y, "=", fontsize=11, color=MUTED, ha="center", va="center")
        ax.text(5.90, y, res, fontsize=9.6, color=col, va="center",
                fontweight="bold")
        ax.text(7.15, y, wr, fontsize=9.0, color=MUTED, va="center")
        ax.text(8.35, y, "√" if ok else "×", fontsize=13, color=col, va="center")
    ax.text(7.15, 3.12, "$w$ 的算术", fontsize=8.6, color=MUTED, ha="center")
    ax.text(3.05, 0.55, "$w\\ne 1$ 时怎么办：整个向量除以 $w$（可以延后做）", fontsize=9.2,
            color=ORANGE)
    ax.text(3.05, 0.20, "「两个点相加」得到的 $w=2$ 既不是点也不是向量 —— 所以它本来就无意义",
            fontsize=9.0, color=MUTED)
    save(fig, "d04-homogeneous-w.png")


# ------------------------------------------------------- d05 变换的层级
def d05():
    fig, ax = canvas(9.8, 4.2, (0, 9.8), (0, 4.2))
    layers = [
        ("Projective 投影", "任意 3×3，底行不受限", "只保直线", 0.55, 2.85, 9.0, "#fef3c7", ORANGE),
        ("Affine 仿射", "线性 + 平移，底行 (0,0,1)", "保平行", 1.05, 2.10, 8.0, "#e0f2fe", BLUE),
        ("Similarity 相似", "刚体 + 均匀缩放", "保角度", 1.55, 1.35, 7.0, "#e6f7f4", TEAL),
        ("Rigid 刚体", "只有旋转 + 平移", "保长度", 2.05, 0.62, 6.0, "#f3e8ff", PURPLE),
    ]
    for name, expr, keep, x, y, w, fc, ec in layers:
        box(ax, x, y, w, 0.62, "", fc=fc, ec=ec)
        ax.text(x + 0.20, y + 0.40, name, fontsize=10.0, color=ec, fontweight="bold")
        ax.text(x + 0.20, y + 0.14, expr, fontsize=8.4, color=MUTED)
        ax.text(x + w - 0.20, y + 0.31, keep, fontsize=9.2, color=ec, ha="right")
    ax.text(0.30, 3.86, "越往里越安全：允许的操作越少，保住的性质越多", fontsize=10.4,
            color=INK, fontweight="bold")
    ax.text(0.30, 0.20, "平移本身不是线性变换，所以「仿射」才需要齐次坐标；越往外越自由，能保证的也越少",
            fontsize=9.0, color=MUTED)
    save(fig, "d05-hierarchy.png")

# ------------------------------------------------------- d06 顺序不能换
def d06():
    fig, ax = canvas(10.6, 3.9, (0, 10.6), (0, 3.9))
    ax.text(0.30, 3.58, "同样的两个变换，换个顺序结果就不同", fontsize=10.4, color=INK,
            fontweight="bold")
    for i, (expr, steps, note, c) in enumerate([
            ("$T(1,0)\\cdot R_{45}$", "先转 45°，再平移 (1,0)", "物体转到新朝向后被整体搬走", TEAL),
            ("$R_{45}\\cdot T(1,0)$", "先平移 (1,0)，再绕原点转 45°", "物体被搬走后又被绕原点甩了一圈", ORANGE)]):
        x0 = 0.55 + i * 5.25
        axes2d(ax, x0, 1.05, L=1.35)
        if i == 0:
            house(ax, x0 + 0.95, 1.62, s=0.34, rot=np.pi / 4, color=c)
        else:
            house(ax, x0 + 0.55, 1.70, s=0.34, rot=np.pi / 4, color=c)
        ax.text(x0 + 0.05, 2.72, expr, fontsize=11, color=c)
        ax.text(x0 + 0.05, 0.62, steps, fontsize=8.8, color=INK)
        ax.text(x0 + 0.05, 0.30, note, fontsize=8.4, color=MUTED)
    ax.text(5.10, 1.55, "≠", fontsize=20, color=RED, ha="center", va="center")
    ax.text(0.30, 0.02, "记忆规则：矩阵从右往左作用 —— $T\\cdot R$ 读作「先 R 后 T」",
            fontsize=9.2, color=RED)
    save(fig, "d06-order-matters.png")


# ------------------------------------------------------- d07 绕点旋转三步
def d07():
    fig, ax = canvas(10.4, 3.3, (0, 10.4), (0, 3.3))
    xs = [0.60, 3.00, 5.40, 7.80]
    names = ["① 把中心移到原点\n$T(-c)$", "② 绕原点旋转\n$R(\\alpha)$",
             "③ 平移回去\n$T(c)$", "合成一个矩阵\n$T(c)\\,R(\\alpha)\\,T(-c)$"]
    for i, (x, nm) in enumerate(zip(xs, names)):
        axes2d(ax, x, 1.10, L=1.05)
        ax.plot(x + 0.62, 1.62, "+", ms=9, color=RED, zorder=6)
        if i == 0:
            house(ax, x + 0.95, 2.00, s=0.30, color=PURPLE, alpha=0.85)
        elif i == 1:
            house(ax, x + 0.62, 1.62, s=0.30, color=ORANGE, alpha=0.9)
        elif i == 2:
            house(ax, x + 0.62, 1.62, s=0.30, rot=np.pi / 4, color=ORANGE, alpha=0.9)
        else:
            house(ax, x + 0.98, 1.72, s=0.30, rot=np.pi / 4, color=TEAL, alpha=0.9)
        ax.text(x + 0.10, 2.95, nm, fontsize=8.8, color=MUTED, va="top",
                linespacing=1.4)
        if i < 3:
            arrow(ax, (x + 1.20, 1.60), (xs[i + 1] - 0.15, 1.60), color=MUTED, lw=1.4)
    ax.text(0.55, 0.35, "这个「移到原点 → 做事 → 移回去」的套路，后面会反复出现"
                        "（旋转任意轴、构造非轴对齐缩放都是它）", fontsize=9.2, color=INK)
    save(fig, "d07-rotate-about-point.png")


# ------------------------------------------------------- d08 非轴对齐缩放
def d08():
    fig, ax = canvas(10.2, 3.4, (0, 10.2), (0, 3.4))
    ax.text(0.30, 3.10, "沿 45° 方向拉伸：转正 → 缩放 → 转回", fontsize=10.4, color=INK,
            fontweight="bold")
    steps = [("$R(-45°)$", "把目标方向转到 x 轴", TEAL),
             ("$S(1,2)$", "在轴对齐方向做缩放", ORANGE),
             ("$R(45°)$", "再转回原方向", TEAL)]
    for i, (expr, note, c) in enumerate(steps):
        x0 = 0.55 + i * 3.35
        axes2d(ax, x0, 0.95, L=1.15)
        if i == 0:
            house(ax, x0 + 0.70, 1.55, s=0.30, rot=np.pi / 4, color=PURPLE)
        elif i == 1:
            house(ax, x0 + 0.70, 1.55, s=0.30, color=ORANGE)
        else:
            house(ax, x0 + 0.70, 1.55, s=0.30, rot=np.pi / 4, color=TEAL)
        ax.text(x0 + 0.05, 2.55, expr, fontsize=10.2, color=c)
        ax.text(x0 + 0.05, 0.55, note, fontsize=8.6, color=MUTED)
    box(ax, 7.55, 0.95, 2.45, 1.55,
        "R(45)·S(1,2)·R(−45)\n= [ 1.5  −0.5 ]\n   [ −0.5  1.5 ]",
        fs=9.2, fc="#fff7ed", ec=ORANGE, tc="#7c3a00")
    save(fig, "d08-oblique-scale.png")


# ------------------------------------------------------- d09 两种解读
def d09():
    fig, ax = canvas(10.4, 4.4, (0, 10.4), (0, 4.4))
    ax.text(0.30, 4.10, "同一个矩阵，两种读法 —— 它们互为逆运算", fontsize=10.4,
            color=INK, fontweight="bold")
    ax.text(0.30, 3.68, "解读 1：动物体（坐标系不动）", fontsize=9.6, color=ORANGE,
            fontweight="bold")
    for x, rot, sc in [(0.70, 0, 0.32), (2.20, np.pi / 5, 0.32), (3.70, np.pi / 5, 0.26)]:
        axes2d(ax, x, 2.10, L=0.80)
        house(ax, x + 0.32, 2.48, s=sc, rot=rot, color=ORANGE, alpha=0.85)
    ax.text(4.95, 2.48, "$T(c)\,S\,R\,T(-c)$", fontsize=9.4, color=ORANGE)
    ax.text(7.55, 2.48, "看到的是小房子在动", fontsize=9.0, color=MUTED)

    ax.text(0.30, 1.80, "解读 2：动坐标系（物体不动）", fontsize=9.6, color=TEAL,
            fontweight="bold")
    for x, ang in [(0.70, 0), (2.20, 0.45), (3.70, 0.45)]:
        ax.plot([x, x + 0.85 * np.cos(ang)], [0.30, 0.30 + 0.85 * np.sin(ang)],
                color=MUTED, lw=1.2)
        ax.plot([x, x - 0.85 * np.sin(ang)], [0.30, 0.30 + 0.85 * np.cos(ang)],
                color=MUTED, lw=1.2)
        house(ax, x + 0.32, 0.62, s=0.32, color=TEAL, alpha=0.85)
    ax.text(4.95, 0.62, "$T(c)\,R(-\\alpha)\,S(1/s)\,T(-c)$", fontsize=9.0,
            color=TEAL)
    ax.text(7.55, 0.62, "小房子没动，是「尺子」转了", fontsize=9.0, color=MUTED)
    ax.plot([0.30, 10.10], [1.92, 1.92], color="#e5e9ef", lw=1.2, ls=(0, (4, 3)))
    ax.text(0.30, 0.02, "注意第二个式子是第一个的逆：把「谁在动」换过来，矩阵就要取逆",
            fontsize=9.0, color=RED)
    save(fig, "d09-two-interpretations.png")

# ------------------------------------------------------- d10 三个轴旋转的符号
def d10():
    fig, ax = canvas(10.2, 3.6, (0, 10.2), (0, 3.6))
    ax.text(0.30, 3.28, "三个轴旋转矩阵：中间那个（$R_y$）的符号是反的", fontsize=10.4,
            color=INK, fontweight="bold")
    mats = [
        ("$R_x$", "绕 x", [[1, 0, 0], [0, "c", "-s"], [0, "s", "c"]], TEAL),
        ("$R_y$", "绕 y", [["c", 0, "s"], [0, 1, 0], ["-s", 0, "c"]], ORANGE),
        ("$R_z$", "绕 z", [["c", "-s", 0], ["s", "c", 0], [0, 0, 1]], PURPLE),
    ]
    for i, (name, sub, m, c) in enumerate(mats):
        x0 = 0.55 + i * 3.35
        ax.text(x0 + 0.62, 2.95, name, fontsize=11, color=c, ha="center")
        ax.text(x0 + 0.62, 2.66, sub + " 轴", fontsize=8.6, color=MUTED, ha="center")
        for r in range(3):
            for cc in range(3):
                v = m[r][cc]
                fc = "#fff7ed" if (c == ORANGE and v == "s") else "white"
                ec = ORANGE if (c == ORANGE and v in ("s", "-s")) else STROKE
                ax.add_patch(Rectangle((x0 + cc * 0.42, 2.10 - r * 0.42), 0.42, 0.42,
                                       facecolor=fc, edgecolor=ec, lw=1.0))
                ax.text(x0 + cc * 0.42 + 0.21, 2.10 - r * 0.42 + 0.21, v,
                        fontsize=9.0, color=INK, ha="center", va="center")
    ax.text(0.55, 0.62, "绕 $y$ 转时，$x\\to z$ 在右手系里是反向的 —— 所以 $R_y$ 的"
                         "$\\sin$ 符号和 $R_x,R_z$ 相反", fontsize=9.4, color=ORANGE)
    ax.text(0.55, 0.22, "默写时最容易错的就是这里：不要「三行都一样」地背", fontsize=9.0,
            color=MUTED)
    save(fig, "d10-rotation-signs.png")


# ------------------------------------------------------- d11 万向节死锁
def d11():
    import matplotlib.patches as mp
    fig, ax = canvas(9.8, 3.8, (0, 9.8), (0, 3.8))
    ax.text(0.30, 3.50, "万向节死锁：两个环转到共面，就丢了一个自由度", fontsize=10.4,
            color=INK, fontweight="bold")
    ax.text(1.55, 3.05, "正常：三个环互相垂直", fontsize=9.4, color=GREEN, ha="center")
    for ang, col in [(0, TEAL), (70, ORANGE), (140, PURPLE)]:
        ax.add_patch(mp.Ellipse((1.55, 1.65), 1.70, 0.55, angle=ang, fill=False,
                                ec=col, lw=2.4))
    ax.text(1.55, 0.55, "三个角各自有效，姿态唯一", fontsize=8.8, color=MUTED, ha="center")

    ax.plot([3.55, 3.55], [0.55, 3.15], color="#e5e9ef", lw=1.2)

    ax.text(5.55, 3.05, "死锁：外环与内环共面", fontsize=9.4, color=RED, ha="center")
    ax.add_patch(mp.Ellipse((5.55, 1.65), 1.70, 0.55, angle=90, fill=False,
                            ec=TEAL, lw=2.4))
    ax.add_patch(mp.Ellipse((5.55, 1.65), 1.55, 0.42, angle=90, fill=False,
                            ec=PURPLE, lw=2.4, ls=(0, (5, 2))))
    ax.add_patch(mp.Ellipse((5.55, 1.65), 0.55, 1.50, angle=0, fill=False,
                            ec=ORANGE, lw=2.0, alpha=0.6))
    ax.text(5.55, 0.55, "这两个环只能绕同一根轴转 → 少一个自由度", fontsize=8.8,
            color=RED, ha="center")

    ax.text(7.85, 2.55, "欧拉角的三个病灶", fontsize=9.6, color=INK)
    ax.text(7.85, 2.18, "• 万向节死锁", fontsize=8.9, color=RED)
    ax.text(7.85, 1.86, "• 表示不唯一", fontsize=8.9, color=RED)
    ax.text(7.85, 1.54, "• 插值会跳变", fontsize=8.9, color=RED)
    ax.text(7.85, 1.08, "⇒ 改用轴角 / 四元数", fontsize=9.0, color=TEAL)
    save(fig, "d11-gimbal-lock.png")

# ------------------------------------------------------- d12 绕任意轴
def d12():
    fig, ax = canvas(10.2, 3.4, (0, 10.2), (0, 3.4))
    ax.text(0.30, 3.10, "绕任意轴：造一个正交坐标系，转正 → 转 → 转回", fontsize=10.4,
            color=INK, fontweight="bold")
    labs = [("原始：轴 $\\mathbf{w}$ 是歪的", "以 $p,u,v,w$ 建正交系 $F$", PURPLE),
            ("$F^{-1}$：把 $w$ 对齐到 z 轴", "现在绕 z 转就行", TEAL),
            ("$F\\,R_z(\\theta)\\,F^{-1}$", "转完再变换回原空间", ORANGE)]
    for i, (t1, t2, c) in enumerate(labs):
        x0 = 0.55 + i * 3.35
        # 一个歪的轴
        if i == 0:
            ax.plot([x0 + 0.35, x0 + 1.05], [1.10, 2.05], color=c, lw=2.4)
            ax.plot(x0 + 0.35, 1.10, "o", ms=5, color=INK)
        elif i == 1:
            ax.plot([x0 + 0.35, x0 + 0.35], [1.10, 2.05], color=c, lw=2.4)
            ax.plot(x0 + 0.35, 1.10, "o", ms=5, color=INK)
            ax.plot([x0 + 0.35], [2.10], ">", ms=6, color=c)
        else:
            ax.plot([x0 + 0.35, x0 + 1.05], [1.10, 2.05], color=c, lw=2.4)
            ax.plot(x0 + 0.35, 1.10, "o", ms=5, color=INK)
            ax.add_patch(matplotlib.patches.Arc((x0 + 0.70, 1.58), 0.55, 0.55,
                                                theta1=200, theta2=340, color=RED,
                                                lw=1.6))
        ax.text(x0 + 0.10, 2.65, t1, fontsize=9.4, color=c)
        ax.text(x0 + 0.10, 0.62, t2, fontsize=8.6, color=MUTED)
        if i < 2:
            arrow(ax, (x0 + 1.55, 1.58), (x0 + 2.05, 1.58), color=MUTED, lw=1.4)
    ax.text(0.55, 0.22, "同样的「移到标准姿态 → 做事 → 移回去」—— 这是图形学里出现频率最高的思维模板",
            fontsize=9.2, color=INK)
    save(fig, "d12-arbitrary-axis.png")


# ------------------------------------------------------- d13 罗德里格：分解
def d13():
    fig, ax = canvas(9.8, 3.6, (0, 9.8), (0, 3.6))
    ax.text(0.30, 3.28, "罗德里格公式：把向量拆成「沿轴」和「垂直于轴」两块", fontsize=10.4,
            color=INK, fontweight="bold")
    o = np.array([1.00, 0.85])
    n = np.array([0.45, 1.55])                     # 轴
    v = np.array([1.95, 1.55])                     # 待转向量
    ax.annotate("", xy=o + n, xytext=o,
                arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.6))
    ax.text(o[0] + n[0] * 0.75, o[1] + n[1] * 0.92, "轴 $\\mathbf{n}$", fontsize=9.4,
            color=MUTED)
    ax.annotate("", xy=o + v, xytext=o,
                arrowprops=dict(arrowstyle="-|>", color=PURPLE, lw=2.0))
    ax.text(o[0] + v[0] + 0.08, o[1] + v[1], "$\\mathbf{x}$", fontsize=10, color=PURPLE)
    # 投影分量
    proj = n * (v @ n) / (n @ n)
    ax.annotate("", xy=o + proj, xytext=o,
                arrowprops=dict(arrowstyle="-|>", color=TEAL, lw=2.2))
    ax.text(o[0] + proj[0] * 0.55 - 0.62, o[1] + proj[1] * 0.55 + 0.10,
            "沿轴分量", fontsize=8.8, color=TEAL)
    perp = v - proj
    ax.annotate("", xy=o + perp + proj, xytext=o + proj,
                arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=2.0, ls=(0, (4, 2))))
    ax.text(o[0] + proj[0] + perp[0] + 0.10, o[1] + proj[1] + perp[1] - 0.30,
            "垂直分量", fontsize=8.8, color=ORANGE)
    # 旋转后的垂直分量
    c, s = np.cos(1.0), np.sin(1.0)
    rot_perp = perp * c + np.cross(np.array([0, 0, 1]), np.append(perp, 0))[:2] * s
    ax.annotate("", xy=o + proj + rot_perp, xytext=o + proj,
                arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.8))
    ax.text(o[0] + proj[0] + rot_perp[0] + 0.08, o[1] + proj[1] + rot_perp[1] + 0.12,
            "转 $\\alpha$ 后", fontsize=8.8, color=RED)
    ax.add_patch(matplotlib.patches.Arc(tuple(o + proj), 0.62, 0.62,
                                        theta1=-20, theta2=40, color=RED, lw=1.2))
    ax.text(4.85, 2.55, "沿轴的分量**完全不动**（$R\\mathbf{n}=\\mathbf{n}$）",
            fontsize=9.4, color=TEAL)
    ax.text(4.85, 2.10, "垂直的分量**只是在自己的平面里转**", fontsize=9.4, color=ORANGE)
    ax.text(4.85, 1.55, "$R(\\mathbf{n},\\alpha)=\\cos\\alpha\\,I+(1-\\cos\\alpha)\\mathbf{n}\\mathbf{n}^T"
                        "+\\sin\\alpha\\,N$", fontsize=10.0, color=INK)
    ax.text(4.85, 1.00, "$N$ 就是叉积矩阵（$\\mathbf{n}\\times\\mathbf{x}=N\\mathbf{x}$）",
            fontsize=9.0, color=MUTED)
    ax.text(4.85, 0.50, "这个分解就是公式三项的来源：常数项 + 斜坡项 + 正弦项", fontsize=9.0,
            color=INK)
    save(fig, "d13-rodrigues.png")


# ------------------------------------------------------- d14 四元数与半角
def d14():
    fig, ax = canvas(10.2, 3.4, (0, 10.2), (0, 3.4))
    ax.text(0.30, 3.10, "四元数旋转向量要用两次（$r\\,x\\,r^*$），所以角度减半", fontsize=10.4,
            color=INK, fontweight="bold")
    box(ax, 0.45, 1.55, 2.35, 1.05, "旋转 $\\theta$\n$r=(\\hat r\\sin\\frac{\\theta}{2},\\cos\\frac{\\theta}{2})$",
        fs=9.4, fc="#fff7ed", ec=ORANGE, tc="#7c3a00")
    arrow(ax, (2.88, 2.07), (3.55, 2.07), color=MUTED, lw=1.5)
    box(ax, 3.62, 1.55, 2.10, 1.05, "$x'=r\\,x\\,r^{*}$\n左乘一次、右乘一次", fs=9.2,
        fc=FILL, ec=STROKE)
    arrow(ax, (5.80, 2.07), (6.45, 2.07), color=MUTED, lw=1.5)
    box(ax, 6.52, 1.55, 1.85, 1.05, "总共转了\n$\\frac{\\theta}{2}+\\frac{\\theta}{2}=\\theta$",
        fs=9.2, fc="#e6f7f4", ec=TEAL, tc=TEAL)
    ax.text(0.45, 1.10, "所以「半角」不是笔误：$r$ 自己只承担一半的旋转量", fontsize=9.2,
            color=ORANGE)
    ax.text(0.45, 0.72, "$r$ 与 $-r$ 表示**同一个旋转**（double cover）—— 这也是"
                        "「最短路径插值」需要额外判断的原因", fontsize=9.2, color=INK)
    ax.text(0.45, 0.32, "实践分工：存储用四元数、渲染用矩阵、界面给人看用欧拉角", fontsize=9.0,
            color=MUTED)
    save(fig, "d14-quaternion-half-angle.png")


# ------------------------------------------------------- d15 层级变换
def d15():
    fig, ax = canvas(10.4, 3.8, (0, 10.4), (0, 3.8))
    ax.text(0.30, 3.50, "层级变换：改一个节点，带动整条子树", fontsize=10.4, color=INK,
            fontweight="bold")
    # 左：线性表示
    ax.text(0.45, 3.05, "线性表示：每个部件各自存一个世界矩阵", fontsize=9.4,
            color=RED, fontweight="bold")
    for i, lab in enumerate(["上臂", "下臂", "手"]):
        box(ax, 0.45 + i * 1.30, 2.20, 1.10, 0.58, lab, fs=8.8, fc="#fee2e2", ec=RED,
            tc="#7f1d1d")
    ax.text(0.45, 1.85, "抬一下手臂 → 要改 3 个矩阵", fontsize=8.8, color=RED)

    # 右：层级
    ax.text(5.30, 3.05, "层级表示：每个节点只存「相对父节点」的变换",
            fontsize=9.4, color=TEAL, fontweight="bold")
    nodes = {"躯干": (6.10, 2.35), "上臂": (7.35, 2.35), "下臂": (7.35, 1.55),
             "手": (7.35, 0.78)}
    for name, (x, y) in nodes.items():
        box(ax, x, y, 0.95, 0.54, name, fs=8.6, fc="#e6f7f4", ec=TEAL, tc=TEAL)
    arrow(ax, (7.06, 2.62), (7.33, 2.62), color=TEAL, lw=1.3)
    arrow(ax, (7.82, 2.33), (7.82, 2.11), color=TEAL, lw=1.3)
    arrow(ax, (7.82, 1.53), (7.82, 1.34), color=TEAL, lw=1.3)
    ax.text(5.30, 0.45, "抬手臂只改 1 个矩阵；叶子的最终变换 = 根到叶路径上所有变换的连乘",
            fontsize=8.8, color=MUTED)
    ax.text(5.30, 0.10, "代价：必须按层级顺序求值，或者用矩阵栈（push / pop）",
            fontsize=8.8, color=MUTED)
    save(fig, "d15-hierarchy.png")


# ------------------------------------------------------- d16 look-at 为什么是逆
def d16():
    fig, ax = canvas(10.4, 3.8, (0, 10.4), (0, 3.8))
    ax.text(0.30, 3.50, "look-at 是「把相机搬到原点」，所以它的逆才长得像转置",
            fontsize=10.4, color=INK, fontweight="bold")
    box(ax, 0.45, 2.20, 2.55, 1.05,
        "相机自己的正交系\n轴 $(r,u,-v)$ + 原点 $e$\n排成列 = 相机→世界",
        fs=8.8, fc="#f3e8ff", ec=PURPLE, tc=PURPLE)
    arrow(ax, (3.12, 2.72), (3.85, 2.72), color=MUTED, lw=1.5)
    box(ax, 3.92, 2.20, 2.75, 1.05,
        "世界→相机 = 它的逆\n旋转部分转置 + 平移取负\n$[r\\ u\\ -v]^T\\cdot T(-e)$",
        fs=8.8, fc="#e6f7f4", ec=TEAL, tc=TEAL)
    ax.text(0.45, 1.95, "相机 → 世界（列是轴）", fontsize=8.8, color=PURPLE)
    ax.text(0.45, 1.62,
            "  [ r_x  u_x  -v_x  e_x ]\n  [ r_y  u_y  -v_y  e_y ]\n"
            "  [ r_z  u_z  -v_z  e_z ]\n  [  0    0    0    1  ]",
            fontsize=8.4, color=INK, family="monospace", va="top", linespacing=1.4)
    ax.text(4.55, 1.95, "世界 → 相机（它的逆）", fontsize=8.8, color=TEAL)
    ax.text(4.55, 1.62,
            "  [ r_x  r_y  r_z  0 ]\n  [ u_x  u_y  u_z  0 ]\n"
            "  [ -v_x -v_y -v_z 0 ]\n  [  0    0    0    1 ]  × T(-e)",
            fontsize=8.4, color=TEAL, family="monospace", va="top", linespacing=1.4)
    ax.text(0.45, 0.72, "为什么旋转部分变成转置：相机三个轴构成**正交矩阵**，正交矩阵的逆就是转置",
            fontsize=9.2, color=ORANGE)
    ax.text(0.45, 0.35, "为什么是 $T(-e)$：把眼睛移到原点，等价于把世界反向平移 —— "
                        "这正是「动坐标系」解读", fontsize=9.2, color=MUTED)
    save(fig, "d16-lookat-inverse.png")


# ------------------------------------------------------- d17 针孔：除以 z
def d17():
    fig, ax = canvas(9.8, 4.0, (0, 9.8), (0, 4.0))
    ax.text(0.30, 3.72, "针孔相机：近大远小的全部数学就是「除以 z」", fontsize=10.4,
            color=INK, fontweight="bold")
    c = np.array([1.00, 1.55])          # 相机中心
    d = 1.55                             # 像平面在 z=d
    # 主光轴
    ax.annotate("", xy=(5.20, 1.55), xytext=c,
                arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.2))
    ax.plot(c[0], c[1], "o", ms=8, color=INK)
    ax.text(c[0] - 0.30, c[1] - 0.35, "$C$", fontsize=10)
    # 像平面
    ax.plot([c[0] + d, c[0] + d], [0.55, 2.65], color=TEAL, lw=2.0)
    ax.text(c[0] + d, 2.78, "像平面 $z=d$", fontsize=9.0, color=TEAL, ha="center")
    # 两个不同深度的场景点
    for z, y, col, lab in [(2.55, 2.35, ORANGE, "远"), (1.90, 2.65, PURPLE, "近")]:
        P = np.array([c[0] + z, y])
        ax.plot(*P, "o", ms=7, color=col, zorder=5)
        ax.plot([c[0], P[0]], [c[1], P[1]], color=col, lw=1.3, ls=(0, (4, 2)))
        t = d / z
        I = c + (P - c) * t
        ax.plot(*I, "o", ms=6, color=col, zorder=6)
        ax.text(P[0] + 0.10, P[1] + 0.08, lab, fontsize=8.6, color=col)
    ax.text(3.05, 0.72, "$x' = x\\cdot\\frac{d}{z}$", fontsize=11, color=INK)
    ax.text(3.05, 0.35, "$z$ 越大 → 投影越小 → 近大远小", fontsize=9.0, color=ORANGE)
    box(ax, 5.55, 1.35, 2.65, 1.55,
        "两个相似的直角三角形\n$\\frac{x'}{d}=\\frac{x}{z}$\n"
        "除法就是全部秘密",
        fs=8.8, fc=FILL, ec=STROKE)
    ax.text(5.55, 0.95, "难点在于：除法不是线性运算", fontsize=9.2, color=RED)
    ax.text(5.55, 0.60, "→ 必须借齐次坐标的 $\\div w$ 来实现", fontsize=9.2, color=TEAL)
    save(fig, "d17-pinhole.png")


# ------------------------------------------------------- d18 投影矩阵与 ÷w
def d18():
    fig, ax = canvas(10.4, 3.9, (0, 10.4), (0, 3.9))
    ax.text(0.30, 3.62, "透视矩阵：把「除以 z」搬到矩阵的最后一行", fontsize=10.4,
            color=INK, fontweight="bold")
    box(ax, 0.45, 1.95, 2.55, 1.10,
        "相机空间\n$(x,y,z,1)$\n视锥 frustum",
        fs=9.0, fc="#f3e8ff", ec=PURPLE, tc=PURPLE)
    arrow(ax, (3.12, 2.50), (3.80, 2.50), color=MUTED, lw=1.5)
    box(ax, 3.87, 1.95, 2.55, 1.10,
        "乘 $P$ 之后\n$w'=-z$\n$(x,y,z,-z)$",
        fs=9.0, fc="#fff7ed", ec=ORANGE, tc="#7c3a00")
    arrow(ax, (6.54, 2.50), (7.22, 2.50), color=MUTED, lw=1.5)
    box(ax, 7.29, 1.95, 2.55, 1.10,
        "齐次除法（÷w）\n$(-x/z,-y/z,\\cdot,1)$\nNDC：$[-1,1]^3$",
        fs=9.0, fc="#e6f7f4", ec=TEAL, tc=TEAL)

    ax.text(0.45, 1.74,
            "P = [ near/right    0          0             0        ]\n"
            "    [    0      near/top      0             0        ]\n"
            "    [    0         0      -(f+n)/(f-n)  -2fn/(f-n)   ]\n"
            "    [    0         0          -1             0        ]",
            fontsize=9.0, color=INK, family="monospace", va="top", linespacing=1.45)
    ax.text(4.85, 1.55, "最后一行 $(-1)$ 是全局关键：", fontsize=9.6, color=ORANGE)
    ax.text(4.85, 1.20, "它让 $w'$ 等于 $-z$，于是「除以 $w$」自动变成「除以 $z$」",
            fontsize=9.2, color=INK)
    ax.text(4.85, 0.85, "这是全课第一次出现「底行不是 $(0,0,0,1)$」的矩阵", fontsize=9.0,
            color=MUTED)
    ax.text(0.45, 0.45, "验证：把近平面角点 $(right,top,-near,1)$ 代进去 → "
                        "$(near,near,\\cdot,near)$ → 除以 $near$ → $(1,1,\\cdot,1)$ ✓",
            fontsize=9.2, color=GREEN)
    ax.text(0.45, 0.12, "注意：透视保住了深度的**顺序**，但不保间距 —— 近处精度高、远处糙",
            fontsize=9.0, color=RED)
    save(fig, "d18-projection-w.png")


if __name__ == "__main__":
    print("generating ->", OUT)
    for fn in [d01, d02, d03, d04, d05, d06, d07, d08, d09,
               d10, d11, d12, d13, d14, d15, d16, d17, d18]:
        fn()
    print("done: 18 diagrams")
