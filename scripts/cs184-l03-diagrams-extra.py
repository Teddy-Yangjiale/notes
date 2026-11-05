# -*- coding: utf-8 -*-
"""CS184 · L03 追加图解（d17–d20），按 v2 标准补齐到 20 张。"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Polygon, Circle

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


# ------------------------------------------------- d17 MSAA 子样本
def d17():
    fig, ax = canvas(9.8, 3.4, (0, 9.8), (0, 3.4), eq=False)
    ax.text(0.30, 3.14, "MSAA：一个像素放 4 个子样本，只在边缘处多花力气", fontsize=10.0,
            color=INK, fontweight="bold")
    # 左：1x 采样（中心一个点）
    ax.add_patch(Rectangle((0.60, 1.15), 1.10, 1.10, facecolor="white", ec=INK, lw=1.3))
    ax.plot(1.15, 1.70, "o", ms=8, color=RED, zorder=8)
    ax.text(1.15, 0.80, "1× SPP", fontsize=8.2, color=RED, ha="center")
    ax.text(1.15, 2.45, "全或无（2 级）", fontsize=7.6, color=MUTED, ha="center")

    # 中：4x MSAA
    ax.add_patch(Rectangle((2.15, 1.15), 1.10, 1.10, facecolor="white", ec=INK, lw=1.3))
    # 三角形覆盖左上角一部分
    ax.add_patch(Polygon([[2.15, 2.25], [3.25, 2.25], [2.15, 1.30]], closed=True,
                         facecolor="#e6f7f4", ec="none", alpha=0.9, zorder=2))
    for dx, dy in [(0.28, 0.28), (0.82, 0.28), (0.28, 0.82), (0.82, 0.82)]:
        ax.plot(2.15 + dx, 1.15 + dy, "o", ms=6.5, color=TEAL, zorder=8)
    ax.text(2.70, 0.80, "4× MSAA", fontsize=8.2, color=TEAL, ha="center")
    ax.text(2.70, 2.45, "5 级（0/0.25/…/1）", fontsize=7.6, color=MUTED, ha="center")

    # 右：16x
    ax.add_patch(Rectangle((3.75, 1.15), 1.10, 1.10, facecolor="white", ec=INK, lw=1.3))
    ax.add_patch(Polygon([[3.75, 2.25], [4.85, 2.25], [3.75, 1.30]], closed=True,
                         facecolor="#fff7ed", ec="none", alpha=0.9, zorder=2))
    for i in range(4):
        for j in range(4):
            ax.plot(3.75 + 0.14 + i * 0.275, 1.15 + 0.14 + j * 0.275, "o", ms=3.4,
                    color=ORANGE, zorder=8)
    ax.text(4.30, 0.80, "16× MSAA", fontsize=8.2, color=ORANGE, ha="center")
    ax.text(4.30, 2.45, "17 级", fontsize=7.6, color=MUTED, ha="center")

    ax.text(5.55, 2.55, "关键：MSAA 只解决「几何边缘」", fontsize=8.4, color=INK)
    ax.text(5.55, 2.22, "• 每个子样本有自己的覆盖位", fontsize=7.4, color=MUTED)
    ax.text(5.55, 1.95, "• 但着色可能只算一次（复用）", fontsize=7.4, color=MUTED)
    ax.text(5.55, 1.68, "• 所以比 SSAA 便宜得多", fontsize=7.4, color=MUTED)
    ax.text(5.55, 1.25, "解决不了：纹理走样、着色走样", fontsize=7.6, color=RED)
    ax.text(5.55, 0.95, "（那些要靠 mipmap 和更高频着色）", fontsize=7.4, color=MUTED)
    box(ax, 8.05, 1.15, 1.45, 0.85, "代价\n显存 ×N\n带宽 ×N", fs=7.0, fc="#fff7ed",
        ec=ORANGE, tc="#7c3a00")
    save(fig, "d17-msaa.png")


# ------------------------------------------------- d18 抖动模式
def d18():
    fig, ax = canvas(9.8, 3.2, (0, 9.8), (0, 3.2), eq=False)
    ax.text(0.30, 2.94, "抖动：把「规则走样」变成「随机噪声」—— 眼睛更容忍后者", fontsize=10.0,
            color=INK, fontweight="bold")
    rng = np.random.default_rng(7)
    # 规则网格
    ax.text(1.35, 2.62, "规则采样", fontsize=8.4, color=MUTED, ha="center")
    for i in range(8):
        for j in range(8):
            ax.plot(0.55 + i * 0.22, 0.85 + j * 0.19, "o", ms=2.6, color=TEAL)
    ax.text(1.35, 0.55, "→ 出现规则的摩尔纹", fontsize=7.4, color=RED, ha="center")

    # 白噪声
    ax.text(3.85, 2.62, "白噪声抖动", fontsize=8.4, color=MUTED, ha="center")
    for i in range(8):
        for j in range(8):
            ax.plot(3.05 + i * 0.22 + rng.uniform(-0.07, 0.07),
                    0.85 + j * 0.19 + rng.uniform(-0.06, 0.06), "o", ms=2.6, color=ORANGE)
    ax.text(3.85, 0.55, "→ 噪声，但结成团", fontsize=7.4, color=ORANGE, ha="center")

    # 蓝噪声（用分层抖动近似）
    ax.text(6.35, 2.62, "蓝噪声抖动", fontsize=8.4, color=MUTED, ha="center")
    for i in range(8):
        for j in range(8):
            ax.plot(5.55 + i * 0.22 + rng.uniform(-0.08, 0.08),
                    0.85 + j * 0.19 + rng.uniform(-0.07, 0.07), "o", ms=2.6, color=PURPLE)
    ax.text(6.35, 0.55, "→ 噪声均匀，视觉最舒服", fontsize=7.4, color=GREEN, ha="center")

    ax.text(7.85, 2.45, "为什么抖动有效：", fontsize=8.0, color=INK)
    ax.text(7.85, 2.15, "走样是「相干」的", fontsize=7.4, color=RED)
    ax.text(7.85, 1.90, "（条纹、摩尔纹）", fontsize=7.4, color=MUTED)
    ax.text(7.85, 1.60, "噪声是「不相干」的", fontsize=7.4, color=GREEN)
    ax.text(7.85, 1.35, "（人眼会自动平均掉）", fontsize=7.4, color=MUTED)
    ax.text(7.85, 0.95, "所以 TAA/光追降噪", fontsize=7.4, color=TEAL)
    ax.text(7.85, 0.72, "都靠抖动 + 累积", fontsize=7.4, color=TEAL)
    save(fig, "d18-dither.png")


# ------------------------------------------------- d19 重建核对比
def d19():
    fig, ax = canvas(9.8, 3.4, (0, 9.8), (0, 3.4), eq=False)
    ax.text(0.30, 3.14, "四种重建核：从「最近邻」到「理想 sinc」，越往后越贵也越准", fontsize=9.6,
            color=INK, fontweight="bold")
    x = np.linspace(-3, 3, 600)
    kernels = [("box（最近邻）", np.where(np.abs(x) < 0.5, 1.0, 0.0), RED),
               ("tent（双线性）", np.clip(1 - np.abs(x), 0, None), ORANGE),
               ("Gaussian", np.exp(-2 * x ** 2), TEAL),
               ("sinc（理想）", np.sinc(x), PURPLE)]
    for k, (name, y, c) in enumerate(kernels):
        ox = 0.55 + k * 2.35
        ax.plot(ox + 1.05 + x * 0.30, 1.35 + 0.85 * y, color=c, lw=1.6)
        ax.plot([ox, ox + 2.10], [1.35, 1.35], color="#e5e7eb", lw=0.8)
        ax.text(ox + 1.05, 0.98, name, fontsize=7.4, color=c, ha="center")
    ax.text(0.30, 0.62, "「宽」= 更模糊（滤得狠）　「窄」= 更锐（但可能走样）　"
                        "「有负瓣」= 会振铃（ringing）", fontsize=7.6, color=MUTED)
    ax.text(0.30, 0.34, "实践：双线性（tent）是性价比最高的；sinc 无限宽不可实现，"
                        "所以真实系统用近似（Lanczos、bicubic）", fontsize=7.6, color=INK)
    ax.text(0.30, 0.08, "注意 sinc 的负瓣：它在频域是完美矩形（理想低通），但在空域会「过冲」—— 这就是振铃",
            fontsize=7.4, color=PURPLE)
    save(fig, "d19-reconstruction-kernels.png")


# ------------------------------------------------- d20 伪影分类
def d20():
    fig, ax = canvas(9.8, 3.2, (0, 9.8), (0, 3.2), eq=False)
    ax.text(0.30, 2.94, "三种采样伪影：成因不同，修法也不同", fontsize=10.0, color=INK,
            fontweight="bold")
    cols = [("锯齿 / 阶梯", "几何边缘只采 1 点\n→ 覆盖率只有 0/1", "MSAA / SSAA\n（几何抗锯齿）", RED),
            ("摩尔纹", "高频纹理欠采样\n→ 折叠成低频", "mipmap / 各向异性\n（纹理抗锯齿）", ORANGE),
            ("闪烁 / 噪点", "时间上采样点乱跳\n→ 帧间不一致", "TAA / 抖动累积\n（时间抗锯齿）", PURPLE)]
    for k, (name, cause, fix, c) in enumerate(cols):
        ox = 0.55 + k * 3.15
        ax.add_patch(Rectangle((ox, 1.50), 2.85, 1.05, facecolor="white", ec=c, lw=1.3))
        ax.text(ox + 1.42, 2.25, name, fontsize=8.6, color=c, ha="center", fontweight="bold")
        ax.text(ox + 1.42, 1.92, cause, fontsize=7.0, color=MUTED, ha="center",
                linespacing=1.5, va="top")
        ax.text(ox + 1.42, 1.22, "修法：" + fix, fontsize=7.0, color=TEAL, ha="center",
                linespacing=1.5, va="top")
    ax.text(0.30, 0.55, "共同点：都是「采样率不够」，只是发生在三个不同的维度 —— "
                        "空间（几何）、空间（纹理）、时间。", fontsize=7.8, color=INK)
    ax.text(0.30, 0.28, "所以「先滤后采」这条原则对三者都成立，只是滤的对象不同。", fontsize=7.8,
            color=MUTED)
    save(fig, "d20-artifact-taxonomy.png")


if __name__ == "__main__":
    print("generating ->", OUT)
    for fn in [d17, d18, d19, d20]:
        fn()
    print("done: 4 extra diagrams")
