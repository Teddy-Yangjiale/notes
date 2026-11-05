# -*- coding: utf-8 -*-
"""CS184 · L02 追加图解（d15–d20），按 v2 标准补齐到 20 张。"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Polygon, Circle

plt.rcParams["font.family"] = ["Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

OUT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "src", "content",
                                    "notes", "cs184-02-drawing-triangles", "diagrams"))
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


# ------------------------------------------------- d15 边缘函数三重身份
def d15():
    fig, ax = canvas(10.0, 3.4, (0, 10.0), (0, 3.4), eq=False)
    ax.text(0.30, 3.14, "同一个边缘函数，三种身份：判内、算面积、当重心坐标", fontsize=10.0,
            color=INK, fontweight="bold")
    # 三角形
    A, B, C = np.array([0.75, 1.05]), np.array([3.05, 1.05]), np.array([0.75, 2.75])
    ax.add_patch(Polygon([A, B, C], closed=True, facecolor="#e6f7f4", ec=TEAL, lw=1.4))
    P = np.array([1.55, 1.65])
    ax.plot(*P, "o", ms=6, color=RED, zorder=8)
    ax.text(P[0] + 0.10, P[1] + 0.12, "P", fontsize=8.4, color=RED)
    for p, lab, off in [(A, "A", (-0.20, -0.26)), (B, "B", (0.10, -0.26)),
                        (C, "C", (-0.20, 0.14))]:
        ax.plot(*p, "o", ms=4.5, color=INK, zorder=8)
        ax.text(p[0] + off[0], p[1] + off[1], lab, fontsize=8.4, color=INK)

    ax.text(3.60, 2.75, "① 判内：三个符号同时 ≥ 0", fontsize=8.4, color=TEAL)
    ax.text(3.80, 2.45, r"$L_0 \geq 0$、$L_1 \geq 0$、$L_2 \geq 0$（同时）", fontsize=8.6,
            color=TEAL)
    ax.text(3.60, 2.00, "② 算面积：$L_i$ 的绝对值 = 2 × 子三角形面积", fontsize=8.4,
            color=ORANGE)
    ax.text(3.80, 1.70, "$\\alpha = A_\\alpha / A_{\\text{total}} = L_0 / \\Sigma L$",
            fontsize=8.4, color=ORANGE)
    ax.text(3.60, 1.25, "③ 重心坐标：归一化后就是插值权重", fontsize=8.4, color=PURPLE)
    ax.text(3.80, 0.95, "同一个数，三种用法", fontsize=8.0, color=MUTED)

    box(ax, 7.35, 1.40, 2.35, 1.15, "所以光栅化只需要\n算三个 L\n后面全免费", fs=7.8,
        fc="#fff7ed", ec=ORANGE, tc="#7c3a00")
    ax.text(0.30, 0.55, "这一点很关键：第 6 讲的重心坐标不是新东西 —— 它就是光栅化时已经算过的 L 归一化。",
            fontsize=7.8, color=INK)
    ax.text(0.30, 0.28, "所以「光栅化」和「属性插值」在实现上是同一段代码的两个出口。", fontsize=7.8,
            color=MUTED)
    save(fig, "d15-edge-function-3roles.png")


# ------------------------------------------------- d16 退化三角形
def d16():
    fig, ax = canvas(9.8, 3.2, (0, 9.8), (0, 3.2), eq=False)
    ax.text(0.30, 2.94, "四种退化/病态三角形：要么画不出来，要么画得很慢", fontsize=10.0, color=INK, fontweight="bold")
    cases = [("零面积（共线）", 0.55, "三个点共线\n$\\Sigma L = 0$ → 除零", RED),
             ("退化成线", 3.05, "两个顶点重合\n只剩一条线段", ORANGE),
             ("退化成点", 5.55, "三个顶点重合\n只有一个像素", MUTED),
             ("超细长（针）", 8.05, "包围盒巨大\n但只覆盖极少像素", PURPLE)]
    for name, ox, note, c in cases:
        ax.add_patch(Rectangle((ox, 1.15), 1.55, 1.05, facecolor="white", ec=c, lw=1.3))
        if "零面积" in name:
            ax.plot([ox + 0.25, ox + 1.30], [1.35, 1.95], color=c, lw=2.0)
            ax.plot(ox + 0.78, 1.65, "o", ms=4, color=c)
        elif "线" in name:
            ax.plot([ox + 0.35, ox + 1.20], [1.50, 1.85], color=c, lw=2.4)
            ax.plot(ox + 0.35, 1.50, "o", ms=5, color=c)
            ax.plot(ox + 1.20, 1.85, "o", ms=5, color=c)
        elif "点" in name:
            ax.plot(ox + 0.78, 1.68, "o", ms=6, color=c)
        else:
            ax.add_patch(Polygon([[ox + 0.28, 1.22], [ox + 1.28, 1.24],
                                  [ox + 0.30, 2.12]], closed=True,
                                 facecolor="#f3e8ff", ec=c, lw=1.2))
        ax.text(ox + 0.78, 0.92, name, fontsize=7.4, color=c, ha="center")
        ax.text(ox + 0.78, 0.52, note, fontsize=6.6, color=MUTED, ha="center",
                linespacing=1.5, va="top")
    ax.text(0.30, 0.18, "处理：退化三角形应该在建网格时就剔除（L11–12 的「三角形质量」就是干这个）；"
                        "但如果运行时出现，光栅化器要能安全跳过（不能除零）", fontsize=7.6,
            color=INK)
    save(fig, "d16-degenerate.png")


# ------------------------------------------------- d17 解析覆盖率
def d17():
    fig, ax = canvas(9.8, 3.4, (0, 9.8), (0, 3.4), eq=False)
    ax.text(0.30, 3.14, "边缘的三种处理：0/1 采样、4× 采样、解析覆盖率", fontsize=10.0,
            color=INK, fontweight="bold")
    NX, NY, CW, CH = 5, 4, 0.42, 0.36
    for k, (ox, lab, c) in enumerate([(0.55, "1 采样（0/1）", RED),
                                      (3.55, "4× 采样（5 级）", ORANGE),
                                      (6.55, "解析（无穷级）", GREEN)]):
        y_base = 1.15
        y_top = y_base + NY * CH
        # 斜边：从左上走到右下，斜率让它在格子里穿过
        def edge_at(x):
            return y_top - (x - ox) * 0.62
        for i in range(NX):
            for j in range(NY):
                x0 = ox + i * CW
                y0 = y_base + j * CH
                if k == 0:
                    px, py = x0 + CW / 2, y0 + CH / 2
                    cov = 1.0 if py < edge_at(px) else 0.0
                elif k == 1:
                    cnt = 0
                    for dx in (0.25, 0.75):
                        for dy in (0.25, 0.75):
                            if y0 + dy * CH < edge_at(x0 + dx * CW):
                                cnt += 1
                    cov = cnt / 4.0
                else:
                    # 近似解析：逐像素细分 40 段求平均
                    cnt = 0.0
                    S = 40
                    for s_ in range(S):
                        yy = y0 + (s_ + 0.5) / S * CH
                        # 该高度上被覆盖的 x 比例
                        xe = ox + (y_top - yy) / 0.62
                        frac = max(0.0, min(1.0, (xe - x0) / CW))
                        cnt += frac
                    cov = cnt / S
                shade = 1.0 - 0.88 * cov
                ax.add_patch(Rectangle((x0, y0), CW, CH,
                                       facecolor=(shade, shade, shade), ec="#d1d5db",
                                       lw=0.4))
        ax.text(ox + NX * CW / 2, 0.85, lab, fontsize=7.6, color=c, ha="center")
    ax.text(0.30, 0.55, "解析覆盖率：直接算「像素方块被三角形盖住的比例」—— 理论上完美，"
                        "但每个像素要算多边形裁剪，太贵。", fontsize=7.6, color=INK)
    ax.text(0.30, 0.28, "所以实际用的是 4×/8×/16× 采样逼近（上图中列）—— 级数够多时肉眼看不出差别。",
            fontsize=7.6, color=MUTED)
    save(fig, "d17-coverage.png")

# ------------------------------------------------- d18 分块局部性
def d18():
    fig, ax = canvas(9.8, 3.2, (0, 9.8), (0, 3.2), eq=False)
    ax.text(0.30, 2.94, "分块光栅化：把屏幕切成 tile，让写内存变成连续的", fontsize=10.0, color=INK, fontweight="bold")
    # 左：行优先扫描（跨行跳）
    ax.text(2.05, 2.60, "逐行扫描", fontsize=8.4, color=RED, ha="center")
    for j in range(8):
        for i in range(14):
            ax.add_patch(Rectangle((0.55 + i * 0.21, 1.00 + j * 0.20), 0.21, 0.20,
                                   facecolor="#fde8e8" if j % 2 == 0 else "white",
                                   ec="#e5e7eb", lw=0.4))
    ax.text(2.05, 0.72, "每扫完一行要「跳」回左边", fontsize=6.8, color=MUTED, ha="center")

    # 右：tile
    ax.text(6.55, 2.60, "分块（tile）", fontsize=8.4, color=TEAL, ha="center")
    for j in range(8):
        for i in range(14):
            ti, tj = i // 4, j // 4
            col = "#e6f7f4" if (ti + tj) % 2 == 0 else "white"
            ax.add_patch(Rectangle((5.05 + i * 0.21, 1.00 + j * 0.20), 0.21, 0.20,
                                   facecolor=col, ec="#e5e7eb", lw=0.4))
    for tx in range(4):
        for ty in range(2):
            ax.add_patch(Rectangle((5.05 + tx * 4 * 0.21, 1.00 + ty * 4 * 0.20),
                                   4 * 0.21, 4 * 0.20, facecolor="none", ec=TEAL, lw=1.2))
    ax.text(6.55, 0.72, "一个 tile 写完整块，缓存命中高", fontsize=6.8, color=MUTED,
            ha="center")
    ax.text(0.30, 0.42, "为什么有效：深度缓冲、颜色缓冲都是二维数组，"
                        "但内存是一维的 —— 逐行扫描会在行末跳一大步，"
                        "而 tile 让「写同一块」的时间局部性变好", fontsize=7.6, color=INK)
    ax.text(0.30, 0.16, "这也是为什么 GPU 的渲染顺序不是「按三角形」而是「按 tile」—— 移动端 GPU 甚至是 TBDR（tile-based deferred）",
            fontsize=7.6, color=MUTED)
    save(fig, "d18-tiled-locality.png")


# ------------------------------------------------- d19 亚像素精度
def d19():
    fig, ax = canvas(9.6, 3.2, (0, 9.6), (0, 3.2), eq=False)
    ax.text(0.30, 2.94, "亚像素精度：边缘位置的量化误差", fontsize=10.0, color=INK,
            fontweight="bold")
    ax.text(0.55, 2.55, "浮点（理想）：", fontsize=8.2, color=TEAL)
    for k in range(12):
        x = 0.95 + k * 0.22
        ax.plot([x, x], [1.85, 2.35], color=TEAL, lw=1.0)
        ax.plot(x, 2.10, "o", ms=2.6, color=TEAL)
    ax.text(0.55, 1.60, "1/256 固定点（常见）：", fontsize=8.2, color=ORANGE)
    rng = np.random.default_rng(3)
    for k in range(12):
        x = 0.95 + k * 0.22
        ax.plot([x, x], [0.95, 1.45], color=ORANGE, lw=1.0)
        ax.plot(x, 1.20 + rng.uniform(-0.06, 0.06), "o", ms=2.6, color=ORANGE)
    ax.text(5.55, 2.20, "差别在哪：", fontsize=8.2, color=INK)
    ax.text(5.55, 1.90, "• 浮点：边缘位置精确到 float 精度", fontsize=7.4, color=MUTED)
    ax.text(5.55, 1.64, "• 1/256：边缘只能落在 1/256 像素的格点上", fontsize=7.4, color=MUTED)
    ax.text(5.55, 1.38, "• 后果：边缘有轻微抖动/阶梯", fontsize=7.4, color=RED)
    box(ax, 5.55, 0.55, 3.60, 0.60, "但 1/256 已经足够 —— 因为屏幕只有 8 bit 深度", fs=7.4,
        fc="#e6f7f4", ec=TEAL, tc=TEAL)
    ax.text(0.30, 0.20, "历史：早期硬件用 1/16 或 1/8 亚像素精度，边缘明显抖动；现代 GPU 用 1/256 或浮点",
            fontsize=7.6, color=MUTED)
    save(fig, "d19-subpixel.png")


# ------------------------------------------------- d20 采样模式
def d20():
    fig, ax = canvas(9.8, 3.2, (0, 9.8), (0, 3.2), eq=False)
    ax.text(0.30, 2.94, "一个像素内的采样位置：规则、旋转网格、泊松", fontsize=10.0, color=INK, fontweight="bold")
    # 中心
    ax.add_patch(Rectangle((0.55, 1.10), 1.10, 1.10, facecolor="white", ec=INK, lw=1.2))
    ax.plot(1.10, 1.65, "o", ms=6, color=RED)
    ax.text(1.10, 0.85, "中心（1×）", fontsize=7.4, color=RED, ha="center")
    ax.text(1.10, 0.55, "最省，但走样", fontsize=6.6, color=MUTED, ha="center")

    # 规则 2x2
    ax.add_patch(Rectangle((2.05, 1.10), 1.10, 1.10, facecolor="white", ec=INK, lw=1.2))
    for dx in (0.28, 0.82):
        for dy in (0.28, 0.82):
            ax.plot(2.05 + dx, 1.10 + dy, "o", ms=4.2, color=TEAL)
    ax.text(2.60, 0.85, "规则 2×2", fontsize=7.4, color=TEAL, ha="center")
    ax.text(2.60, 0.55, "子样本成网格", fontsize=6.6, color=MUTED, ha="center")

    # 旋转网格
    ax.add_patch(Rectangle((3.55, 1.10), 1.10, 1.10, facecolor="white", ec=INK, lw=1.2))
    c = np.array([4.10, 1.65])
    for dx, dy in [(-0.27, -0.27), (0.27, -0.27), (0.27, 0.27), (-0.27, 0.27)]:
        th = np.radians(26)
        rx = dx * np.cos(th) - dy * np.sin(th)
        ry = dx * np.sin(th) + dy * np.cos(th)
        ax.plot(c[0] + rx, c[1] + ry, "o", ms=4.2, color=ORANGE)
    ax.text(4.10, 0.85, "旋转网格", fontsize=7.4, color=ORANGE, ha="center")
    ax.text(4.10, 0.55, "避免与轴向对齐", fontsize=6.6, color=MUTED, ha="center")

    # 泊松/抖动
    ax.add_patch(Rectangle((5.05, 1.10), 1.10, 1.10, facecolor="white", ec=INK, lw=1.2))
    rng = np.random.default_rng(11)
    for _ in range(4):
        ax.plot(5.05 + rng.uniform(0.12, 0.98), 1.10 + rng.uniform(0.12, 0.98), "o",
                ms=4.2, color=PURPLE)
    ax.text(5.60, 0.85, "抖动/泊松", fontsize=7.4, color=PURPLE, ha="center")
    ax.text(5.60, 0.55, "把走样变噪声", fontsize=6.6, color=MUTED, ha="center")

    ax.text(6.75, 2.45, "怎么选：", fontsize=8.0, color=INK)
    ax.text(6.95, 2.15, "• 规则网格：确定性，好实现", fontsize=7.0, color=MUTED)
    ax.text(6.95, 1.90, "• 旋转网格：打破轴向规则", fontsize=7.0, color=MUTED)
    ax.text(6.95, 1.65, "• 泊松：蓝噪声，视觉最优", fontsize=7.0, color=MUTED)
    ax.text(6.95, 1.25, "GPU 的 MSAA 用固定的", fontsize=7.0, color=TEAL)
    ax.text(6.95, 1.00, "「旋转网格」模式", fontsize=7.0, color=TEAL)
    ax.text(6.95, 0.62, "可编程 AA（TAA）", fontsize=7.0, color=PURPLE)
    ax.text(6.95, 0.38, "用抖动", fontsize=7.0, color=PURPLE)
    save(fig, "d20-sample-patterns.png")


if __name__ == "__main__":
    print("generating ->", OUT)
    for fn in [d15, d16, d17, d18, d19, d20]:
        fn()
    print("done: 6 extra diagrams")
