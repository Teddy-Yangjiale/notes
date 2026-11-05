# -*- coding: utf-8 -*-
"""CS184 课程笔记 · L06–07（纹理映射）原创图解

风格遵循 scripts/cs184-notes-standard.md：
一图一关系 / 不画 matplotlib 坐标轴 / 图内无标题 / 图注写在正文 / 颜色语义固定
颜色语义：teal=主链路/内侧，orange=本讲焦点，purple=纹理/数据，red=错误/异常，灰=说明

注意：所有含 LaTeX 的字符串都用 r"" 原始字符串，避免 \a \b 之类被 Python 当成转义。
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
                                    "notes", "cs184-06-07-texture-mapping", "diagrams"))
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


def box(ax, x, y, w, h, text, fc=FILL, ec=STROKE, tc=INK, fs=10, lw=1.4,
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


# ------------------------------------------------------- d01 三个空间
def d01():
    fig, ax = canvas(10.6, 3.4, (0, 10.6), (0, 3.4))
    ax.text(0.30, 3.12, "纹理映射横跨三个空间，每个空间里量都不一样", fontsize=10.4,
            color=INK, fontweight="bold")
    items = [("世界空间\n$(x,y,z)$", 0.40, PURPLE, "表面真正在哪"),
             ("纹理空间\n$(u,v)$", 4.15, ORANGE, "图像上取哪一点"),
             ("屏幕空间\n$(x_s,y_s)$", 7.90, TEAL, "最终画到哪个像素")]
    for t, x, c, note in items:
        box(ax, x, 1.55, 2.55, 1.05, t, fs=10, fc="#fff7ed" if c == ORANGE else FILL,
            ec=c, tc=c)
        ax.text(x + 1.27, 1.20, note, fontsize=8.6, color=MUTED, ha="center")
    arrow(ax, (3.02, 2.07), (4.10, 2.07), color=ORANGE, lw=1.7)
    ax.text(3.56, 2.28, "展开 UV", fontsize=8.4, color=ORANGE, ha="center")
    arrow(ax, (6.77, 2.07), (7.85, 2.07), color=TEAL, lw=1.7)
    ax.text(7.31, 2.28, "变换+投影", fontsize=8.4, color=TEAL, ha="center")
    ax.text(0.40, 0.55, "展开（unwrapping）是把曲面摊平，这一步决定了纹理怎么被拉伸；"
                        "投影（projection）是第 4–5 讲的内容，它会让 $(u,v)$ 的间距在屏幕上变得不均匀",
            fontsize=9.0, color=MUTED)
    save(fig, "d01-three-spaces.png")


# ------------------------------------------------------- d02 巧克力纸
def d02():
    fig, ax = canvas(10.2, 3.6, (0, 10.2), (0, 3.6))
    ax.text(0.30, 3.30, "展开就像拆巧克力包装纸：曲面必须被「剪开」才能摊平", fontsize=10.4,
            color=INK, fontweight="bold")
    # 左：曲面上的格网
    ax.add_patch(matplotlib.patches.Wedge((3.10, 0.95), 2.15, 40, 140,
                                          facecolor="#fde8e8", ec=RED, lw=1.6))
    for k in range(1, 6):
        a = np.radians(40 + k * 16.7)
        ax.plot([3.10, 3.10 + 2.15 * np.cos(a)], [0.95, 0.95 + 2.15 * np.sin(a)],
                color="#f87171", lw=0.8)
    for r in (0.7, 1.2, 1.7):
        th = np.linspace(np.radians(40), np.radians(140), 40)
        ax.plot(3.10 + r * np.cos(th), 0.95 + r * np.sin(th), color="#f87171", lw=0.8)
    ax.text(3.10, 0.55, "曲面（有弯曲）", fontsize=9.2, color=RED, ha="center")

    arrow(ax, (5.45, 1.75), (6.15, 1.75), color=MUTED, lw=1.6)
    ax.text(5.80, 1.98, "剪开", fontsize=8.6, color=MUTED, ha="center")
    ax.text(5.80, 1.36, "（切口 = seam）", fontsize=8.0, color=RED, ha="center")

    # 右：摊平后的矩形
    ax.add_patch(Rectangle((6.35, 0.85), 2.85, 1.85, facecolor="#e6f7f4",
                           ec=TEAL, lw=1.6))
    for k in range(1, 6):
        ax.plot([6.35 + k * 0.475] * 2, [0.85, 2.70], color="#5eead4", lw=0.8)
    for k in range(1, 3):
        ax.plot([6.35, 9.20], [0.85 + k * 0.617] * 2, color="#5eead4", lw=0.8)
    ax.text(7.78, 0.52, "摊平后：一张 $(u,v)$ 图", fontsize=9.2, color=TEAL, ha="center")
    ax.text(0.30, 0.30, "「剪开」是不可避免的：球面、环面都无法在无拉伸的情况下摊平（高斯绝妙定理）。"
                        "切口处会出现接缝，这就是纹理映射最难处理的问题之一。", fontsize=9.0,
            color=MUTED)
    save(fig, "d02-unwrap.png")


# ------------------------------------------------------- d03 重心坐标 = 面积比
def d03():
    fig, ax = canvas(8.0, 5.2, (-0.4, 6.4), (-0.4, 4.6))
    A, B, C = np.array([0.4, 0.4]), np.array([5.6, 0.4]), np.array([2.2, 4.0])
    P = np.array([2.4, 1.5])
    ax.add_patch(Polygon([A, B, C], closed=True, facecolor="white", ec=INK, lw=1.6))
    for tri, col, lab, pos in [([P, B, C], TEAL, r"$A_\alpha$", (3.45, 1.55)),
                               ([P, C, A], ORANGE, r"$A_\beta$", (1.35, 1.95)),
                               ([P, A, B], PURPLE, r"$A_\gamma$", (2.05, 0.78))]:
        ax.add_patch(Polygon(tri, closed=True, facecolor=col, alpha=0.22,
                             ec=col, lw=1.0))
        ax.text(pos[0], pos[1], lab, fontsize=10.5, color=col, ha="center",
                fontweight="bold")
    for p, lab, off in [(A, "A", (-0.28, -0.22)), (B, "B", (0.16, -0.22)),
                        (C, "C", (-0.05, 0.16))]:
        ax.plot(*p, "o", ms=7, color=INK, zorder=6)
        ax.text(p[0] + off[0], p[1] + off[1], lab, fontsize=11, color=INK,
                fontweight="bold")
    ax.plot(*P, "o", ms=8, color=RED, zorder=7)
    ax.text(P[0] + 0.16, P[1] + 0.10, r"$P$", fontsize=10.5, color=RED)
    ax.text(5.95, 3.55, r"$\alpha=\dfrac{A_\alpha}{A_\alpha+A_\beta+A_\gamma}$",
            fontsize=11, color=TEAL)
    ax.text(5.95, 2.55, r"$\beta=\dfrac{A_\beta}{\sum A}$", fontsize=11, color=ORANGE)
    ax.text(5.95, 1.65, r"$\gamma=1-\alpha-\beta$", fontsize=11, color=PURPLE)
    ax.text(5.95, 0.85, "三个面积之和 = 整个三角形", fontsize=8.8, color=MUTED)
    ax.text(5.95, 0.45, "所以三个权重自动和为 1", fontsize=8.8, color=MUTED)
    save(fig, "d03-barycentric-area.png")


# ------------------------------------------------------- d04 重心坐标 = 距离比
def d04():
    fig, ax = canvas(8.6, 4.4, (-0.4, 7.4), (-0.6, 4.2))
    A, B, C = np.array([0.6, 0.5]), np.array([6.2, 0.5]), np.array([2.6, 3.7])
    P = np.array([2.7, 1.55])
    ax.add_patch(Polygon([A, B, C], closed=True, facecolor="#f8fafc", ec=INK, lw=1.5))
    # 到 BC 边的距离
    ax.plot([A[0], P[0]], [A[1], P[1]], color=ORANGE, lw=1.2, ls=(0, (4, 3)))
    ax.plot([P[0], P[0] + 1.9], [P[1], P[1] - 1.05], color=RED, lw=1.4)
    ax.plot(*P, "o", ms=8, color=RED, zorder=7)
    ax.text(P[0] + 0.10, P[1] + 0.16, r"$P$", fontsize=10.5, color=RED)
    for p, lab in [(A, "A"), (B, "B"), (C, "C")]:
        ax.plot(*p, "o", ms=6, color=INK, zorder=6)
        ax.text(p[0] - 0.05, p[1] + 0.16, lab, fontsize=10.5, color=INK,
                ha="center", fontweight="bold")
    ax.plot([B[0], C[0]], [B[1], C[1]], color=INK, lw=3.0, alpha=0.35)
    ax.text(5.35, 2.55, r"$\alpha=\dfrac{L_{BC}(x,y)}{L_{BC}(x_A,y_A)}$", fontsize=12,
            color=ORANGE)
    ax.text(5.35, 1.72, "分子：P 到 BC 边的有符号距离", fontsize=8.8, color=MUTED)
    ax.text(5.35, 1.38, "分母：A 到 BC 边的有符号距离", fontsize=8.8, color=MUTED)
    ax.text(5.35, 0.85, r"$L_{BC}$ 就是第 2 讲那个直线方程", fontsize=9.2, color=TEAL)
    ax.text(5.35, 0.45, "所以重心坐标不用重新发明 —— 光栅化时已经算过了", fontsize=9.0,
            color=INK)
    ax.text(0.60, -0.42, "红线 = P 到 BC 的距离；虚线 = A 到 P 的连线（示意 α 是「P 在 A→BC 方向的进度」）",
            fontsize=8.6, color=MUTED)
    save(fig, "d04-barycentric-distance.png")


# ------------------------------------------------------- d05 线性代数视角
def d05():
    fig, ax = canvas(9.6, 3.4, (0, 9.6), (0, 3.4), eq=False)
    ax.text(0.30, 3.08, "重心坐标也是一次矩阵求逆：从屏幕位置反解出三个权重", fontsize=10.2,
            color=INK, fontweight="bold")
    ax.text(0.30, 2.50, "  [ x ]     [ A_x  B_x  C_x ] [ α ]", fontsize=9.4,
            color=INK, family="monospace")
    ax.text(0.30, 2.14, "  [ y ]  =  [ A_y  B_y  C_y ] [ β ]", fontsize=9.4,
            color=INK, family="monospace")
    ax.text(0.30, 1.78, "  [ 1 ]     [  1    1    1  ] [ γ ]", fontsize=9.4,
            color=INK, family="monospace")
    ax.text(4.15, 2.14, "⟹", fontsize=14, color=MUTED, ha="center", va="center")
    ax.text(4.55, 2.30, r"$[\alpha\ \beta\ \gamma]^T = M^{-1}[x\ y\ 1]^T$", fontsize=10,
            color=TEAL)
    ax.text(4.55, 1.75, "底行全 1 就是在保证 α+β+γ=1", fontsize=8.8, color=MUTED)
    ax.text(0.30, 1.15, "纹理坐标也走同一个矩阵：", fontsize=9.2, color=INK)
    ax.text(0.30, 0.75, r"$[s\ t\ 1]^T = M_{\mathrm{texture}}M_{\mathrm{screen}}^{-1}[x\ y\ 1]^T$",
            fontsize=10.5, color=PURPLE)
    ax.text(6.20, 0.95, "两个三角形的 M 不同", fontsize=8.8, color=MUTED)
    ax.text(6.20, 0.55, "一次 3×3 求逆就能\n把屏幕点搬到纹理空间", fontsize=8.8, color=MUTED)
    ax.text(0.30, 0.22, "注意：这个式子默认两边都是仿射 —— 一旦有透视，必须先把 s/w、t/w、1/w 一起插值",
            fontsize=8.8, color=RED)
    save(fig, "d05-barycentric-linear-algebra.png")


# ------------------------------------------------------- d06 透视插值是错的
def d06():
    fig, ax = canvas(10.2, 4.6, (0, 10.2), (0, 4.6))
    ax.text(0.30, 4.32, "同一块地板、同一张贴图：左边按透视插值，右边按屏幕线性插值",
            fontsize=10.2, color=INK, fontweight="bold")
    N = 10
    y_hor, y_near = 3.05, 0.70          # 地平线 / 最近处的屏幕高度
    z0, zN = 1.0, 6.0

    def draw(ox, correct):
        cx = ox + 1.95
        half = 1.95
        # 行边界：correct 用 1/z 关系（世界等距），wrong 用屏幕等距
        if correct:
            zs = [z0 + (zN - z0) * k / N for k in range(N + 1)]
            ys = [y_hor - (y_hor - y_near) * (z0 / z) for z in zs]
        else:
            ys = [y_near + (y_hor - y_near) * k / N for k in range(N + 1)]
        # 无论哪种排布，地板本身的宽度都按真实透视走
        zs = [z0 * (y_hor - y_near) / max(y_hor - y, 1e-6) for y in ys]
        for i in range(N):
            ya, yb = ys[i], ys[i + 1]
            za, zb = zs[i], zs[i + 1]
            wa = half * z0 / za
            wb = half * z0 / zb
            for j in range(N):
                xa0 = cx - wa + 2 * wa * j / N
                xa1 = cx - wa + 2 * wa * (j + 1) / N
                xb0 = cx - wb + 2 * wb * j / N
                xb1 = cx - wb + 2 * wb * (j + 1) / N
                col = "#111827" if (i + j) % 2 == 0 else "#f8fafc"
                ax.add_patch(Polygon([[xa0, ya], [xa1, ya], [xb1, yb], [xb0, yb]],
                                     closed=True, facecolor=col, ec="none", zorder=2))
        ax.plot([cx - half, cx + half], [y_near, y_near], color=MUTED, lw=1.0)
        ax.plot([cx - half * z0 / zN, cx + half * z0 / zN], [y_hor, y_hor],
                color=MUTED, lw=1.0)
        ax.text(cx, y_hor + 0.16, "地平线", fontsize=7.6, color=MUTED, ha="center")

    draw(0.35, True)
    draw(5.20, False)
    ax.text(2.30, 4.00, "透视正确", fontsize=10, color=GREEN, ha="center",
            fontweight="bold")
    ax.text(7.15, 4.00, "屏幕线性插值", fontsize=10, color=RED, ha="center",
            fontweight="bold")
    ax.text(2.30, 0.34, "格子在远处自然变密", fontsize=8.8, color=GREEN, ha="center")
    ax.text(7.15, 0.34, "远处被拉长、近处被压扁", fontsize=8.8, color=RED, ha="center")
    ax.text(4.78, 1.95, "≠", fontsize=18, color=RED, ha="center", va="center")
    save(fig, "d06-perspective-wrong.png")

# ------------------------------------------------------- d07 为什么错
def d07():
    fig, ax = canvas(9.8, 4.0, (0, 9.8), (0, 4.0))
    ax.text(0.30, 3.72, "屏幕上的等距，在世界里并不等距 —— 所以要除以 $w$", fontsize=10.4,
            color=INK, fontweight="bold")
    # 屏幕空间：等距
    ax.plot([0.70, 0.70], [0.80, 3.30], color=TEAL, lw=2.0)
    for k in range(5):
        y = 0.80 + k * 0.625
        ax.plot([0.55, 0.85], [y, y], color=TEAL, lw=1.4)
        ax.text(0.42, y, f"{k*0.25:.2f}", fontsize=8.4, color=TEAL, ha="right",
                va="center")
    ax.text(0.70, 3.46, "屏幕空间", fontsize=9.4, color=TEAL, ha="center")
    ax.text(0.70, 0.55, "等间距", fontsize=8.6, color=MUTED, ha="center")

    ax.text(1.75, 2.05, "投影", fontsize=8.8, color=MUTED, ha="center")
    ax.text(1.75, 1.75, "÷ w", fontsize=9.0, color=RED, ha="center")

    # 世界空间：不等距（透视压缩）
    ax.plot([2.95, 3.55], [0.80, 3.30], color=ORANGE, lw=2.0)
    ys_w = [0.80, 1.05, 1.60, 2.50, 3.30]
    for k, y in enumerate(ys_w):
        x = 2.95 + (y - 0.80) / 2.50 * 0.60
        ax.plot([x - 0.18, x + 0.18], [y, y], color=ORANGE, lw=1.4)
        ax.text(x - 0.26, y, f"{k*0.25:.2f}", fontsize=8.4, color=ORANGE, ha="right",
                va="center")
    ax.text(3.25, 3.46, "世界空间（纹理空间）", fontsize=9.4, color=ORANGE, ha="center")
    ax.text(3.25, 0.55, "真实的 $u$ 值不等距", fontsize=8.6, color=MUTED, ha="center")

    box(ax, 4.85, 1.55, 4.55, 1.55,
        "正确做法：屏幕空间里插值的是\n"
        r"$u/w$、$v/w$、$1/w$" + "\n"
        r"插完再除以 $1/w$，得到真实的 $(u,v)$",
        fs=9.2, fc="#fff7ed", ec=ORANGE, tc="#7c3a00")
    ax.text(4.85, 1.10, r"等价说法：$u$ 在屏幕空间是 $1/z$ 的函数，不是线性的", fontsize=9.0,
            color=MUTED)
    ax.text(4.85, 0.70, "GPU 硬件默认做这件事（perspective-correct interpolation）", fontsize=9.0,
            color=TEAL)
    ax.text(4.85, 0.30, "自己写软件光栅器时最容易忘 —— 忘了就是 d06 右边那张图", fontsize=9.0,
            color=RED)
    save(fig, "d07-perspective-correct.png")


# ------------------------------------------------------- d08 像素足迹
def d08():
    fig, ax = canvas(9.0, 4.2, (0, 9.0), (0, 4.2))
    ax.text(0.30, 3.90, "一个屏幕像素在纹理空间里是一个「斜的平行四边形」", fontsize=10.4,
            color=INK, fontweight="bold")
    # 屏幕空间 2x2 像素
    for i in range(2):
        for j in range(2):
            ax.add_patch(Rectangle((0.60 + i * 0.55, 1.55 + j * 0.55), 0.55, 0.55,
                                   facecolor="#e0f2fe" if i == 0 and j == 0 else "white",
                                   ec=BLUE, lw=1.2))
    ax.text(1.15, 1.30, "屏幕：一个像素", fontsize=8.8, color=BLUE, ha="center")
    ax.text(1.15, 3.05, "屏幕空间", fontsize=9.4, color=BLUE, ha="center")

    arrow(ax, (1.95, 2.05), (2.85, 2.05), color=MUTED, lw=1.5)
    ax.text(2.40, 2.26, "映射", fontsize=8.4, color=MUTED, ha="center")

    # 纹理空间：平行四边形
    o = np.array([3.30, 1.60])
    e1 = np.array([1.55, 0.55])
    e2 = np.array([-0.35, 1.25])
    poly = [o, o + e1, o + e1 + e2, o + e2]
    ax.add_patch(Polygon(poly, closed=True, facecolor="#fde8e8", ec=RED, lw=1.6,
                         alpha=0.75))
    for k in range(1, 4):
        ax.plot([o[0] + e1[0] * k / 4, o[0] + e1[0] * k / 4 + e2[0]],
                [o[1] + e1[1] * k / 4, o[1] + e1[1] * k / 4 + e2[1]],
                color="#f87171", lw=0.7)
        ax.plot([o[0] + e2[0] * k / 4, o[0] + e2[0] * k / 4 + e1[0]],
                [o[1] + e2[1] * k / 4, o[1] + e2[1] * k / 4 + e1[1]],
                color="#f87171", lw=0.7)
    ax.text(4.05, 1.30, "纹理空间：斜四边形", fontsize=8.8, color=RED, ha="center")
    ax.text(4.05, 3.05, "纹理空间", fontsize=9.4, color=RED, ha="center")

    # 右边：mipmap 用正方形近似
    ax.add_patch(Rectangle((5.85, 1.55), 1.35, 1.35, facecolor="#e6f7f4", ec=TEAL,
                           lw=1.6))
    ax.text(6.52, 1.30, "mipmap 用一个正方形近似它", fontsize=8.8, color=TEAL,
            ha="center")
    ax.text(6.52, 3.05, "近似：正方形", fontsize=9.4, color=TEAL, ha="center")
    ax.text(0.30, 0.62, "这个四边形的两条边就是 $\\partial(u,v)/\\partial x$ 与 $\\partial(u,v)/\\partial y$（雅可比矩阵的两列）",
            fontsize=9.0, color=INK)
    ax.text(0.30, 0.24, "它既不轴对齐、也不各向同性 —— 这个「形状不匹配」就是 mipmap 过度模糊（overblur）的根源",
            fontsize=9.0, color=RED)
    save(fig, "d08-footprint.png")


# ------------------------------------------------------- d09 重采样链
def d09():
    fig, ax = canvas(10.2, 3.2, (0, 10.2), (0, 3.2), eq=False)
    ax.text(0.30, 2.90, "「贴纹理」其实是一次重采样（resampling）", fontsize=10.4,
            color=INK, fontweight="bold")
    box(ax, 0.40, 1.35, 2.35, 1.05, "离散纹理\n$f(x,y)$\n只在整数格点上非零",
        fs=8.8, fc="#f3e8ff", ec=PURPLE, tc=PURPLE)
    arrow(ax, (2.88, 1.88), (3.55, 1.88), color=MUTED, lw=1.5)
    box(ax, 3.62, 1.35, 2.65, 1.05, "重建连续函数\n$f_{cont} = f * k$\n用重建核 $k$ 做卷积",
        fs=8.8, fc="#e0f2fe", ec=BLUE, tc=BLUE)
    arrow(ax, (6.40, 1.88), (7.07, 1.88), color=MUTED, lw=1.5)
    box(ax, 7.14, 1.35, 2.60, 1.05, "在 $(u,v)$ 处求值\n$f_{cont}(u,v)$\n得到纹理颜色",
        fs=8.8, fc="#e6f7f4", ec=TEAL, tc=TEAL)
    ax.text(0.40, 0.85, "关键：$u,v$ 一般**不是整数**，所以不能直接查表 —— 必须「重建 + 取点」",
            fontsize=9.2, color=INK)
    ax.text(0.40, 0.45, "第 3 讲的所有概念（频谱、Nyquist、滤波、抗锯齿）在这里全部复用："
                        "重建核 $k$ 选得好不好，直接决定放大后的画质", fontsize=9.0, color=MUTED)
    save(fig, "d09-resampling.png")


# ------------------------------------------------------- d10 放大 vs 缩小
def d10():
    fig, ax = canvas(10.0, 3.5, (0, 10.0), (0, 3.5))
    ax.text(0.30, 3.20, "同一个映射，三种情形：像素足迹里装了多少个 texel", fontsize=10.4,
            color=INK, fontweight="bold")
    cases = [("1 : 1", "一个像素 ≈ 一个 texel", 1, TEAL),
             ("放大（magnification）", "像素里不到一个 texel", 2, ORANGE),
             ("缩小（minification）", "像素里一大堆 texel", 6, RED)]
    for i, (name, note, n, c) in enumerate(cases):
        x0 = 0.55 + i * 3.20
        ax.add_patch(Rectangle((x0, 1.35), 1.55, 1.55, facecolor="white", ec=MUTED, lw=1.2))
        step = 1.55 / max(n, 1)
        for k in range(n):
            for j in range(n):
                ax.add_patch(Rectangle((x0 + k * step, 1.35 + j * step), step, step,
                                       facecolor=c, alpha=0.30, ec=c, lw=0.7))
        ax.add_patch(Rectangle((x0, 1.35), 1.55, 1.55, facecolor="none", ec=c, lw=2.0))
        ax.text(x0 + 0.78, 1.10, name, fontsize=9.2, color=c, ha="center",
                fontweight="bold")
        ax.text(x0 + 1.85, 2.10, note, fontsize=8.8, color=MUTED, va="center")
    ax.text(0.30, 0.55, "放大：一个 texel 被铺到多个像素上 → 需要「插值」让它平滑（双线性）",
            fontsize=9.0, color=ORANGE)
    ax.text(0.30, 0.22, "缩小：一个像素要覆盖成百个 texel → 需要「预先滤波」，否则必然走样（mipmap）",
            fontsize=9.0, color=RED)
    save(fig, "d10-magnify-minify.png")


# ------------------------------------------------------- d11 双线性
def d11():
    fig, ax = canvas(8.4, 4.6, (-0.5, 6.4), (-0.9, 3.9))
    pts = {}
    for i, u in enumerate([0.6, 2.1, 3.6]):
        for j, v in enumerate([0.5, 2.0, 3.5]):
            pts[(i, j)] = (u, v)
            ax.plot(u, v, "o", ms=5, color=MUTED, zorder=3)
    # 四个 texel
    x0, x1 = 0.6, 2.1
    y0, y1 = 0.5, 2.0
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, facecolor="#fff7ed",
                           ec=ORANGE, lw=1.4, zorder=2))
    for (i, j), lab in [((0, 0), "$u_{00}$"), ((1, 0), "$u_{10}$"),
                        ((0, 1), "$u_{01}$"), ((1, 1), "$u_{11}$")]:
        px, py = pts[(i, j)]
        ax.plot(px, py, "o", ms=8, color=ORANGE, zorder=5)
        ax.text(px - 0.16, py + 0.16, lab, fontsize=8.6, color=ORANGE, ha="center")
    P = (x0 + 0.42 * (x1 - x0), y0 + 0.62 * (y1 - y0))
    ax.plot(*P, "o", ms=8, color=RED, zorder=6)
    ax.text(P[0] + 0.14, P[1] + 0.02, r"$f(u,v)$", fontsize=9.0, color=RED)
    arrow(ax, (P[0], y0 - 0.06), (x0, y0 - 0.06), color=MUTED, lw=1.0, ms=9)
    ax.text(x0 + 0.42 * (x1 - x0) / 2, y0 - 0.26, r"$s$", fontsize=9.0, color=MUTED,
            ha="center")
    ax.text(4.55, 3.35, r"$u_0 = \mathrm{lerp}(s, u_{00}, u_{10})$", fontsize=9.6,
            color=TEAL)
    ax.text(4.55, 2.85, r"$u_1 = \mathrm{lerp}(s, u_{01}, u_{11})$", fontsize=9.6,
            color=TEAL)
    ax.text(4.55, 2.20, r"$f = \mathrm{lerp}(t, u_0, u_1)$", fontsize=9.6, color=ORANGE)
    ax.text(4.55, 1.55, r"$\mathrm{lerp}(x,v_0,v_1)=v_0+x(v_1-v_0)$", fontsize=9.0,
            color=MUTED)
    ax.text(4.55, 0.95, "先横向两次，再纵向一次", fontsize=9.0, color=INK)
    ax.text(4.55, 0.55, "总共 3 次 lerp、4 次 texel 读取", fontsize=9.0, color=TEAL)
    ax.text(4.55, 0.15, "先纵后横结果完全一样（双线性可交换）", fontsize=8.8, color=MUTED)
    save(fig, "d11-bilinear.png")


# ------------------------------------------------------- d12 mipmap 金字塔
def d12():
    fig, ax = canvas(9.8, 3.6, (0, 9.8), (0, 3.6), eq=False)
    ax.text(0.30, 3.28, "mipmap：预先把每个分辨率层级都算好，总共只多 1/3 内存", fontsize=10.2,
            color=INK, fontweight="bold")
    sizes = [128, 64, 32, 16, 8, 4, 2, 1]
    base, x = 1.05, 0.55
    for k, sz in enumerate(sizes):
        w = 1.25 * (0.80 ** k)
        ax.add_patch(Rectangle((x, base), w, w, facecolor="#e6f7f4", ec=TEAL,
                               lw=1.2, alpha=0.9))
        ax.text(x + w / 2, base + w + 0.14, f"{sz}", fontsize=7.6, color=MUTED,
                ha="center")
        ax.text(x + w / 2, base - 0.22, f"L{k}", fontsize=8.4, color=TEAL, ha="center")
        x += 0.72
    ax.text(0.30, 0.42, "每级 = 上一级低通滤波后再降采样一半；方框上的数字是该级的边长（texel）",
            fontsize=8.8, color=MUTED)
    box(ax, 6.35, 1.55, 3.00, 1.20,
        "总内存\n1 + 1/4 + 1/16 + … = 4/3",
        fs=9.4, fc="#fff7ed", ec=ORANGE, tc="#7c3a00")
    ax.text(6.35, 1.18, "只多 33%，换来 O(1) 的缩小滤波", fontsize=8.8, color=ORANGE)
    ax.text(6.35, 0.86, "这就是 mipmap 几乎零成本的原因", fontsize=8.6, color=MUTED)
    save(fig, "d12-mipmap-pyramid.png")

# ------------------------------------------------------- d13 mipmap 层级
def d13():
    fig, ax = canvas(9.8, 3.6, (0, 9.8), (0, 3.6), eq=False)
    ax.text(0.30, 3.32, "层级 $D$ 由「像素足迹在纹理空间里有多大」决定", fontsize=10.4,
            color=INK, fontweight="bold")
    ax.text(0.30, 2.70, "取两个方向导数长度的最大值：", fontsize=9.6, color=INK)
    ax.text(0.65, 2.34, "L = max( ||∂(u,v)/∂x|| , ||∂(u,v)/∂y|| )", fontsize=9.8,
            color=INK, family="monospace")
    ax.text(0.30, 1.90, r"$D = \log_2 L$", fontsize=11, color=ORANGE)
    box(ax, 4.30, 1.95, 2.30, 1.15, "L = 1\n1 像素 : 1 texel\n→ D = 0", fs=8.8,
        fc=FILL, ec=STROKE)
    box(ax, 6.85, 1.95, 2.30, 1.15, "L = 8\n1 像素装 8 texel\n→ D = 3", fs=8.8,
        fc="#fde8e8", ec=RED, tc="#7f1d1d")
    ax.text(0.30, 1.42, "取 max 是因为要按「最坏方向」选层级：宁可模糊，也不能走样",
            fontsize=9.0, color=INK)
    ax.text(0.30, 1.02, "L 用各方向的导数长度，而不是面积 —— 因为 mipmap 只有各向同性的层级",
            fontsize=9.0, color=MUTED)
    ax.text(0.30, 0.55, r"$du/dx$ 这类导数由硬件对相邻像素的 $(u,v)$ 做差分得到（光栅化时顺手算）",
            fontsize=9.0, color=TEAL)
    ax.text(0.30, 0.18, "D 一般是小数，所以还要在两个相邻层级之间再插值一次 → 三线性", fontsize=9.0,
            color=ORANGE)
    save(fig, "d13-mipmap-level.png")


# ------------------------------------------------------- d14 三线性
def d14():
    fig, ax = canvas(10.0, 3.6, (0, 10.0), (0, 3.6), eq=False)
    ax.text(0.30, 3.30, "三线性 = 两个层级各做一次双线性，再按小数部分插值", fontsize=10.4,
            color=INK, fontweight="bold")
    box(ax, 0.50, 1.85, 2.35, 1.00, "层级 $D = 2$\n4 次 texel 读取\n→ 双线性结果 $c_2$",
        fs=8.8, fc="#e0f2fe", ec=BLUE, tc=BLUE)
    box(ax, 0.50, 0.55, 2.35, 1.00, "层级 $D+1 = 3$\n4 次 texel 读取\n→ 双线性结果 $c_3$",
        fs=8.8, fc="#e0f2fe", ec=BLUE, tc=BLUE)
    arrow(ax, (2.98, 2.35), (3.95, 1.85), color=MUTED, lw=1.4, rad=-0.15)
    arrow(ax, (2.98, 1.05), (3.95, 1.55), color=MUTED, lw=1.4, rad=0.15)
    box(ax, 4.02, 1.20, 2.55, 1.00, "按小数部分 $\\mathrm{frac}(D)$ 插值\n$c = \\mathrm{lerp}(\\mathrm{frac}(D), c_2, c_3)$",
        fs=8.6, fc="#fff7ed", ec=ORANGE, tc="#7c3a00")
    arrow(ax, (6.67, 1.70), (7.35, 1.70), color=MUTED, lw=1.4)
    box(ax, 7.42, 1.20, 2.05, 1.00, "最终颜色\n8 次读取 / 7 次 lerp", fs=8.8,
        fc="#e6f7f4", ec=TEAL, tc=TEAL)
    ax.text(0.50, 0.22, "代价是双线性的两倍（4→8 次读取），换来的是层级切换时不再有可见的「接缝」",
            fontsize=9.0, color=MUTED)
    save(fig, "d14-trilinear.png")


# ------------------------------------------------------- d15 过度模糊
def d15():
    fig, ax = canvas(9.6, 3.8, (0, 9.6), (0, 3.8))
    ax.text(0.30, 3.50, "mipmap 的过度模糊：足迹是长条， lookup 却是方块", fontsize=10.4,
            color=INK, fontweight="bold")
    # 左：细长足迹
    o = np.array([0.75, 1.35])
    e1 = np.array([2.55, 0.30])
    e2 = np.array([0.22, 0.42])
    ax.add_patch(Polygon([o, o + e1, o + e1 + e2, o + e2], closed=True,
                         facecolor="#fde8e8", ec=RED, lw=1.6, alpha=0.8))
    ax.text(2.05, 1.05, "真实足迹（各向异性）", fontsize=8.8, color=RED, ha="center")
    ax.text(2.05, 2.55, "掠射角下的地面", fontsize=9.2, color=INK, ha="center")

    # 中：mipmap 用的正方形
    side = np.sqrt(2.55 * 0.42)
    ax.add_patch(Rectangle((3.55, 1.35), side, side, facecolor="#e6f7f4", ec=TEAL,
                           lw=1.6, alpha=0.85))
    ax.text(3.55 + side / 2, 1.05, "mipmap 用的正方形", fontsize=8.8, color=TEAL,
            ha="center")
    ax.text(3.55 + side / 2, 2.55, "面积相同，但形状不对", fontsize=9.2, color=INK,
            ha="center")
    arrow(ax, (3.45, 1.90), (2.42, 1.90), color=MUTED, lw=1.3, ls=(0, (3, 2)))

    box(ax, 5.55, 1.55, 3.75, 1.35,
        "短边方向：正方形比足迹「宽」\n→ 把不该混的 texel 混进来\n→ 细节被抹平（overblur）",
        fs=8.8, fc="#fff7ed", ec=ORANGE, tc="#7c3a00")
    ax.text(5.55, 1.10, "掠射角的地面、倾斜的墙面、远处的地板 —— 这些地方最容易看出来",
            fontsize=9.0, color=MUTED)
    ax.text(5.55, 0.70, "解决方向：允许「非正方形」的查找（ripmap / EWA），或多查几次加权",
            fontsize=9.0, color=TEAL)
    save(fig, "d15-overblur.png")


# ------------------------------------------------------- d16 各向异性
def d16():
    fig, ax = canvas(9.4, 3.6, (0, 9.4), (0, 3.6))
    ax.text(0.30, 3.28, "各向异性过滤：沿长轴方向多查几次，再按权重平均", fontsize=10.4,
            color=INK, fontweight="bold")
    o = np.array([0.70, 1.10])
    e1 = np.array([3.00, 0.35])
    e2 = np.array([0.24, 0.46])
    ax.add_patch(Polygon([o, o + e1, o + e1 + e2, o + e2], closed=True,
                         facecolor="#e6f7f4", ec=TEAL, lw=1.5, alpha=0.75))
    # 沿长轴的多次取样
    for k in range(5):
        t = (k + 0.5) / 5
        c = o + e1 * t + e2 * 0.5
        ax.add_patch(Polygon([[c[0] - 0.16, c[1] - 0.16], [c[0] + 0.16, c[1] - 0.16],
                              [c[0] + 0.16, c[1] + 0.16], [c[0] - 0.16, c[1] + 0.16]],
                             closed=True, facecolor="white", ec=ORANGE, lw=1.2,
                             alpha=0.95, zorder=5))
    ax.text(2.30, 0.80, "沿长轴取 5 个方形样本，各自双线性，再加权平均", fontsize=8.8,
            color=ORANGE, ha="center")
    ax.text(2.30, 2.25, "足迹", fontsize=9.2, color=TEAL, ha="center")
    box(ax, 5.20, 1.55, 3.95, 1.35,
        "EWA（椭圆加权平均）：直接按椭圆足迹加权\n"
        "ripmap：预先存「各向异性」的层级\n"
        "两者都能把长条足迹拟合得更好",
        fs=8.6, fc="#fff7ed", ec=ORANGE, tc="#7c3a00")
    ax.text(5.20, 1.05, "代价：多次读取 + 加权，比三线性贵得多（通常 4–16 次采样）",
            fontsize=9.0, color=MUTED)
    ax.text(5.20, 0.62, "所以现代硬件把「采样次数」做成可调档位（2x / 4x / 8x / 16x AF）",
            fontsize=9.0, color=INK)
    save(fig, "d16-anisotropic.png")


# ------------------------------------------------------- d17 环境贴图
def d17():
    fig, ax = canvas(10.0, 3.6, (0, 10.0), (0, 3.6))
    ax.text(0.30, 3.28, "环境贴图：把一个方向映射成纹理坐标", fontsize=10.4, color=INK,
            fontweight="bold")
    # 球
    ax.add_patch(Circle((1.55, 1.70), 0.95, facecolor="#e2e8f0", ec=MUTED, lw=1.4))
    th = np.linspace(0, 2 * np.pi, 80)
    for k in range(-2, 3):
        r = 0.95 * np.sqrt(max(0.0, 1 - (k * 0.28) ** 2))
        ax.plot(1.55 + r * np.cos(th), np.full_like(th, 1.70 + k * 0.28),
                color="#94a3b8", lw=0.6)
    for k in range(6):
        phi = np.linspace(0, 2 * np.pi, 80)
        ax.plot(1.55 + 0.28 * np.cos(phi + k * np.pi / 6) * 0,
                np.full_like(phi, 0), color="none")
    ax.plot(1.55, 1.70, "o", ms=6, color=INK, zorder=6)
    arrow(ax, (1.55, 1.70), (2.35, 2.35), color=ORANGE, lw=2.0)
    arrow(ax, (1.55, 1.70), (0.85, 2.20), color=TEAL, lw=2.0, ls=(0, (4, 2)))
    ax.text(2.42, 2.40, "视线", fontsize=8.6, color=ORANGE)
    ax.text(0.55, 2.26, "反射方向 R", fontsize=8.6, color=TEAL)
    ax.text(1.55, 0.50, "球面：R 决定采哪", fontsize=8.8, color=MUTED, ha="center")

    arrow(ax, (2.65, 1.70), (3.35, 1.70), color=MUTED, lw=1.4)
    ax.text(3.00, 1.92, "查表", fontsize=8.4, color=MUTED, ha="center")

    # lat/long 贴图
    ax.add_patch(Rectangle((3.45, 1.10), 0.95, 1.20, facecolor="#fff7ed", ec=ORANGE,
                           lw=1.4, alpha=0.85))
    box(ax, 4.55, 1.10, 0.90, 1.20, "", fc="#e6f7f4", ec=TEAL)
    ax.text(3.92, 0.85, "lat / long 贴图", fontsize=8.6, color=MUTED, ha="center")
    ax.text(5.00, 2.55, "一个方向 → 一个 $(u,v)$", fontsize=9.0, color=INK, ha="center")
    ax.text(5.00, 0.50, "$u=\\phi/2\\pi,\\ v=\\theta/\\pi$", fontsize=9.0, color=TEAL,
            ha="center")

    # cube map
    ax.add_patch(Rectangle((6.55, 1.05), 0.85, 0.85, facecolor="#f8fafc", ec=MUTED, lw=1.1))
    ax.add_patch(Rectangle((7.10, 1.40), 0.85, 0.85, facecolor="#e2e8f0", ec=MUTED, lw=1.1))
    ax.add_patch(Rectangle((7.65, 1.05), 0.85, 0.85, facecolor="#f8fafc", ec=MUTED, lw=1.1))
    ax.text(7.55, 0.72, "cube map：六张贴图", fontsize=8.6, color=MUTED, ha="center")
    ax.text(7.55, 2.55, "方向落在哪个面就用哪张", fontsize=9.0, color=INK, ha="center")
    ax.text(0.30, 0.22, "环境贴图把「从任何方向来的光」存成一张纹理；反射光线直接查表 —— "
                        "这是 L16–17 全局光照的入口", fontsize=9.0, color=MUTED)
    save(fig, "d17-envmap.png")


# ------------------------------------------------------- d18 bump vs displacement
def d18():
    fig, ax = canvas(9.8, 3.4, (0, 9.8), (0, 3.4))
    ax.text(0.30, 3.12, "凹凸贴图改的是法线，位移贴图改的是位置", fontsize=10.4, color=INK,
            fontweight="bold")
    x = np.linspace(0, 1, 400)

    # 几何（光滑）
    ax.plot(0.45 + 2.55 * x, 2.15 + 0.12 * np.sin(6 * x), color=MUTED, lw=1.6)
    ax.plot(0.45 + 2.55 * x, 2.15 + 0.12 * np.sin(6 * x), color=MUTED, lw=1.6)
    ax.text(0.45, 2.55, "① 几何：一个光滑曲面", fontsize=8.8, color=MUTED)

    # bump：表面不变，法线抖动
    ax.plot(0.45 + 2.55 * x, 1.30 + 0.12 * np.sin(6 * x), color=TEAL, lw=1.6)
    for k in range(9):
        xx = 0.45 + 2.55 * (k + 0.5) / 9
        ax.plot([xx, xx + 0.06], [1.30 + 0.12 * np.sin(6 * (k + 0.5) / 9),
                                  1.30 + 0.12 * np.sin(6 * (k + 0.5) / 9) + 0.22],
                color=TEAL, lw=1.0, alpha=0.8)
    ax.text(0.45, 1.72, "② bump：表面不动，法线被扰动", fontsize=8.8, color=TEAL)

    # displacement：表面真的起伏
    ax.plot(0.45 + 2.55 * x, 0.45 + 0.12 * np.sin(6 * x) + 0.16 * np.sign(np.sin(9 * x)),
            color=ORANGE, lw=1.8)
    ax.text(0.45, 0.86, "③ displacement：表面真的被推开", fontsize=8.8, color=ORANGE)

    box(ax, 5.55, 1.35, 3.60, 1.55,
        "bump：只改着色用的法线\n→ 轮廓还是光滑的\n\n"
        "displacement：真的改几何\n→ 轮廓出现起伏，能自遮挡",
        fs=8.6, fc="#fff7ed", ec=ORANGE, tc="#7c3a00")
    ax.text(5.55, 0.95, "代价：displacement 需要极高细分的网格（或曲面细分）", fontsize=9.0,
            color=MUTED)
    ax.text(5.55, 0.55, "所以实时渲染里 bump 用得多，displacement 用在近景/离线", fontsize=9.0,
            color=INK)
    save(fig, "d18-bump-displace.png")


if __name__ == "__main__":
    print("generating ->", OUT)
    for fn in [d01, d02, d03, d04, d05, d06, d07, d08, d09,
               d10, d11, d12, d13, d14, d15, d16, d17, d18]:
        fn()
    print("done: 18 diagrams")
