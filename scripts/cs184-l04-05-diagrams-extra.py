# -*- coding: utf-8 -*-
"""CS184 · L04–05 追加图解（d19–d22），按 v2 标准补齐到 22 张。"""
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


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=DPI, bbox_inches="tight",
                facecolor="white", pad_inches=0.12)
    plt.close(fig)
    print("  ", name)


# ------------------------------------------------- d19 矩阵分解 T·R·S
def d19():
    fig, ax = canvas(10.0, 3.2, (0, 10.0), (0, 3.2), eq=False)
    ax.text(0.30, 2.94, "任何仿射矩阵都能拆成 T·R·S：平移、旋转、缩放", fontsize=10.0,
            color=INK, fontweight="bold")
    # 三个方块：原始 → S → R → T
    def square(ox, oy, w, h, shear=0.0, rot=0.0, col=BLUE, alpha=1.0):
        pts = np.array([[0, 0], [w, 0], [w, h], [0, h]])
        pts[:, 0] += shear * pts[:, 1]
        c, s = np.cos(rot), np.sin(rot)
        R = np.array([[c, -s], [s, c]])
        pts = pts @ R.T
        pts += [ox, oy]
        ax.add_patch(Polygon(pts, closed=True, facecolor="white", ec=col, lw=1.5,
                             alpha=alpha, zorder=3))

    square(0.55, 1.05, 1.05, 1.05, 0, 0, MUTED)
    ax.text(1.07, 0.72, "原图", fontsize=7.6, color=MUTED, ha="center")

    square(2.25, 1.05, 1.85, 0.62, 0, 0, ORANGE)
    ax.text(3.17, 0.72, "S（缩放，可能非均匀）", fontsize=7.2, color=ORANGE, ha="center")

    square(4.95, 1.30, 1.30, 1.30, 0, np.radians(28), TEAL)
    ax.text(5.60, 0.72, "R（旋转）", fontsize=7.6, color=TEAL, ha="center")

    square(7.55, 1.30, 1.30, 1.30, 0, np.radians(28), PURPLE)
    ax.text(8.20, 0.72, "T（平移）", fontsize=7.6, color=PURPLE, ha="center")

    arrow(ax, (1.75, 1.57), (2.15, 1.57), color=MUTED, lw=1.2)
    arrow(ax, (4.20, 1.57), (4.85, 1.57), color=MUTED, lw=1.2)
    arrow(ax, (6.45, 1.57), (7.45, 1.57), color=MUTED, lw=1.2)
    ax.text(6.95, 1.75, "+ 平移", fontsize=6.6, color=MUTED, ha="center")

    ax.text(0.55, 0.35, "顺序：先缩放、再旋转、最后平移（矩阵写法 $M = T\\,R\\,S$，作用到点上是先 S）",
            fontsize=7.8, color=INK)
    ax.text(0.55, 0.10, "为什么这个顺序：缩放要对齐物体自身轴，旋转要绕自身中心，"
                        "平移才把它放到世界位置 —— 换成别的顺序语义就变了",
            fontsize=7.8, color=MUTED)
    save(fig, "d19-trs-decompose.png")


# ------------------------------------------------- d20 四元数插值
def d20():
    fig, ax = canvas(9.8, 3.4, (0, 9.8), (0, 3.4))
    ax.text(0.30, 3.14, "旋转插值：矩阵线性插值会「缩水」，四元数不会", fontsize=10.0,
            color=INK, fontweight="bold")
    # 左：线性插值矩阵（会缩）
    ax.add_patch(Circle((1.85, 1.65), 0.85, facecolor="white", ec=INK, lw=1.3))
    for k, ang in enumerate([0, 45, 90]):
        c, s = np.cos(np.radians(ang)), np.sin(np.radians(ang))
        L = 0.80 * (1 - 0.18 * (k == 1))
        ax.plot([1.85, 1.85 + L * c], [1.65, 1.65 + L * s], color=RED if k == 1 else MUTED,
                lw=2.0 if k == 1 else 1.2)
    ax.text(1.85, 0.52, "矩阵线性插值", fontsize=8.0, color=RED, ha="center")
    ax.text(1.85, 2.65, "中间帧变短（长度 < 1）", fontsize=7.4, color=RED, ha="center")

    # 右：四元数 slerp（保持长度）
    ax.add_patch(Circle((5.35, 1.65), 0.85, facecolor="white", ec=INK, lw=1.3))
    for k, ang in enumerate([0, 45, 90]):
        c, s = np.cos(np.radians(ang)), np.sin(np.radians(ang))
        ax.plot([5.35, 5.35 + 0.80 * c], [1.65, 1.65 + 0.80 * s],
                color=GREEN if k == 1 else MUTED, lw=2.0 if k == 1 else 1.2)
    ax.text(5.35, 0.52, "四元数 slerp", fontsize=8.0, color=GREEN, ha="center")
    ax.text(5.35, 2.65, "中间帧仍在单位圆上", fontsize=7.4, color=GREEN, ha="center")

    ax.text(7.10, 2.45, "为什么：", fontsize=8.2, color=INK)
    ax.text(7.10, 2.15, "矩阵是 9 个数的", fontsize=7.2, color=MUTED)
    ax.text(7.10, 1.92, "线性组合 → 一般", fontsize=7.2, color=MUTED)
    ax.text(7.10, 1.69, "不再正交 → 有缩放", fontsize=7.2, color=MUTED)
    ax.text(7.10, 1.32, "四元数只在单位", fontsize=7.2, color=TEAL)
    ax.text(7.10, 1.09, "球面上走弧（slerp）", fontsize=7.2, color=TEAL)
    ax.text(7.10, 0.74, "$q = (\\cos\\frac{\\theta}{2},\\ \\sin\\frac{\\theta}{2}\\,\\hat{n})$",
            fontsize=7.0, color=PURPLE)
    ax.text(7.10, 0.40, "半角是关键", fontsize=7.0, color=ORANGE)
    save(fig, "d20-quat-interp.png")


# ------------------------------------------------- d21 深度非线性
def d21():
    fig, ax = canvas(9.8, 3.4, (0, 9.8), (0, 3.4), eq=False)
    ax.text(0.30, 3.14, "常规透视 + 定点深度：约 90% 的取值范围落在近处 0.9 米", fontsize=9.6,
            color=INK, fontweight="bold")
    n, f = 0.1, 1000.0
    z = np.logspace(-1, 3, 400)  # 0.1 .. 1000
    ndc = (f + n) / (f - n) - 2 * f * n / ((f - n) * z)
    xs = 0.70 + 3.30 * (np.log10(z) + 1) / 4.0
    ax.plot(xs, 0.80 + 1.90 * (ndc + 1) / 2, color=TEAL, lw=2.0)
    ax.text(2.40, 2.90, "$z_{ndc}$ vs $s=-z_{eye}$（对数横轴）", fontsize=7.8, color=MUTED,
            ha="center")
    # 标几个点
    for zz, lab in [(0.1, "0.1"), (1.0, "1"), (10.0, "10"), (100.0, "100"), (1000.0, "1000")]:
        v = (f + n) / (f - n) - 2 * f * n / ((f - n) * zz)
        x = 0.70 + 3.30 * (np.log10(zz) + 1) / 4.0
        ax.plot(x, 0.80 + 1.90 * (v + 1) / 2, "o", ms=4, color=ORANGE, zorder=8)
        ax.text(x, 0.58, lab, fontsize=6.8, color=MUTED, ha="center")

    ax.text(4.55, 2.55, "读法：", fontsize=8.2, color=INK)
    ax.text(4.55, 2.25, "$s=0.1$（近裁剪面）→ $z_{ndc}=-1$", fontsize=7.4, color=MUTED)
    ax.text(4.55, 1.98, "$s=1$ → 已经到 $z_{ndc}\\approx0.80018$", fontsize=7.4, color=ORANGE)
    ax.text(4.55, 1.70, "$s=1000$（远裁剪面）→ $z_{ndc}=+1$", fontsize=7.4, color=MUTED)
    ax.text(4.55, 1.35, "$s\\in[0.1,1]$：约占定点深度取值范围的 90%", fontsize=7.4, color=RED)
    ax.text(4.55, 1.05, "远处距离分辨率低 → 邻近表面易发生 z-fighting", fontsize=7.4, color=ORANGE)
    ax.text(4.55, 0.70, "缓解①：把近裁剪面推远（n 从 0.1 → 0.5）", fontsize=7.2, color=TEAL)
    ax.text(4.55, 0.42, "缓解②：反向 Z（reversed-Z）配合浮点深度", fontsize=7.2, color=TEAL)
    ax.text(0.30, 0.08, "注意：横轴是 log 尺度 —— 如果用线性横轴，曲线会在最左边几乎垂直，"
                        "右侧完全贴平", fontsize=7.4, color=MUTED)
    save(fig, "d21-depth-nonlinear.png")


# ------------------------------------------------- d22 fovy 与 aspect
def d22():
    fig, ax = canvas(9.6, 3.4, (0, 9.6), (0, 3.4))
    ax.text(0.30, 3.14, "fovy 与 aspect 怎么决定视锥：两个方向各有一个 tan", fontsize=10.0,
            color=INK, fontweight="bold")
    eye = np.array([0.75, 1.65])
    ax.plot(*eye, "o", ms=6, color=INK)
    ax.text(eye[0] - 0.05, eye[1] - 0.30, "眼睛", fontsize=7.8, color=INK)
    # 视锥（俯视）
    d = 3.0
    half = d * np.tan(np.radians(25))
    apex = eye + np.array([d, 0])
    ax.add_patch(Polygon([eye, apex + [0, half], apex - [0, half]], closed=True,
                         facecolor="#e6f7f4", ec=TEAL, lw=1.3, alpha=0.6))
    ax.plot([apex[0], apex[0]], [apex[1] - half, apex[1] + half], color=TEAL, lw=1.6)
    ax.text(apex[0] + 0.08, apex[1] + half * 0.5, "近裁剪面", fontsize=7.2, color=TEAL)
    # 角度标注
    ax.plot([eye[0], eye[0] + 1.2], [eye[1], eye[1]], color=MUTED, lw=0.8, ls=(0, (3, 2)))
    ax.text(eye[0] + 0.55, eye[1] + 0.12, "$fovy/2$", fontsize=7.2, color=MUTED)

    ax.text(4.45, 2.75, "纵向：", fontsize=8.2, color=INK)
    ax.text(4.65, 2.45, "$\\tan\\dfrac{fovy}{2} = \\dfrac{h/2}{d}$", fontsize=9.0, color=TEAL)
    ax.text(4.45, 1.95, "横向由 aspect 推出来：", fontsize=8.0, color=INK)
    ax.text(4.65, 1.62, "$\\tan\\dfrac{fovx}{2} = \\text{aspect}\\cdot\\tan\\dfrac{fovy}{2}$",
            fontsize=9.0, color=ORANGE)
    ax.text(4.45, 1.10, "屏幕坐标：", fontsize=8.0, color=INK)
    ax.text(4.65, 0.80, "$x_s = \\dfrac{x_c}{-z_c\\tan(fovx/2)},\\quad "
                        "y_s = \\dfrac{y_c}{-z_c\\tan(fovy/2)}$", fontsize=8.2, color=PURPLE)
    box(ax, 7.35, 1.25, 2.15, 1.15, "只给 fovy 就够\naspect 决定横向\n（不给就拉伸）", fs=7.2,
        fc="#fff7ed", ec=ORANGE, tc="#7c3a00")
    ax.text(0.30, 0.20, "常见错误：给了 fovy 却忘了用 aspect 算横向 → 图被拉伸；"
                        "或者 fov 指水平而非垂直（不同 API 约定不同）", fontsize=7.6, color=RED)
    save(fig, "d22-fovy-aspect.png")


if __name__ == "__main__":
    print("generating ->", OUT)
    for fn in [d19, d20, d21, d22]:
        fn()
    print("done: 4 extra diagrams")
