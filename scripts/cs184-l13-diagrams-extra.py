# -*- coding: utf-8 -*-
"""CS184 · L13 追加图解（d17–d22），供「新标准」扩写使用。

风格与 cs184-l13-diagrams.py 一致：一图一关系、无坐标轴、
颜色语义固定（teal=主链路，orange=焦点，purple=数据，red=错误，灰=说明）。
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


def box(ax, x, y, w, h, text, fc=FILL, ec=STROKE, tc=INK, fs=9.0, lw=1.4,
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


# ------------------------------------------------- d17 像素 → 光线
def d17():
    fig, ax = canvas(9.8, 3.4, (0, 9.8), (0, 3.4), eq=False)
    ax.text(0.30, 3.14, "一个像素怎么变成一条光线：三次坐标系转换", fontsize=10.2,
            color=INK, fontweight="bold")
    steps = [("① 像素索引\n$(i,j)$", "整数，左上角为原点", TEAL),
             ("② 归一化\n$(u,v)$", "u=(i+0.5)/W\nv=(j+0.5)/H", ORANGE),
             ("③ 屏幕坐标\n$(x_s,y_s)$", "映射到 $[-1,1]$ 或 $[0,1]$\n（看约定）", PURPLE),
             ("④ 相机空间方向\n$(x_c,y_c,-1)$", "乘 fov 的 tan", "blue"),
             ("⑤ 世界空间方向", "乘相机旋转\n再归一化", "green")]
    colors = {TEAL: TEAL, ORANGE: ORANGE, PURPLE: PURPLE, "blue": BLUE, "green": GREEN}
    for i, (t1, t2, c) in enumerate(steps):
        x = 0.30 + i * 1.92
        col = colors[c]
        box(ax, x, 1.55, 1.62, 1.05, t1, fs=8.0, fc="white", ec=col, tc=col)
        ax.text(x + 0.81, 1.18, t2, fontsize=7.0, color=MUTED, ha="center",
                va="top", linespacing=1.6)
        if i < 4:
            arrow(ax, (x + 1.66, 2.07), (x + 1.90, 2.07), color=MUTED, lw=1.1, ms=9)
    ax.text(0.30, 0.55, "关键：加 0.5 是为了取像素「中心」，而不是用整数索引 —— 否则整张图会偏半个像素",
            fontsize=8.4, color=RED)
    ax.text(0.30, 0.28, "最后一定要归一化 $d$：这样 $t$ 才是真实距离，AABB 的 slab 公式和"
                        "「取最小 $t$」都依赖这一点", fontsize=8.4, color=INK)
    save(fig, "d17-ray-generation.png")


# ------------------------------------------------- d18 折射
def d18():
    fig, ax = canvas(9.8, 3.6, (0, 9.8), (0, 3.6))
    ax.text(0.30, 3.34, "折射：Snell 定律给角度，向量形式给方向", fontsize=10.2,
            color=INK, fontweight="bold")
    # 界面
    ax.plot([0.55, 3.75], [1.75, 1.75], color=INK, lw=1.6)
    ax.text(3.78, 1.62, "界面", fontsize=8.0, color=MUTED)
    P = np.array([2.15, 1.75])
    N = np.array([0.0, 1.0])
    arrow(ax, tuple(P), tuple(P + N * 0.95), color=INK, lw=1.2, ms=10)
    ax.text(P[0] + 0.06, P[1] + 1.00, "$n$", fontsize=9.0, color=INK)
    # 入射
    I = np.array([0.50, -0.86]); I = I / np.linalg.norm(I)
    arrow(ax, tuple(P - I * 1.35), tuple(P), color=TEAL, lw=1.8)
    ax.text(*(P - I * 1.45), "入射 $d$", fontsize=8.4, color=TEAL)
    # 反射
    R = I - 2 * (I @ N) * N
    arrow(ax, tuple(P), tuple(P + R * 1.20), color=BLUE, lw=1.4, ls=(0, (4, 3)))
    ax.text(*(P + R * 1.28), "反射（部分）", fontsize=7.8, color=BLUE)
    # 折射
    eta = 1.5
    cosi = -(I @ N)
    k = 1 - eta ** 2 * (1 - cosi ** 2)
    T = eta * I + (eta * cosi - np.sqrt(max(k, 1e-9))) * N
    T = T / np.linalg.norm(T)
    arrow(ax, tuple(P), tuple(P + T * 1.25), color=PURPLE, lw=1.8)
    ax.text(*(P + T * 1.33), "折射 $t$", fontsize=8.4, color=PURPLE)

    ax.text(4.30, 2.85, r"$\dfrac{\sin\theta_i}{\sin\theta_t}=\dfrac{\eta_t}{\eta_i}$",
            fontsize=12, color=INK)
    ax.text(4.30, 2.10, "向量形式（已知 $k$）：", fontsize=8.6, color=MUTED)
    ax.text(4.30, 1.75, r"$t=\eta d+\left(\eta\cos\theta_i-\sqrt{k}\right)n$", fontsize=9.6,
            color=PURPLE)
    ax.text(4.30, 1.35, r"$\eta=\eta_i/\eta_t,\quad k=1-\eta^2(1-\cos^2\theta_i)$",
            fontsize=8.6, color=MUTED)
    box(ax, 4.30, 0.62, 2.75, 0.60, "$k<0$ ⇒ 全反射", fs=8.4, fc="#fff7ed",
        ec=ORANGE, tc="#7c3a00")
    ax.text(7.30, 2.30, "两个实现要点：", fontsize=8.6, color=INK)
    ax.text(7.30, 1.98, "① $k<0$ 时没有实根", fontsize=8.2, color=RED)
    ax.text(7.48, 1.70, "→ 只能全反射", fontsize=7.8, color=MUTED)
    ax.text(7.30, 1.30, "② 进入物体后", fontsize=8.2, color=TEAL)
    ax.text(7.48, 1.02, "法向要取反", fontsize=7.8, color=MUTED)
    ax.text(7.30, 0.62, "否则会在内部", fontsize=7.8, color=MUTED)
    ax.text(7.48, 0.38, "立刻「折射出去」", fontsize=7.8, color=MUTED)
    save(fig, "d18-refraction.png")


# ------------------------------------------------- d19 递归树的代价
def d19():
    fig, ax = canvas(9.8, 3.4, (0, 9.8), (0, 3.4), eq=False)
    ax.text(0.30, 3.14, "递归的代价是指数增长 —— 所以必须有深度上限", fontsize=10.2,
            color=INK, fontweight="bold")
    # 三档深度
    for k, (depth, n) in enumerate([(1, 12), (2, 40), (3, 90)]):
        ox = 0.75 + k * 3.05
        ax.text(ox + 0.85, 2.72, f"深度 {depth}", fontsize=8.8, color=MUTED, ha="center")
        ax.text(ox + 0.85, 2.44, f"约 {n} 条光线/像素", fontsize=7.8, color=MUTED,
                ha="center")
        for i in range(min(n, 30)):
            px = ox + 0.85 + (i % 6) * 0.28 - 0.70
            py = 1.95 - (i // 6) * 0.30
            c = TEAL if i < 10 else (ORANGE if i < 20 else PURPLE)
            ax.plot(px, py, "o", ms=3.2, color=c)
    ax.text(0.30, 0.80, "每层都有 2 条次级光线（反射 + 折射）时：总光线数 $\\approx 2^{d+1}$",
            fontsize=9.0, color=TEAL)
    box(ax, 5.55, 0.30, 3.90, 0.62,
        "Whitted 典型深度 5–10；路径追踪则用「按概率截断」", fs=8.0, fc="#fff7ed",
        ec=ORANGE, tc="#7c3a00")
    ax.text(0.30, 0.42, "所以「最大递归深度」不是可选的优化，而是**必须**的 —— 否则玻璃球会无限反射下去",
            fontsize=8.4, color=RED)
    save(fig, "d19-recursion-tree.png")


# ------------------------------------------------- d20 自相交与 epsilon
def d20():
    fig, ax = canvas(9.6, 3.4, (0, 9.6), (0, 3.4))
    ax.text(0.30, 3.14, "阴影光线会「打到自己」：epsilon 偏移", fontsize=10.2, color=INK,
            fontweight="bold")
    P = np.array([1.55, 1.55])
    N = np.array([0.0, 1.0])
    ax.plot([0.35, 2.85], [1.55, 1.55], color=INK, lw=1.4)
    ax.plot(*P, "o", ms=6, color=RED, zorder=8)
    ax.text(P[0] + 0.06, P[1] - 0.30, "交点 $p$", fontsize=8.2, color=RED)
    arrow(ax, tuple(P), tuple(P + N * 1.15), color=INK, lw=1.1, ms=10)
    ax.text(P[0] + 0.06, P[1] + 1.20, "$n$", fontsize=8.6, color=INK)
    # 光线从左下射来
    o = np.array([0.45, 0.55])
    arrow(ax, tuple(o), tuple(P), color=TEAL, lw=1.6)
    # 起点正好在表面：会立刻再命中自己
    ax.plot(P[0] + 0.02, P[1] + 0.02, "x", ms=7, color=RED, zorder=9)
    ax.text(P[0] - 1.05, P[1] + 0.42, "起点恰在面上 → 立刻命中自己", fontsize=7.6, color=RED)

    ax.text(3.45, 2.70, "解法一：沿法线偏移", fontsize=8.8, color=TEAL)
    ax.text(3.65, 2.38, r"$p' = p + \varepsilon\,n$", fontsize=9.6, color=TEAL)
    ax.text(3.45, 1.95, "解法二：给 $t$ 一个下界", fontsize=8.8, color=ORANGE)
    ax.text(3.65, 1.63, r"$t_{\min} = \varepsilon$（如 $10^{-4}$）", fontsize=9.4, color=ORANGE)
    ax.text(3.45, 1.20, "两种都要用：", fontsize=8.4, color=INK)
    ax.text(3.65, 0.92, "偏移量不能太大 —— 否则近处阴影会「漏光」；", fontsize=7.8, color=MUTED)
    ax.text(3.65, 0.66, "也不能太小 —— 否则浮点误差仍会自相交", fontsize=7.8, color=MUTED)
    box(ax, 6.95, 1.30, 2.35, 1.20,
        "常见做法\n$\\varepsilon$ 随 $|p|$ 缩放\n（因为远处的浮点\n绝对误差更大）", fs=7.6,
        fc="#fff7ed", ec=ORANGE, tc="#7c3a00")
    save(fig, "d20-epsilon.png")


# ------------------------------------------------- d21 SAH 前缀扫描
def d21():
    fig, ax = canvas(10.0, 3.4, (0, 10.0), (0, 3.4), eq=False)
    ax.text(0.30, 3.14, "分桶 + 前缀/后缀扫描：把 SAH 从 O(N²) 降到 O(N)", fontsize=10.2,
            color=INK, fontweight="bold")
    B = 6
    counts = [8, 3, 0, 5, 12, 2]
    for i, c in enumerate(counts):
        x = 0.55 + i * 1.05
        ax.add_patch(Rectangle((x, 1.15), 0.90, 1.00, facecolor="#f8fafc", ec=MUTED,
                               lw=0.9))
        ax.text(x + 0.45, 1.95, f"$b_{i}$", fontsize=8.0, color=MUTED, ha="center")
        ax.text(x + 0.45, 1.55, str(c), fontsize=9.0, color=PURPLE, ha="center")
    ax.text(0.55, 0.85, "① 每个桶里物体数", fontsize=8.2, color=MUTED)

    # 三个候选切面
    for k, cut in enumerate([2, 3, 4]):
        x = 0.55 + cut * 1.05
        ax.plot([x, x], [1.15, 2.25], color=RED, lw=1.6, ls=(0, (3, 2)))
        ax.text(x + 0.05, 2.32, f"切 {cut}", fontsize=7.4, color=RED)

    ax.text(4.30, 2.62, "② 对每个候选切面算", fontsize=8.8, color=INK)
    ax.text(4.55, 2.28, r"$SA(L)N(L)+SA(R)N(R)$", fontsize=10, color=TEAL)
    ax.text(4.30, 1.80, "关键技巧：", fontsize=8.4, color=ORANGE)
    ax.text(4.55, 1.52, "从左往右扫一遍，", fontsize=7.8, color=MUTED)
    ax.text(4.55, 1.26, "累计 $N(L)$ 和 $bbox(L)$；", fontsize=7.8, color=MUTED)
    ax.text(4.55, 1.00, "从右往左扫一遍，", fontsize=7.8, color=MUTED)
    ax.text(4.55, 0.74, "累计 $N(R)$ 和 $bbox(R)$。", fontsize=7.8, color=MUTED)
    ax.text(4.30, 0.36, "于是每个候选 $O(1)$，总共 $O(B)$ —— 而不是 $O(N)$。", fontsize=8.2,
            color=GREEN)
    box(ax, 7.35, 1.25, 2.35, 1.25, "复杂度\n$O(N)$ 填桶\n$+\\,O(B)$ 评估\n（$B<32$）",
        fs=7.8, fc="#e6f7f4", ec=TEAL, tc=TEAL)
    save(fig, "d21-sah-sweep.png")


# ------------------------------------------------- d22 两种遍历的代码对照
def d22():
    fig, ax = canvas(10.0, 3.7, (0, 10.0), (0, 3.7), eq=False)
    ax.text(0.30, 3.44, "同一件事，两段代码：KD 树 vs BVH 的遍历", fontsize=10.2,
            color=INK, fontweight="bold")
    kd = ("if (!hitBox) return;\n"
          "tSplit = (xSplit-o.x)/d.x;\n"
          "if (tMax < tSplit)\n"
          "    recurse(L, tMin, tMax);\n"
          "else if (tSplit < tMin)\n"
          "    recurse(R, tMin, tMax);\n"
          "else {\n"
          "    recurse(L, tMin, tSplit);\n"
          "    recurse(R, tSplit, tMax);\n"
          "}")
    bvh = ("if (!hitBox) return;\n"
           "if (leaf) {\n"
           "    test all objs;\n"
           "    return closest;\n"
           "}\n"
           "h1 = recurse(child1);\n"
           "h2 = recurse(child2);\n"
           "return closer(h1, h2);")
    ax.add_patch(Rectangle((0.40, 1.05), 4.45, 2.10, facecolor="#fff7ed", ec=ORANGE,
                           lw=1.3))
    ax.text(0.52, 3.00, "KD \u6811\u904d\u5386", fontsize=8.4, color=ORANGE)
    ax.text(0.55, 2.82, kd, fontsize=6.6, color="#7c3a00", va="top", linespacing=1.45,
            family="monospace")
    ax.add_patch(Rectangle((5.15, 1.05), 4.45, 2.10, facecolor="#e6f7f4", ec=TEAL,
                           lw=1.3))
    ax.text(5.27, 3.00, "BVH \u904d\u5386", fontsize=8.4, color=TEAL)
    ax.text(5.30, 2.82, bvh, fontsize=6.6, color="#0b4f4a", va="top", linespacing=1.45,
            family="monospace")
    for i, s in enumerate(["\u2605 \u8981\u5206\u4e09\u79cd\u60c5\u51b5\uff08\u5de6 / \u53f3 / \u8de8\uff09",
                           "\u2605 \u9700\u8981\u7ef4\u62a4 tMin / tMax",
                           "\u2605 \u7269\u4f53\u8de8\u683c \u2192 \u9700\u8981 mailboxing"]):
        ax.text(0.40, 0.92 - i * 0.24, s, fontsize=7.8, color="#7c3a00")
    for i, s in enumerate(["\u2605 \u53ea\u6709\u4e00\u6b21\u5224\u65ad\uff08\u76d2\u5b50\u6253\u4e0d\u4e2d\uff1f\uff09",
                           "\u2605 \u4e0d\u7528 tMin / tMax",
                           "\u2605 \u7269\u4f53\u53ea\u5c5e\u4e8e\u4e00\u4e2a\u53f6\u5b50"]):
        ax.text(5.15, 0.92 - i * 0.24, s, fontsize=7.8, color="#0b4f4a")
    ax.text(0.40, 0.10, "\u8fd9\u5c31\u662f BVH \u80dc\u51fa\u7684\u552f\u4e00\u539f\u56e0\uff1a\u904d\u5386\u7b80\u5355 \u2192 "
                        "\u5206\u652f\u5c11 \u2192 \u5bf9 GPU / SIMD \u53cb\u597d", fontsize=8.2, color=INK)
    save(fig, "d22-kd-vs-bvh.png")


if __name__ == "__main__":
    print("generating ->", OUT)
    for fn in [d17, d18, d19, d20, d21, d22]:
        fn()
    print("done: 6 extra diagrams")
