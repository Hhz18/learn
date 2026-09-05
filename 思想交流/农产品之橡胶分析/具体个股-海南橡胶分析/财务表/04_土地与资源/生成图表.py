# -*- coding: utf-8 -*-
"""
海南橡胶（601118）· 土地与资源 图表生成脚本
=============================================

根据 04_土地与资源 目录下的两个图表数据源，用 matplotlib 重新绘制 4 张静态图表：

1. 橡胶种植面积（2009—2025）        柱状图  ← 16-17_种植面积与土地面积_图表.html
2. 总土地面积（2009—2025）          柱状图  ← 16-17_种植面积与土地面积_图表.html
3. 土地承包费历年金额（2009—2025）   柱状图  ← 土地承包费_图表.html
4. 土地承包费占收入比               折线图  ← 土地承包费_图表.html

运行：
    python 生成图表.py
输出：本目录下的 4 张 PNG 图片。
"""

import matplotlib
matplotlib.use("Agg")  # 无窗口环境，直接导出图片

import matplotlib.pyplot as plt
import math
import os

# ---------------------------------------------------------------------------
# 中文字体设置（Windows 下优先微软雅黑 / 黑体）
# ---------------------------------------------------------------------------
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "SimSun"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.family"] = "sans-serif"

# ---------------------------------------------------------------------------
# 配色（与源 HTML 的浅色主题保持一致）
# ---------------------------------------------------------------------------
SERIES_1       = "#2a78d6"   # 蓝（橡胶种植面积 / 土地承包费）
SERIES_1_SOFT  = "#d7e5f7"   # 蓝浅色填充（协议金额）
SERIES_2       = "#eb6834"   # 橙（总土地面积）
SERIES_2_SOFT  = "#fadcd0"   # 橙浅色填充
EVENT_RED      = "#d03b3b"   # 事件标注
GRID           = "#e1e0d9"   # 网格线
BASELINE       = "#c3c2b7"   # 底部基线
GAP_COLOR      = "#c3c2b7"   # 缺口占位描边
GAP_FILL       = "#ecebe5"   # 缺口占位填充
INK_1          = "#0b0b0b"   # 主文字
INK_2          = "#52514e"   # 次级文字
INK_3          = "#898781"   # 浅文字

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------
# 数据（取自两个源 HTML 的 <script> 数据块）
# ---------------------------------------------------------------------------
# ① 橡胶种植面积（万亩）。v=None 表示当年无数据点
RUBBER = [
    {"y": 2009, "v": 328, "domestic": 328, "overseas": 0},
    {"y": 2010, "v": 328, "domestic": 328, "overseas": 0},
    {"y": 2011, "v": None}, {"y": 2012, "v": None}, {"y": 2013, "v": None},
    {"y": 2014, "v": None}, {"y": 2015, "v": None},
    {"y": 2016, "v": 328, "domestic": 328, "overseas": 0},
    {"y": 2017, "v": 328, "domestic": 328, "overseas": 0, "event": "控股股东收购 KM/ART"},
    {"y": 2018, "v": None},
    {"y": 2019, "v": 316, "domestic": 316, "overseas": 0},
    {"y": 2020, "v": 316, "domestic": 316, "overseas": 0},
    {"y": 2021, "v": 316, "domestic": 316, "overseas": 0},
    {"y": 2022, "v": 316, "domestic": 316, "overseas": 0},
    {"y": 2023, "v": 400, "domestic": 341, "overseas": 60, "event": "合并合盛农业（+164 万亩）"},
    {"y": 2024, "v": 369, "domestic": 310, "overseas": 60, "event": "台风“摩羯” -23 万亩"},
    {"y": 2025, "v": 400, "domestic": 341, "overseas": 60, "event": "合盛农业整合完成，最新披露"},
]

# ② 总土地面积（万亩）
LAND = [
    {"y": 2009, "v": 353.20},
    {"y": 2010, "v": 351.55},
    {"y": 2011, "v": None}, {"y": 2012, "v": None}, {"y": 2013, "v": None},
    {"y": 2014, "v": None}, {"y": 2015, "v": None},
    {"y": 2016, "v": 353},
    {"y": 2017, "v": 353, "event": "控股股东收购 KM/ART"},
    {"y": 2018, "v": 353},
    {"y": 2019, "v": 341}, {"y": 2020, "v": 341},
    {"y": 2021, "v": 341}, {"y": 2022, "v": 341},
    {"y": 2023, "v": 500, "event": "合并合盛农业（+160 万亩海外）"},
    {"y": 2024, "v": 477, "event": "台风“摩羯” -23 万亩"},
    {"y": 2025, "v": 490},
]

# ③ 土地承包费（万元）。is_protocol 表示 2010 协议金额
FEE = [
    {"y": 2009, "v": None, "note": "上市前"},
    {"y": 2010, "v": 21470.51, "note": "《补充协议》金额 · 351.55 万亩", "is_protocol": True},
    {"y": 2011, "v": None}, {"y": 2012, "v": None}, {"y": 2013, "v": None},
    {"y": 2014, "v": None}, {"y": 2015, "v": None}, {"y": 2016, "v": None},
    {"y": 2017, "v": None}, {"y": 2018, "v": None}, {"y": 2019, "v": None},
    {"y": 2020, "v": None}, {"y": 2021, "v": None}, {"y": 2022, "v": None},
    {"y": 2023, "v": 19745.05, "note": "年报披露"},
    {"y": 2024, "v": 19745.05, "note": "2025 年报披露"},
    {"y": 2025, "v": 19716.68, "note": "2025 年报披露"},
]

# ④ 占收入比测算：营业收入（亿元）
REVENUE = {2010: 63.42, 2023: 376.87, 2024: 496.73, 2025: 422.37}


def nice_tick(rough):
    """按 1/2/5 取整刻度，返回步长。"""
    import math
    exp = 10 ** math.floor(math.log10(rough))
    f = rough / exp
    if f < 1.5:
        nice = 1
    elif f < 3:
        nice = 2
    elif f < 7:
        nice = 5
    else:
        nice = 10
    return nice * exp


def nice_y_max(vals, pad=1.18):
    """根据数据最大值求一个取整的 y 轴上限。"""
    y_max = max(vals) * pad
    step = nice_tick(y_max / 5)
    return int(math.ceil(y_max / step) * step)


def style_axis(ax, y_max, y_ticks, fmt_y):
    """统一坐标轴风格：隐藏边框、浅网格、底部基线。"""
    ax.set_ylim(0, y_max)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels([fmt_y(v) for v in y_ticks], fontsize=10, color=INK_2)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(BASELINE)
    ax.grid(axis="y", color=GRID, linewidth=1)
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", length=0)


# ---------------------------------------------------------------------------
# 图 1 / 图 2：柱状图（含缺口占位 + 事件竖线）
# ---------------------------------------------------------------------------
def draw_bar_chart(data, color, soft_color, title, subtitle, ylabel,
                   out_name, fmt_value, event_color=EVENT_RED):
    years = [d["y"] for d in data]
    vals = [d["v"] for d in data if d["v"] is not None]
    y_max = nice_y_max(vals)
    step = nice_tick(y_max / 5)
    y_ticks = [step * i for i in range(6)]

    fig, ax = plt.subplots(figsize=(12.5, 5.6))
    fig.subplots_adjust(left=0.07, right=0.97, top=0.84, bottom=0.13)

    style_axis(ax, y_max, y_ticks, lambda v: f"{v:g}")
    ax.set_xlim(-0.6, len(years) - 0.4)

    n = len(years)
    gap_h = y_max * 0.92

    for i, d in enumerate(data):
        x = i
        # 事件竖线（先画，置于底层）
        if d.get("event"):
            ax.axvline(x, color=event_color, linewidth=1.2, linestyle=(0, (4, 4)),
                       alpha=0.55, zorder=1)
            ax.text(x, y_max * 1.045, "★ " + d["event"], ha="center", va="bottom",
                    fontsize=9, color=event_color, fontweight="bold", zorder=5)

        if d["v"] is None:
            # 缺口占位：浅色虚线框
            ax.bar(x, gap_h, width=0.55, color=GAP_FILL, edgecolor=GAP_COLOR,
                   linewidth=1, linestyle=(0, (3, 3)), zorder=2)
            continue

        ax.bar(x, d["v"], width=0.55, color=color, zorder=3)
        # 数值标签
        ax.text(x, d["v"] + y_max * 0.015, fmt_value(d["v"]), ha="center",
                va="bottom", fontsize=10, color=INK_1, fontweight="bold", zorder=4)

    # 年份标签
    ax.set_xticks(range(n))
    ax.set_xticklabels([str(y) for y in years], fontsize=9.5, color=INK_2)

    ax.set_ylabel(ylabel, fontsize=11, color=INK_2)
    ax.set_title(title, fontsize=15, color=INK_1, fontweight="bold",
                 loc="left", pad=26)
    ax.text(0, 1.055, subtitle, transform=ax.transAxes, fontsize=10, color=INK_2)

    path = os.path.join(OUT_DIR, out_name)
    fig.savefig(path, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"已生成：{path}")


# ---------------------------------------------------------------------------
# 图 3：土地承包费柱状图
# ---------------------------------------------------------------------------
def draw_fee_chart():
    data = FEE
    years = [d["y"] for d in data]
    y_max = 25000
    step = 5000
    y_ticks = [step * i for i in range(6)]

    fig, ax = plt.subplots(figsize=(12.5, 5.6))
    fig.subplots_adjust(left=0.08, right=0.97, top=0.84, bottom=0.13)

    style_axis(ax, y_max, y_ticks, lambda v: f"{v / 10000:.2f}")
    ax.set_xlim(-0.6, len(years) - 0.4)

    n = len(years)
    gap_h = y_max * 0.92

    for i, d in enumerate(data):
        x = i
        if d["v"] is None:
            ax.bar(x, gap_h, width=0.62, color=GAP_FILL, edgecolor=GAP_COLOR,
                   linewidth=1, linestyle=(0, (3, 3)), zorder=2)
            continue

        if d.get("is_protocol"):
            ax.bar(x, d["v"], width=0.62, color=SERIES_1_SOFT, edgecolor=SERIES_1,
                   linewidth=2, linestyle=(0, (4, 3)), zorder=3)
            # 《补充协议》标注 + 箭头
            ax.text(x, d["v"] + y_max * 0.055, "《补充协议》", ha="center",
                    va="bottom", fontsize=10, color=SERIES_1, fontweight="bold",
                    zorder=5)
            ax.annotate("", xy=(x, d["v"] + y_max * 0.022),
                        xytext=(x, d["v"] + y_max * 0.048),
                        arrowprops=dict(arrowstyle="-", color=SERIES_1,
                                        linestyle=(0, (2, 2)), linewidth=1))
        else:
            ax.bar(x, d["v"], width=0.62, color=SERIES_1, zorder=3)

        ax.text(x, d["v"] + y_max * 0.015, f"{d['v'] / 10000:.2f}", ha="center",
                va="bottom", fontsize=10, color=INK_1, fontweight="bold", zorder=4)

    ax.set_xticks(range(n))
    ax.set_xticklabels([str(y) for y in years], fontsize=9.5, color=INK_2)
    ax.set_ylabel("土地承包费（亿元）", fontsize=11, color=INK_2)
    ax.set_title("海南橡胶 · 土地承包费历年金额（2009—2025）", fontsize=15,
                 color=INK_1, fontweight="bold", loc="left", pad=26)
    ax.text(0, 1.055, "单位：万元 · 柱状图。2010 为协议金额；2023/24/25 为年报披露；中间年份未单独披露",
            transform=ax.transAxes, fontsize=10, color=INK_2)

    path = os.path.join(OUT_DIR, "土地承包费_2009-2025.png")
    fig.savefig(path, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"已生成：{path}")


# ---------------------------------------------------------------------------
# 图 4：土地承包费占收入比折线图
# ---------------------------------------------------------------------------
def draw_ratio_chart():
    ratio_years = [2010, 2023, 2024, 2025]
    ratios = []
    for y in ratio_years:
        fee = next(d["v"] for d in FEE if d["y"] == y)
        ratio = (fee / 10000) / REVENUE[y] * 100
        ratios.append(ratio)

    y_max = 4.0
    y_ticks = [0.0, 1.0, 2.0, 3.0, 4.0]

    fig, ax = plt.subplots(figsize=(7.2, 5.6))
    fig.subplots_adjust(left=0.12, right=0.95, top=0.84, bottom=0.13)

    ax.set_ylim(0, y_max)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels([f"{v:.1f}%" for v in y_ticks], fontsize=10, color=INK_2)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(BASELINE)
    ax.grid(axis="y", color=GRID, linewidth=1)
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", length=0)
    ax.set_xlim(-0.25, len(ratios) - 0.75)

    xs = range(len(ratios))
    ax.plot(xs, ratios, color=SERIES_1, linewidth=2.5, zorder=3,
            solid_capstyle="round")

    for x, y, ratio, yr in zip(xs, ratios, ratios, ratio_years):
        ax.scatter(x, y, s=42, facecolor="white", edgecolor=SERIES_1,
                   linewidth=2.5, zorder=4)
        ax.text(x, y + 0.12, f"{ratio:.2f}%", ha="center", va="bottom",
                fontsize=10, color=INK_1, fontweight="bold", zorder=5)

    ax.set_xticks(list(xs))
    ax.set_xticklabels([str(y) for y in ratio_years], fontsize=10, color=INK_2)
    ax.set_ylabel("占收入比 (%)", fontsize=11, color=INK_2)
    ax.set_title("海南橡胶 · 土地承包费占收入比", fontsize=15, color=INK_1,
                 fontweight="bold", loc="left", pad=26)
    ax.text(0, 1.055, "结构变化：贸易/加工业务规模化后，刚性费用被稀释",
            transform=ax.transAxes, fontsize=10, color=INK_2)

    path = os.path.join(OUT_DIR, "土地承包费占收入比.png")
    fig.savefig(path, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"已生成：{path}")


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # 图 1：橡胶种植面积
    draw_bar_chart(
        data=RUBBER, color=SERIES_1, soft_color=SERIES_1_SOFT,
        title="① 橡胶种植面积（境内外合计）",
        subtitle="单位：万亩 · 2009—2022 仅境内；2023 起含合盛农业海外",
        ylabel="万亩",
        out_name="橡胶种植面积_2009-2025.png",
        fmt_value=lambda v: f"{v:.0f}",
    )

    # 图 2：总土地面积
    draw_bar_chart(
        data=LAND, color=SERIES_2, soft_color=SERIES_2_SOFT,
        title="② 总土地面积（含海外）",
        subtitle="单位：万亩 · 境内承包 + 海外经营土地",
        ylabel="万亩",
        out_name="总土地面积_2009-2025.png",
        fmt_value=lambda v: f"{v:.1f}".rstrip("0").rstrip("."),
    )

    # 图 3：土地承包费
    draw_fee_chart()

    # 图 4：占收入比
    draw_ratio_chart()

    print("\n全部完成。")
