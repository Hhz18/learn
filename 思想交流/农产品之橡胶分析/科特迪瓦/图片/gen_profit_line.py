# -*- coding: utf-8 -*-
"""三大作物每公顷净利润趋势折线图 (FCFA/ha, 2010-2025)"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import FuncFormatter

font_path = r"C:\Windows\Fonts\msyh.ttc"
zh = font_manager.FontProperties(fname=font_path)
plt.rcParams["axes.unicode_minus"] = False

years = list(range(2010, 2026))

rubber = [161000, 279400, 211480, 173420, 78055, 59822, 136148, 289593,
          268960, 341320, 437660, 612700, 616500, 662322, 798228, 695130]
cocoa  = [150000, 210000, -37500, -25000, 45000, 170000, 170000, -50000,
          -87500, 12500, 50000, -50000, -150000, 250000, 750000, 900000]
palm   = [350000, 528000, 470000, 360000, 280000, 180000, 260000, 280000,
          200000, 180000, 230000, 450000, 490000, 280000, 320000, 300000]
avg    = [(r+c+p)/3 for r, c, p in zip(rubber, cocoa, palm)]

C_RUBBER = "#2e7d32"
C_COCOA  = "#c62828"
C_PALM   = "#e8a33d"
C_AVG    = "#5c6bc0"

fig, ax = plt.subplots(figsize=(14.5, 8))
fig.patch.set_facecolor("white")
ax.set_facecolor("#fbfdfb")

# 零轴基准线
ax.axhline(0, color="#999999", lw=1.2, ls="-", zorder=1)

ax.plot(years, rubber, marker="o", lw=2.6, ms=6, color=C_RUBBER, label="橡胶净利 (Rubber)", zorder=4)
ax.plot(years, cocoa,  marker="o", lw=2.6, ms=6, color=C_COCOA,  label="可可净利 (Cocoa)", zorder=4)
ax.plot(years, palm,   marker="o", lw=2.6, ms=6, color=C_PALM,   label="棕榈油净利 (Palm Oil)", zorder=4)
ax.plot(years, avg,    marker="s", lw=1.8, ms=4, color=C_AVG, ls="--", label="三者平均", alpha=0.85, zorder=3)

def note(x, y, text, color, dy=45000, dx=0):
    ax.annotate(text, (x, y), xytext=(x+dx, y+dy),
                fontproperties=zh, fontsize=10, color=color, fontweight="bold", ha="center")

note(2022, -150000, "可可亏损谷底 -150,000", C_COCOA, dy=-70000, dx=-0.3)
note(2025, 900000, "可可反超 900,000", C_COCOA, dy=48000, dx=-1.4)
note(2024, 798228, "橡胶峰值 798,228", C_RUBBER, dy=55000, dx=-1.6)
note(2011, 528000, "棕榈油早期领先", C_PALM, dy=55000, dx=1.2)

ax.set_xticks(years)
ax.set_xticklabels(years, rotation=45, fontproperties=zh, fontsize=10)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{int(v):,}"))
ax.set_ylim(-250000, 1000000)
ax.set_ylabel("每公顷净利润 (FCFA/ha)", fontproperties=zh, fontsize=13)
ax.set_xlabel("年份", fontproperties=zh, fontsize=13)
ax.set_title("科特迪瓦三大作物每公顷净利润趋势（2010–2025）",
             fontproperties=zh, fontsize=20, fontweight="bold", color="#1a3c34", pad=16)

ax.grid(True, axis="y", ls="--", lw=0.6, color="#d0d7d0", alpha=0.8)
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)

leg = ax.legend(prop=zh, fontsize=12, loc="upper left", frameon=True, framealpha=0.95)
leg.get_frame().set_edgecolor("#cccccc")

fig.text(0.99, 0.01, "注：可可多年为负=亏损；2011–2024 部分标注为峰值/谷底。单位 FCFA/ha",
         ha="right", va="bottom", fontproperties=zh, fontsize=9, color="#888888")

plt.tight_layout()
out_path = r"C:\Users\23075\Desktop\learn\思想交流\农产品之橡胶分析\科特迪瓦\图片\三大作物每公顷净利润趋势折线图.png"
plt.savefig(out_path, dpi=200, bbox_inches="tight", facecolor="white")
print("已保存:", out_path)
