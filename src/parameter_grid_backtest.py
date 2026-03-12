"""
Extremum Strategy - Parameter Grid Search
Runs multiple backtests to find the optimal timeframe and TP/SL settings.
"""
import sys
import os
import MetaTrader5 as mt5
import pandas as pd

# Add src to path
sys.path.append(os.path.dirname(__file__))
from backtest_engine import ExtremumBacktester

def run_grid_search():
    symbol = "XAUUSD+"
    
    # 定义网格参数
    timeframes = {
        "M5": mt5.TIMEFRAME_M5,
        "M15": mt5.TIMEFRAME_M15,
        "H1": mt5.TIMEFRAME_H1
    }
    
    tp_multipliers = [1.0, 1.5, 2.0]
    sl_multipliers = [1.0, 1.5, 2.0]
    orders = [3, 5]
    
    results = []
    
    print(f"Starting Grid Search for {symbol}...")
    print("Testing Timeframes: M5, M15, H1")
    print("-" * 60)

    for tf_name, tf_val in timeframes.items():
        for order in orders:
            for tp_mult in tp_multipliers:
                for sl_mult in sl_multipliers:
                    print(f"Testing: TF={tf_name}, Order={order}, TP={tp_mult}, SL={sl_mult}...", end="\r")
                    
                    backtester = ExtremumBacktester(symbol=symbol, timeframe=tf_val)
                    # 我们在网格搜索中静默运行回测 (通过重定向 stdout 或修改代码，这里我们简单处理)
                    # 运行 3000 根 K 线以获得更多样本
                    res = backtester.run_backtest(
                        bars=3000, 
                        order=order, 
                        tp_multiplier=tp_mult, 
                        sl_multiplier=sl_mult,
                        use_trend_filter=True,
                        use_key_level_filter=True
                    )
                    
                    if res:
                        res['tf'] = tf_name
                        res['order'] = order
                        res['tp_mult'] = tp_mult
                        res['sl_mult'] = sl_mult
                        results.append(res)

    print("\nGrid Search Complete!\n")
    
    # 转换为 DataFrame 并排序
    df_results = pd.DataFrame(results)
    
    # 按照 Profit Factor 排序
    df_sorted = df_results.sort_values(by='profit_factor', ascending=False)
    
    # 打印前 15 个最佳结果
    headers = ["TF", "Order", "TP", "SL", "Trades", "WinRate%", "PF", "Total PnL"]
    table_data = []
    for _, row in df_sorted.head(15).iterrows():
        table_data.append([
            row['tf'], row['order'], row['tp_mult'], row['sl_mult'],
            row['total_trades'], f"{row['win_rate']:.1f}", 
            f"{row['profit_factor']:.2f}", f"${row['total_pnl']:.2f}"
        ])
    
    print("Top 15 Parameter Combinations (Sorted by Profit Factor):")
    print("-" * 100)
    header_str = f"{'TF':<6} {'Order':<6} {'TP':<6} {'SL':<6} {'Trades':<8} {'WinRate%':<10} {'PF':<8} {'Total PnL':<12}"
    print(header_str)
    print("-" * 100)
    
    for _, row in df_sorted.head(15).iterrows():
        row_str = f"{row['tf']:<6} {row['order']:<6} {row['tp_mult']:<6} {row['sl_mult']:<6} " \
                  f"{int(row['total_trades']):<8} {row['win_rate']:<10.1f} {row['profit_factor']:<8.2f} ${row['total_pnl']:<12.2f}"
        print(row_str)
    print("-" * 100)
    
    # 保存结果到 CSV
    output_file = os.path.join("output", "grid_search_results.csv")
    df_sorted.to_csv(output_file, index=False)
    print(f"\nFull results saved to: {output_file}")

if __name__ == "__main__":
    try:
        run_grid_search()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        mt5.shutdown()
