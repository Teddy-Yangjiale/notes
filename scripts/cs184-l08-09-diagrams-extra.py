# -*- coding: utf-8 -*-
"""CS184 · L08–09 追加图解（d17–d22），按 v2 标准补齐到 22 张。"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Polygon, Circle

plt.rcParams["font.family"] = ["Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

OUT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "src", "content",
                                    "notes", "cs184-08-09-rasterization-shading",
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


def sphere(ax, cx, cy, r, base, ka=0.0, kd=1.0, ks=0.0, p=16, ldir=(-0.6, 0.8)):
    n = 160
    xs = np.linspace(-1, 1, n)
    X, Y = np.meshgrid(xs, xs)
    R2 = X ** 2 + Y ** 2
    inside = R2 <= 1.0
    Z = np.sqrt(np.clip(1 - R2, 0, 1))
    L = np.array([ldir[0], ldir[1], 0.55]); L /= np.linalg.norm(L)
    V = np.array([0.0, 0.0, 1.0])
    H = L + V; H /= np.linalg.norm(H)
    NdL = np.clip(X * L[0] + Y * L[1] + Z * L[2], 0, None)
    NdH = np.clip(X * H[0] + Y * H[1] + Z * H[2], 0, None)
    shade = np.clip(ka + kd * NdL + ks * NdH ** p, 0, 1.0)
    rgb = np.clip(np.dstack([base[0] * shade, base[1] * shade, base[2] * shade]), 0, 1)
    rgb[~inside] = 1.0
    ax.imshow(rgb, extent=(cx - r, cx + r, cy - r, cy + r), origin="lower", zorder=3)


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=DPI, bbox_inches="tight",
                facecolor="white", pad_inches=0.12)
    plt.close(fig)
    print("  ", name)


# ------------------------------------------------- d17 参数矩阵
def d17():
    fig, ax = canvas(10.0, 3.2, (0, 10.0), (0, 3.2), eq=False)
    ax.text(0.30, 2.94, "三个参数各管一件事：k_d 管明暗、k_s 管亮斑、p 管锐度",
            fontsize=10.0, color=INK, fontweight="bold")
    base = (0.42, 0.58, 0.92)
    # 行 1：变 kd
    for k, kd in enumerate([0.2, 0.6, 1.0]):
        sphere(ax, 0.95 + k * 1.05, 1.95, 0.42, base, ka=0.1, kd=kd, ks=0.0)
    ax.text(2.00, 1.42, "$k_d$：0.2 / 0.6 / 1.0", fontsize=7.6, color=MUTED, ha="center")
    ax.text(0.30, 1.95, "变\n$k_d$", fontsize=7.6, color=MUTED, ha="center", va="center")
    # 行 2：变 ks
    for k, ks in enumerate([0.0, 0.4, 0.9]):
        sphere(ax, 0.95 + k * 1.05, 0.85, 0.40, base, ka=0.1, kd=0.55, ks=ks, p=40)
    ax.text(2.00, 0.32, "$k_s$：0 / 0.4 / 0.9", fontsize=7.6, color=MUTED, ha="center")
    ax.text(0.30, 0.85, "变\n$k_s$", fontsize=7.6, color=MUTED, ha="center", va="center")
    # 右侧：变 p
    for k, p in enumerate([4, 16, 64, 256]):
        sphere(ax, 4.75 + k * 0.92, 1.45, 0.38, base, ka=0.1, kd=0.55, ks=0.9, p=p)
        ax.text(4.75 + k * 0.92, 0.94, f"$p$={p}", fontsize=6.8, color=MUTED, ha="center")
    ax.text(6.10, 2.50, "变 $p$：叶瓣越来越窄", fontsize=7.6, color=MUTED, ha="center")

    ax.text(8.45, 2.50, "读法：", fontsize=8.4, color=INK)
    ax.text(8.45, 2.20, "$k_d$ ↑ → 整体变亮", fontsize=7.4, color=MUTED)
    ax.text(8.45, 1.95, "$k_s$ ↑ → 亮斑变强", fontsize=7.4, color=MUTED)
    ax.text(8.45, 1.70, "$p$ ↑ → 亮斑变小", fontsize=7.4, color=MUTED)
    ax.text(8.45, 1.30, "三者独立可调", fontsize=7.6, color=TEAL)
    ax.text(8.45, 1.00, "这就是为什么", fontsize=7.4, color=MUTED)
    ax.text(8.45, 0.78, "它适合做美术工具", fontsize=7.4, color=MUTED)
    save(fig, "d17-param-matrix.png")


# ------------------------------------------------- d18 h·n vs r·v
def d18():
    fig, ax = canvas(9.8, 3.4, (0, 9.8), (0, 3.4), eq=False)
    ax.text(0.30, 3.14, "Blinn 的 n·h 与 Phong 的 r·v：不是同一个量，但很接近",
            fontsize=10.2, color=INK, fontweight="bold")
    # 在二维平面里算：n=(0,1)，v 固定 30°，l 从 -80° 到 10°
    th = np.linspace(-80, 10, 300)
    n = np.array([0.0, 1.0])
    vang = np.radians(30)
    v = np.array([np.sin(vang), np.cos(vang)])
    rdotv = []
    ndoth = []
    for a in th:
        l = np.array([np.sin(np.radians(a)), np.cos(np.radians(a))])
        d = -l  # 入射方向（从表面指向光源的反向）
        r = d - 2 * (d @ n) * n
        rdotv.append(float(np.clip(r @ v, 0, 1)))
        h = v + l
        hn = np.linalg.norm(h)
        ndoth.append(float(np.clip((h @ n) / hn, 0, 1)) if hn > 1e-9 else 0.0)
    xs = 0.85 + 3.2 * (th - th[0]) / (th[-1] - th[0])
    ax.plot(xs, 0.65 + 1.9 * np.array(rdotv), color=TEAL, lw=2.0)
    ax.plot(xs, 0.65 + 1.9 * np.array(ndoth), color=ORANGE, lw=2.0, ls=(0, (4, 2)))
    ax.text(3.30, 2.70, "$n\\cdot h$（Blinn）", fontsize=8.2, color=ORANGE)
    ax.text(1.10, 2.70, "$r\\cdot v$（Phong）", fontsize=8.2, color=TEAL)
    ax.text(2.55, 0.40, "光源方向 $\\theta_l$（度）", fontsize=7.8, color=MUTED, ha="center")

    ax.text(4.60, 2.55, "两条曲线的差别：", fontsize=8.8, color=INK)
    ax.text(4.80, 2.22, "• 在镜面方向（峰值）几乎重合", fontsize=7.6, color=MUTED)
    ax.text(4.80, 1.94, "• 偏离后 $n\\cdot h$ 衰减得更慢", fontsize=7.6, color=MUTED)
    ax.text(4.80, 1.62, "⇒ Blinn 的高光「更宽、更亮」", fontsize=7.6, color=ORANGE)
    ax.text(4.60, 1.18, "这就是为什么 Blinn-Phong", fontsize=7.8, color=TEAL)
    ax.text(4.80, 0.92, "看起来比 Phong「更润」", fontsize=7.8, color=TEAL)
    box(ax, 7.30, 1.05, 2.30, 1.15, "代价：掠射角时\nBlinn 会高估高光\n（不守能量守恒）",
        fs=7.2, fc="#fff7ed", ec=ORANGE, tc="#7c3a00")
    ax.text(0.30, 0.08, "两者都是「近似」——真正的镜面反射要用微表面 BRDF（L16–17）",
            fontsize=7.8, color=MUTED)
    save(fig, "d18-blinn-vs-phong.png")


# ------------------------------------------------- d19 阴影贴图 bias
def d19():
    fig, ax = canvas(9.8, 3.4, (0, 9.8), (0, 3.4))
    ax.text(0.30, 3.14, "阴影贴图的两个失真：自遮挡痤疮 与 悬浮（peter-panning）",
            fontsize=10.0, color=INK, fontweight="bold")
    # 左：acne
    ax.add_patch(Rectangle((0.55, 1.35), 3.05, 0.85, facecolor="#e0f2fe", ec=BLUE, lw=1.2))
    for k in range(9):
        x = 0.70 + k * 0.33
        ax.plot([x, x], [1.35, 1.95], color=RED, lw=1.4, alpha=0.8)
    ax.text(2.05, 2.05, "bias 太小：表面自己遮自己", fontsize=7.8, color=RED, ha="center")
    ax.text(2.05, 1.10, "条纹状噪点（shadow acne）", fontsize=7.4, color=MUTED, ha="center")

    # 右：peter-panning
    ox = 5.10
    ax.add_patch(Rectangle((ox, 1.35), 3.05, 0.85, facecolor="#e0f2fe", ec=BLUE, lw=1.2))
    ax.add_patch(Rectangle((ox + 1.35, 1.55), 0.55, 0.90, facecolor="#e2e8f0", ec=INK, lw=1.1))
    ax.add_patch(Polygon([[ox + 1.90, 1.35], [ox + 2.85, 1.35], [ox + 2.55, 1.05],
                          [ox + 2.05, 1.05]], closed=True, facecolor="#334155", alpha=0.35,
                         ec="none"))
    ax.text(ox + 1.55, 2.60, "bias 太大：阴影「飘」离物体", fontsize=7.8, color=ORANGE,
            ha="center")
    ax.text(ox + 1.55, 0.88, "物体和它的影子之间有缝（peter-panning）", fontsize=7.4,
            color=MUTED, ha="center")

    box(ax, 0.55, 0.30, 3.05, 0.45, "正解：法线偏移 + 斜率缩放 bias", fs=7.2,
        fc="#e6f7f4", ec=TEAL, tc=TEAL)
    box(ax, 5.10, 0.30, 3.05, 0.45, "正解：偏移量随入射角变大", fs=7.2,
        fc="#e6f7f4", ec=TEAL, tc=TEAL)
    ax.text(8.55, 2.10, "bias 的选择：", fontsize=8.0, color=INK)
    ax.text(8.55, 1.80, "太小 → acne", fontsize=7.4, color=RED)
    ax.text(8.55, 1.55, "太大 → 悬浮", fontsize=7.4, color=ORANGE)
    ax.text(8.55, 1.20, "常用：", fontsize=7.6, color=MUTED)
    ax.text(8.55, 0.95, "$bias \\propto \\tan\\theta$", fontsize=7.6, color=TEAL)
    save(fig, "d19-shadow-bias.png")


# ------------------------------------------------- d20 透视对插值的影响
def d20():
    fig, ax = canvas(9.8, 3.4, (0, 9.8), (0, 3.4))
    ax.text(0.30, 3.14, "为什么属性要用 1/w 插值：w 差得越多，线性插值偏得越远",
            fontsize=10.0, color=INK, fontweight="bold")
    # 屏幕空间一条边，两端 w 不同
    A = np.array([1.05, 2.10]); B = np.array([3.35, 1.15])
    ax.plot([A[0], B[0]], [A[1], B[1]], color=INK, lw=1.6)
    ax.plot(*A, "o", ms=6, color=TEAL, zorder=8)
    ax.plot(*B, "o", ms=6, color=ORANGE, zorder=8)
    ax.text(A[0] - 0.10, A[1] + 0.18, "$w=1$", fontsize=8.0, color=TEAL)
    ax.text(B[0] - 0.10, B[1] - 0.30, "$w=4$", fontsize=8.0, color=ORANGE)
    M = (A + B) / 2
    ax.plot(*M, "o", ms=6, color=RED, zorder=8)
    ax.text(M[0] + 0.10, M[1] + 0.16, "屏幕中点", fontsize=7.6, color=RED)

    ax.text(4.10, 2.70, "屏幕中点处，属性 $u$ 应该是多少？", fontsize=8.8, color=INK)
    ax.text(4.30, 2.35, "线性插值（错）：$u = (0+1)/2 = 0.5$", fontsize=7.8, color=RED)
    ax.text(4.30, 2.05, "透视正确：插 $u/w$ 与 $1/w$", fontsize=7.8, color=TEAL)
    ax.text(4.55, 1.75, "$u/w$: $(0/1 + 1/4)/2 = 0.125$", fontsize=7.4, color=MUTED)
    ax.text(4.55, 1.50, "$1/w$: $(1/1 + 1/4)/2 = 0.625$", fontsize=7.4, color=MUTED)
    ax.text(4.55, 1.22, "$u = 0.125/0.625 = 0.2$", fontsize=8.0, color=TEAL)
    box(ax, 4.30, 0.55, 2.85, 0.50, "两者差 0.3 —— 这就是「挤扁」的来源", fs=7.4,
        fc="#fff7ed", ec=ORANGE, tc="#7c3a00")
    ax.text(7.55, 2.10, "什么时候可以偷懒：", fontsize=8.0, color=INK)
    ax.text(7.75, 1.80, "• 正交投影（w 恒定）", fontsize=7.4, color=MUTED)
    ax.text(7.75, 1.55, "• 物体很小（w 变化小）", fontsize=7.4, color=MUTED)
    ax.text(7.75, 1.30, "• 用屏幕空间效果", fontsize=7.4, color=MUTED)
    ax.text(7.55, 0.85, "否则必须校正", fontsize=7.6, color=RED)
    save(fig, "d20-perspective-interp.png")


# ------------------------------------------------- d21 Gouraud 高光消失
def d21():
    fig, ax = canvas(9.8, 3.4, (0, 9.8), (0, 3.4))
    ax.text(0.30, 3.14, "Gouraud 的致命伤：高光落在三角形内部时，它「不存在」",
            fontsize=10.0, color=INK, fontweight="bold")
    # 一个粗糙的三角形网格（球的一部分）
    for k, (ox, lab) in enumerate([(0.55, "高光在顶点上"), (3.45, "高光在三角形内部")]):
        # 画 4 个三角形
        A = np.array([ox, 1.10]); B = np.array([ox + 1.30, 1.10])
        Cc = np.array([ox, 2.20]); D = np.array([ox + 1.30, 2.20])
        if k == 0:
            for tri in [[A, B, Cc], [B, D, Cc]]:
                ax.add_patch(Polygon(tri, closed=True, facecolor="#e6f7f4", ec=TEAL, lw=1.0))
            ax.plot(A[0], A[1], "o", ms=8, color=ORANGE, zorder=8)
            ax.text(A[0] - 0.10, A[1] - 0.28, "亮点在顶点", fontsize=7.2, color=ORANGE)
            ax.text(ox + 0.65, 2.45, "顶点被照亮 → 插值后可见", fontsize=7.4, color=GREEN,
                    ha="center")
        else:
            for tri in [[A, B, Cc], [B, D, Cc]]:
                ax.add_patch(Polygon(tri, closed=True, facecolor="#f8fafc", ec=MUTED, lw=1.0))
            mid = np.array([ox + 0.85, 1.75])
            ax.plot(mid[0], mid[1], "o", ms=8, color=RED, zorder=8)
            ax.text(mid[0] + 0.08, mid[1] - 0.30, "亮点在内部", fontsize=7.2, color=RED)
            ax.text(ox + 0.65, 2.45, "顶点都不亮 → 插值后消失", fontsize=7.4, color=RED,
                    ha="center")

    ax.text(6.10, 2.60, "为什么会这样：", fontsize=8.6, color=INK)
    ax.text(6.30, 2.28, "Gouraud 只在顶点算光照。", fontsize=7.6, color=MUTED)
    ax.text(6.30, 2.00, "如果高光没落到任何一个顶点，", fontsize=7.6, color=MUTED)
    ax.text(6.30, 1.74, "三个顶点都不亮 → 插值全是暗的。", fontsize=7.6, color=MUTED)
    ax.text(6.10, 1.30, "反过来的问题：", fontsize=7.8, color=ORANGE)
    ax.text(6.30, 1.02, "高光落在顶点上时，会被", fontsize=7.4, color=MUTED)
    ax.text(6.30, 0.78, "线性插值摊满整个三角形", fontsize=7.4, color=ORANGE)
    ax.text(6.10, 0.38, "⇒ 低面数时高光要么消失、要么糊成一片", fontsize=7.6, color=RED)
    save(fig, "d21-gouraud-highlight.png")


# ------------------------------------------------- d22 管线中的着色位置
def d22():
    fig, ax = canvas(10.2, 3.4, (0, 10.2), (0, 3.4), eq=False)
    ax.text(0.30, 3.14, "着色发生在哪：vertex shader 还是 fragment shader", fontsize=10.2,
            color=INK, fontweight="bold")
    stages = [("① Vertex\nProcessing", "vertex shader\n（每顶点一次）", TEAL),
              ("② Triangle\nProcessing", "不可编程\n（装配/裁剪）", "#94a3b8"),
              ("③ Rasterization", "不可编程\n（插值 varying）", "#94a3b8"),
              ("④ Fragment\nProcessing", "fragment shader\n（每片段一次）", ORANGE),
              ("⑤ Framebuffer", "深度测试\n混合", "#94a3b8")]
    for i, (a, b, c) in enumerate(stages):
        x = 0.30 + i * 1.95
        box(ax, x, 1.55, 1.70, 0.90, a, fs=7.6, fc="white", ec=c, tc=c)
        ax.text(x + 0.85, 1.28, b, fontsize=6.6, color=MUTED, ha="center", va="top",
                linespacing=1.5)
        if i < 4:
            arrow(ax, (x + 1.74, 2.00), (x + 1.93, 2.00), color="#cbd5e1", lw=1.0, ms=9)
    ax.text(0.30, 0.62, "Flat / Gouraud 着色：把光照算在 **vertex shader** 里（顶点少但可能漏细节）",
            fontsize=7.8, color=TEAL)
    ax.text(0.30, 0.36, "Phong 着色：把法线传到 **fragment shader**，每个像素重算光照（贵但正确）",
            fontsize=7.8, color=ORANGE)
    ax.text(0.30, 0.10, "关键：`varying` 变量的插值是硬件做的 —— 所以「逐像素」不增加顶点数据量，只增加计算量",
            fontsize=7.6, color=MUTED)
    save(fig, "d22-shading-stage.png")


if __name__ == "__main__":
    print("generating ->", OUT)
    for fn in [d17, d18, d19, d20, d21, d22]:
        fn()
    print("done: 6 extra diagrams")
