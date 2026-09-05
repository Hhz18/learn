# -*- coding: utf-8 -*-
"""可可种植面积 + 每公顷净利润 双轴组合图 (2010-2025)"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import FuncFormatter

font_path = r"C:\Windows\Fonts\msyh.ttc"
zh = font_manager.FontProperties(fname=font_path)
plt.rcParams["axes.unicode_minus"] = False

labels = ["2010/11","2011/12","2012/13","2013/14","2014/15","2015/16","2016/17",
          "2017/18","2018/19","2019/20","2020/21","2021/22","2022/23","2023/24",
          "2024/25","2025/26"]
x = list(range(len(labels)))

area  = [1500,1600,1700,1800,1900,2000,2150,2300,2400,2200,2050,2100,2500,2500,2400,2350]  # 千公顷
profit= [150000,210000,-37500,-25000,45000,170000,170000,-50000,-87500,12500,50000,
         -50000,-150000,250000,940000,1260000]  # FCFA/ha

C_AREA   = "#a5d6a7"   # 浅绿柱
C_AREA_E = "#66bb6a"
C_PROFIT = "#c62828"   # 红折线

fig, ax1 = plt.subplots(figsize=(15, 8))
fig.patch.set_facecolor("white")
ax1.set_facecolor("#fbfdfb")

# 左轴：种植面积柱状
bars = ax1.bar(x, area, width=0.62, color=C_AREA, edgecolor=C_AREA_E, lw=1, label="种植面积（千公顷）", zorder=2)
ax1.set_ylabel("可可种植面积（千公顷）", fontproperties=zh, fontsize=13, color="#2e7d32")
ax1.set_ylim(0, 2800)
ax1.tick_params(axis="y", labelcolor="#2e7d32")
for b, a in zip(bars, area):
    ax1.text(b.get_x()+b.get_width()/2, a+30, f"{a:,}", ha="center", va="bottom",
             fontproperties=zh, fontsize=8.5, color="#2e7d32")

# 右轴：每公顷净利折线
ax2 = ax1.twinx()
ax2.axhline(0, color="#999999", lw=1.1, ls="-", zorder=1)
ax2.plot(x, profit, marker="o", lw=2.8, ms=7, color=C_PROFIT, label="每公顷净利 (FCFA/ha)", zorder=4)
ax2.set_ylabel("每公顷净利润（FCFA/ha）", fontproperties=zh, fontsize=13, color=C_PROFIT)
ax2.set_ylim(-300000, 1400000)
ax2.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{int(v):,}"))
ax2.tick_params(axis="y", labelcolor=C_PROFIT)

# 标注亏损年 & 峰值
for xi, p in zip(x, profit):
    if p < 0:
        ax2.annotate(f"{p:,}", (xi, p), xytext=(xi, p-55000), ha="center",
                     fontproperties=zh, fontsize=8, color=C_PROFIT, fontweight="bold")
ax2.annotate("暴利 940,000", (14, 940000), xytext=(12.6, 1000000),
             fontproperties=zh, fontsize=10, color=C_PROFIT, fontweight="bold", ha="center")
ax2.annotate("历史峰值 1,260,000", (15, 1260000), xytext=(13.6, 1300000),
             fontproperties=zh, fontsize=10, color=C_PROFIT, fontweight="bold", ha="center")

ax1.set_xticks(x)
ax1.set_xticklabels(labels, rotation=45, fontproperties=zh, fontsize=10)
ax1.set_xlabel("年度", fontproperties=zh, fontsize=13)
ax1.set_title("科特迪瓦可可：种植面积 vs 每公顷净利润（2010–2025）",
              fontproperties=zh, fontsize=20, fontweight="bold", color="#1a3c34", pad=16)
ax1.grid(True, axis="y", ls="--", lw=0.6, color="#e0e6e0", alpha=0.7, zorder=0)
for spine in ["top"]:
    ax1.spines[spine].set_visible(False)
    ax2.spines[spine].set_visible(False)

# 合并图例
l1, lab1 = ax1.get_legend_handles_labels()
l2, lab2 = ax2.get_legend_handles_labels()
leg = ax1.legend(l1+l2, lab1+lab2, prop=zh, fontsize=12, loc="upper left", frameon=True, framealpha=0.95)
leg.get_frame().set_edgecolor("#cccccc")

fig.text(0.99, 0.01, "注：红线低于 0 = 亏损年（共 6 年）；2025/26 为行业预测。面积单位千公顷，净利单位 FCFA/ha",
         ha="right", va="bottom", fontproperties=zh, fontsize=9, color="#888888")

plt.tight_layout()
out_path = r"C:\Users\23075\Desktop\learn\思想交流\农产品之橡胶分析\科特迪瓦\图片\可可种植面积与净利润双轴图.png"
plt.savefig(out_path, dpi=200, bbox_inches="tight", facecolor="white")
print("已保存:", out_path)
