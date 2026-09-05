# -*- coding: utf-8 -*-
"""
海南橡胶 (601118) 2009—2025 利润表数据可视化
====================================================

读取 *海南橡胶利润表.xlsx*（覆盖 2009—2025 年共 17 个会计年度），生成 5 张折线图：

1. 营业总收入 vs 营业总成本
2. 净利润
3. 扣非后归母净利润
4. 归属于母公司股东的净利润
5. 净利润 / 扣非后归母净利润 / 归母净利润 三线对比

设计原则（参考 dataviz skill）：
- 时间序列 -> 折线图（2px 描边、圆角接/帽）
- 数据点 -> 8px 圆形标记 + 2px 表面色描边圈
- 配色 -> 调色盘 slot-1/2/3（蓝/橙/青），已通过色觉安全校验
- 网格 -> 1px 极细实线，发丝灰
- 标签 -> 仅在端点处直接标注，避免「每点贴数字」的视觉噪声
- 单位 -> 亿元；负值绘制在 0 轴下方

执行：python 海南橡胶利润表图表.py
"""

from __future__ import annotations

import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import rcParams

# ---------- 路径 ----------
HERE = Path(__file__).resolve().parent
SRC = HERE / "海南橡胶利润表.xlsx"

# ---------- 调色盘（dataviz skill 已校验） ----------
SURFACE = "#fcfcfb"     # 图表底色
PAGE = "#f9f9f7"        # 卡片/页面底
INK_PRIMARY = "#0b0b0b"  # 主文字
INK_SECONDARY = "#52514e"  # 次文字
INK_MUTED = "#898781"   # 轴/标签
GRID = "#e1e0d9"        # 发丝网格
AXIS = "#c3c2b7"        # 轴线
CALLOUT = "#9a9892"     # 引线/注释灰

# categorical slot-1/2/3（相邻 ΔE ≥ 8，已通过 CVD 校验）
C1 = "#2a78d6"  # 蓝
C2 = "#eb6834"  # 橙
C3 = "#1baf7a"  # 青

# ---------- 经营现金流数据（2008—2025，单位：亿元） ----------
CASH_FLOW: dict[int, float] = {
    2008: 4.513,
    2009: 4.142,
    2010: -1.514,
    2011: 8.823,
    2012: -4.632,
    2013: 3.501,
    2014: -0.1705,
    2015: -2.379,
    2016: 5.364,
    2017: -0.7937,
    2018: 7.491,
    2019: 9.244,
    2020: 4.695,
    2021: 2.662,
    2022: 12.248,
    2023: 12.049,
    2024: 15.553,
    2025: 25.048,
}

# ---------- 资产负债表数据（2009—2025，单位：亿元） ----------
# 来源：[资产负债表.md](资产负债表.md)，已与 07_负债.md 四张分段表交叉校验
BS_YEARS = list(range(2009, 2026))

TOTAL_ASSETS = [65.13, 125.32, 111.33, 111.24, 120.17, 122.68, 128.92, 134.84,
                131.68, 162.61, 166.87, 177.28, 193.92, 223.29, 339.50, 360.70, 338.34]
TOTAL_LIABILITIES = [29.44, 42.14, 19.30, 19.29, 28.09, 31.66, 47.65, 55.31,
                     54.50, 60.12, 68.76, 78.38, 96.88, 126.37, 223.16, 247.71, 237.82]
TOTAL_EQUITY = [35.68, 83.18, 92.03, 91.94, 92.09, 91.02, 81.27, 79.53,
                77.18, 102.49, 98.10, 98.90, 97.04, 96.92, 116.34, 112.98, 100.52]
CURRENT_ASSETS = [16.73, 74.13, 55.16, 51.30, 54.82, 51.80, 53.63, 52.57,
                  44.18, 72.48, 67.65, 69.25, 63.34, 91.26, 128.72, 154.66, 133.90]
NONCURRENT_ASSETS = [48.39, 51.19, 56.16, 59.93, 65.36, 70.87, 75.28, 82.26,
                     87.51, 90.14, 99.22, 108.02, 130.58, 132.03, 210.79, 206.04, 204.44]
FIXED_ASSETS = [6.86, 7.43, 10.71, 11.29, 14.96, 15.68, 15.54, 16.21,
                16.43, 16.23, 18.03, 20.72, 22.56, 27.50, 38.81, 37.00, 38.43]
CURRENT_LIABILITIES = [23.15, 34.32, 16.49, 16.56, 25.36, 29.52, 30.44, 36.04,
                       47.98, 46.02, 59.24, 38.45, 51.97, 63.28, 144.61, 151.93, 145.03]
NONCURRENT_LIABILITIES = [6.29, 7.82, 2.81, 2.73, 2.73, 2.14, 17.21, 19.26,
                          6.51, 14.10, 9.52, 39.93, 44.91, 63.08, 78.55, 95.78, 92.79]

# ---------- 利润与净利润数据（2009—2025 升序，单位：亿元） ----------
# 来源：[利润表.md](利润表.md)「三、利润与净利润」，已与年报核对，为验证无误口径。
# 直接硬编码以避免依赖 Excel 列对齐/表头解析，确保图表与校验后的 markdown 完全一致。
NET_PROFIT = [2.83, 5.77, 7.63, 3.05, 1.62, 0.29, -9.83, 0.64, -2.77,
              2.32, 1.16, 0.66, 1.34, 0.46, 1.11, -0.86, -3.13]           # 净利润
PARENT_PROFIT = [2.86, 5.73, 7.61, 2.97, 1.56, 0.22, -9.90, 0.61, -2.64,
                 2.35, 1.35, 0.71, 1.51, 0.76, 2.97, 1.03, -1.03]         # 归属于母公司股东的净利润
NONRECUR_PROFIT = [2.68, 5.97, 8.45, 2.37, -3.04, -3.53, -12.70, -5.16, -7.37,
                   -6.80, -1.07, -0.89, -2.33, -6.33, -9.69, -6.15, -9.75]  # 扣非后归母净利润

# ---------- 全局 matplotlib 风格 ----------
rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": [
        "Microsoft YaHei", "PingFang SC", "Source Han Sans CN",
        "Noto Sans CJK SC", "WenQuanYi Zen Hei", "Segoe UI", "DejaVu Sans",
    ],
    "axes.unicode_minus": False,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "axes.edgecolor": AXIS,
    "axes.linewidth": 0.8,
    "axes.labelcolor": INK_SECONDARY,
    "xtick.color": INK_MUTED,
    "ytick.color": INK_MUTED,
    "axes.spines.top": False,
    "axes.spines.right": False,
})


# ---------- 数据加载 ----------
def load_data(path: Path) -> pd.DataFrame:
    """读取 Excel 利润表，把每个项目转成 {year: value} 的 Series。"""
    df = pd.read_excel(path, sheet_name=0, header=None)

    # 第 2 行（index=1）是年份列
    year_row = df.iloc[1, 1:]
    years = []
    for v in year_row:
        m = re.search(r"\d{4}", str(v))
        years.append(int(m.group())) if m else years.append(None)
    years = [y for y in years if y is not None]
    years_sorted = sorted(years)  # 时间升序：2009...2025

    # 行索引：项目名 -> 数据列（按 year 升序）
    # 注意：原表 header 是 2025→2009 倒序，因此 values 也是倒序的，
    # 需要 reverse 后再与升序 years 对齐。
    series_map: dict[str, list[float]] = {}
    label_col = df.iloc[2:, 0].astype(str)
    for label_idx, raw_label in enumerate(label_col):
        label = raw_label.strip()
        if not label or label.lower() == "项目":
            continue
        values = df.iloc[2 + label_idx, 1:].tolist()[: len(years_sorted)]
        if len(values) < len(years_sorted):
            values = values + [float("nan")] * (len(years_sorted) - len(values))
        series_map[label] = list(reversed(values))

    out = pd.DataFrame(series_map, index=years_sorted).T
    out.columns = years_sorted
    return out


def pick_row(df: pd.DataFrame, *needles: str, exact: bool = False) -> str:
    """在项目名中挑选唯一匹配的行名。

    exact=False（默认）：所有 needles 都作为子串出现在 label 中；
    exact=True：label 必须与所有 needles 完全相等（去除两端空白）。
    """
    candidates = []
    for label in df.index:
        norm = label.strip()
        if exact:
            if all(n.strip() == norm for n in needles):
                candidates.append(label)
        else:
            if all(n in norm for n in needles):
                candidates.append(label)
    if len(candidates) != 1:
        raise RuntimeError(
            f"无法唯一定位 {needles}（exact={exact}），候选: {candidates}"
        )
    return candidates[0]


# ---------- 绘图单元 ----------
def style_axes(ax, ylabel: str) -> None:
    ax.set_ylabel(ylabel, color=INK_SECONDARY, fontsize=11, labelpad=8)
    ax.tick_params(axis="both", length=0, labelsize=9)
    ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0)
    ax.grid(axis="x", color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.axhline(0, color=AXIS, linewidth=0.8, zorder=0)


def plot_series(
    ax,
    years: list[int],
    values: list[float],
    color: str,
    label: str,
    *,
    end_label: str | None = None,
) -> None:
    ax.plot(
        years, values,
        color=color, linewidth=2.0,
        solid_capstyle="round", solid_joinstyle="round",
        marker="o", markersize=8,
        markerfacecolor=color, markeredgecolor=SURFACE, markeredgewidth=2,
        label=label, zorder=3,
    )
    if end_label is not None:
        ax.text(
            years[-1] + 0.2, values[-1], end_label,
            color=INK_PRIMARY, fontsize=9, va="center", ha="left",
        )


def render_cashflow_chart(
    *,
    title: str,
    subtitle: str,
    values: dict[int, float],
    out_path: Path,
    ylabel: str = "金额（亿元）",
    ylim_pad: float = 1.18,
) -> None:
    """单条经营现金流折线 + 关键事件标注（leader line 形式）。"""
    years = sorted(values.keys())
    series_vals = [values[y] for y in years]

    fig, ax = plt.subplots(figsize=(12, 5.4), dpi=160)
    fig.subplots_adjust(left=0.07, right=0.94, top=0.82, bottom=0.12)

    plot_series(ax, years, series_vals, C1, "经营活动现金流量净额")
    style_axes(ax, ylabel)

    # y 轴自适应
    y_min, y_max = min(series_vals), max(series_vals)
    if y_min >= 0:
        ax.set_ylim(0, y_max * ylim_pad)
    elif y_max <= 0:
        ax.set_ylim(y_min * ylim_pad, 0)
    else:
        # 正负都有：分别向上/向下扩张，顶部额外给标注留位，
        # 底部只留 30% 余白以减少无用的空白。
        ax.set_ylim(y_min - abs(y_min) * 0.30, y_max + y_max * 0.30)

    ax.set_xlim(min(years) - 0.6, max(years) + 0.8)
    ax.set_xticks(years)
    ax.set_xticklabels([str(y) for y in years], rotation=45, ha="right")

    # 标题区
    fig.text(0.07, 0.94, title, color=INK_PRIMARY,
             fontsize=15, fontweight="semibold")
    fig.text(0.07, 0.885, subtitle, color=INK_SECONDARY, fontsize=10)

    # 关键事件标注：(year, anchor_offset_x, anchor_offset_y, text_lines)
    # 2011 → 当年高点，对应橡胶价格 4.3 万元/吨；2016 → 收购合盛农业
    annotations = [
        {
            "year": 2011, "value": values[2011],
            "xytext": (2010.5, values[2011] + 4.0),
            "lines": ["2011  橡胶价格 43,000 元/吨",
                      "经营现金流 8.8 亿"],
        },
        {
            "year": 2016, "value": values[2016],
            "xytext": (2016.0, values[2016] + 6.0),
            "lines": ["2016  收购合盛农业",
                      "(Hershey Agriculture)"],
        },
    ]
    for anno in annotations:
        ax.annotate(
            "\n".join(anno["lines"]),
            xy=(anno["year"], anno["value"]),
            xytext=anno["xytext"],
            ha="center", va="bottom",
            fontsize=9, color=INK_PRIMARY,
            bbox={
                "boxstyle": "round,pad=0.4",
                "facecolor": SURFACE, "edgecolor": CALLOUT,
                "linewidth": 0.8,
            },
            arrowprops={
                "arrowstyle": "-",
                "color": CALLOUT, "linewidth": 0.8,
                "shrinkA": 2, "shrinkB": 4,
            },
            zorder=5,
        )

    fig.savefig(out_path, dpi=200, facecolor=SURFACE)
    plt.close(fig)


def render_line_chart(
    *,
    title: str,
    subtitle: str,
    series: list[tuple[list[float], str, str]],
    out_path: Path,
    ylabel: str = "金额（亿元）",
    ylim_pad: float = 1.15,
) -> None:
    """series: [(values, label, color_hex), ...]"""
    years = list(range(2009, 2026))

    fig, ax = plt.subplots(figsize=(12, 5.4), dpi=160)
    fig.subplots_adjust(left=0.07, right=0.78, top=0.82, bottom=0.12)

    for values, label, color in series:
        plot_series(ax, years, values, color, label)

    style_axes(ax, ylabel)

    # y 轴范围：根据数据正负分布自适应
    all_vals = [v for s in series for v in s[0] if v is not None]
    y_min, y_max = min(all_vals), max(all_vals)
    if y_min >= 0:
        # 全部为正：以 0 为底，留 ylim_pad 余白
        ax.set_ylim(0, y_max * ylim_pad)
    elif y_max <= 0:
        # 全部为负：以 0 为顶
        ax.set_ylim(y_min * ylim_pad, 0)
    else:
        # 正负都有：对称到 0 轴
        span = max(abs(y_min), abs(y_max))
        ax.set_ylim(-span * ylim_pad, span * ylim_pad)

    # x 轴：年份
    ax.set_xlim(2008.6, 2025.6)
    ax.set_xticks(years)
    ax.set_xticklabels([str(y) for y in years], rotation=45, ha="right")

    # 标题区
    fig.text(0.07, 0.94, title, color=INK_PRIMARY,
             fontsize=15, fontweight="semibold")
    fig.text(0.07, 0.885, subtitle, color=INK_SECONDARY, fontsize=10)

    # 图例：≥ 2 条线时显示；放在右上、紧贴图区
    if len(series) >= 2:
        legend = ax.legend(
            loc="upper left",
            bbox_to_anchor=(1.01, 1.0),
            frameon=False,
            handlelength=1.6,
            handletextpad=0.6,
            labelspacing=0.4,
            fontsize=10,
        )
        for txt in legend.get_texts():
            txt.set_color(INK_PRIMARY)

    fig.savefig(out_path, dpi=200, facecolor=SURFACE)
    plt.close(fig)


# ---------- 主流程 ----------
def main() -> None:
    df = load_data(SRC)
    years = list(range(2009, 2026))

    # 行名定位（兼容不同表头写法）
    r_rev = pick_row(df, "营业总收入")
    r_cost = pick_row(df, "营业总成本")

    revenue = df.loc[r_rev, years].astype(float).tolist()
    cost = df.loc[r_cost, years].astype(float).tolist()

    # 净利润 / 扣非后归母 / 归母净利润：直接使用上方已验证口径（2009—2025 升序，单位：亿元），
    # 与「利润表.md」三、利润与净利润保持一致，避免 Excel 解析差异导致图表数据对不上。
    net_profit = NET_PROFIT
    parent_profit = PARENT_PROFIT
    nonrecurring_profit = NONRECUR_PROFIT

    # ---------- 图表 1：营收 vs 成本 ----------
    render_line_chart(
        title="海南橡胶 营业总收入 vs 营业总成本 (2009—2025)",
        subtitle="单位：亿元；2023 年起并表带动收入跃升至 400 亿级",
        series=[
            (revenue, "营业总收入", C1),
            (cost, "营业总成本", C2),
        ],
        out_path=HERE / "01_营业总收入_营业总成本.png",
    )

    # ---------- 图表 2：净利润 ----------
    render_line_chart(
        title="海南橡胶 净利润 (2009—2025)",
        subtitle="单位：亿元；多数年份在 0 轴附近徘徊，2015 / 2017 / 2024—2025 出现亏损",
        series=[(net_profit, "净利润", C1)],
        out_path=HERE / "02_净利润.png",
    )

    # ---------- 图表 3：扣非净利润 ----------
    render_line_chart(
        title="海南橡胶 扣非后归母净利润 (2009—2025)",
        subtitle="单位：亿元；2014 年起主营业务持续亏损，仅 2009—2012 录得正值",
        series=[(nonrecurring_profit, "扣非后归母净利润", C1)],
        out_path=HERE / "03_扣非净利润.png",
    )

    # ---------- 图表 4：归母净利润 ----------
    render_line_chart(
        title="海南橡胶 归属于母公司股东的净利润 (2009—2025)",
        subtitle="单位：亿元；少数股东损益持续亏损时，归母净利润高于合并净利润",
        series=[(parent_profit, "归属于母公司股东的净利润", C1)],
        out_path=HERE / "04_归母净利润.png",
    )

    # ---------- 图表 5：三线对比 ----------
    render_line_chart(
        title="海南橡胶 净利润 / 扣非净利润 / 归母净利润 对比 (2009—2025)",
        subtitle="单位：亿元；扣非净利润长期低于另两项，揭示主业造血能力不足",
        series=[
            (net_profit, "净利润", C1),
            (nonrecurring_profit, "扣非后归母净利润", C2),
            (parent_profit, "归属于母公司股东的净利润", C3),
        ],
        out_path=HERE / "05_净利润_扣非_归母_三线对比.png",
    )

    # ---------- 图表 6：经营活动现金流量净额（含事件标注） ----------
    render_cashflow_chart(
        title="海南橡胶 经营活动产生的现金流量净额 (2008—2025)",
        subtitle="单位：亿元；2011 年高点对应橡胶价格 4.3 万元/吨，2016 年完成对合盛农业的收购",
        values=CASH_FLOW,
        out_path=HERE / "06_经营现金流净额.png",
    )

    # ---------- 图表 7：资产总额 vs 负债总额 ----------
    render_line_chart(
        title="海南橡胶 资产总额 vs 负债总额 (2009—2025)",
        subtitle="单位：亿元；2023 年合并范围扩大推动资产跃升至 340 亿级",
        series=[
            (TOTAL_ASSETS, "资产总额", C1),
            (TOTAL_LIABILITIES, "负债总额", C2),
        ],
        out_path=HERE / "07_资产总额_负债总额.png",
    )

    # ---------- 图表 8：股东权益 ----------
    render_line_chart(
        title="海南橡胶 股东权益合计 (2009—2025)",
        subtitle="单位：亿元；2010 年增发后股东权益翻倍，2023 年并表再上 116 亿",
        series=[(TOTAL_EQUITY, "股东权益合计", C1)],
        out_path=HERE / "08_股东权益.png",
    )

    # ---------- 图表 9：资产负债率 ----------
    debt_ratio = [round(L / A * 100, 1) for L, A in zip(TOTAL_LIABILITIES, TOTAL_ASSETS)]
    render_line_chart(
        title="海南橡胶 资产负债率 (2009—2025)",
        subtitle="负债 ÷ 资产（%）；2011—2012 年降至 17% 历史低点，2025 年抬升至 70%",
        series=[(debt_ratio, "资产负债率", C2)],
        out_path=HERE / "09_资产负债率.png",
        ylabel="负债率（%）",
    )

    # ---------- 图表 10：负债结构 —— 三条线同一坐标系 ----------
    # 流动负债、非流动负债、流动负债占比 三者在同一坐标系。
    # 占比按百分比数值（0—100）直接画在亿元轴上，读数时按图例区分单位。
    current_ratio = [
        round(c / (c + n) * 100, 1)
        for c, n in zip(CURRENT_LIABILITIES, NONCURRENT_LIABILITIES)
    ]
    render_line_chart(
        title="海南橡胶 负债结构 (2009—2025)",
        subtitle="单位：亿元（左轴绝对值）；占比（%，同坐标系）；2025 年流动负债 145 亿、占比 61%",
        series=[
            (CURRENT_LIABILITIES, "流动负债（亿元）", C1),
            (NONCURRENT_LIABILITIES, "非流动负债（亿元）", C2),
            (current_ratio, "流动负债占比（%）", C3),
        ],
        out_path=HERE / "10_负债结构_三线同轴.png",
        ylabel="亿元 / 占比（%）",
    )

    # ---------- 图表 11：流动资产 vs 非流动资产 ----------
    render_line_chart(
        title="海南橡胶 流动资产 vs 非流动资产 (2009—2025)",
        subtitle="单位：亿元；非流动资产占比稳定在 55—70%，主因橡胶林生物资产",
        series=[
            (CURRENT_ASSETS, "流动资产", C1),
            (NONCURRENT_ASSETS, "非流动资产", C2),
        ],
        out_path=HERE / "11_流动资产_非流动资产.png",
    )

    # ---------- 图表 12：流动资产合计 vs 固定资产合计 ----------
    render_line_chart(
        title="海南橡胶 流动资产合计 vs 固定资产合计 (2009—2025)",
        subtitle="单位：亿元；固定资产是更窄口径（仅厂房/机器等），橡胶林属生产性生物资产",
        series=[
            (CURRENT_ASSETS, "流动资产合计", C1),
            (FIXED_ASSETS, "固定资产合计", C2),
        ],
        out_path=HERE / "12_流动资产合计_固定资产合计.png",
    )

    # ---------- 输出文件清单 ----------
    outputs = [
        "01_营业总收入_营业总成本.png",
        "02_净利润.png",
        "03_扣非净利润.png",
        "04_归母净利润.png",
        "05_净利润_扣非_归母_三线对比.png",
        "06_经营现金流净额.png",
        "07_资产总额_负债总额.png",
        "08_股东权益.png",
        "09_资产负债率.png",
        "10_负债结构_三线同轴.png",
        "11_流动资产_非流动资产.png",
        "12_流动资产合计_固定资产合计.png",
    ]
    print("生成完成：")
    for name in outputs:
        path = HERE / name
        size_kb = path.stat().st_size / 1024
        print(f"  - {name}  ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()