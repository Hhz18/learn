# -*- coding: utf-8 -*-
"""
海南橡胶（601118）· 股本与股东 图表生成脚本
=============================================

根据 05_股本与股东 目录下的图表数据源，用 matplotlib 重新绘制 2 张静态图表：

1. 股本数量（总股本，亿股） 2009—2025     柱状图
2. 股东人数（股东户数，万户） 2018—2025    折线图

运行：
    python 生成图表.py
输出：本目录下的 2 张 PNG 图片。
"""

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import math
import os

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "SimSun"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.family"] = "sans-serif"

# 配色（与源 HTML 浅色主题一致）
SERIES_CAP       = "#2a78d6"   # 蓝 —— 股本数量
SERIES_CAP_SOFT  = "#cde2fb"   # 蓝浅 —— 上市前
SERIES_HOLD      = "#eb6834"   # 橙 —— 股东人数
SERIES_HOLD_SOFT = "#fbdccb"
CRIT             = "#d03b3b"   # 事件/步骤标注
GRID             = "#e1e0d9"
BASELINE         = "#c3c2b7"
INK_1            = "#0b0b0b"
INK_2            = "#52514e"
INK_3            = "#898781"

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------
# 数据（取自源 HTML <script> 数据块）
# ---------------------------------------------------------------------------
# 股本数量（亿股）年度快照
CAP = [
    {"y": 2009, "v": 31.45, "note": "上市前"},
    {"y": 2010, "v": 31.45, "note": "上市前"},
    {"y": 2011, "v": 39.31, "note": "IPO 发行", "flag": "IPO"},
    {"y": 2012, "v": 39.31},
    {"y": 2013, "v": 39.31},
    {"y": 2014, "v": 39.31},
    {"y": 2015, "v": 39.31},
    {"y": 2016, "v": 39.31},
    {"y": 2017, "v": 39.31},
    {"y": 2018, "v": 42.79, "note": "定向增发", "flag": "定增"},
    {"y": 2019, "v": 42.79},
    {"y": 2020, "v": 42.79},
    {"y": 2021, "v": 42.79},
    {"y": 2022, "v": 42.79},
    {"y": 2023, "v": 42.79},
    {"y": 2024, "v": 42.79},
    {"y": 2025, "v": 42.79},
]

# 股东户数：t = 十进制年份，v = 万户，gap 表示与上一点之间为缺口
HOLD = [
    {"t": 2018.75, "label": "2018-09", "v": 9.17, "hu": "约 91,700"},
    {"t": 2021.75, "label": "2021-09", "v": 10.41, "hu": "104,104", "gap": True},
    {"t": 2021.95, "label": "2021 末", "v": 10.77, "hu": "约 107,718"},
    {"t": 2022.20, "label": "2022-Q1", "v": 10.39, "hu": "103,871"},
    {"t": 2022.45, "label": "2022-06", "v": 10.20, "hu": "101,950"},
    {"t": 2022.70, "label": "2022-09", "v": 9.76, "hu": "97,554"},
    {"t": 2023.20, "label": "2023-03", "v": 9.68, "hu": "约 96,800"},
    {"t": 2023.45, "label": "2023-06", "v": 9.93, "hu": "约 99,300"},
    {"t": 2023.70, "label": "2023-09", "v": 9.57, "hu": "约 95,676"},
    {"t": 2023.95, "label": "2023-12", "v": 9.48, "hu": "约 94,815"},
    {"t": 2024.20, "label": "2024-03", "v": 9.23, "hu": "约 92,326"},
    {"t": 2024.45, "label": "2024-06", "v": 8.86, "hu": "约 88,570"},
    {"t": 2024.70, "label": "2024-09", "v": 8.10, "hu": "80,959"},
    {"t": 2025.20, "label": "2025-03", "v": 8.24, "hu": "约 82,400"},
    {"t": 2025.53, "label": "2025-07", "v": 8.30, "hu": "约 83,000"},
]


def style_axis(ax, y_ticks, fmt_y):
    """统一坐标轴风格：隐藏上/右/左边框、浅网格、底部基线。"""
    ax.set_yticks(y_ticks)
    ax.set_yticklabels([fmt_y(v) for v in y_ticks], fontsize=10, color=INK_2)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(BASELINE)
    ax.grid(axis="y", color=GRID, linewidth=1)
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", length=0)


# ---------------------------------------------------------------------------
# 图 1：股本数量柱状图
# ---------------------------------------------------------------------------
def draw_cap():
    years = [d["y"] for d in CAP]
    n = len(years)
    fig, ax = plt.subplots(figsize=(12.5, 5.6))
    fig.subplots_adjust(left=0.07, right=0.97, top=0.84, bottom=0.13)

    y_ticks = [0, 10, 20, 30, 40]
    style_axis(ax, y_ticks, lambda v: f"{v}")
    ax.set_ylim(0, 45)
    ax.set_xlim(-0.6, n - 0.4)

    for i, d in enumerate(CAP):
        soft = d["y"] < 2011
        color = SERIES_CAP_SOFT if soft else SERIES_CAP
        ax.bar(i, d["v"], width=0.62, color=color, zorder=3)
        if d.get("flag"):
            ax.text(i, d["v"] + 0.8, f"{d['v']:.2f}", ha="center", va="bottom",
                    fontsize=10.5, color=INK_1, fontweight="bold", zorder=5)
            ax.text(i, d["v"] - 3.2, d["flag"], ha="center", va="bottom",
                    fontsize=10.5, color=CRIT, fontweight="bold", zorder=5)

    # x 刻度：每 2 年 + 首尾
    tick_idx = [i for i, d in enumerate(CAP) if d["y"] % 2 == 1 or i == 0 or i == n - 1]
    ax.set_xticks(tick_idx)
    ax.set_xticklabels(["'" + str(years[i])[2:] for i in tick_idx],
                       fontsize=9.5, color=INK_2)

    ax.set_ylabel("亿股", fontsize=11, color=INK_2)
    ax.set_title("海南橡胶 · 股本数量（总股本，亿股）", fontsize=15, color=INK_1,
                 fontweight="bold", loc="left", pad=26)
    ax.text(0, 1.055, "两次扩股：2011 年 IPO 与 2018 年定增；其余年份保持不变。\n浅色为上市前（2009—2010）",
            transform=ax.transAxes, fontsize=10, color=INK_2, va="top")

    path = os.path.join(OUT_DIR, "股本数量_2009-2025.png")
    fig.savefig(path, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"已生成：{path}")


# ---------------------------------------------------------------------------
# 图 2：股东人数折线图
# ---------------------------------------------------------------------------
def draw_hold():
    x_min, x_max = 2018.5, 2025.7
    y_min, y_max = 7.5, 11.0

    fig, ax = plt.subplots(figsize=(12.5, 5.6))
    fig.subplots_adjust(left=0.07, right=0.96, top=0.84, bottom=0.13)

    y_ticks = [8, 9, 10, 11]
    style_axis(ax, y_ticks, lambda v: f"{v}")
    ax.set_ylim(y_min, y_max)
    ax.set_xlim(x_min, x_max)

    # 折线分段（缺口段用虚线）
    for i in range(1, len(HOLD)):
        a, b = HOLD[i - 1], HOLD[i]
        ls = (0, (4, 5)) if b.get("gap") else "-"
        ax.plot([a["t"], b["t"]], [a["v"], b["v"]], color=SERIES_HOLD,
                linewidth=2, linestyle=ls, solid_capstyle="round", zorder=3)

    # 数据点 + 峰值/低点标注
    for d in HOLD:
        ax.scatter(d["t"], d["v"], s=42, facecolor=SERIES_HOLD, edgecolor="white",
                   linewidth=2, zorder=4)
        if d["v"] == 10.77:
            ax.text(d["t"], d["v"] - 0.28, "10.77", ha="center", va="top",
                    fontsize=10.5, color=INK_1, fontweight="bold", zorder=5)
        elif d["v"] == 8.10:
            ax.text(d["t"], d["v"] + 0.28, "8.10", ha="center", va="bottom",
                    fontsize=10.5, color=INK_1, fontweight="bold", zorder=5)

    # x 年份刻度
    x_year_ticks = list(range(2019, 2026))
    ax.set_xticks(x_year_ticks)
    ax.set_xticklabels([str(y) for y in x_year_ticks], fontsize=9.5, color=INK_2)

    ax.set_ylabel("万户", fontsize=11, color=INK_2)
    ax.set_title("海南橡胶 · 股东人数（股东户数，万户）", fontsize=15, color=INK_1,
                 fontweight="bold", loc="left", pad=26)
    ax.text(0, 1.055,
            "上市初期公开数据分散，自 2018 年起按披露报告期绘制。\n虚线段（2018→2021）代表期间缺少可核对数据，非真实连续走势。",
            transform=ax.transAxes, fontsize=10, color=INK_2, va="top")

    path = os.path.join(OUT_DIR, "股东人数_2018-2025.png")
    fig.savefig(path, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"已生成：{path}")


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    draw_cap()
    draw_hold()
    print("\n全部完成。")
