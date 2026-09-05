# -*- coding: utf-8 -*-
"""
华天科技 (002185) 2025 Q2 行情数据计算脚本
数据源: 东方财富 push2his.eastmoney.com
计算指标:
  1) 每日收盘价算术平均价
  2) 成交额加权平均价 (VWAP) = Σ(收盘价 × 成交量) / Σ成交量  (近似, 实际应使用 VWAP = Σ成交额 / Σ成交量)
  3) 中位数、最高、最低、波动率(标准差)、区间涨跌幅
"""

import json
import statistics
from pathlib import Path

BASE = Path(__file__).parent
RAW = BASE / "raw.json"

# 1. 读取原始数据
data = json.loads(RAW.read_text(encoding="utf-8"))
klines = data["data"]["klines"]

# 2. 解析每条记录
# 字段顺序: 日期,开盘,收盘,最高,最低,成交量,成交额,振幅,涨跌幅,涨跌额,换手率
records = []
for line in klines:
    parts = line.split(",")
    rec = {
        "date": parts[0],
        "open": float(parts[1]),
        "close": float(parts[2]),
        "high": float(parts[3]),
        "low": float(parts[4]),
        "volume": int(parts[5]),       # 成交量(手)
        "amount": float(parts[6]),     # 成交额(元)
        "amplitude": float(parts[7]),
        "change_pct": float(parts[8]),
        "change_amt": float(parts[9]),
        "turnover_rate": float(parts[10]),
    }
    records.append(rec)

print(f"交易日数量: {len(records)}")
print(f"首日: {records[0]['date']}, 末日: {records[-1]['date']}")

# 3. 计算指标
closes = [r["close"] for r in records]
volumes = [r["volume"] for r in records]
amounts = [r["amount"] for r in records]
highs = [r["high"] for r in records]
lows = [r["low"] for r in records]

# (1) 每日收盘价算术平均
arithmetic_mean = sum(closes) / len(closes)

# (2) 成交额加权平均价 VWAP = Σ成交额 / Σ成交量  (单位: 元)
#    注意: 成交量单位是"手", 1手 = 100股; 成交额单位是"元"
#    VWAP (元/股) = Σ成交额(元) / (Σ成交量(手) × 100)
total_amount = sum(amounts)
total_volume_shares = sum(volumes) * 100
vwap = total_amount / total_volume_shares

# (3) 另一种更常见的 VWAP 计算:  Σ(每日典型价 × 成交量) / Σ成交量
#     典型价 = (高+低+收)/3
typical_prices = [(h + l + c) / 3 for h, l, c in zip(highs, lows, closes)]
vwap_typical = sum(tp * v for tp, v in zip(typical_prices, volumes)) / sum(volumes)

# (4) 中位数
median_close = statistics.median(closes)

# (5) 最高 / 最低 (区间内出现的最高价最低价)
period_high = max(highs)
period_low = min(lows)

# (6) 收盘价标准差 (样本标准差) - 波动率
std_close = statistics.stdev(closes)

# (7) 区间涨跌幅 (Q2 第一天开盘 vs 最后一天收盘)
period_chg = (records[-1]["close"] / records[0]["open"] - 1) * 100

# (8) 总成交额、总成交量
total_volume_lots = sum(volumes)

print("\n" + "=" * 60)
print(f"【1】每日收盘价算术平均价: {arithmetic_mean:.4f} 元")
print(f"【2】成交额加权平均价 VWAP (Σ额/Σ量): {vwap:.4f} 元")
print(f"【3】VWAP (基于典型价): {vwap_typical:.4f} 元")
print(f"【4】中位数收盘价: {median_close:.4f} 元")
print(f"【5】区间最高价: {period_high:.2f} 元")
print(f"【6】区间最低价: {period_low:.2f} 元")
print(f"【7】收盘价标准差 (波动率): {std_close:.4f} 元")
print(f"【8】区间涨跌幅: {period_chg:+.2f}%")
print(f"【9】总成交额: {total_amount/1e8:.2f} 亿元")
print(f"【10】总成交量: {total_volume_lots/1e4:.2f} 万手")
print("=" * 60)

# 9. 输出每月分项
from collections import defaultdict
monthly = defaultdict(list)
for r in records:
    m = r["date"][:7]
    monthly[m].append(r)

print("\n【分月统计】")
for m in sorted(monthly.keys()):
    rs = monthly[m]
    cs = [x["close"] for x in rs]
    avg = sum(cs) / len(cs)
    print(f"  {m}: 交易日={len(rs)}, 收盘均价={avg:.4f}, 区间最高={max(x['high'] for x in rs):.2f}, 区间最低={min(x['low'] for x in rs):.2f}")

# 10. 保存为结构化 JSON
result = {
    "stock": "华天科技",
    "code": "002185",
    "period": "2025Q2 (2025-04-01 ~ 2025-06-30)",
    "data_source": "东方财富 push2his.eastmoney.com",
    "trading_days": len(records),
    "first_day": records[0]["date"],
    "last_day": records[-1]["date"],
    "metrics": {
        "arithmetic_mean_close": round(arithmetic_mean, 4),
        "vwap_amount_over_volume": round(vwap, 4),
        "vwap_typical_price": round(vwap_typical, 4),
        "median_close": round(median_close, 4),
        "period_high": period_high,
        "period_low": period_low,
        "std_close": round(std_close, 4),
        "period_change_pct": round(period_chg, 2),
        "total_amount_yi": round(total_amount / 1e8, 2),
        "total_volume_wan_shou": round(total_volume_lots / 1e4, 2),
    },
    "monthly": {
        m: {
            "trading_days": len(monthly[m]),
            "avg_close": round(sum(x["close"] for x in monthly[m]) / len(monthly[m]), 4),
            "high": max(x["high"] for x in monthly[m]),
            "low": min(x["low"] for x in monthly[m]),
        }
        for m in sorted(monthly.keys())
    },
    "daily": records,
}

out = BASE / "result.json"
out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n结果已保存到: {out}")