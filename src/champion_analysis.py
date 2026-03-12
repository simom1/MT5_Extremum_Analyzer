"""
Champion Strategy Detailed Analysis
Runs 1000 bars backtest and reports detailed stats (Avg/Max TP/SL).
"""
import sys
import os
import MetaTrader5 as mt5
import pandas as pd

# Add src to path
sys.path.append(os.path.dirname(__file__))
from backtest_engine import ExtremumBacktester

def run_champion_analysis():
    symbol = "XAUUSD+"
    bars = 10000 # 增加到 10,000 根 K 线
    
    # Champion parameters: M5, Order=3, TP=2.0, SL=1.5
    print(f"Running Champion Strategy Analysis for {symbol} ({bars} bars)...")
    print("-" * 60)
    
    backtester = ExtremumBacktester(symbol=symbol, timeframe=mt5.TIMEFRAME_M5)
    res = backtester.run_backtest(
        bars=bars, 
        order=3, 
        tp_multiplier=2.0, 
        sl_multiplier=1.5,
        use_trend_filter=True,
        use_key_level_filter=True
    )
    
    if not backtester.history:
        print("No trades executed in this period.")
        return

    # Extract history and calculate stats
    history_df = pd.DataFrame(backtester.history)
    
    avg_tp_dist = history_df['tp_dist'].mean()
    max_tp_dist = history_df['tp_dist'].max()
    avg_sl_dist = history_df['sl_dist'].mean()
    max_sl_dist = history_df['sl_dist'].max()
    
    print("\n" + "=" * 60)
    print("CHAMPION STRATEGY - TP/SL STATISTICS")
    print("=" * 60)
    print(f"Average TP Distance: ${avg_tp_dist:.2f}")
    print(f"Maximum TP Distance: ${max_tp_dist:.2f}")
    print(f"Average SL Distance: ${avg_sl_dist:.2f}")
    print(f"Maximum SL Distance: ${max_sl_dist:.2f}")
    print("-" * 60)
    
    # Display detailed trade log
    print("\nDETAILED TRADE LOG (1000 Bars):")
    cols = ['entry_time', 'type', 'entry_price', 'exit_price', 'pnl', 'reason', 'tp_dist', 'sl_dist']
    print(history_df[cols].to_string(index=False))
    
    # Save to CSV
    output_file = os.path.join("output", "champion_1000_bars_analysis.csv")
    history_df.to_csv(output_file, index=False)
    print(f"\nDetailed trade log saved to: {output_file}")

if __name__ == "__main__":
    try:
        run_champion_analysis()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        mt5.shutdown()
