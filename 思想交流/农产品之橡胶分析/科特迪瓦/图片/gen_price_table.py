# -*- coding: utf-8 -*-
"""生成三大作物农户收购价对比表格图片 (FCFA/kg)"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

font_path = r"C:\Windows\Fonts\msyh.ttc"
zh = font_manager.FontProperties(fname=font_path)
plt.rcParams["axes.unicode_minus"] = False

headers = ["年份", "橡胶 (Rubber)", "可可 (Cocoa)", "棕榈油 (Palm Oil)", "数据性质"]

# 每格: (文本, 标注类型)  标注: None / 'peak'(峰值▲红) / 'real'(真实●绿) / 'low'(谷底绿)
rows = [
    ["2010", "500",              "1,000",            "350", "估算"],
    ["2011", "700 ▲峰值",        "1,100",            "440", "估算/真实"],
    ["2012", "520",              "725",              "410", "真实(可可)"],
    ["2013", "420",              "750",              "360", "真实(可可)"],
    ["2014", "295 ●真实",        "850",              "330", "真实(可可)"],
    ["2015", "237 ●谷底",        "1,100",            "280", "真实(可可/橡胶)"],
    ["2016", "282 ●真实",        "1,100",            "320", "真实(可可/橡胶)"],
    ["2017", "359 ●真实",        "700 ●真实",        "340", "真实"],
    ["2018", "290",              "825 ●真实",        "300", "真实(可可)"],
    ["2019", "310",              "825",              "290", "真实(可可)"],
    ["2020", "340",              "1,000",            "340", "真实(可可)"],
    ["2021", "390",              "900",              "450", "真实"],
    ["2022", "340",              "900",              "470", "真实"],
    ["2023", "307 ●真实",        "1,500 ●真实",      "390", "真实"],
    ["2024", "372 ●真实",        "1,800→2,200 ▲",   "410", "真实"],
    ["2025", "390",              "2,200 ▲历史峰值",  "400", "真实/预测"],
]

headers_render = headers
n_cols = len(headers)
col_widths = [0.10, 0.22, 0.26, 0.20, 0.22]

fig, ax = plt.subplots(figsize=(15, 9))
ax.axis("off")

ax.text(0.5, 0.975, "三大作物农户收购价对比（FCFA/kg）", ha="center", va="center",
        fontproperties=zh, fontsize=24, fontweight="bold", color="#1a3c34")

table = ax.table(
    cellText=rows,
    colLabels=headers_render,
    colWidths=col_widths,
    cellLoc="center",
    loc="center",
    bbox=[0.0, 0.0, 1.0, 0.93],
)

table.auto_set_font_size(False)
table.set_fontsize(12)

header_color = "#2e7d32"
white = "#ffffff"
alt_color = "#f1f8e9"

for (row, col), cell in table.get_celld().items():
    cell.set_edgecolor("#cfd8dc")
    cell.set_linewidth(0.8)
    txt = cell.get_text()
    txt.set_fontproperties(zh)
    if row == 0:
        cell.set_facecolor(header_color)
        txt.set_color(white)
        txt.set_fontweight("bold")
        cell.set_height(0.055)
        txt.set_fontsize(13)
    else:
        data_i = row - 1
        cell.set_facecolor(white if data_i % 2 == 0 else alt_color)
        cell.set_height(0.052)
        content = rows[data_i][col]
        if col == 0:
            txt.set_fontweight("bold")
        # 峰值标注红色，真实/谷底标注绿色
        if "▲" in content:
            txt.set_color("#c62828")
            txt.set_fontweight("bold")
        elif "●" in content:
            txt.set_color("#2e7d32")
            txt.set_fontweight("bold")

plt.subplots_adjust(left=0.02, right=0.98, top=0.93, bottom=0.02)

# 图例说明
fig.text(0.5, 0.005,
         "标注：▲ = 峰值 / 历史高点（红）    ● = 真实数据 / 谷底（绿）    单位：FCFA/kg",
         ha="center", va="bottom", fontproperties=zh, fontsize=11, color="#555555")

out_path = r"C:\Users\23075\Desktop\learn\思想交流\农产品之橡胶分析\科特迪瓦\图片\三大作物农户收购价对比.png"
plt.savefig(out_path, dpi=200, bbox_inches="tight", facecolor="white")
print("已保存:", out_path)
