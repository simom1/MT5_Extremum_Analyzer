"""
MT5 Extremum Strategy - Top 5 Long-term Validation
Runs backtests on the Top 5 parameter combinations over 10,000 bars.
"""
import sys
import os
import MetaTrader5 as mt5
import pandas as pd

# Add src to path
sys.path.append(os.path.dirname(__file__))
from backtest_engine import ExtremumBacktester

def run_long_term_validation():
    symbol = "XAUUSD+"
    bars = 10000  # 大约覆盖 3-5 个月的 M5 数据
    
    # 定义 Top 5 参数组合
    top_5_configs = [
        {"tf_name": "M5", "tf_val": mt5.TIMEFRAME_M5, "order": 3, "tp": 2.0, "sl": 1.0},
        {"tf_name": "M5", "tf_val": mt5.TIMEFRAME_M5, "order": 3, "tp": 2.0, "sl": 1.5},
        {"tf_name": "M15", "tf_val": mt5.TIMEFRAME_M15, "order": 5, "tp": 2.0, "sl": 1.0},
        {"tf_name": "M5", "tf_val": mt5.TIMEFRAME_M5, "order": 3, "tp": 2.0, "sl": 2.0},
        {"tf_name": "M5", "tf_val": mt5.TIMEFRAME_M5, "order": 5, "tp": 2.0, "sl": 1.5}
    ]
    
    results = []
    
    print(f"Starting Long-term Validation (10,000 bars) for {symbol}...")
    print("-" * 80)

    for i, config in enumerate(top_5_configs):
        print(f"[{i+1}/5] Testing: TF={config['tf_name']}, Order={config['order']}, TP={config['tp']}, SL={config['sl']}...")
        
        backtester = ExtremumBacktester(symbol=symbol, timeframe=config['tf_val'])
        res = backtester.run_backtest(
            bars=bars, 
            order=config['order'], 
            tp_multiplier=config['tp'], 
            sl_multiplier=config['sl'],
            use_trend_filter=True,
            use_key_level_filter=True
        )
        
        if res:
            res['tf'] = config['tf_name']
            res['order'] = config['order']
            res['tp_mult'] = config['tp']
            res['sl_mult'] = config['sl']
            results.append(res)

    print("\nLong-term Validation Complete!\n")
    
    # 转换为 DataFrame 并显示
    df_results = pd.DataFrame(results)
    df_sorted = df_results.sort_values(by='profit_factor', ascending=False)
    
    print("Long-term Performance (Sorted by Profit Factor):")
    print("-" * 100)
    header_str = f"{'Rank':<5} {'TF':<6} {'Order':<6} {'TP':<6} {'SL':<6} {'Trades':<8} {'WinRate%':<10} {'PF':<8} {'Total PnL':<12}"
    print(header_str)
    print("-" * 100)
    
    for idx, row in enumerate(df_sorted.iterrows()):
        row = row[1]
        row_str = f"#{idx+1:<4} {row['tf']:<6} {row['order']:<6} {row['tp_mult']:<6} {row['sl_mult']:<6} " \
                  f"{int(row['total_trades']):<8} {row['win_rate']:<10.1f} {row['profit_factor']:<8.2f} ${row['total_pnl']:<12.2f}"
        print(row_str)
    print("-" * 100)
    
    # 保存结果
    output_file = os.path.join("output", "long_term_validation_results.csv")
    df_sorted.to_csv(output_file, index=False)
    print(f"\nLong-term results saved to: {output_file}")

if __name__ == "__main__":
    try:
        run_long_term_validation()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        mt5.shutdown()
