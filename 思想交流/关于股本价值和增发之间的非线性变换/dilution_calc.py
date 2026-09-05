# -*- coding: utf-8 -*-
"""
股本增发稀释度分析脚本
=====================
对应「股本增发与价值投资稀释分析.md」的配套计算与绘图。

模型设定(上帝视角):
    F  = 原始终值(每股),默认为 10
    P  = 增发价
    d  = 增发比例,新增股本 / 原股本
公式:
    F'(d)      = (F + d*P) / (1 + d)
    稀释率(d)  = d*(1 - P/F) / (1 + d)     # 分式线性(非线性,上凸)
    线性近似    = (1 - P/F) * d            # 增发比例很小时的切线
"""
import csv
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---- 字体:Windows 下用微软雅黑/黑体,保证中文字符正常显示 ----
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 110

# ---- 参数 ----
F = 10.0          # 原始终值(每股)
P = 1.0           # 增发价(等于当前市价)
ratio_PF = P / F  # 增发价相对终值的比,场景下 = 0.1

# 增发比例扫描范围:0% ~ 50%
d_list = np.linspace(0.0, 0.5, 101)

# ---- 核心计算 ----
def f_prime(d, F=F, P=P):
    return (F + d * P) / (1 + d)

def dilution(d, r=ratio_PF):
    return d * (1 - r) / (1 + d)

Fp  = np.array([f_prime(d) for d in d_list])
DIL = np.array([dilution(d) for d in d_list])
LIN = np.array([(1 - ratio_PF) * d for d in d_list])  # 线性近似(切线)

# ---- 关键点位 ----
d_std = 0.10                     # 案例中外:增发 10%
Fp_std   = f_prime(d_std)
DIL_std  = dilution(d_std)
LIN_std  = (1 - ratio_PF) * d_std

print("=" * 60)
print("增发稀释度分析  (F = %.1f, P = %.1f, P/F = %.2f)" % (F, P, ratio_PF))
print("=" * 60)
print(f"增发比例 d=10% :")
print(f"  新每股终值 F'      = {Fp_std:.4f} 元")
print(f"  稀释率             = {DIL_std:.4f}  ({DIL_std*100:.2f}%)")
print(f"  线性近似(切线值)   = {LIN_std:.4f}  ({LIN_std*100:.2f}%)")
print(f"  实际 vs 线性的差值 = {DIL_std - LIN_std:.4f}  (强调「边际稀释递减」= 非线性)")
print()

# ---- 输出数据表(CSV) ----
out_csv = "dilution_table.csv"
with open(out_csv, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["增发比例 d%", "新增股本占比", "新每股终值 F'", "稀释率 %", "线性近似 %", "实际-线性(非线性差)"])
    for d, fp, di, li in zip(d_list, Fp, DIL, LIN):
        w.writerow([f"{d*100:.0f}%", f"{d:.4f}", f"{fp:.4f}", f"{di*100:.4f}", f"{li*100:.4f}", f"{(di-li)*100:.4f}"])
print(f"数据表已输出 -> {out_csv}")

# ---- 关键行:提取几档常用增发比例做成对照 ----
print("若干增发比例对照:")
print(f"{'d':>6} {'新每股F':>10} {'稀释率%':>9} {'线性%':>9} {'非线差%':>9}")
for dpct in [0, 2, 5, 10, 15, 20, 30, 40, 50]:
    d = dpct / 100.0
    fp = f_prime(d); di = dilution(d); li = (1 - ratio_PF) * d
    print(f"{d:6.2f} {fp:10.4f} {di*100:9.3f} {li*100:9.3f} {(di-li)*100:9.4f}")
print()

# ---- 绘图:非线性梯度图 ----
# 用「验证过的默认调色板」取色
SERIES_BLUE = "#2a78d6"   # categorical slot 1 / sequential 450
GRID        = "#e1e0d9"
MUTED       = "#898781"
INK         = "#0b0b0b"

fig, ax = plt.subplots(figsize=(9, 5.5))

# 真实稀释率(蓝色,主曲线)
ax.plot(d_list * 100, DIL * 100, color=SERIES_BLUE, lw=2.2, zorder=3, label="实际稀释率 (非线性, 上凸)")
# 线性近似(虚线,对照)
ax.plot(d_list * 100, LIN * 100, color=MUTED, lw=1.6, ls="--", zorder=2, label="线性近似 (增发比例很小时的切线)")

# 填充「非线性差」区域(曲线与线性之间的差)
ax.fill_between(d_list * 100, DIL * 100, LIN * 100, color=SERIES_BLUE, alpha=0.08, zorder=1)

# 关键点标注:d = 10%
ax.scatter([d_std * 100], [LIN_std * 100], color=MUTED, s=42, zorder=4, edgecolor="#fcfcfb", lw=1.5)
ax.scatter([d_std * 100], [DIL_std * 100], color=SERIES_BLUE, s=46, zorder=5, edgecolor="#fcfcfb", lw=1.5, label=f"案例点 d=10% (稀释 {DIL_std*100:.2f}%)")
ax.annotate(
    f"稀释 {DIL_std*100:.2f}%\n(10% 增发)",
    xy=(d_std * 100, DIL_std * 100),
    xytext=(d_std * 100 + 10, DIL_std * 100 - 4.2),
    color=INK, fontsize=9,
    arrowprops=dict(arrowstyle="->", color=MUTED, lw=1),
)

# 轴与网格
ax.set_xlim(0, 50)
ax.set_ylim(0, max(DIL) * 100 * 1.12)
ax.set_xlabel("增发比例 d (%)", color=INK, fontsize=11)
ax.set_ylabel("稀释率 (%)", color=INK, fontsize=11)
ax.grid(color=GRID, lw=0.8, ls="-", alpha=0.7, zorder=0)
ax.set_axisbelow(True)
for spine in ax.spines.values():
    spine.set_color(MUTED)
    spine.set_lw(0.8)

# 标题与注释
ax.set_title("增发比例 → 稀释率的非线性梯度", color=INK, fontsize=13, fontweight="bold", loc="left")
ax.text(
    0.995, 0.985, "随着增发比例增大,稀释率增长逐渐放缓(边际稀释递减)\n曲线上凸,并不随增发比例线性放大",
    transform=ax.transAxes, color=MUTED, fontsize=8.5, va="top", ha="right",
)

# 图例(>=2 序列,必须保留)
ax.legend(loc="upper left", frameon=True, framealpha=0.95, edgecolor=GRID, fontsize=8.5)

fig.tight_layout()
out_png = "dilution_curve.png"
fig.savefig(out_png, dpi=110, facecolor="#fcfcfb")
print(f"梯度图已输出 -> {out_png}")
