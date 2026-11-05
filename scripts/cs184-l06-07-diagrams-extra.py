# -*- coding: utf-8 -*-
"""CS184 · L06–07 追加图解（d19–d22），按 v2 标准补齐到 22 张。"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Polygon, Circle, Ellipse

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


# ------------------------------------------------- d19 平铺接缝
def d19():
    fig, ax = canvas(9.8, 3.4, (0, 9.8), (0, 3.4), eq=False)
    ax.text(0.30, 3.14, "平铺的接缝：UV 从 0.99 跳到 0.01，导数会「爆炸」", fontsize=10.0,
            color=INK, fontweight="bold")
    # 一条 u 轴，标出平铺的 0..1 和 1..2
    xs = np.linspace(0.55, 4.35, 400)
    ax.plot(xs, np.full_like(xs, 1.90), color=INK, lw=1.4)
    for x in [0.55, 2.45, 4.35]:
        ax.plot([x, x], [1.80, 2.00], color=INK, lw=1.2)
    ax.text(0.55, 1.55, "$u=0$", fontsize=8.0, color=MUTED, ha="center")
    ax.text(2.45, 1.55, "$u=1$（接缝）", fontsize=8.0, color=RED, ha="center")
    ax.text(4.35, 1.55, "$u=2$", fontsize=8.0, color=MUTED, ha="center")
    # 采样点
    pts = [(2.35, "0.98"), (2.55, "1.02")]
    for k, (x, lab) in enumerate(pts):
        ax.plot(x, 1.90, "o", ms=6, color=RED, zorder=8)
        ax.text(x - 0.28 + k * 0.56, 2.12, lab, fontsize=7.6, color=RED, ha="center")
    ax.text(2.45, 2.45, "相邻两像素：$u$ 从 0.98 到 1.02", fontsize=7.8, color=INK,
            ha="center")

    ax.text(0.55, 1.05, "朴素做法：$\\Delta u = 1.02 - 0.98 = 0.04$", fontsize=8.0,
            color=GREEN)
    ax.text(0.55, 0.72, "如果做了 $\\mathrm{frac}()$：$0.02 - 0.98 = -0.96$", fontsize=8.0,
            color=RED)
    ax.text(0.55, 0.38, "$\\Rightarrow$ 算出来的 $L$ 差 24 倍，mipmap 层级跳 4~5 级", fontsize=8.0,
            color=RED)

    box(ax, 5.55, 1.45, 3.90, 1.15,
        "症状：平铺地面的接缝处\n出现一条模糊带（或一条硬线）", fs=7.8,
        fc="#fff7ed", ec=ORANGE, tc="#7c3a00")
    ax.text(5.55, 1.05, "正解：", fontsize=8.2, color=TEAL)
    ax.text(5.75, 0.78, "① 算导数时不要先 frac()", fontsize=7.6, color=MUTED)
    ax.text(5.75, 0.52, "② 或用 wrap-aware 的差分（取最小环绕距离）", fontsize=7.6,
            color=MUTED)
    ax.text(5.75, 0.26, "③ 或干脆用 clamp + 手工铺边界", fontsize=7.6, color=MUTED)
    save(fig, "d19-tiling-seam.png")


# ------------------------------------------------- d20 EWA 椭圆
def d20():
    fig, ax = canvas(9.4, 3.4, (0, 9.4), (0, 3.4))
    ax.text(0.30, 3.14, "EWA 的核心：用椭圆拟合足迹，按椭圆做加权平均", fontsize=10.0,
            color=INK, fontweight="bold")
    # 左：真实足迹（长条）
    o = np.array([0.70, 1.25])
    e1 = np.array([2.30, 0.55])
    e2 = np.array([0.20, 0.38])
    ax.add_patch(Polygon([o, o + e1, o + e1 + e2, o + e2], closed=True,
                         facecolor="#fde8e8", ec=RED, lw=1.4, alpha=0.75))
    ax.text(1.95, 0.85, "真实足迹", fontsize=8.0, color=RED, ha="center")

    # 中：椭圆拟合
    cx, cy = 5.05, 1.65
    ang = np.degrees(np.arctan2(0.55, 2.30))
    ax.add_patch(Ellipse((cx, cy), 2.45, 0.55, angle=ang, facecolor="#e6f7f4",
                         ec=TEAL, lw=1.4, alpha=0.85))
    ax.plot(cx, cy, "o", ms=4, color=TEAL)
    ax.text(cx, 0.85, "椭圆拟合（EWA）", fontsize=8.0, color=TEAL, ha="center")

    # 右：圆形/正方形（mipmap）
    ax.add_patch(Circle((8.05, 1.65), 0.62, facecolor="#f8fafc", ec=MUTED, lw=1.3,
                        ls=(0, (4, 3))))
    ax.text(8.05, 0.85, "正方形（mipmap）", fontsize=8.0, color=MUTED, ha="center")

    ax.text(0.55, 0.42, "EWA 的做法：", fontsize=8.2, color=INK)
    ax.text(1.65, 0.42, "把足迹拟合成椭圆 → 沿长轴取若干 mipmap 样本 → 按椭圆高斯权重加权",
            fontsize=7.6, color=MUTED)
    ax.text(0.55, 0.14, "代价：每像素 4–16 次纹理采样（vs 三线性的 8 次），但斜视时质量高得多",
            fontsize=7.6, color=ORANGE)
    save(fig, "d20-ewa-ellipse.png")


# ------------------------------------------------- d21 Nyquist 与摩尔纹
def d21():
    fig, ax = canvas(9.8, 3.4, (0, 9.8), (0, 3.4), eq=False)
    ax.text(0.30, 3.14, "摩尔纹的根源：采样率低于信号频率的两倍（Nyquist）", fontsize=10.0,
            color=INK, fontweight="bold")
    # 上：高频信号 + 稀疏采样
    x = np.linspace(0, 1, 500)
    sig = 0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 9 * x))  # 9 周期的方波（棋盘格）
    ax.plot(0.60 + 3.10 * x, 2.15 + 0.60 * sig, color=TEAL, lw=1.2)
    xf = np.array([0.75, 1.10, 1.45, 1.80, 2.15, 2.50, 2.85, 3.20, 3.55])
    yf = 2.15 + 0.60 * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 9 * (xf - 0.60) / 3.10)))
    ax.plot(xf, yf, "o", ms=4.5, color=RED, zorder=8)
    ax.plot(xf, yf, color=RED, lw=1.0, ls=(0, (3, 2)))
    ax.text(2.15, 2.95, "高频信号（棋盘格）+ 稀疏采样 = 低频假信号", fontsize=7.8,
            color=RED, ha="center")

    # 下：正确的做法（先低通）
    ax.plot(0.60 + 3.10 * x, 0.75 + 0.60 * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 1.5 * x))),
            color=ORANGE, lw=1.2)
    ax.text(2.15, 1.55, "先低通（取平均）→ 采样就对了", fontsize=7.8, color=ORANGE,
            ha="center")

    ax.text(4.10, 2.55, "Nyquist 定理：", fontsize=8.8, color=INK)
    ax.text(4.30, 2.22, "采样率必须 $> 2 \\times$ 最高频率", fontsize=8.0, color=TEAL)
    ax.text(4.10, 1.78, "换算到纹理：", fontsize=8.2, color=MUTED)
    ax.text(4.30, 1.48, "一个像素覆盖的 texel 数 > 1", fontsize=7.6, color=MUTED)
    ax.text(4.30, 1.22, "就必然欠采样", fontsize=7.6, color=RED)
    box(ax, 6.85, 1.30, 2.60, 1.15, "mipmap 就是「预先把\n高频滤掉」", fs=7.8,
        fc="#e6f7f4", ec=TEAL, tc=TEAL)
    ax.text(0.30, 0.12, "直觉：一个像素只能记住「平均颜色」，记不住「里面有几个黑白格」—— "
                        "所以必须先把格子平均掉再采样", fontsize=7.8, color=MUTED)
    save(fig, "d21-nyquist-moire.png")


# ------------------------------------------------- d22 纹理显存
def d22():
    fig, ax = canvas(9.8, 3.0, (0, 9.8), (0, 3.0), eq=False)
    ax.text(0.30, 2.74, "纹理的显存：格式选择能省 4–8 倍", fontsize=10.0, color=INK,
            fontweight="bold")
    rows = [("RGBA8（未压缩）", "4 B/texel", "2048² = 16 MB", "1×", RED),
            ("RGB565", "2 B/texel", "8 MB", "2×", ORANGE),
            ("BC1 / DXT1（4:1）", "0.5 B/texel", "2 MB", "8×", TEAL),
            ("BC7（高质量 4:1）", "1 B/texel", "4 MB", "4×", TEAL),
            ("ASTC 6×6", "0.44 B/texel", "1.8 MB", "9×", GREEN)]
    ax.text(0.55, 2.40, "格式", fontsize=8.0, color=INK, fontweight="bold")
    ax.text(3.35, 2.40, "每 texel", fontsize=8.0, color=INK, fontweight="bold")
    ax.text(5.15, 2.40, "2048×2048 大小", fontsize=8.0, color=INK, fontweight="bold")
    ax.text(7.35, 2.40, "相对未压缩", fontsize=8.0, color=INK, fontweight="bold")
    for i, (a, b, c, d, col) in enumerate(rows):
        y = 2.10 - i * 0.36
        ax.text(0.55, y, a, fontsize=7.6, color=col)
        ax.text(3.35, y, b, fontsize=7.6, color=MUTED)
        ax.text(5.15, y, c, fontsize=7.6, color=MUTED)
        ax.text(7.35, y, d, fontsize=7.6, color=col)
    ax.text(0.30, 0.35, "注意：以上是单级大小。加上 mipmap 再乘 4/3。", fontsize=7.8,
            color=ORANGE)
    ax.text(0.30, 0.10, "所以 2048² RGBA8 带 mipmap ≈ 21 MB；用 BC1 只要约 2.7 MB —— "
                        "这就是为什么游戏纹理几乎全是压缩格式", fontsize=7.8, color=MUTED)
    save(fig, "d22-texture-memory.png")


if __name__ == "__main__":
    print("generating ->", OUT)
    for fn in [d19, d20, d21, d22]:
        fn()
    print("done: 4 extra diagrams")
