# -*- coding: utf-8 -*-
"""生成科特迪瓦主要经济作物表格图片"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

# 中文字体
font_path = r"C:\Windows\Fonts\msyh.ttc"
zh = font_manager.FontProperties(fname=font_path)
plt.rcParams["axes.unicode_minus"] = False

# 表头
headers = ["排名", "作物", "全球地位", "全球占比", "主要用途", "主要产区"]

# 数据行
rows = [
    ["🥇", "可可 (Cocoa)",   "世界第一",      "~40%", "巧克力原料",   "全国（南部、中部、西部）"],
    ["🥇", "腰果 (Cashew)",  "世界第一",      "~25%", "坚果零食",     "北部、中部、东部"],
    ["🥈", "橡胶 (Rubber)",  "世界第三/第四", "~8%",  "轮胎、医疗用品", "南部、东南部、西部"],
    ["🥉", "棕榈油 (Palm Oil)", "世界第五",   "~3%",  "食用油、工业",   "西南部、东南部"],
    ["4",  "咖啡 (Coffee)",  "世界第十二",    "~1%",  "饮品",         "西部山区、中部"],
    ["5",  "棉花 (Cotton)",  "非洲前三",      "—",    "纺织",         "北部、萨瓦纳区"],
    ["6",  "香蕉、菠萝、木瓜", "西非主要",     "—",    "鲜果/加工",    "南部"],
    ["7",  "玉米、稻米、木薯", "粮食为主",     "—",    "粮食安全",     "全国"],
]

# emoji 字体不一定可用，用文字替代奖牌以保证渲染
medal_map = {"🥇": "①", "🥈": "②", "🥉": "③"}
for r in rows:
    r[0] = medal_map.get(r[0], r[0])

n_rows = len(rows) + 1
n_cols = len(headers)

# 列宽比例
col_widths = [0.07, 0.20, 0.15, 0.10, 0.18, 0.30]

fig, ax = plt.subplots(figsize=(14, 6.5))
ax.axis("off")

# 标题
title = "🌍 科特迪瓦主要经济作物"
ax.text(0.5, 0.965, "科特迪瓦主要经济作物", ha="center", va="center",
        fontproperties=zh, fontsize=24, fontweight="bold", color="#1a3c34")

table = ax.table(
    cellText=rows,
    colLabels=headers,
    colWidths=col_widths,
    cellLoc="center",
    loc="center",
    bbox=[0.0, 0.0, 1.0, 0.90],
)

table.auto_set_font_size(False)
table.set_fontsize(13)

header_color = "#2e7d32"
alt_color = "#f1f8e9"
white = "#ffffff"

# 前三名高亮色
rank_bg = {0: "#fff8e1", 1: "#fff8e1", 2: "#fbe9e7", 3: "#fff3e0"}

for (row, col), cell in table.get_celld().items():
    cell.set_edgecolor("#cfd8dc")
    cell.set_linewidth(0.8)
    cell.get_text().set_fontproperties(zh)
    if row == 0:
        # 表头
        cell.set_facecolor(header_color)
        cell.get_text().set_color(white)
        cell.get_text().set_fontweight("bold")
        cell.set_height(0.09)
        cell.get_text().set_fontsize(14)
    else:
        data_i = row - 1
        if data_i in rank_bg:
            cell.set_facecolor(rank_bg[data_i])
        else:
            cell.set_facecolor(white if data_i % 2 == 0 else alt_color)
        cell.set_height(0.10)
        # 作物名加粗
        if col == 1:
            cell.get_text().set_fontweight("bold")
        if col == 0:
            cell.get_text().set_fontweight("bold")
            cell.get_text().set_fontsize(15)

plt.subplots_adjust(left=0.02, right=0.98, top=0.92, bottom=0.03)

out_path = r"C:\Users\23075\Desktop\learn\思想交流\农产品之橡胶分析\科特迪瓦\图片\科特迪瓦主要经济作物.png"
plt.savefig(out_path, dpi=200, bbox_inches="tight", facecolor="white")
print("已保存:", out_path)
