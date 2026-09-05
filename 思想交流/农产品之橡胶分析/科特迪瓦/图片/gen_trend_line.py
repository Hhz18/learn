# -*- coding: utf-8 -*-
"""三大作物农户收购价趋势折线图 (FCFA/kg, 2010-2025)"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

font_path = r"C:\Windows\Fonts\msyh.ttc"
zh = font_manager.FontProperties(fname=font_path)
plt.rcParams["axes.unicode_minus"] = False

years = list(range(2010, 2026))

# 可可 2024 为 1800→2200 的过渡，取 2000 表示上升过程
rubber = [500, 700, 520, 420, 295, 237, 282, 359, 290, 310, 340, 390, 340, 307, 372, 390]
cocoa  = [1000, 1100, 725, 750, 850, 1100, 1100, 700, 825, 825, 1000, 900, 900, 1500, 2000, 2200]
palm   = [350, 440, 410, 360, 330, 280, 320, 340, 300, 290, 340, 450, 470, 390, 410, 400]

C_RUBBER = "#2e7d32"   # 绿
C_COCOA  = "#c62828"   # 红棕
C_PALM   = "#e8a33d"   # 棕榈黄

fig, ax = plt.subplots(figsize=(14, 7.5))
fig.patch.set_facecolor("white")
ax.set_facecolor("#fbfdfb")

ax.plot(years, cocoa,  marker="o", lw=2.6, ms=6, color=C_COCOA,  label="可可 (Cocoa)", zorder=3)
ax.plot(years, rubber, marker="o", lw=2.6, ms=6, color=C_RUBBER, label="橡胶 (Rubber)", zorder=3)
ax.plot(years, palm,   marker="o", lw=2.6, ms=6, color=C_PALM,   label="棕榈油 (Palm Oil)", zorder=3)

# 关键点标注
def note(x, y, text, color, dy=45, dx=0):
    ax.annotate(text, (x, y), xytext=(x+dx, y+dy),
                fontproperties=zh, fontsize=10, color=color, fontweight="bold",
                ha="center")

note(2011, 700, "橡胶峰值 700", C_RUBBER, dy=60)
note(2015, 237, "橡胶谷底 237", C_RUBBER, dy=-95)
note(2025, 2200, "可可历史峰值 2,200", C_COCOA, dy=-120, dx=-1.2)
note(2023, 1500, "可可起飞 1,500", C_COCOA, dy=70, dx=-1.3)

# 网格与坐标
ax.set_xticks(years)
ax.set_xticklabels(years, rotation=45, fontproperties=zh, fontsize=10)
ax.set_ylim(0, 2500)
ax.set_ylabel("农户收购价 (FCFA/kg)", fontproperties=zh, fontsize=13)
ax.set_xlabel("年份", fontproperties=zh, fontsize=13)
ax.set_title("科特迪瓦三大作物农户收购价趋势（2010–2025）",
             fontproperties=zh, fontsize=20, fontweight="bold", color="#1a3c34", pad=16)

ax.grid(True, axis="y", ls="--", lw=0.6, color="#d0d7d0", alpha=0.8)
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)

leg = ax.legend(prop=zh, fontsize=13, loc="upper left", frameon=True, framealpha=0.95)
leg.get_frame().set_edgecolor("#cccccc")

fig.text(0.99, 0.01, "注：2024 年可可为 1,800→2,200 过渡取 2,000；2010–2011 部分为估算。单位 FCFA/kg",
         ha="right", va="bottom", fontproperties=zh, fontsize=9, color="#888888")

plt.tight_layout()
out_path = r"C:\Users\23075\Desktop\learn\思想交流\农产品之橡胶分析\科特迪瓦\图片\三大作物收购价趋势折线图.png"
plt.savefig(out_path, dpi=200, bbox_inches="tight", facecolor="white")
print("已保存:", out_path)
