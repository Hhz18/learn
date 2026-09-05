# -*- coding: utf-8 -*-
"""生成'9·24前后国资入主上市公司'数据趋势图。数据口径不一，图中已标注。"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

# ---- 全局样式（dataviz 调色板 + 中文字体）----
plt.rcParams.update({
    "font.sans-serif": ["Microsoft YaHei"],
    "axes.unicode_minus": False,
    "figure.facecolor": "#fcfcfb",
    "axes.facecolor": "#fcfcfb",
    "savefig.facecolor": "#fcfcfb",
})
BLUE   = "#2a78d6"   # slot1
AQUA   = "#1baf7a"   # slot2
YELLOW = "#eda100"   # slot3
RED    = "#e34948"   # highlight
INK    = "#0b0b0b"; SEC = "#52514e"; MUTED = "#898781"
GRID   = "#e1e0d9"; BASE = "#c3c2b7"

def style_axis(ax):
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    for s in ["left", "bottom"]:
        ax.spines[s].set_color(BASE)
    ax.tick_params(colors=MUTED, labelsize=10)
    ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)

# ================== 图1：主趋势线 ==================
fig, ax = plt.subplots(figsize=(11, 6.2), dpi=200)
style_axis(ax)

years = [2021, 2022, 2023, 2024]
total = [169, 152, 110, 140]          # 口径A 控制权变更总数
gm    = [None, 18, 18, 21]            # 口径C 国资收购民企(Wind严口径)
enter = [None, None, 27, 30]          # 口径B 地方国资入主

x = list(range(len(years)))
# 主线：控制权变更总数
ax.plot(x, total, color=BLUE, lw=2.4, marker="o", ms=8,
        markerfacecolor=BLUE, markeredgecolor="#fcfcfb", markeredgewidth=1.6,
        zorder=5, label="A股控制权变更总数（口径A）")
for xi, v in zip(x, total):
    ax.annotate(f"{v}", (xi, v), textcoords="offset points", xytext=(0, 12),
                ha="center", fontsize=11, color=INK, fontweight="bold")

# 国资收购民企
xs2 = [i for i, v in zip(x, gm) if v is not None]
ys2 = [v for v in gm if v is not None]
ax.plot(xs2, ys2, color=AQUA, lw=2.2, marker="s", ms=7,
        markeredgecolor="#fcfcfb", markeredgewidth=1.4, zorder=5,
        label="国资收购民营上市公司（口径C·Wind严口径）")
for xi, v in zip(xs2, ys2):
    ax.annotate(f"{v}", (xi, v), textcoords="offset points", xytext=(0, -18),
                ha="center", fontsize=10, color="#12805a")

# 地方国资入主
xs3 = [i for i, v in zip(x, enter) if v is not None]
ys3 = [v for v in enter if v is not None]
ax.plot(xs3, ys3, color=YELLOW, lw=2.2, marker="D", ms=7,
        markeredgecolor="#fcfcfb", markeredgewidth=1.4, zorder=5,
        label="地方国资入主（口径B·实控人变国资）")
for xi, v in zip(xs3, ys3):
    ax.annotate(f"{v}", (xi, v), textcoords="offset points", xytext=(0, 12),
                ha="center", fontsize=10, color="#9c6b00")

# 9·24 政策竖线（位于2024）
ax.axvline(3, color=RED, lw=1.4, ls=(0, (4, 3)), zorder=2)
ax.annotate("2024/9/24\n『并购六条』", (3, 172), color=RED, fontsize=10,
            ha="center", va="bottom", fontweight="bold")

ax.set_xticks(x)
ax.set_xticklabels([str(y) for y in years], fontsize=11, color=SEC)
ax.set_ylim(0, 190)
ax.yaxis.set_major_locator(MultipleLocator(30))
ax.set_ylabel("数量（家 / 起）", fontsize=11, color=SEC)
ax.set_title("A股控制权变更与国资入主：数量趋势（2021–2024）",
             fontsize=15, color=INK, fontweight="bold", pad=14, loc="left")
ax.legend(loc="lower left", frameon=False, fontsize=10, labelcolor=SEC)
fig.text(0.008, 0.008,
         "注：各口径统计范围不同，不可直接横向相加；2025/26未列因全年口径未完整。数据为媒体/券商不完全统计。",
         fontsize=8, color=MUTED)
fig.tight_layout(rect=[0, 0.03, 1, 1])
fig.savefig("/tmp/国资入主_主趋势.png", dpi=200)
print("saved 主趋势")

# ================== 图2：四面板辅助看板 ==================
fig2, axs = plt.subplots(2, 2, figsize=(12.5, 9), dpi=200)
fig2.suptitle("『9·24』前后：国资收购上市公司的爆发与延续",
              fontsize=16, color=INK, fontweight="bold", x=0.02, ha="left")

# --- 面板A：2024四季度并购集中度 ---
axA = axs[0, 0]; style_axis(axA)
labels = ["Q1–Q3\n合计", "Q4单季\n(9·24后)"]
vals = [50, 50]
bars = axA.bar([0, 1], vals, width=0.55, color=[BLUE, RED], zorder=3)
for b, v in zip(bars, vals):
    axA.annotate(f"≈{v}%", (b.get_x()+b.get_width()/2, v), xytext=(0, 6),
                 textcoords="offset points", ha="center", fontsize=13,
                 fontweight="bold", color=INK)
axA.set_xticks([0, 1]); axA.set_xticklabels(labels, fontsize=10, color=SEC)
axA.set_ylim(0, 62); axA.set_ylabel("占全年并购启动量", fontsize=10, color=SEC)
axA.set_title("① 政策拐点：2024 Q4 单季 ≈ 全年一半",
              fontsize=12, color=INK, fontweight="bold", loc="left", pad=8)

# --- 面板B：政策后即时脉冲 ---
axB = axs[0, 1]; style_axis(axB)
mlab = ["重组公告\n环比", "重大重组\n交易额同比", "上海辖区\n重大重组同比"]
mval = [113, 75, 400]
bars = axB.bar(range(3), mval, width=0.6,
               color=[YELLOW, AQUA, BLUE], zorder=3)
for b, v in zip(bars, mval):
    axB.annotate(f"+{v}%", (b.get_x()+b.get_width()/2, v), xytext=(0, 6),
                 textcoords="offset points", ha="center", fontsize=12,
                 fontweight="bold", color=INK)
axB.set_xticks(range(3)); axB.set_xticklabels(mlab, fontsize=9.5, color=SEC)
axB.set_ylim(0, 470); axB.set_ylabel("同比 / 环比增幅", fontsize=10, color=SEC)
axB.set_title("② 政策后脉冲（2024Q4 / 一周年）",
              fontsize=12, color=INK, fontweight="bold", loc="left", pad=8)

# --- 面板C：地方国资收购案例逐年 ---
axC = axs[1, 0]; style_axis(axC)
yrs = ["2022", "2023", "2024", "2025"]
cases = [18, 27, 30, 40]      # 混合口径示意（收民企/入主/收购）
cols = [BLUE, BLUE, BLUE, RED]
bars = axC.bar(range(4), cases, width=0.6, color=cols, zorder=3)
for b, v in zip(bars, cases):
    axC.annotate(f"{v}", (b.get_x()+b.get_width()/2, v), xytext=(0, 5),
                 textcoords="offset points", ha="center", fontsize=12,
                 fontweight="bold", color=INK)
axC.annotate("2025：涉资 545.74 亿元\n(34起为获取控制权)", (3, 40),
             xytext=(-8, -34), textcoords="offset points", ha="right",
             fontsize=9.5, color="#a8302f")
axC.set_xticks(range(4)); axC.set_xticklabels(yrs, fontsize=10, color=SEC)
axC.set_ylim(0, 48); axC.set_ylabel("地方国资收购案例（起）", fontsize=10, color=SEC)
axC.set_title("③ 逐年攀升（口径示意）",
              fontsize=12, color=INK, fontweight="bold", loc="left", pad=8)

# --- 面板D：三阶段演进（文字块）---
axD = axs[1, 1]; axD.axis("off")
axD.set_title("④ 动机三阶段演进", fontsize=12, color=INK,
              fontweight="bold", loc="left", pad=8)
stages = [
    (AQUA,  "阶段一 纾困救火（2018–2023）",
     "民企质押爆仓 → 国资当『救火队长』\n约18起/年，本地为主"),
    (YELLOW,"阶段二 政策催化（2024 Q4）",
     "『并购六条』落地 → 主动布局\nQ4占全年近半，创五年新高"),
    (RED,   "阶段三 产业整合（2025→今）",
     "六成投向半导体/医药/新能源\n超7成不再要求迁址，重产业协同"),
]
y0 = 0.86
for c, title, body in stages:
    axD.add_patch(plt.Rectangle((0.02, y0-0.205), 0.035, 0.20,
                  transform=axD.transAxes, color=c, clip_on=False))
    axD.text(0.09, y0, title, transform=axD.transAxes, fontsize=11.5,
             color=INK, fontweight="bold", va="top")
    axD.text(0.09, y0-0.075, body, transform=axD.transAxes, fontsize=9.8,
             color=SEC, va="top")
    y0 -= 0.30

fig2.text(0.02, 0.012,
          "数据来源：证监会、上交所、中上协及新浪/证券时报/腾讯等媒体不完全统计；口径不一，仅供参考。",
          fontsize=8, color=MUTED)
fig2.tight_layout(rect=[0, 0.03, 1, 0.96])
fig2.savefig("/tmp/国资入主_看板.png", dpi=200)
print("saved 看板")
