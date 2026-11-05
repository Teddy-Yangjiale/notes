# -*- coding: utf-8 -*-
"""CS184 课程笔记 · L13（光线追踪与加速结构）原创图解

风格遵循 scripts/cs184-notes-standard.md。
颜色语义：teal=主链路，orange=本讲焦点，purple=数据，red=错误/异常，灰=说明
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
                                    "notes", "cs184-13-ray-tracing-acceleration",
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


def box(ax, x, y, w, h, text, fc=FILL, ec=STROKE, tc=INK, fs=9.2, lw=1.4,
        pad=0.07, rad=0.13):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle=f"round,pad={pad},rounding_size={rad}",
                                facecolor=fc, edgecolor=ec, linewidth=lw, zorder=3))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            color=tc, zorder=4, linespacing=1.5)


def arrow(ax, p, q, color=TEAL, lw=1.8, ls="-", z=5, ms=13, rad=0.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=ms, color=color,
                                 lw=lw, linestyle=ls, zorder=z,
                                 connectionstyle=f"arc3,rad={rad}",
                                 shrinkA=1, shrinkB=1))


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=DPI, bbox_inches="tight",
                facecolor="white", pad_inches=0.12)
    plt.close(fig)
    print("  ", name)


# ------------------------------------------------- d01 光线投射
def d01():
    fig, ax = canvas(9.8, 3.6, (0, 9.8), (0, 3.6))
    ax.text(0.30, 3.34, "光线投射：每个像素发一条光线，取最近的交点", fontsize=10.2,
            color=INK, fontweight="bold")
    eye = np.array([0.70, 1.85])
    ax.plot(*eye, "o", ms=6, color=INK)
    ax.text(eye[0] - 0.10, eye[1] - 0.28, "眼睛", fontsize=8.2, color=INK)
    # 像平面
    ax.plot([1.75, 1.75], [0.95, 2.75], color=INK, lw=1.4)
    for k in range(4):
        ax.plot(1.75, 1.05 + k * 0.55, "s", ms=4, color=MUTED)
    ax.text(1.75, 0.72, "像平面（像素网格）", fontsize=7.8, color=MUTED, ha="center")
    # 场景：球和方
    ax.add_patch(Circle((4.40, 2.35), 0.62, facecolor="#e0f2fe", ec=BLUE, lw=1.3))
    ax.add_patch(Polygon([[4.10, 0.85], [5.55, 0.85], [5.55, 1.70], [4.10, 1.70]],
                         closed=True, facecolor="#f3e8ff", ec=PURPLE, lw=1.3))
    # 主光线
    P = np.array([1.75, 2.10])
    dirv = np.array([4.40, 2.35]) - P
    dirv = dirv / np.linalg.norm(dirv)
    hit = P + dirv * 2.20
    arrow(ax, tuple(eye), tuple(hit), color=TEAL, lw=1.8)
    ax.plot(*hit, "o", ms=6, color=RED, zorder=8)
    ax.text(hit[0] + 0.08, hit[1] + 0.16, "最近交点", fontsize=8.2, color=RED)
    # 继续前进（更多交点）
    arrow(ax, tuple(hit), tuple(hit + dirv * 1.2), color=MUTED, lw=1.2, ls=(0, (4, 3)))
    ax.text(hit[0] + 1.0, hit[1] - 0.30, "更远的交点（忽略）", fontsize=7.6, color=MUTED)
    # 阴影光线
    L = np.array([6.35, 3.05])
    ax.plot(*L, "o", ms=7, color=ORANGE, zorder=8)
    for k in range(8):
        a = 2 * np.pi * k / 8
        ax.plot([L[0], L[0] + 0.22 * np.cos(a)], [L[1], L[1] + 0.22 * np.sin(a)],
                color=ORANGE, lw=1.0)
    ax.text(L[0] - 0.20, L[1] - 0.30, "光源", fontsize=8.2, color=ORANGE)
    arrow(ax, tuple(hit), tuple(L), color=ORANGE, lw=1.4, ls=(0, (4, 3)))
    ax.text(5.35, 2.95, "阴影光线", fontsize=7.8, color=ORANGE)

    ax.text(0.40, 0.40, "步骤：① 从眼睛穿过像素中心发射一条光线　② 求它与所有物体的交点、取最近的一个　"
                        "③ 在该点做着色（第 8 讲 Blinn-Phong）　④ 向光源发一条「阴影光线」判断可见性",
            fontsize=8.4, color=INK)
    save(fig, "d01-ray-casting.png")


# ------------------------------------------------- d02 递归光线
def d02():
    fig, ax = canvas(9.8, 3.6, (0, 9.8), (0, 3.6))
    ax.text(0.30, 3.34, "Whitted 递归光线追踪：一次交点，四条光线", fontsize=10.2,
            color=INK, fontweight="bold")
    eye = np.array([0.60, 1.90])
    P = np.array([3.40, 1.55])
    ax.plot(*eye, "o", ms=5.5, color=INK)
    ax.text(eye[0] - 0.05, eye[1] - 0.26, "眼睛", fontsize=7.8, color=INK)
    arrow(ax, tuple(eye), tuple(P), color=TEAL, lw=2.0)
    ax.text(1.55, 1.72, "主光线", fontsize=8.0, color=TEAL)
    ax.plot(*P, "o", ms=6.5, color=RED, zorder=8)
    ax.text(P[0] + 0.05, P[1] - 0.26, "交点", fontsize=7.8, color=RED)
    # 法线
    N = np.array([0.0, 1.0])
    arrow(ax, tuple(P), tuple(P + N * 0.95), color=INK, lw=1.2, ms=10)
    ax.text(P[0] + 0.06, P[1] + 1.00, "$n$", fontsize=8.4, color=INK)
    # 反射
    d = (P - eye) / np.linalg.norm(P - eye)
    R = d - 2 * (d @ N) * N
    arrow(ax, tuple(P), tuple(P + R * 1.55), color=BLUE, lw=1.7)
    ax.text(*(P + R * 1.62), "反射光线", fontsize=8.0, color=BLUE)
    # 折射
    T = np.array([0.55, -1.0]); T = T / np.linalg.norm(T)
    arrow(ax, tuple(P), tuple(P + T * 1.45), color=PURPLE, lw=1.7)
    ax.text(*(P + T * 1.52), "折射光线", fontsize=8.0, color=PURPLE)
    # 阴影
    L = np.array([6.40, 2.95])
    ax.plot(*L, "o", ms=6.5, color=ORANGE, zorder=8)
    ax.text(L[0] - 0.10, L[1] + 0.16, "光源", fontsize=7.8, color=ORANGE)
    arrow(ax, tuple(P), tuple(L), color=ORANGE, lw=1.4, ls=(0, (4, 3)))
    ax.text(4.75, 2.10, "阴影光线", fontsize=7.6, color=ORANGE)

    ax.text(0.40, 0.55, "递归规则：", fontsize=8.8, color=INK)
    ax.text(1.45, 0.55, "沿反射/折射继续追，直到撞上「非镜面」表面，或者到达最大递归深度",
            fontsize=8.2, color=MUTED)
    ax.text(0.40, 0.22, "最终颜色 = 本地着色 + 反射项×权重 + 折射项×权重 —— 未命中任何物体时返回「环境色」，这就是为什么早期反射图背景总是渐变",
            fontsize=8.2, color=TEAL)
    save(fig, "d02-recursive-rays.png")


# ------------------------------------------------- d03 光线方程
def d03():
    fig, ax = canvas(9.4, 3.2, (0, 9.4), (0, 3.2), eq=False)
    ax.text(0.30, 2.94, "光线方程：一个起点 + 一个方向，参数 t 就是时间", fontsize=10.2,
            color=INK, fontweight="bold")
    ax.text(0.55, 2.35, r"$r(t)=o+t\,d,\qquad 0\leq t<\infty$", fontsize=13, color=TEAL)
    ax.text(0.55, 1.75, "$o$：起点（origin）", fontsize=8.8, color=MUTED)
    ax.text(0.55, 1.45, "$d$：方向（一般取单位向量）", fontsize=8.8, color=MUTED)
    ax.text(0.55, 1.15, "$t$：沿光线的距离（因为 $d$ 归一化，$t$ 就等于真实距离）", fontsize=8.8,
            color=ORANGE)
    ax.text(0.55, 0.72, "为什么用参数形式：", fontsize=8.8, color=INK)
    ax.text(0.55, 0.42, "把「求交点」变成「解一个关于 t 的方程」—— 这就是后面所有求交的统一套路",
            fontsize=8.4, color=MUTED)
    box(ax, 6.40, 1.55, 2.70, 1.00,
        "求交 = 把 $r(t)$ 代入\n物体的隐式方程 $f(p)=0$\n解出正的实数 $t$",
        fs=8.2, fc="#fff7ed", ec=ORANGE, tc="#7c3a00")
    save(fig, "d03-ray-equation.png")


# ------------------------------------------------- d04 光线-平面
def d04():
    fig, ax = canvas(9.6, 3.4, (0, 9.6), (0, 3.4))
    ax.text(0.30, 3.14, "光线与平面：解一个线性方程", fontsize=10.2, color=INK,
            fontweight="bold")
    # 平面
    ax.plot([0.55, 3.75], [1.35, 2.25], color=INK, lw=1.6)
    p0 = np.array([2.05, 1.88])
    ax.plot(*p0, "o", ms=5, color=INK, zorder=6)
    ax.text(p0[0] - 0.05, p0[1] - 0.26, "$p_0$", fontsize=9.0, color=INK)
    N = np.array([-0.35, 0.94]); N = N / np.linalg.norm(N)
    arrow(ax, tuple(p0), tuple(p0 + N * 0.85), color=INK, lw=1.3, ms=10)
    ax.text(*(p0 + N * 0.92), "$N$", fontsize=9.0, color=INK)
    # 光线
    o = np.array([1.05, 0.55])
    d = np.array([0.55, 0.85]); d = d / np.linalg.norm(d)
    # 求交
    t = ((p0 - o) @ N) / (d @ N)
    hit = o + t * d
    arrow(ax, tuple(o), tuple(hit), color=TEAL, lw=1.8)
    ax.plot(*hit, "o", ms=6, color=RED, zorder=8)
    ax.text(o[0] - 0.08, o[1] - 0.24, "$o$", fontsize=9.0, color=TEAL)
    ax.text((o[0] + hit[0]) / 2 - 0.30, (o[1] + hit[1]) / 2, "$d$", fontsize=9.0,
            color=TEAL)

    ax.text(4.45, 2.70, "平面：$(p-p_0)\\cdot N=0$", fontsize=10, color=INK)
    ax.text(4.45, 2.15, "把 $p=r(t)=o+td$ 代进去：", fontsize=9.0, color=INK)
    ax.text(4.45, 1.75, r"$(o+td-p_0)\cdot N=0$", fontsize=10, color=TEAL)
    ax.text(4.45, 1.30, r"$t=\dfrac{(p_0-o)\cdot N}{d\cdot N}$", fontsize=11.5, color=RED)
    ax.text(4.45, 0.72, "几何直觉：分子是「起点偏离平面多远」，", fontsize=8.4, color=MUTED)
    ax.text(4.45, 0.45, "分母是「每走单位长度靠近平面多少」", fontsize=8.4, color=MUTED)
    ax.text(4.45, 0.12, "分母为 0 ⇒ 光线平行于平面（无交点）", fontsize=8.4, color=ORANGE)
    save(fig, "d04-ray-plane.png")


# ------------------------------------------------- d05 光线-三角形
def d05():
    fig, ax = canvas(9.8, 3.4, (0, 9.8), (0, 3.4))
    ax.text(0.30, 3.14, "光线与三角形：先打到平面，再判断在不在三角形内", fontsize=10.2,
            color=INK, fontweight="bold")
    A, B, C = np.array([0.65, 1.05]), np.array([3.05, 1.05]), np.array([1.75, 2.60])
    ax.add_patch(Polygon([A, B, C], closed=True, facecolor="#e0f2fe", ec=BLUE, lw=1.4))
    for p, lab in [(A, "A"), (B, "B"), (C, "C")]:
        ax.plot(*p, "o", ms=4.5, color=BLUE, zorder=6)
        ax.text(p[0] - 0.05, p[1] - 0.26, lab, fontsize=8.6, color=BLUE)
    o = np.array([1.35, 0.25])
    hit = np.array([1.85, 1.72])
    arrow(ax, tuple(o), tuple(hit), color=TEAL, lw=1.8)
    ax.plot(*hit, "o", ms=6.5, color=RED, zorder=8)
    ax.text(hit[0] + 0.10, hit[1] + 0.10, "在内部 ✓", fontsize=8.2, color=GREEN)
    hit2 = np.array([2.85, 1.20])
    arrow(ax, tuple(o + [1.2, 0]), tuple(hit2), color=MUTED, lw=1.4, ls=(0, (4, 3)))
    ax.plot(*hit2, "o", ms=5.5, color=MUTED, zorder=8)
    ax.text(hit2[0] + 0.08, hit2[1] - 0.26, "在外部 ✗", fontsize=8.0, color=MUTED)

    ax.text(3.55, 2.55, "两步：", fontsize=9.2, color=INK)
    ax.text(3.55, 2.20, "① 求与三角**所在平面**的交点（用 d04）", fontsize=8.6, color=MUTED)
    ax.text(3.55, 1.90, "② 判断交点是否在三角形内（第 2 讲的 `L` 函数 / 重心坐标）",
            fontsize=8.6, color=MUTED)
    ax.text(3.55, 1.40, "更快的做法：Möller–Trumbore", fontsize=9.0, color=ORANGE)
    ax.text(3.55, 1.08, "把两个步骤合成一次 3×3 求解，", fontsize=8.4, color=MUTED)
    ax.text(3.55, 0.80, "顺便直接得到重心坐标 $(u,v)$", fontsize=8.4, color=MUTED)
    box(ax, 6.60, 1.10, 2.85, 1.35,
        "为什么用三角形求交\n而不是四边形？\n三角形一定是平面的", fs=8.2,
        fc="#e6f7f4", ec=TEAL, tc=TEAL)
    ax.text(0.30, 0.20, "注意：光线与三角形可以有 0 个、1 个、或（在边上时）多个交点 —— "
                        "退化情形要小心处理", fontsize=8.4, color=MUTED)
    save(fig, "d05-ray-triangle.png")


# ------------------------------------------------- d06 光线-球
def d06():
    fig, ax = canvas(9.6, 3.4, (0, 9.6), (0, 3.4))
    ax.text(0.30, 3.14, "光线与球：解一个二次方程（可能 0/1/2 个根）", fontsize=10.2,
            color=INK, fontweight="bold")
    c = np.array([2.15, 1.60])
    ax.add_patch(Circle(tuple(c), 0.95, facecolor="#e0f2fe", ec=BLUE, lw=1.4))
    ax.plot(*c, "o", ms=4.5, color=BLUE)
    ax.text(c[0] - 0.05, c[1] - 0.26, "$c$", fontsize=8.8, color=BLUE)
    o = np.array([0.55, 0.75])
    d = np.array([0.62, 0.38]); d = d / np.linalg.norm(d)
    t1, t2 = 1.30, 2.95
    p1, p2 = o + d * t1, o + d * t2
    ax.plot([o[0], p2[0] + 0.55 * d[0]], [o[1], p2[1] + 0.55 * d[1]], color=MUTED,
            lw=1.2, ls=(0, (4, 3)))
    ax.plot(*p1, "o", ms=6, color=GREEN, zorder=8)
    ax.plot(*p2, "o", ms=6, color=RED, zorder=8)
    ax.text(p1[0] - 0.35, p1[1] - 0.30, "$t_1$（近）", fontsize=8.2, color=GREEN)
    ax.text(p2[0] + 0.06, p2[1] + 0.12, "$t_2$（远）", fontsize=8.2, color=RED)
    arrow(ax, tuple(o), tuple(p1), color=TEAL, lw=1.6)
    ax.text(o[0] - 0.08, o[1] - 0.24, "$o$", fontsize=8.8, color=TEAL)

    ax.text(3.85, 2.60, r"$(o+td-c)^2-R^2=0$", fontsize=10, color=INK)
    ax.text(3.85, 2.10, r"$at^2+bt+c'=0$", fontsize=10, color=INK)
    ax.text(3.55, 1.62, r"$a=d\cdot d$", fontsize=8.6, color=MUTED)
    ax.text(3.55, 1.34, r"$b=2(o-c)\cdot d$", fontsize=8.6, color=MUTED)
    ax.text(3.55, 1.06, r"$c'=(o-c)\cdot(o-c)-R^2$", fontsize=8.6, color=MUTED)
    box(ax, 6.60, 1.55, 2.85, 1.15, "判别式 $b^2-4ac'$：\n>0 两个交点\n=0 相切（一个）\n<0 无交点",
        fs=8.0, fc="#fff7ed", ec=ORANGE, tc="#7c3a00")
    ax.text(0.30, 0.42, "取哪个根：取**较小的正根**（最近的那个）；如果较小根为负，说明球在相机背后，取较大根或判为未命中",
            fontsize=8.4, color=INK)
    ax.text(0.30, 0.12, "如果 $d$ 已经归一化，则 $a=1$，公式可以简化成 $t=-b/2\\pm\\sqrt{(b/2)^2-c'}$ —— "
                        "这是实现时的标准优化", fontsize=8.4, color=TEAL)
    save(fig, "d06-ray-sphere.png")


# ------------------------------------------------- d07 包围盒
def d07():
    fig, ax = canvas(9.6, 3.2, (0, 9.6), (0, 3.2))
    ax.text(0.30, 2.94, "包围盒：先花小代价排除掉绝大多数物体", fontsize=10.2, color=INK,
            fontweight="bold")
    ax.add_patch(Rectangle((0.75, 0.90), 2.10, 1.45, facecolor="#f8fafc", ec=ORANGE,
                           lw=1.6, ls=(0, (4, 3))))
    ax.add_patch(Polygon([[1.05, 1.15], [2.55, 1.05], [2.60, 1.95], [1.85, 2.15],
                          [1.10, 1.70]], closed=True, facecolor="#e0f2fe", ec=BLUE,
                         lw=1.2))
    ax.text(1.80, 0.62, "物体被包围盒完全包住", fontsize=8.2, color=MUTED, ha="center")
    # 两条光线：一条穿过盒子，一条没打中
    o1, o2 = np.array([0.35, 0.35]), np.array([3.35, 2.85])
    arrow(ax, tuple(o1), tuple(o1 + [1.6, 1.2]), color=TEAL, lw=1.6)
    ax.text(0.55, 0.20, "打中盒子 → 再测物体", fontsize=7.8, color=TEAL)
    arrow(ax, tuple(np.array([4.15, 0.45])), tuple(np.array([5.55, 1.85])), color=MUTED,
          lw=1.4)
    ax.text(4.15, 0.20, "没打中盒子 → 直接跳过", fontsize=7.8, color=MUTED)

    ax.text(6.10, 2.45, "两级测试：", fontsize=9.0, color=INK)
    ax.text(6.10, 2.12, "① 测包围盒（便宜）", fontsize=8.6, color=TEAL)
    ax.text(6.10, 1.82, "② 命中后再测物体（贵）", fontsize=8.6, color=BLUE)
    ax.text(6.10, 1.35, "前提：包围盒必须「完全包含」物体", fontsize=8.4, color=ORANGE)
    ax.text(6.10, 1.05, "否则会漏掉真实交点", fontsize=8.4, color=RED)
    ax.text(6.10, 0.60, "最常用：轴对齐包围盒（AABB）", fontsize=8.6, color=GREEN)
    ax.text(6.10, 0.32, "因为求交可以退化成三次「slab 比较」", fontsize=8.2, color=MUTED)
    save(fig, "d07-bounding-volume.png")


# ------------------------------------------------- d08 slab
def d08():
    fig, ax = canvas(9.8, 3.6, (0, 9.8), (0, 3.6))
    ax.text(0.30, 3.34, "AABB 求交：三个 slab 的 $t$ 区间求交集", fontsize=10.2,
            color=INK, fontweight="bold")
    # 盒子
    x0, x1, y0, y1 = 1.10, 3.30, 0.95, 2.55
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, facecolor="#f8fafc", ec=INK,
                           lw=1.4))
    # 光线
    o = np.array([0.45, 2.05]); d = np.array([1.0, -0.42]); d = d / np.linalg.norm(d)
    ts = [(x0 - o[0]) / d[0], (x1 - o[0]) / d[0],
          (y0 - o[1]) / d[1], (y1 - o[1]) / d[1]]
    tmin, tmax = max(min(ts[0], ts[1]), min(ts[2], ts[3])), min(max(ts[0], ts[1]),
                                                               max(ts[2], ts[3]))
    p_in, p_out = o + d * tmin, o + d * tmax
    ax.plot([o[0], o[0] + d[0] * 3.6], [o[1], o[1] + d[1] * 3.6], color=TEAL, lw=1.8)
    ax.plot(*p_in, "o", ms=6, color=GREEN, zorder=8)
    ax.plot(*p_out, "o", ms=6, color=RED, zorder=8)
    ax.text(p_in[0] - 0.10, p_in[1] + 0.22, "$t_{min}$", fontsize=8.6, color=GREEN)
    ax.text(p_out[0] + 0.08, p_out[1] + 0.16, "$t_{max}$", fontsize=8.6, color=RED)
    ax.plot([p_in[0], p_in[1]], [p_in[0], p_in[1]], color="none")
    ax.text(o[0] - 0.05, o[1] + 0.18, "$o$", fontsize=8.8, color=TEAL)

    ax.text(4.05, 3.05, "对每个轴各算一个 $[t_{near}, t_{far}]$：", fontsize=9.0, color=INK)
    ax.text(4.05, 2.70, r"$t_x=\dfrac{x_{0,1}-o_x}{d_x}$", fontsize=9.6, color=TEAL)
    ax.text(4.05, 2.28, r"$t_y=\dfrac{y_{0,1}-o_y}{d_y}$", fontsize=9.6, color=TEAL)
    ax.text(4.05, 1.90, "然后取**交集**：", fontsize=8.8, color=ORANGE)
    ax.text(4.05, 1.58, r"$t_{min}=\max(\min t_x,\min t_y)$", fontsize=9.2, color=GREEN)
    ax.text(4.05, 1.24, r"$t_{max}=\min(\max t_x,\max t_y)$", fontsize=9.2, color=RED)
    box(ax, 7.00, 1.10, 2.55, 1.25,
        "判据：\n$t_{min}<t_{max}$ 且 $t_{max}>0$\n否则没打中", fs=8.4,
        fc="#fff7ed", ec=ORANGE, tc="#7c3a00")
    ax.text(0.30, 0.42, "为什么比「测六个面」好：六个面要算 6 次平面求交 + 判断交点是否在面内（12 次比较）；"
                        "slab 法只需要 3 次除法 + 几次 max/min", fontsize=8.4, color=INK)
    ax.text(0.30, 0.12, "实现要点：$d$ 的分量为 0 时会出现除零 —— 标准做法是用 $\\pm\\infty$ 代替，"
                        "让 max/min 自动处理", fontsize=8.4, color=MUTED)
    save(fig, "d08-slab.png")


# ------------------------------------------------- d09 均匀网格
def d09():
    fig, ax = canvas(9.4, 3.6, (0, 9.4), (0, 3.6))
    ax.text(0.30, 3.34, "均匀网格：把空间切成格子，只测光线经过的格子", fontsize=10.2,
            color=INK, fontweight="bold")
    n = 6
    for i in range(n):
        for j in range(n):
            ax.add_patch(Rectangle((0.55 + i * 0.55, 0.55 + j * 0.45), 0.55, 0.45,
                                   facecolor="white", ec="#e5e7eb", lw=0.7))
    # 放几个物体
    for (cx, cy, s) in [(1.35, 1.30, 0.35), (2.35, 0.85, 0.28), (3.30, 1.80, 0.30),
                        (2.55, 2.05, 0.24)]:
        ax.add_patch(Circle((cx, cy), s, facecolor="#f3e8ff", ec=PURPLE, lw=1.1))
    # 光线 DDA 路径
    pts = [(0.35, 0.35), (1.10, 1.05), (1.65, 1.50), (2.20, 1.50), (2.75, 1.95),
           (3.60, 2.55)]
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color=TEAL, lw=1.6, ls="-")
    for k in range(len(pts) - 1):
        arrow(ax, pts[k], pts[k + 1], color=TEAL, lw=1.4, ms=9)
    for (px, py) in pts[1:-1]:
        ax.add_patch(Rectangle(((px - 0.55) // 0.55 * 0.55 + 0.55, (py - 0.45) // 0.45 * 0.45 + 0.55),
                               0.55, 0.45, facecolor="#ccfbf1", ec=TEAL, lw=0.9, alpha=0.6))

    ax.text(4.25, 2.75, "遍历：3D DDA", fontsize=9.2, color=INK)
    ax.text(4.25, 2.42, "从进入点开始，每次前进一个格子，", fontsize=8.4, color=MUTED)
    ax.text(4.25, 2.14, "只测「这个格子里存的物体」", fontsize=8.4, color=MUTED)
    ax.text(4.25, 1.70, "预处理（P81–P84）：", fontsize=8.8, color=ORANGE)
    ax.text(4.25, 1.38, "① 求整个场景包围盒", fontsize=8.2, color=MUTED)
    ax.text(4.25, 1.10, "② 划分成格子", fontsize=8.2, color=MUTED)
    ax.text(4.25, 0.82, "③ 把每个物体存进它覆盖的所有格子", fontsize=8.2, color=MUTED)
    box(ax, 6.85, 1.10, 2.35, 1.15, "格子数 = $C\\times$物体数\n$C\\approx 27$（3D 经验值）",
        fs=8.2, fc="#e6f7f4", ec=TEAL, tc=TEAL)
    ax.text(0.30, 0.20, "优点：构建极快、内存规整、遍历简单（DDA）。缺点见下两张图。",
            fontsize=8.4, color=MUTED)
    save(fig, "d09-grid.png")


# ------------------------------------------------- d10 网格分辨率
def d10():
    fig, ax = canvas(9.8, 3.2, (0, 9.8), (0, 3.2))
    ax.text(0.30, 2.94, "网格分辨率：太粗没加速，太细都在空转", fontsize=10.2, color=INK,
            fontweight="bold")
    for k, (n, lab, note, c) in enumerate([(1, "1 个格子", "等于没加速", RED),
                                           (5, "合适", "格子数与物体数同量级", GREEN),
                                           (14, "太细", "光线穿过大量空格", ORANGE)]):
        ox = 0.45 + k * 3.10
        for i in range(n):
            for j in range(n):
                ax.add_patch(Rectangle((ox + i * 1.95 / n, 0.95 + j * 1.55 / n),
                                       1.95 / n, 1.55 / n, facecolor="white",
                                       ec="#e5e7eb", lw=0.5))
        for (cx, cy, s) in [(0.5, 0.4, 0.16), (1.45, 1.15, 0.14), (1.0, 0.45, 0.12)]:
            ax.add_patch(Circle((ox + cx * 1.55, 0.95 + cy * 1.55), s, facecolor="#f3e8ff",
                                ec=PURPLE, lw=0.9))
        ax.text(ox + 0.98, 0.62, lab, fontsize=9.0, color=c, ha="center",
                fontweight="bold")
        ax.text(ox + 0.98, 0.32, note, fontsize=7.6, color=MUTED, ha="center")
        ax.text(ox + 0.98, 2.65, f"{n}×{n}", fontsize=8.2, color=MUTED, ha="center")
    ax.text(0.30, 0.05, "经验公式：格子数 ≈ C × 物体数，C ≈ 27（3D）。这是「每格平均放一个物体」的直觉。",
            fontsize=8.4, color=INK)
    save(fig, "d10-grid-resolution.png")


# ------------------------------------------------- d11 跨格物体
def d11():
    fig, ax = canvas(9.6, 3.4, (0, 9.6), (0, 3.4))
    ax.text(0.30, 3.14, "网格的坑：物体跨多格时，可能先撞到「更远」的物体", fontsize=10.2,
            color=INK, fontweight="bold")
    n = 5
    for i in range(n):
        for j in range(n):
            ax.add_patch(Rectangle((0.55 + i * 0.62, 0.75 + j * 0.50), 0.62, 0.50,
                                   facecolor="white", ec="#e5e7eb", lw=0.7))
    # 一个大物体跨多格（红），一个小物体只在一格（绿）
    ax.add_patch(Rectangle((1.15, 1.20), 1.85, 0.95, facecolor="#fde8e8", ec=RED, lw=1.4,
                           alpha=0.7))
    ax.text(2.05, 1.62, "大物体（远）", fontsize=8.0, color=RED, ha="center")
    ax.add_patch(Circle((2.55, 0.98), 0.22, facecolor="#dcfce7", ec=GREEN, lw=1.3))
    ax.text(2.55, 0.52, "小物体（近）", fontsize=7.6, color=GREEN, ha="center")
    # 光线
    o = np.array([0.35, 0.85])
    ax.plot([o[0], 3.40], [o[1], 1.60], color=TEAL, lw=1.6)
    ax.plot(*o, "o", ms=5, color=TEAL)
    # 顺序：先经过大物体的格子
    ax.plot(1.55, 1.28, "o", ms=5.5, color=RED, zorder=8)
    ax.text(1.05, 1.02, "① 先测到大物体", fontsize=7.6, color=RED)

    ax.text(4.05, 2.60, "问题：", fontsize=9.0, color=RED)
    ax.text(4.05, 2.28, "光线先进入「大物体所在的格子」，", fontsize=8.4, color=MUTED)
    ax.text(4.05, 2.00, "于是先测到了它 —— 但它其实更远。", fontsize=8.4, color=MUTED)
    ax.text(4.05, 1.55, "解法 ①：检查交点是否在本格内", fontsize=8.6, color=TEAL)
    ax.text(4.05, 1.25, "不在就继续往下一格走", fontsize=8.2, color=MUTED)
    ax.text(4.05, 0.85, "解法 ②：mailboxing（信箱法）", fontsize=8.6, color=TEAL)
    ax.text(4.05, 0.55, "同一个物体只在第一次遇到时测一次，", fontsize=8.2, color=MUTED)
    ax.text(4.05, 0.28, "之后用「已测过」标记跳过", fontsize=8.2, color=MUTED)
    save(fig, "d11-grid-overlap.png")


# ------------------------------------------------- d12 KD 树
def d12():
    fig, ax = canvas(9.8, 3.6, (0, 9.8), (0, 3.6))
    ax.text(0.30, 3.34, "KD 树：不均匀地切空间（每次只沿一个轴切一刀）", fontsize=10.2,
            color=INK, fontweight="bold")
    # 左：切分后的空间
    ax.add_patch(Rectangle((0.55, 0.65), 3.60, 2.50, facecolor="white", ec=INK, lw=1.3))
    ax.plot([2.15, 2.15], [0.65, 2.35], color=ORANGE, lw=1.6)
    ax.plot([0.55, 2.15], [1.70, 1.70], color=TEAL, lw=1.5)
    ax.plot([2.15, 4.15], [1.45, 1.45], color=PURPLE, lw=1.5)
    ax.plot([2.95, 2.95], [1.45, 3.15], color=BLUE, lw=1.5)
    for (cx, cy, s, lab) in [(1.35, 2.35, 0.16, "1"), (1.35, 1.15, 0.16, "2"),
                             (3.10, 2.35, 0.16, "3"), (3.10, 0.95, 0.16, "4")]:
        ax.add_patch(Circle((cx, cy), s, facecolor="#f3e8ff", ec=PURPLE, lw=1.0))
        ax.text(cx, cy, lab, fontsize=7.6, color=PURPLE, ha="center", va="center")
    ax.text(2.10, 0.42, "递归地沿 x / y / z 交替切开", fontsize=8.0, color=MUTED,
            ha="center")

    # 右：树的示意
    ax.text(5.35, 3.05, "对应的树：", fontsize=9.0, color=INK)
    nodes = [(5.90, 2.55, "根：x 切", ORANGE), (5.25, 1.75, "左：y 切", TEAL),
             (6.60, 1.75, "右：y 切", PURPLE),
             (4.95, 1.00, "叶 1", GREEN), (5.60, 1.00, "叶 2", GREEN),
             (6.30, 1.00, "叶 3", GREEN), (6.95, 1.00, "叶 4", GREEN)]
    for (x, y, lab, c) in nodes:
        box(ax, x - 0.30, y - 0.14, 0.60, 0.28, lab, fs=6.6, fc="white", ec=c, tc=c,
            pad=0.04)
    for a, b in [(nodes[0], nodes[1]), (nodes[0], nodes[2]), (nodes[1], nodes[3]),
                 (nodes[1], nodes[4]), (nodes[2], nodes[5]), (nodes[2], nodes[6])]:
        arrow(ax, (a[0], a[1] - 0.16), (b[0], b[1] + 0.18), color="#cbd5e1",
              lw=0.9, ms=8)
    ax.text(5.35, 0.62, "只切空间、不切物体 —— 一个物体可以被多个区域包含", fontsize=8.0,
            color=RED)
    ax.text(0.30, 0.20, "三种划分方式（P102）：Oct-Tree（每层沿三轴各切一刀，8 叉）、KD-Tree（每层只沿一个轴切一刀，2 叉）、"
                        "BSP-Tree（切面可以任意方向）", fontsize=8.4, color=INK)
    save(fig, "d12-kdtree.png")


# ------------------------------------------------- d13 KD 遍历的三种情况
def d13():
    fig, ax = canvas(10.2, 3.0, (0, 10.2), (0, 3.0), eq=False)
    ax.text(0.30, 2.76, "KD 树遍历：光线与切割面的三种位置关系", fontsize=10.2, color=INK,
            fontweight="bold")
    cases = [("$t_{max}<t_{split}$", "整条线段都在左边", "只访问左子树", TEAL),
             ("$t_{min}<t_{split}<t_{max}$", "跨过切割面", "两边都要访问（先近后远）", ORANGE),
             ("$t_{split}<t_{min}$", "整条线段都在右边", "只访问右子树", PURPLE)]
    for i, (cond, note, act, c) in enumerate(cases):
        ox = 0.55 + i * 3.25
        ax.add_patch(Rectangle((ox, 1.05), 2.60, 1.35, facecolor="white", ec=INK, lw=1.0))
        ax.plot([ox + 1.10, ox + 1.10], [1.05, 2.40], color=RED, lw=2.0)
        ax.text(ox + 1.10, 2.52, "$t_{split}$", fontsize=7.6, color=RED, ha="center")
        y = 1.35 + i * 0.0
        if i == 0:
            ax.plot([ox + 0.15, ox + 0.85], [1.75, 1.75], color=c, lw=2.4)
            ax.plot([ox + 0.15, ox + 0.85], [1.75, 1.75], "o", ms=3.5, color=c)
        elif i == 1:
            ax.plot([ox + 0.25, ox + 2.30], [1.45, 2.05], color=c, lw=2.4)
            ax.plot([ox + 0.25, ox + 2.30], [1.45, 2.05], "o", ms=3.5, color=c)
        else:
            ax.plot([ox + 1.35, ox + 2.30], [1.75, 1.75], color=c, lw=2.4)
            ax.plot([ox + 1.35, ox + 2.30], [1.75, 1.75], "o", ms=3.5, color=c)
        ax.text(ox + 1.30, 0.72, cond, fontsize=9.0, color=c, ha="center")
        ax.text(ox + 1.30, 0.42, note, fontsize=7.6, color=MUTED, ha="center")
        ax.text(ox + 1.30, 0.14, act, fontsize=7.8, color=INK, ha="center",
                fontweight="bold")
    save(fig, "d13-kdtree-traversal.png")


# ------------------------------------------------- d14 空间划分 vs 物体划分
def d14():
    fig, ax = canvas(9.8, 3.4, (0, 9.8), (0, 3.4))
    ax.text(0.30, 3.14, "两种划分哲学：切空间 vs 切物体", fontsize=10.2, color=INK,
            fontweight="bold")
    # 空间划分
    ax.text(1.95, 2.80, "空间划分（KD 树）", fontsize=8.8, color=ORANGE, ha="center")
    ax.add_patch(Rectangle((0.55, 0.80), 2.85, 1.75, facecolor="white", ec=INK, lw=1.1))
    ax.plot([1.95, 1.95], [0.80, 2.55], color=RED, lw=1.5)
    ax.plot([0.55, 1.95], [1.65, 1.65], color=RED, lw=1.2)
    ax.add_patch(Circle((1.35, 1.95), 0.52, facecolor="#fff7ed", ec=ORANGE, lw=1.2,
                        alpha=0.8))
    ax.text(1.35, 1.95, "物体", fontsize=7.4, color=ORANGE, ha="center", va="center")
    ax.text(1.95, 0.50, "区域互不重叠，但物体可跨多个区域", fontsize=7.4, color=MUTED,
            ha="center")

    # 物体划分
    ax.text(5.95, 2.80, "物体划分（BVH）", fontsize=8.8, color=TEAL, ha="center")
    for (cx, cy, s, c) in [(5.10, 1.35, 0.42, TEAL), (5.90, 1.35, 0.36, TEAL),
                           (6.60, 1.95, 0.30, TEAL)]:
        ax.add_patch(Circle((cx, cy), s, facecolor="#e6f7f4", ec=c, lw=1.2))
    ax.add_patch(Rectangle((4.55, 0.80), 1.75, 1.10, facecolor="none", ec=RED, lw=1.4,
                           ls=(0, (4, 3))))
    ax.add_patch(Rectangle((6.10, 1.45), 1.05, 1.05, facecolor="none", ec=RED, lw=1.4,
                           ls=(0, (4, 3))))
    ax.text(5.95, 0.50, "物体不重复，但包围盒可以重叠", fontsize=7.4, color=MUTED,
            ha="center")

    ax.text(0.30, 0.20, "为什么 BVH 更好实现：每个物体只属于一个叶子节点，不需要「检查交点是否在本格内」，"
                        "也不需要 mailboxing", fontsize=8.4, color=TEAL)
    ax.text(0.30, 0.02, "但 BVH 的包围盒会重叠 —— 重叠越严重，加速比越差", fontsize=8.4,
            color=RED)
    save(fig, "d14-spatial-vs-object.png")


# ------------------------------------------------- d15 BVH
def d15():
    fig, ax = canvas(9.8, 3.6, (0, 9.8), (0, 3.6))
    ax.text(0.30, 3.34, "BVH：每个节点罩住一棵子树的全部三角形", fontsize=10.2,
            color=INK, fontweight="bold")
    # 左：嵌套包围盒
    ax.add_patch(Rectangle((0.55, 0.75), 4.05, 2.45, facecolor="none", ec=INK, lw=1.8))
    ax.text(0.62, 3.05, "根", fontsize=7.8, color=INK)
    ax.add_patch(Rectangle((0.80, 0.95), 1.85, 2.05, facecolor="none", ec=TEAL, lw=1.3,
                           ls=(0, (4, 3))))
    ax.add_patch(Rectangle((2.75, 0.95), 1.65, 2.05, facecolor="none", ec=ORANGE, lw=1.3,
                           ls=(0, (4, 3))))
    for (cx, cy, s, c) in [(1.30, 2.55, 0.24, TEAL), (1.95, 1.40, 0.24, TEAL),
                           (3.15, 2.35, 0.24, ORANGE), (3.75, 1.55, 0.24, ORANGE)]:
        ax.add_patch(Circle((cx, cy), s, facecolor="white", ec=c, lw=1.1))
    ax.text(1.70, 0.55, "左子树包围盒", fontsize=7.4, color=TEAL, ha="center")
    ax.text(3.55, 0.55, "右子树包围盒", fontsize=7.4, color=ORANGE, ha="center")

    # 右：树
    ax.text(5.15, 3.05, "树结构：", fontsize=9.0, color=INK)
    box(ax, 5.55, 2.45, 1.10, 0.35, "根 bbox", fs=7.4, fc="white", ec=INK, tc=INK, pad=0.04)
    box(ax, 5.05, 1.75, 1.00, 0.35, "左 bbox", fs=7.2, fc="white", ec=TEAL, tc=TEAL,
        pad=0.04)
    box(ax, 6.35, 1.75, 1.00, 0.35, "右 bbox", fs=7.2, fc="white", ec=ORANGE, tc=ORANGE,
        pad=0.04)
    for x in (5.30, 5.80):
        box(ax, x - 0.22, 1.02, 0.44, 0.30, "叶", fs=6.6, fc="white", ec="#9ca3af",
            tc=MUTED, pad=0.03)
    for x in (6.55, 7.00):
        box(ax, x - 0.22, 1.02, 0.44, 0.30, "叶", fs=6.6, fc="white", ec="#9ca3af",
            tc=MUTED, pad=0.03)
    for a, b in [((6.10, 2.42), (5.55, 2.13)), ((6.10, 2.42), (6.85, 2.13)),
                 ((5.50, 1.72), (5.30, 1.35)), ((5.60, 1.72), (5.80, 1.35)),
                 ((6.80, 1.72), (6.55, 1.35)), ((6.90, 1.72), (7.00, 1.35))]:
        arrow(ax, a, b, color="#cbd5e1", lw=0.9, ms=8)

    ax.text(5.15, 0.62, "遍历只有四行：", fontsize=8.6, color=INK)
    ax.text(5.15, 0.34, "miss 就 return；是叶子就测所有物体；", fontsize=7.8, color=MUTED)
    ax.text(5.15, 0.10, "否则递归两个孩子、取更近的", fontsize=7.8, color=MUTED)
    save(fig, "d15-bvh.png")


# ------------------------------------------------- d16 SAH
def d16():
    fig, ax = canvas(10.0, 3.4, (0, 10.0), (0, 3.4))
    ax.text(0.30, 3.14, "SAH：按「被光线命中的概率」来选切法", fontsize=10.2, color=INK,
            fontweight="bold")
    # 两个候选切分
    for k, (ox, lab, cost, c) in enumerate([
            (0.55, "按中位数切：两个子盒大小接近", 0.62, ORANGE),
            (5.15, "按 SAH 切：子盒更紧、重叠更少", 0.41, GREEN)]):
        ax.add_patch(Rectangle((ox, 0.95), 4.10, 1.75, facecolor="white", ec=INK, lw=1.0))
        if k == 0:
            ax.add_patch(Rectangle((ox + 0.10, 1.05), 1.95, 1.55, facecolor="none",
                                   ec=c, lw=1.3, ls=(0, (4, 3))))
            ax.add_patch(Rectangle((ox + 2.05, 1.05), 1.95, 1.55, facecolor="none",
                                   ec=c, lw=1.3, ls=(0, (4, 3))))
        else:
            ax.add_patch(Rectangle((ox + 0.10, 1.05), 1.25, 1.55, facecolor="none",
                                   ec=c, lw=1.3, ls=(0, (4, 3))))
            ax.add_patch(Rectangle((ox + 1.45, 1.05), 2.50, 1.55, facecolor="none",
                                   ec=c, lw=1.3, ls=(0, (4, 3))))
        for i in range(5):
            for j in range(2):
                ax.add_patch(Circle((ox + 0.45 + i * 0.75, 1.35 + j * 0.75), 0.11,
                                    facecolor="#f3e8ff", ec=PURPLE, lw=0.7))
        ax.text(ox + 2.05, 0.62, lab, fontsize=7.6, color=MUTED, ha="center")
        ax.text(ox + 2.05, 0.32, f"估计代价 {cost}", fontsize=8.4, color=c, ha="center",
                fontweight="bold")

    ax.text(0.30, 0.02, "SAH 公式：$Cost = C_{trav} + SA(L)\\,N(L) + SA(R)\\,N(R)$ —— "
                        "面积比 ≈ 命中概率，$N$ 是子树的三角形数", fontsize=8.6, color=INK)
    save(fig, "d16-sah.png")


if __name__ == "__main__":
    print("generating ->", OUT)
    for fn in [d01, d02, d03, d04, d05, d06, d07, d08,
               d09, d10, d11, d12, d13, d14, d15, d16]:
        fn()
    print("done: 16 diagrams")
