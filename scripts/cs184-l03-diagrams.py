# -*- coding: utf-8 -*-
"""CS184 课程笔记 · L03（采样与走样）原创图解

风格遵循 scripts/cs184-notes-standard.md：
一图一关系 / 不画 matplotlib 坐标轴 / 图内无标题 / 图注写在正文 / 颜色语义固定

颜色语义：teal=主链路/内侧，orange=本讲焦点，purple=数据形态，red=异常/走样，灰=说明
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle

plt.rcParams["font.family"] = ["Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

OUT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "src", "content",
                                    "notes", "cs184-03-sampling-aliasing", "diagrams"))
os.makedirs(OUT, exist_ok=True)
DPI = 200

INK, MUTED = "#16202c", "#5b6b7c"
FILL, STROKE = "#f4f6f9", "#c3ccd6"
TEAL, ORANGE, PURPLE = "#0f766e", "#b45309", "#5b21b6"
BLUE, RED, GREEN = "#1d4ed8", "#b91c1c", "#15803d"


def canvas(w, h, xlim, ylim, x=True):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axis("off")
    if x:
        ax.set_aspect("equal")
    return fig, ax


def box(ax, x, y, w, h, text, fc=FILL, ec=STROKE, tc=INK, fs=10.5, lw=1.4,
        pad=0.08, rad=0.14):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle=f"round,pad={pad},rounding_size={rad}",
                                facecolor=fc, edgecolor=ec, linewidth=lw, zorder=3))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            color=tc, zorder=4)


def arrow(ax, p, q, color=TEAL, lw=1.8, ls="-", z=2, ms=13, rad=0.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=ms, color=color,
                                 lw=lw, linestyle=ls, zorder=z,
                                 connectionstyle=f"arc3,rad={rad}",
                                 shrinkA=1, shrinkB=1))


def axis_h(ax, x0, x1, y, marks, label=None, color=MUTED, fs=8.6, arrow_tip=True):
    """手绘一条水平频率轴（不是 matplotlib 坐标轴）：只画线 + 少量刻度文字。"""
    ax.plot([x0, x1], [y, y], color=color, lw=1.3, zorder=2)
    if arrow_tip:
        ax.add_patch(FancyArrowPatch((x1, y), (x1 + 0.02 * (x1 - x0), y),
                                     arrowstyle="-|>", mutation_scale=10,
                                     color=color, lw=1.3, zorder=2))
    for xm, txt, col in marks:
        ax.plot([xm, xm], [y - 0.30, y + 0.30], color=col, lw=1.1, zorder=3)
        ax.text(xm, y - 0.55, txt, fontsize=fs, color=col, ha="center", va="top")
    if label:
        ax.text((x0 + x1) / 2, y + 0.95, label, fontsize=fs + 0.6, color=MUTED,
                ha="center", va="bottom")


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=DPI, bbox_inches="tight",
                facecolor="white", pad_inches=0.12)
    plt.close(fig)
    print("  ", name)


# ---------------------------------------------------------- d01 采样无处不在
def d01():
    fig, ax = canvas(11.0, 2.9, (0, 11.0), (0, 2.9))
    cols = [
        ("视频 = 采样时间", "1D · t", TEAL),
        ("照片 = 采样传感器", "2D · x,y", TEAL),
        ("光栅化 = 采样位置", "2D · x,y", ORANGE),
        ("光线追踪 = 采样光线", "2D · 方向", TEAL),
        ("光照 = 采样入射角", "2D · θ,φ", TEAL),
    ]
    t = np.linspace(0, 1, 80)
    for i, (t1, t2, c) in enumerate(cols):
        x = 0.35 + i * 2.12
        fc = "#fff7ed" if c == ORANGE else FILL
        box(ax, x, 0.55, 1.85, 1.55, "", fc=fc, ec=c if c == ORANGE else STROKE)
        ax.text(x + 0.925, 1.32, t1, fontsize=9.4, color=c, ha="center",
                fontweight="bold", zorder=5)
        ax.text(x + 0.925, 0.90, t2, fontsize=8.8, color=MUTED, ha="center", zorder=5)
        cx = x + 0.925
        if i == 0:      # 信号 + 采样点
            yy = 1.72 + 0.12 * np.sin(2 * np.pi * 3 * t)
            ax.plot(cx - 0.70 + 1.40 * t, yy, color=c, lw=1.2, zorder=5)
            for k in range(7):
                ax.plot(cx - 0.70 + 1.40 * k / 6,
                        1.72 + 0.12 * np.sin(2 * np.pi * 3 * k / 6), "o", ms=2.4,
                        color=c, zorder=6)
        elif i == 1:    # 传感器网格
            g = np.arange(5)
            for a in g:
                for b in g:
                    ax.plot(cx - 0.52 + a * 0.26, 1.62 + b * 0.14, ".", ms=2.2,
                            color=c, zorder=5)
        elif i == 2:    # 三角形 + 采样点
            ax.add_patch(plt.Polygon([[cx - 0.55, 1.58], [cx + 0.50, 1.58],
                                      [cx - 0.10, 1.86]], closed=True,
                                     fill=False, ec=c, lw=1.2, zorder=5))
            for a in range(4):
                for b in range(3):
                    ax.plot(cx - 0.52 + a * 0.30, 1.62 + b * 0.12, ".", ms=1.8,
                            color=c, alpha=0.75, zorder=4)
        elif i == 3:    # 光线扇
            ax.plot(cx - 0.62, 1.72, "o", ms=3.2, color=c, zorder=6)
            for k in range(5):
                ax.plot([cx - 0.62, cx + 0.55],
                        [1.72, 1.58 + k * 0.07], color=c, lw=0.8, zorder=5)
        else:           # 半球上的入射方向
            th = np.linspace(0, np.pi, 60)
            ax.plot(cx + 0.42 * np.cos(th), 1.60 + 0.22 * np.sin(th), color=c, lw=1.0,
                    zorder=5)
            for a in np.linspace(0.35, np.pi - 0.35, 4):
                ax.plot([cx, cx + 0.40 * np.cos(a)], [1.60, 1.60 + 0.21 * np.sin(a)],
                        color=c, lw=0.8, zorder=4)
    ax.text(0.35, 2.62, "同一件事发生在五种维度上：屏幕上的离散化只是其中一例",
            fontsize=10, color=INK)
    save(fig, "d01-ubiquitous-sampling.png")


# ---------------------------------------------------------- d02 先滤后采样
def d02():
    fig, ax = canvas(11.4, 4.8, (0, 11.4), (0, 4.8))
    xs = np.linspace(0, 1, 800)

    def curve(x0, x1, y, f, color, lw=1.8, ls="-", amp=0.28):
        ax.plot(x0 + (x1 - x0) * xs, y + amp * np.sin(2 * np.pi * f * xs),
                color=color, lw=lw, ls=ls, zorder=3, solid_capstyle="round")

    # ---- 行 A：先采样、后滤波 ----
    ya = 3.30
    ax.text(0.30, ya + 0.96, "A　先采样，后滤波", fontsize=10.2, color=RED,
            fontweight="bold")
    curve(0.30, 1.95, ya, 5, BLUE)
    ax.text(1.12, ya - 0.52, "连续信号（含高频）", fontsize=8.6, color=MUTED, ha="center")
    arrow(ax, (2.02, ya), (2.62, ya), color=RED)
    ax.text(2.32, ya + 0.20, "采样", fontsize=8.8, color=RED, ha="center")
    box(ax, 2.68, ya - 0.34, 1.10, 0.68, "只剩离散点", fs=8.8, tc=MUTED)
    for k in range(9):
        t = k / 8
        ax.plot(2.68 + 1.10 * (0.06 + 0.88 * t), ya, "o", ms=3.4, color=RED, zorder=6)
    arrow(ax, (3.86, ya), (4.46, ya), color=MUTED)
    ax.text(4.16, ya + 0.20, "滤波", fontsize=8.8, color=MUTED, ha="center")
    curve(4.55, 7.05, ya, 3, "#9ca3af", lw=2.2)
    ax.text(5.80, ya - 0.52, "滤出来的已经不是原来那个信号", fontsize=8.6, color=RED,
            ha="center")
    ax.text(7.30, ya, "高频在采样时\n就已经折成假低频，\n滤不回来", fontsize=9.2,
            color=RED, va="center")

    # ---- 行 B：先滤波、后采样 ----
    yb = 1.25
    ax.text(0.30, yb + 0.96, "B　先滤波，后采样", fontsize=10.2, color=TEAL,
            fontweight="bold")
    curve(0.30, 1.95, yb, 5, BLUE)
    arrow(ax, (2.02, yb), (2.62, yb), color=TEAL)
    ax.text(2.32, yb + 0.20, "滤波", fontsize=8.8, color=TEAL, ha="center")
    box(ax, 2.68, yb - 0.34, 1.10, 0.68, "高频被削掉", fs=8.8, tc=TEAL, ec=TEAL)
    arrow(ax, (3.86, yb), (4.46, yb), color=MUTED)
    ax.text(4.16, yb + 0.20, "采样", fontsize=8.8, color=MUTED, ha="center")
    curve(4.55, 7.05, yb, 1, TEAL, lw=2.2)
    for k in range(9):
        t = k / 8
        ax.plot(4.55 + 2.50 * t, yb + 0.28 * np.sin(2 * np.pi * 1 * t), "o", ms=4.0,
                markerfacecolor="white", markeredgecolor=TEAL, markeredgewidth=1.4,
                zorder=6)
    ax.text(5.80, yb - 0.56, "采到的是真实存在的低频", fontsize=8.6, color=TEAL,
            ha="center")
    ax.text(7.30, yb, "没有假成分\n所以能还原", fontsize=9.2, color=TEAL, va="center")

    ax.text(0.30, 4.50, "两行只差「滤波放在采样前还是后」——结果完全不同",
            fontsize=11, color=INK, fontweight="bold")
    ax.text(0.30, 0.45, "采样之后再用滤波器，救不回来：高频已经折成假低频，两者叠在一起分不开",
            fontsize=9.2, color=MUTED)
    save(fig, "d02-filter-then-sample.png")


# ---------------------------------------------------------- d03 频率 = 1/周期
def d03():
    fig, ax = canvas(9.2, 3.6, (0, 9.2), (0, 3.6))
    x = np.linspace(0, 1, 700)
    for i, (f, c, lab) in enumerate([(1, TEAL, "$f=1$，$T=1$"),
                                     (2, ORANGE, "$f=2$，$T=1/2$"),
                                     (4, PURPLE, "$f=4$，$T=1/4$")]):
        y0 = 2.55 - i * 1.02
        ax.plot(1.1 + 4.0 * x, y0 + 0.32 * np.sin(2 * np.pi * f * x),
                color=c, lw=1.9, zorder=3)
        ax.text(0.25, y0, lab, fontsize=9.6, color=c, va="center")
        # 标一个周期
        ax.annotate("", xy=(1.1 + 4.0 / f, y0 + 0.52), xytext=(1.1, y0 + 0.52),
                    arrowprops=dict(arrowstyle="<|-|>", color=MUTED, lw=1.0,
                                    mutation_scale=9))
        ax.text(1.1 + 2.0 / f, y0 + 0.66, "一个周期 T", fontsize=8.2, color=MUTED,
                ha="center")
    ax.plot([6.0, 6.0], [0.15, 3.05], color="#e5e9ef", lw=1.2)
    ax.text(6.35, 2.35, "频率 = 单位长度里\n重复几次 = 1/T", fontsize=10, color=INK)
    ax.text(6.35, 1.45, "周期越短，\n频率越高，\n越难采样", fontsize=9.6, color=RED)
    ax.text(0.25, 3.35, "正弦的「频率」就是周期长度的倒数", fontsize=10.5, color=INK,
            fontweight="bold")
    save(fig, "d03-sine-frequency.png")


# ---------------------------------------------------------- d04 傅里叶：方波分解
def d04():
    fig, ax = canvas(9.8, 3.8, (0, 9.8), (0, 3.8))
    t = np.linspace(0, 3, 1200)
    sq = np.sign(np.sin(2 * np.pi * t))
    ax.plot(0.45 + 2.55 * t / 3, 1.75 + 0.62 * sq, color=INK, lw=1.5,
            ls=(0, (4, 3)), zorder=2)
    ax.text(0.45, 2.62, "目标：方波", fontsize=9.4, color=INK)

    def partial(n_terms):
        s = np.zeros_like(t)
        for k in [1, 3, 5, 7, 9, 11][:n_terms]:
            s += (4 / np.pi) * np.sin(2 * np.pi * k * t) / k
        return s

    for n, c, lab in [(2, TEAL, "2 个谐波"), (6, ORANGE, "6 个谐波")]:
        ax.plot(0.45 + 2.55 * t / 3, 1.75 + 0.62 * partial(n), color=c, lw=1.8,
                zorder=3, label=lab)
    ax.text(3.35, 2.55, "叠加奇数谐波，项数越多越接近方波", fontsize=9.6, color=INK)
    ax.text(3.35, 2.05, r"$f(x)=\dfrac{4}{\pi}\left(\sin\omega t+\dfrac{\sin 3\omega t}{3}+\dfrac{\sin 5\omega t}{5}+\cdots\right)$",
            fontsize=10.2, color=INK)
    ax.text(3.35, 1.35, "● 2 个谐波：还在“打摆子”", fontsize=9.2, color=TEAL)
    ax.text(3.35, 0.98, "● 6 个谐波：接近方波，但边缘永远有过冲", fontsize=9.2, color=ORANGE)
    ax.text(3.35, 0.50, "两点结论：① 硬边缘需要无穷多高频分量 ② 这些分量衰减很慢（1/k）\n→ 所以方波的频谱“又宽又长尾”，最难采样",
            fontsize=9.0, color=RED, va="bottom")
    save(fig, "d04-fourier-sum.png")


# ---------------------------------------------------------- d05 空域 ↔ 频域
def d05():
    fig, ax = canvas(9.4, 3.4, (0, 9.4), (0, 3.4), x=False)
    x = np.linspace(0, 1, 700)
    ax.plot(0.45 + 3.4 * x, 1.55 + 0.75 * np.sin(2 * np.pi * 3 * x),
            color=BLUE, lw=2.0, zorder=3)
    ax.text(0.45, 2.95, "空域（spatial domain）", fontsize=10, color=INK,
            fontweight="bold")
    ax.text(2.15, 0.62, "一条正弦", fontsize=9.2, color=MUTED, ha="center")

    arrow(ax, (4.15, 1.55), (4.95, 1.55), color=MUTED, lw=1.6)
    ax.text(4.55, 1.85, "傅里叶", fontsize=8.6, color=MUTED, ha="center")

    # 频域：两个脉冲
    axh = 1.55
    ax.plot([5.25, 8.85], [axh, axh], color=MUTED, lw=1.2, zorder=2)
    for xm, sgn in [(6.35, "−f"), (7.75, "+f")]:
        ax.plot([xm, xm], [axh, axh + 1.05], color=RED, lw=2.4, zorder=3)
        ax.plot(xm, axh + 1.05, "o", ms=4, color=RED, zorder=4)
        ax.text(xm, axh - 0.30, sgn, fontsize=9.4, color=RED, ha="center")
    ax.text(7.05, axh - 0.30, "0", fontsize=9.0, color=MUTED, ha="center")
    ax.text(7.05, 2.95, "频域（frequency domain）", fontsize=10, color=INK,
            fontweight="bold")
    ax.text(7.05, 0.62, "两个脉冲：±f", fontsize=9.2, color=MUTED, ha="center")
    ax.text(5.25, 0.20, "一条正弦 ↔ 频域里两个点。整个频域语言都建立在这个对应上",
            fontsize=9.0, color=INK)
    save(fig, "d05-spatial-vs-freq.png")


# ---------------------------------------------------------- d06 欠采样 → 假低频
def d06():
    fig, ax = canvas(10.0, 3.9, (0, 10.0), (0, 3.9), x=False)
    x = np.linspace(0, 10, 2000)
    f_true, fs = 0.9, 1.0
    ax.plot(0.45 + 9.1 * x / 10, 2.30 + 0.80 * np.sin(2 * np.pi * f_true * x),
            color="#93c5fd", lw=1.3, ls=(0, (5, 3)), zorder=2)
    xs = np.arange(0, 10.001, 1 / fs)
    ys = 2.30 + 0.80 * np.sin(2 * np.pi * f_true * xs)
    ax.plot(0.45 + 9.1 * xs / 10, ys, "o", ms=8, markerfacecolor="white",
            markeredgecolor=RED, markeredgewidth=2.0, zorder=6)
    f_alias = abs(f_true - round(f_true / fs) * fs)      # = 0.1
    ax.plot(0.45 + 9.1 * x / 10, 2.30 + 0.80 * np.sin(2 * np.pi * f_alias * x),
            color=RED, lw=2.4, zorder=5)
    ax.text(0.45, 3.48, "真正的高频（蓝色虚线，9 个周期）穿过采样点后，最“慢”的重建曲线（红色实线）只有 1 个周期",
            fontsize=9.4, color=INK)
    ax.text(5.0, 1.28, "采样频率 $f_s=1$，信号频率 0.9 周期/单位", fontsize=9.2,
            color=MUTED, ha="center")
    ax.text(5.0, 0.75, "重建得到 $|0.9-1|=0.1$ —— 慢了 9 倍", fontsize=11, color=RED,
            ha="center", fontweight="bold")
    ax.text(5.0, 0.28, "同一组采样点可以对应无数个频率，取最低的那个就是幻觉。所以“采样不足时高频会被误认成低频”",
            fontsize=8.8, color=MUTED, ha="center")
    save(fig, "d06-alias-undersample.png")


# ---------------------------------------------------------- d07 频率折叠
def d07():
    fig, ax = canvas(9.6, 3.6, (0, 9.6), (0, 3.6))
    x0, x1, y = 0.6, 8.9, 1.55
    ax.plot([x0, x1], [y, y], color=MUTED, lw=1.4, zorder=2)

    def mk(frac, txt, col=MUTED, fs=9.0):
        xm = x0 + (x1 - x0) * frac
        ax.plot([xm, xm], [y - 0.42, y + 0.42], color=col, lw=1.2, zorder=3)
        ax.text(xm, y - 0.62, txt, fontsize=fs, color=col, ha="center", va="top")
        return xm

    mk(0.0, "0")
    nq = mk(0.5, "$f_s/2$  ← Nyquist", ORANGE, 9.2)
    fsx = mk(1.0, "$f_s$", MUTED)
    # 一个超出 Nyquist 的频率，折回
    xf = x0 + (x1 - x0) * 0.80
    ax.plot([xf, xf], [y, y + 0.95], color=RED, lw=2.4, zorder=4)
    ax.plot(xf, y + 0.95, "o", ms=5, color=RED, zorder=5)
    ax.text(xf + 0.12, y + 1.02, "真实频率 0.8$f_s$", fontsize=9.2, color=RED)
    xfold = x0 + (x1 - x0) * 0.20
    ax.plot([xfold, xfold], [y, y + 0.50], color=TEAL, lw=2.4, zorder=4)
    ax.plot(xfold, y + 0.50, "o", ms=5, color=TEAL, zorder=5)
    ax.text(xfold - 0.12, y + 0.58, "看起来像 0.2$f_s$", fontsize=9.2, color=TEAL,
            ha="right")
    ax.annotate("", xy=(xfold, y + 0.12), xytext=(xf, y + 0.12),
                arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.4,
                                connectionstyle="arc3,rad=0.28"))
    ax.text((xfold + xf) / 2, y + 0.02, "以 $f_s$ 为周期折叠", fontsize=8.8, color=RED,
            ha="center", va="top")
    ax.text(0.6, 3.25, "频域里其实是「复制 + 叠加」：采样把频谱以 $f_s$ 为周期复制一份",
            fontsize=9.8, color=INK)
    ax.text(0.6, 0.30, "超过 $f_s/2$ 的成分折回到低频区，与真低频混在一起 —— 这就是走样",
            fontsize=9.2, color=RED)
    save(fig, "d07-alias-fold.png")


# ---------------------------------------------------------- d08 2D 频域画廊
def d08():
    fig, ax = canvas(10.4, 4.4, (0, 10.4), (0, 4.4), x=False)
    N = 96
    u = np.linspace(-1, 1, N)
    X, Y = np.meshgrid(u, u)
    cases = [
        ("常数", np.ones_like(X), [(0, 0)]),
        (r"$\sin 2\pi x/32$", 0.5 + 0.5 * np.sin(2 * np.pi * X * 3), [(-3, 0), (3, 0)]),
        (r"$\sin 2\pi y/16$", 0.5 + 0.5 * np.sin(2 * np.pi * Y * 3), [(0, -3), (0, 3)]),
        ("两者相乘", (0.5 + 0.5 * np.sin(2 * np.pi * X * 3)) *
                   (0.5 + 0.5 * np.sin(2 * np.pi * Y * 3)),
         [(-3, -3), (-3, 3), (3, -3), (3, 3)]),
    ]
    for i, (name, img, dots) in enumerate(cases):
        cx = 0.35 + i * 2.52
        ax.imshow(img, cmap="gray", extent=(cx, cx + 1.55, 0.95, 2.50), origin="lower",
                  vmin=0, vmax=1, zorder=2)
        ax.add_patch(Rectangle((cx, 0.95), 1.55, 1.55, fill=False, ec=STROKE, lw=1.0))
        ax.text(cx + 0.775, 0.70, name, fontsize=9.2, color=INK, ha="center")
        # 频域小图
        fy0 = 0.30
        ax.add_patch(Rectangle((cx, fy0 - 0.30), 1.55, 1.30, facecolor="#0b1220",
                               ec="#0b1220"))
        for (dx, dy) in dots:
            px = cx + 0.775 + dx * 0.19
            py = fy0 + 0.35 + dy * 0.19
            ax.plot(px, py, "o", ms=4.2, color="#fbbf24", zorder=4)
        ax.plot(cx + 0.775, fy0 + 0.35, "+", ms=6, color="#64748b", zorder=4)
        ax.text(cx + 0.775, 3.02, "空域", fontsize=8.0, color=MUTED, ha="center")
        ax.text(cx + 0.775, 1.02, "频域", fontsize=8.0, color="#9ca3af", ha="center")
    ax.text(0.35, 4.05, "二维频域的读法：原点 = 常数，某方向上的点 = 该方向的条纹，点数 = 分量个数",
            fontsize=9.8, color=INK, fontweight="bold")
    save(fig, "d08-2d-freq-gallery.png")


# ---------------------------------------------------------- d09 卷积定理
def d09():
    fig, ax = canvas(10.0, 3.6, (0, 10.0), (0, 3.6))
    top, bot = 2.75, 1.05
    for y, lab, c in [(top, "空域 spatial", TEAL), (bot, "频域 frequency", PURPLE)]:
        ax.text(0.25, y + 0.52, lab, fontsize=9.6, color=c, fontweight="bold")
        box(ax, 1.85, y - 0.32, 1.15, 0.72, "图像", fs=9.5)
        box(ax, 4.05, y - 0.32, 1.15, 0.72, "核", fs=9.5)
        box(ax, 6.55, y - 0.32, 1.35, 0.72, "结果", fs=9.5, ec=c, tc=c)
        ax.text(3.55, y + 0.04, "⊛" if y == top else "×", fontsize=17, color=INK,
                ha="center", va="center")
        ax.text(5.55, y + 0.04, "=", fontsize=17, color=INK, ha="center", va="center")
        arrow(ax, (3.02, y + 0.04), (4.02, y + 0.04), color=MUTED, lw=1.2)
        arrow(ax, (5.22, y + 0.04), (6.52, y + 0.04), color=MUTED, lw=1.2)
    ax.annotate("", xy=(4.62, bot + 0.45), xytext=(4.62, top - 0.38),
                arrowprops=dict(arrowstyle="<|-|>", color=MUTED, lw=1.3,
                                linestyle=(0, (3, 3))))
    ax.text(4.75, 1.90, "傅里叶变换", fontsize=8.8, color=MUTED)
    ax.text(0.25, 0.30, "空域的卷积 ≡ 频域的乘法。所以「滤波」有两种实现：直接卷积，或变换→相乘→变换回",
            fontsize=9.4, color=INK)
    save(fig, "d09-conv-theorem.png")


# ---------------------------------------------------------- d10 核宽 ↔ 频带
def d10():
    fig, ax = canvas(10.0, 4.2, (0, 10.0), (0, 4.2), x=False)
    rows = [
        ("窄核", 2.85, 0.20, 0.55, TEAL, "频域响应宽 → 只削掉很高频"),
        ("宽核", 1.05, 0.68, 0.20, ORANGE, "频域响应窄 → 削掉更多高频"),
    ]
    fx = np.linspace(-1, 1, 500)
    for name, y, kw, fw, c, note in rows:
        ax.text(0.30, y + 0.74, name, fontsize=10, color=c, fontweight="bold")
        if c == ORANGE:
            ax.text(0.30, y + 0.48, "（宽核）", fontsize=8.4, color=MUTED)
        # 空域核
        ax.add_patch(Rectangle((0.95, y + 0.02), kw, 0.72, facecolor=c, alpha=0.32,
                               ec=c, lw=1.4))
        ax.text(0.95 + kw / 2, y - 0.26, "空域核（%s）" % ("窄" if kw < 0.4 else "宽"),
                fontsize=8.4, color=MUTED, ha="center")
        # 频域响应
        resp = np.sinc(fx / fw) ** 2
        ax.plot(4.05 + 2.55 * fx, y + 0.38 + 0.52 * resp, color=c, lw=1.9)
        base = y + 0.38
        ax.plot([4.05, 4.05], [y - 0.02, y + 0.98], color="#e5e9ef", lw=0.9)
        ax.text(4.05 + 2.55, base - 0.28, "f", fontsize=8.4, color=MUTED, ha="center")
        ax.text(7.05, y + 0.38, note, fontsize=9.0, color=c, va="center")
    ax.text(0.30, 3.92, "核在空域越宽，频域响应越窄 —— 两个域里的宽度成反比",
            fontsize=10.2, color=INK, fontweight="bold")
    ax.text(0.30, 0.42, "想多滤掉一点高频，就得换更宽的核；代价是把真实细节也一起削掉",
            fontsize=9.2, color=MUTED)
    save(fig, "d10-filter-width.png")


# ---------------------------------------------------------- d11 1 像素盒式滤波
def d11():
    fig, ax = canvas(10.2, 3.8, (0, 10.2), (0, 3.8), x=False)
    # 空域：1 像素宽的盒子
    ax.text(0.40, 3.32, "空域：1 像素宽的盒式核", fontsize=10, color=TEAL,
            fontweight="bold")
    for k in range(-2, 3):
        ax.add_patch(Rectangle((2.05 + k * 0.46, 1.95), 0.46, 0.46, fill=False,
                               ec="#dbe2ea", lw=0.9))
    ax.add_patch(Rectangle((2.05, 1.95), 0.46, 0.46, facecolor=TEAL, alpha=0.32,
                           ec=TEAL, lw=1.6))
    ax.annotate("", xy=(2.05 + 0.46, 1.80), xytext=(2.05, 1.80),
                arrowprops=dict(arrowstyle="<|-|>", color=TEAL, lw=1.2,
                                mutation_scale=9))
    ax.text(2.28, 1.58, "1 像素", fontsize=8.6, color=TEAL, ha="center")
    ax.text(2.28, 1.32, "盒里的值等权相加再除以 9（二维）", fontsize=8.4, color=MUTED,
            ha="center")

    # 频域：|sinc|
    ax.text(5.35, 3.42, "频域：sinc 包络", fontsize=10, color=PURPLE, fontweight="bold")
    f = np.linspace(-4.2, 4.2, 1400)
    ax.plot(6.55 + 0.62 * f, 2.55 + 0.62 * np.abs(np.sinc(f)), color=PURPLE, lw=1.8)
    ax.plot([6.55 - 0.62 * 4.2, 6.55 + 0.62 * 4.2], [2.55, 2.55], color=MUTED, lw=1.0)
    for xf in (-1, 1):
        ax.plot([6.55 + 0.62 * xf] * 2, [1.95, 3.18], color=RED, lw=1.3,
                ls=(0, (4, 3)))
    ax.text(6.55 + 0.62 + 0.10, 2.98, "f = 1\n周期/像素", fontsize=8.2, color=RED,
            ha="left", va="center")
    ax.text(6.55, 1.72, "旁瓣衰减慢，但主瓣外的响应已经被压低", fontsize=8.4,
            color=MUTED, ha="center")
    ax.text(9.05, 1.95, "盒子越窄\n频域越宽\n旁瓣越慢", fontsize=9.0, color=INK,
            va="center")
    ax.text(0.40, 0.72, "为什么工程上偏爱盒式核：只要在像素内做平均，不需要真正的卷积运算 —— 这就是超采样的由来",
            fontsize=9.2, color=ORANGE)
    ax.text(0.40, 0.32, "代价：它对「周期 ≤ 1 像素」的成分只能部分削弱，不是理想的低通",
            fontsize=8.8, color=MUTED)
    save(fig, "d11-box-sinc.png")


# ---------------------------------------------------------- d12 Nyquist 三种情形
def d12():
    fig, ax = canvas(10.4, 5.6, (0, 10.4), (0, 5.6))
    cases = [
        ("信号 1/32，采样每 16 像素", "Nyquist = 1/32", 0.42, False, GREEN, "无走样"),
        ("信号 1/16，采样每 16 像素", "Nyquist = 1/32", 0.78, True, RED, "走样！"),
        ("信号 1/16，采样每 8 像素", "Nyquist = 1/16", 0.60, False, GREEN, "无走样"),
    ]
    for i, (title, nqtxt, sigfrac, alias, col, verdict) in enumerate(cases):
        y = 4.05 - i * 1.55
        ax.text(0.30, y + 0.86, title, fontsize=9.8, color=INK, fontweight="bold")
        ax.plot([1.05, 6.65], [y, y], color=MUTED, lw=1.3)
        nqx = 1.05 + 5.6 * 0.42
        ax.plot([nqx, nqx], [y - 0.30, y + 0.56], color=ORANGE, lw=1.6,
                ls=(0, (4, 3)))
        ax.text(nqx, y + 0.64, nqtxt, fontsize=8.4, color=ORANGE, ha="center")
        sx = 1.05 + 5.6 * sigfrac
        ax.plot([sx, sx], [y, y + 0.42], color=col, lw=2.6)
        ax.plot(sx, y + 0.42, "o", ms=5, color=col)
        ax.text(sx, y - 0.30, "信号", fontsize=8.0, color=col, ha="center")
        if alias:
            ax.annotate("", xy=(1.05 + 5.6 * 0.84, y - 0.62),
                        xytext=(sx, y - 0.62),
                        arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.3,
                                        connectionstyle="arc3,rad=0.30"))
            ax.text((sx + 1.05 + 5.6 * 0.84) / 2, y - 0.95, "折回到 1/32", fontsize=8.0,
                    color=RED, ha="center")
        ax.text(6.95, y + 0.10, verdict, fontsize=10, color=col, va="center",
                fontweight="bold")
        ax.text(8.55, y + 0.10, "✓" if not alias else "✗", fontsize=16, color=col,
                va="center")
    ax.text(0.30, 5.25, "判据只有一条：信号最高频率 vs Nyquist（$f_s/2$）",
            fontsize=10.4, color=INK, fontweight="bold")
    ax.text(0.30, 0.30, "超出就折回；此时唯一出路是提高采样率，或先滤掉超出的部分",
            fontsize=9.2, color=MUTED)
    save(fig, "d12-nyquist-cases.png")


# ---------------------------------------------------------- d13 超采样步骤
def d13():
    fig, ax = canvas(10.4, 3.6, (0, 10.4), (0, 3.6), x=False)
    ox, oy, w = 0.55, 0.95, 1.85
    ax.add_patch(Rectangle((ox, oy), w, w, facecolor="white", ec=INK, lw=1.5))
    ax.add_patch(plt.Polygon([[ox, oy], [ox + w, oy], [ox, oy + w * 0.78]],
                             closed=True, facecolor="#fca5a5", alpha=0.6,
                             ec="#c53030", lw=1.3))
    hit = 0
    for i in range(4):
        for j in range(4):
            cx, cy = ox + (i + 0.5) * w / 4, oy + (j + 0.5) * w / 4
            ok = (cx - ox) / w + (cy - oy) / w < 0.78
            hit += ok
            ax.plot(cx, cy, "o", ms=4.6,
                    markerfacecolor="#c53030" if ok else "white",
                    markeredgecolor="#c53030" if ok else "#9aa7b4", markeredgewidth=1.0)
    ax.text(ox + w / 2, 0.68, "① 每像素取 4×4 个子样本", fontsize=8.8, color=MUTED,
            ha="center")
    arrow(ax, (ox + w + 0.10, oy + w / 2), (2.75, oy + w / 2), color=MUTED, lw=1.4)
    box(ax, 2.90, 1.35, 1.30, 1.05, f"② 求平均\n{hit}/16", fs=10, fc="#fde8e8",
        ec="#c53030", tc="#7f1d1d")
    ax.text(3.55, 0.68, "覆盖率 → 一个值", fontsize=8.8, color=MUTED, ha="center")
    arrow(ax, (4.32, oy + w / 2), (5.05, oy + w / 2), color=MUTED, lw=1.4)

    vals = [25, 50, 75, 100, 50]
    for k, v in enumerate(vals):
        x = 5.20 + k * 0.92
        g = 1 - v / 100 * 0.78
        ax.add_patch(Rectangle((x, 1.15), 0.80, 1.15,
                               facecolor=(g, g * 0.72 + 0.06, g * 0.72 + 0.06),
                               ec="#c53030" if v < 100 else "#7f1d1d", lw=1.2))
        ax.text(x + 0.40, 1.62, f"{v}%", fontsize=8.6, color="white" if v > 55 else "#333",
                ha="center", va="center")
    ax.text(7.25, 0.68, "③ 每条边得到中间灰", fontsize=8.8, color=MUTED, ha="center")
    ax.text(0.55, 3.18, "超采样 = 用「像素内的平均值」近似「1 像素盒式滤波」",
            fontsize=10.0, color=INK, fontweight="bold")
    ax.text(0.55, 0.38, "代价：采样数 ×16。效果：边缘从 2 级灰度变成 17 级",
            fontsize=9.0, color=ORANGE)
    save(fig, "d13-supersample.png")


# ---------------------------------------------------------- d14 规则 vs 抖动
def d14():
    fig, ax = canvas(10.0, 3.5, (0, 10.0), (0, 3.5))
    rng = np.random.default_rng(3)

    def grid(x0, y0, n, jitter):
        w = 2.30
        c = w / n
        for i in range(n):
            for j in range(n):
                cx = x0 + (i + 0.5) * c
                cy = y0 + (j + 0.5) * c
                if jitter:
                    cx += (rng.random() - 0.5) * c * 0.92
                    cy += (rng.random() - 0.5) * c * 0.92
                ax.plot(cx, cy, "o", ms=2.6, color=MUTED)
        ax.add_patch(Rectangle((x0, y0), w, w, fill=False, ec=STROKE, lw=1.1))

    grid(0.40, 0.55, 7, False)
    grid(3.30, 0.55, 7, True)
    ax.text(1.55, 3.02, "规则网格", fontsize=9.8, color=INK, fontweight="bold")
    ax.text(4.45, 3.02, "抖动网格", fontsize=9.8, color=INK, fontweight="bold")
    ax.text(1.55, 0.30, "误差是「相干」的：缝隙排成可辨认的图案", fontsize=8.8,
            color=RED, ha="center")
    ax.text(4.45, 0.30, "误差变成「噪声」：不形成图案", fontsize=8.8, color=GREEN,
            ha="center")
    ax.text(6.60, 2.35, "同一个欠采样事实，\n两种呈现：", fontsize=9.4, color=INK)
    ax.text(6.60, 1.55, "规则 → 人眼认出结构性伪影（锯齿/摩尔纹）", fontsize=9.0,
            color=RED)
    ax.text(6.60, 1.10, "抖动 → 变成随机颗粒，人眼更宽容", fontsize=9.0, color=GREEN)
    ax.text(6.60, 0.55, "代价：画面有噪点感；好处：不出现假图案", fontsize=8.8,
            color=MUTED)
    save(fig, "d14-jitter.png")


# ---------------------------------------------------------- d15 采样压力测试
def d15():
    fig, ax = canvas(10.2, 3.7, (0, 10.2), (0, 3.7), x=False)
    N = 420
    lin = np.linspace(-1, 1, N)
    X, Y = np.meshgrid(lin, lin)
    R2 = X ** 2 + Y ** 2
    z = np.sin(48 * R2)
    ax.imshow(z, cmap="gray", extent=(0.35, 2.65, 0.55, 2.85), origin="lower",
              vmin=-1, vmax=1)
    ax.add_patch(Rectangle((0.35, 0.55), 2.30, 2.30, fill=False, ec=STROKE, lw=1.0))
    ax.text(1.50, 3.02, "参考：足够高的采样率", fontsize=9.6, color=INK, ha="center",
            fontweight="bold")
    ax.text(1.50, 0.30, "频率随半径增大（$\\sin(x^2+y^2)$）", fontsize=8.8, color=MUTED,
            ha="center")

    step = 7
    zz = z[::step, ::step]
    ax.imshow(zz, cmap="gray", extent=(3.55, 5.85, 0.55, 2.85), origin="lower",
              vmin=-1, vmax=1, interpolation="nearest")
    ax.add_patch(Rectangle((3.55, 0.55), 2.30, 2.30, fill=False, ec=RED, lw=1.4))
    ax.text(4.70, 3.02, "欠采样（每 7 像素取 1）", fontsize=9.6, color=RED,
            ha="center", fontweight="bold")
    ax.text(4.70, 0.30, "外圈出现成片的假圆环 = 走样", fontsize=8.8, color=RED,
            ha="center")

    ax.text(6.25, 2.45, "Zone plate 是采样的压力测试：", fontsize=9.6, color=INK)
    ax.text(6.25, 1.95, "• 中心频率低 → 任何采样率都对", fontsize=9.0, color=MUTED)
    ax.text(6.25, 1.55, "• 外圈频率高 → 必须足够密才不出假图", fontsize=9.0, color=MUTED)
    ax.text(6.25, 1.10, "假的圆环比真的圆环更醒目，\n因为它有结构 —— 人眼专挑结构", fontsize=9.0,
            color=RED)
    ax.text(6.25, 0.42, "（图由本脚本现场计算，非课件截图）", fontsize=8.2, color="#9ca3af")
    save(fig, "d15-zoneplate.png")


# ---------------------------------------------------------- d16 一维卷积手算
def d16():
    fig, ax = canvas(10.4, 3.9, (0, 10.4), (0, 3.9))
    sig = [1, 3, 5, 3, 7, 1, 3, 8, 6, 4]
    flt = [1, 2, 1]
    w, h = 0.72, 0.62

    def row(y, vals, label, highlight=None, color=INK):
        ax.text(0.28, y + h / 2, label, fontsize=9.4, color=color, va="center")
        x0 = 1.55
        for i, v in enumerate(vals):
            fc = "#fde8e8" if highlight and i in highlight else "white"
            ax.add_patch(Rectangle((x0 + i * w, y), w, h, facecolor=fc,
                                   ec=color, lw=1.2))
            ax.text(x0 + i * w + w / 2, y + h / 2, str(v), fontsize=9.6,
                    color=color, ha="center", va="center")

    row(3.05, sig, "信号", highlight={0, 1, 2}, color=INK)
    row(2.15, flt, "滤波核", color=PURPLE)
    ax.text(1.55, 1.78, "$1\\times1 + 3\\times2 + 5\\times1 = 12$", fontsize=10, color=RED)
    row(0.95, [12, 16, 18, "", "", "", "", "", "", ""], "结果", highlight={0, 1, 2},
        color=RED)
    ax.annotate("", xy=(1.55 + 1.5 * w, 2.10), xytext=(1.55 + 1.5 * w, 2.98),
                arrowprops=dict(arrowstyle="<|-|>", color=MUTED, lw=1.1))
    ax.text(1.55 + 1.5 * w + 0.12, 2.54, "对齐求和", fontsize=8.2, color=MUTED)
    ax.text(7.15, 3.05, "然后把窗往右滑一格，重复：", fontsize=9.2, color=INK)
    ax.text(7.15, 2.62, "3×1 + 5×2 + 3×1 = 16", fontsize=9.2, color=MUTED)
    ax.text(7.15, 2.24, "5×1 + 3×2 + 7×1 = 18", fontsize=9.2, color=MUTED)
    ax.text(7.15, 1.62, "核 [1,2,1] 的频域响应\n就是一条低通曲线", fontsize=9.0,
            color=PURPLE)
    ax.text(0.28, 0.35, "卷积 = 反转核、滑动、逐点乘加。核的权重要归一化（这里和为 4），否则整体亮度会变",
            fontsize=8.8, color=MUTED)
    save(fig, "d16-conv-1d.png")


if __name__ == "__main__":
    print("generating ->", OUT)
    for fn in [d01, d02, d03, d04, d05, d06, d07, d08, d09, d10,
               d11, d12, d13, d14, d15, d16]:
        fn()
    print("done: 16 diagrams")
