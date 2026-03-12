"""
直接运行XAUUSD+极值点分析
"""
from mt5_extremum_analyzer import ExtremumAnalyzer
import MetaTrader5 as mt5

# 配置参数
symbol = "XAUUSD+"
timeframe = mt5.TIMEFRAME_H1  # 1小时
bars = 1000
order = 5

print("=" * 60)
print(f"开始分析 {symbol}")
print(f"时间框架: 1小时")
print(f"K线数量: {bars}")
print(f"敏感度: {order}")
print("=" * 60)
print()

# 创建分析器并运行
analyzer = ExtremumAnalyzer(symbol=symbol, timeframe=timeframe)
analyzer.run_analysis(bars=bars, order=order)
