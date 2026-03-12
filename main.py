"""
MT5 Extremum Analyzer - One-Click Console
Integrates Analysis, Backtesting, and Real-time Monitoring.
"""
import sys
import os

# 将 src 目录添加到 Python 路径，以便导入模块
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import MetaTrader5 as mt5
from mt5_extremum_analyzer import ExtremumAnalyzer
from backtest_engine import ExtremumBacktester
from realtime_monitor import RealtimeMonitor
from datetime import datetime

def print_header(title):
    print("\n" + "=" * 60)
    print(f" {title} ".center(60, "="))
    print("=" * 60)

def main():
    symbol = "XAUUSD+"
    
    print_header("MT5 Extremum Analyzer Pro")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Symbol: {symbol}")
    
    # 1. 初始分析
    print_header("Step 1: Market Analysis")
    analyzer = ExtremumAnalyzer(symbol=symbol)
    analyzer.run_analysis() # 修正方法名，之前是 run()
    
    # 2. 策略回测
    print_header("Step 2: Strategy Backtesting")
    print("Running backtest with Long-term Champion parameters (M5, Order=3, TP=2.0, SL=1.5)...")
    # 使用长周期验证出的最强参数组合
    backtester = ExtremumBacktester(symbol=symbol, timeframe=mt5.TIMEFRAME_M5)
    # TP=2.0, SL=1.5, Order=3 是长周期表现最稳健的组合 (PF 1.74)
    backtester.run_backtest(bars=5000, order=3, tp_multiplier=2.0, sl_multiplier=1.5, use_trend_filter=True)
    
    # 3. 实时监控选择
    print_header("Step 3: Real-time Monitoring")
    choice = input("Do you want to start Real-time Monitoring? (y/n): ").lower()
    
    if choice == 'y':
        print("\n[INFO] Alerts will be logged to 'output/alerts.log'")
        print("[INFO] Multi-timeframe resonance will trigger a Windows popup.")
        # 实时监控也同步使用 M5 作为核心参考
        monitor = RealtimeMonitor(symbol=symbol)
        # 使用最佳确认参数 (order=3)
        monitor.start(interval_sec=60, order=3)
    else:
        print("\nExiting. All reports and charts are in the 'output/' folder.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] An error occurred: {e}")
        mt5.shutdown()
        sys.exit(1)
