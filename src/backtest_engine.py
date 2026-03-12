"""
Extremum Strategy Backtesting Engine
Simulates trading based on confirmed extremum points.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mt5_extremum_analyzer import ExtremumAnalyzer
import MetaTrader5 as mt5
from datetime import datetime
import os

class ExtremumBacktester:
    def __init__(self, symbol="XAUUSD+", timeframe=mt5.TIMEFRAME_H1, initial_balance=10000.0):
        self.symbol = symbol
        self.timeframe = timeframe
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.equity = [initial_balance]
        self.positions = []  # List of open positions
        self.history = []    # List of closed trades
        self.output_dir = "output"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def calculate_indicators(self, df):
        """计算技术指标"""
        # 1. EMA 100 (趋势过滤)
        df['ema_100'] = df['close'].ewm(span=100, adjust=False).mean()
        
        # 2. ATR (用于动态 TP/SL)
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        df['atr'] = true_range.rolling(14).mean()
        
        # 3. RSI (超买超卖过滤)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        return df

    def run_backtest(self, bars=2000, order=3, tp_multiplier=2.0, sl_multiplier=1.0, use_trend_filter=True, use_key_level_filter=True):
        """
        运行优化后的回测。
        """
        # 使用初始化时指定的 timeframe
        analyzer = ExtremumAnalyzer(self.symbol, self.timeframe)
        if not analyzer.connect_mt5():
            return
        
        df = analyzer.get_historical_data(bars)
        mt5.shutdown()
        
        if df is None or len(df) == 0:
            print("Failed to get data for backtest.")
            return

        # 计算指标
        df = self.calculate_indicators(df)
        
        # 获取极值点和成交量分布
        extremums = analyzer.find_extremum_points(df, order)
        poc_price, hvn_levels = analyzer.calculate_volume_profile(df)
        
        # 分析极值点规律获取平均波动范围
        patterns = analyzer.analyze_extremum_patterns(df, extremums)
        rules = analyzer.find_pattern_rules(patterns)
        avg_ext_range = rules.get('avg_price_range', 100.0)
        
        # 计算成交量均值
        avg_vol = df['tick_volume'].mean()
        
        # 整理信号点
        signals = {}
        filter_stats = {'total': len(extremums), 'trend_filtered': 0, 'key_level_filtered': 0, 'volume_filtered': 0, 'rsi_filtered': 0, 'passed': 0}
        
        for e in extremums:
            confirm_idx = e['index'] + order
            if confirm_idx >= len(df): continue
            
            price = e['price']
            vol = e['volume']
            rsi = df.iloc[confirm_idx]['rsi']
            is_near_key_level = False
            
            # 1. 关键位过滤 (容差 0.5%)
            if use_key_level_filter and poc_price:
                all_levels = [poc_price] + hvn_levels
                for level in all_levels:
                    if abs(price - level) / level < 0.005:
                        is_near_key_level = True
                        break
            else:
                is_near_key_level = True
            
            if not is_near_key_level:
                filter_stats['key_level_filtered'] += 1
                continue

            # 2. 趋势过滤
            ema = df.iloc[confirm_idx]['ema_100']
            is_trend_aligned = True
            if use_trend_filter:
                if e['type'] == 'low' and price < ema: is_trend_aligned = False
                if e['type'] == 'high' and price > ema: is_trend_aligned = False
            
            if not is_trend_aligned:
                filter_stats['trend_filtered'] += 1
                continue
            
            # 3. 成交量过滤
            if vol < avg_vol:
                filter_stats['volume_filtered'] += 1
                continue
            
            # 4. RSI 过滤：避免在超买区买入，超卖区卖出
            if e['type'] == 'low' and rsi > 70: 
                filter_stats['rsi_filtered'] += 1
                continue
            if e['type'] == 'high' and rsi < 30:
                filter_stats['rsi_filtered'] += 1
                continue
            
            # 综合信号强度
            signals[confirm_idx] = 1 if e['type'] == 'low' else -1
            filter_stats['passed'] += 1

        print(f"Backtest Start: {df.iloc[0]['time']} to {df.iloc[-1]['time']}")
        print(f"Initial Balance: ${self.initial_balance}")
        print(f"Average Extremum Range: ${avg_ext_range:.2f}")
        print(f"Filters: Trend={use_trend_filter}, KeyLevel={use_key_level_filter}, Volume=True, RSI=True")
        print(f"Signal Stats: Total={filter_stats['total']}, Passed={filter_stats['passed']}, "
              f"TrendFiltered={filter_stats['trend_filtered']}, KeyLevelFiltered={filter_stats['key_level_filtered']}, "
              f"VolumeFiltered={filter_stats['volume_filtered']}, RSIFiltered={filter_stats['rsi_filtered']}")

        # 交易模拟
        current_pos = None
        entry_price = 0
        tp_price = 0
        sl_price = 0
        is_breakeven = False
        peak_price = 0  # 追踪最高/最低价
        
        # 使用极值点平均波幅和 ATR 的较大值作为基准
        for i in range(len(df)):
            row = df.iloc[i]
            price = row['close']
            atr = row['atr'] if not np.isnan(row['atr']) else 1.0
            
            # 动态调整基准：专为“20-50 盈利”设计的剥头皮模式
            # 黄金 H1 波动大，我们取 ATR 和极值规律的较小部分作为剥头皮基准
            base_range = max(3.0, atr * 1.5) # 保证至少有 $3 的空间基准
            
            # 1. 检查止盈止损和移动止损
            if current_pos:
                if current_pos == 'long':
                    # 更新最高价
                    peak_price = max(peak_price, row['high'])
                    
                    # 极速保本逻辑：
                    # a. 只要获利达到 TP 的 30%，立即移动止损到保本，确保不亏
                    if not is_breakeven and peak_price >= entry_price + (tp_price - entry_price) * 0.3:
                        sl_price = entry_price
                        is_breakeven = True
                    
                    # b. 阶梯追踪：获利超过 TP 一半后，止损紧跟其后 (保持 0.4 * base_range 间距)
                    if peak_price >= entry_price + (tp_price - entry_price) * 0.6:
                        sl_price = max(sl_price, peak_price - (0.4 * base_range))
                    
                    if row['high'] >= tp_price:
                        self._close_trade(tp_price, row['time'], "TP")
                        current_pos = None
                    elif row['low'] <= sl_price:
                        self._close_trade(sl_price, row['time'], "SL/BE/Trailing")
                        current_pos = None
                        
                elif current_pos == 'short':
                    # 更新最低价
                    peak_price = min(peak_price, row['low'])
                    
                    # a. 极速保本
                    if not is_breakeven and peak_price <= entry_price - (entry_price - tp_price) * 0.3:
                        sl_price = entry_price
                        is_breakeven = True
                        
                    # b. 阶梯追踪
                    if peak_price <= entry_price - (entry_price - tp_price) * 0.6:
                        sl_price = min(sl_price, peak_price + (0.4 * base_range))
                        
                    if row['low'] <= tp_price:
                        self._close_trade(tp_price, row['time'], "TP")
                        current_pos = None
                    elif row['high'] >= sl_price:
                        self._close_trade(sl_price, row['time'], "SL/BE/Trailing")
                        current_pos = None

            # 2. 检查新信号
            if i in signals and current_pos is None:
                sig = signals[i]
                entry_price = price
                is_breakeven = False
                peak_price = price
                
                # 核心剥头皮设置：短 TP (目标 $20-$50), 宽 SL (抗震荡)
                if sig == 1:
                    current_pos = 'long'
                    tp_price = entry_price + (base_range * tp_multiplier)
                    sl_price = entry_price - (base_range * sl_multiplier)
                else:
                    current_pos = 'short'
                    tp_price = entry_price - (base_range * tp_multiplier)
                    sl_price = entry_price + (base_range * sl_multiplier)
                
                self.positions.append({
                    'type': current_pos, 
                    'entry_price': entry_price, 
                    'entry_time': row['time'],
                    'tp_dist': abs(tp_price - entry_price),
                    'sl_dist': abs(sl_price - entry_price)
                })

            self.equity.append(self.balance)

        self._generate_report(df)
        
        # 返回回测摘要数据用于网格搜索
        if not self.history:
            return None
            
        trades_df = pd.DataFrame(self.history)
        win_rate = (trades_df['pnl'] > 0).mean() * 100
        total_pnl = trades_df['pnl'].sum()
        profit_factor = trades_df[trades_df['pnl'] > 0]['pnl'].sum() / abs(trades_df[trades_df['pnl'] < 0]['pnl'].sum()) if any(trades_df['pnl'] < 0) else 99.0
        
        return {
            'total_trades': len(trades_df),
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'profit_factor': profit_factor,
            'final_balance': self.balance
        }

    def _close_trade(self, exit_price, exit_time, reason):
        if not self.positions:
            return
            
        pos = self.positions.pop(0)
        pnl = 0
        if pos['type'] == 'long':
            pnl = (exit_price - pos['entry_price']) * 10  # Simplified: 10 units per point
        else:
            pnl = (pos['entry_price'] - exit_price) * 10
            
        self.balance += pnl
        self.history.append({
            'type': pos['type'],
            'entry_price': pos['entry_price'],
            'exit_price': exit_price,
            'pnl': pnl,
            'entry_time': pos['entry_time'],
            'exit_time': exit_time,
            'reason': reason,
            'tp_dist': pos.get('tp_dist', 0),
            'sl_dist': pos.get('sl_dist', 0)
        })

    def _generate_report(self, df):
        if not self.history:
            print("No trades executed.")
            return

        trades_df = pd.DataFrame(self.history)
        win_rate = (trades_df['pnl'] > 0).mean() * 100
        total_pnl = trades_df['pnl'].sum()
        profit_factor = trades_df[trades_df['pnl'] > 0]['pnl'].sum() / abs(trades_df[trades_df['pnl'] < 0]['pnl'].sum()) if any(trades_df['pnl'] < 0) else float('inf')
        
        report = []
        report.append("=" * 60)
        report.append(f"Backtest Report: {self.symbol}")
        report.append(f"Period: {df.iloc[0]['time']} to {df.iloc[-1]['time']}")
        report.append("=" * 60)
        report.append(f"Total Trades: {len(trades_df)}")
        report.append(f"Win Rate: {win_rate:.2f}%")
        report.append(f"Total Profit/Loss: ${total_pnl:.2f}")
        report.append(f"Final Balance: ${self.balance:.2f}")
        report.append(f"Profit Factor: {profit_factor:.2f}")
        report.append(f"Max Consecutive Wins: {self._get_max_consecutive(trades_df['pnl'] > 0)}")
        report.append(f"Max Consecutive Losses: {self._get_max_consecutive(trades_df['pnl'] < 0)}")
        
        report_text = "\n".join(report)
        print("\n" + report_text)
        
        # Save Report
        report_file = os.path.join(self.output_dir, f"backtest_report_{self.symbol}.txt")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
            
        # Visualization
        self._plot_results(df)

    def _get_max_consecutive(self, series):
        max_consecutive = 0
        current_consecutive = 0
        for val in series:
            if val:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        return max_consecutive

    def _plot_results(self, df):
        plt.figure(figsize=(15, 10))
        
        # Subplot 1: Price and Trades
        plt.subplot(2, 1, 1)
        plt.plot(df['time'], df['close'], label='Price', alpha=0.5)
        if 'ema_200' in df.columns:
            plt.plot(df['time'], df['ema_200'], label='EMA 200', color='orange', alpha=0.8, linestyle='--')
        
        for trade in self.history:
            color = 'g' if trade['pnl'] > 0 else 'r'
            plt.scatter(trade['entry_time'], trade['entry_price'], color='blue', marker='o', s=30)
            plt.scatter(trade['exit_time'], trade['exit_price'], color=color, marker='x', s=50)
            plt.plot([trade['entry_time'], trade['exit_time']], [trade['entry_price'], trade['exit_price']], color=color, linestyle='--', alpha=0.3)

        plt.title(f'{self.symbol} Strategy Backtest - Price & Trades')
        plt.legend()
        plt.grid(True, alpha=0.3)

        # Subplot 2: Equity Curve
        plt.subplot(2, 1, 2)
        plt.plot(self.equity, color='blue', label='Equity Curve')
        plt.axhline(y=self.initial_balance, color='red', linestyle='--', alpha=0.5)
        plt.title('Equity Curve')
        plt.xlabel('Bars')
        plt.ylabel('Balance ($)')
        plt.legend()
        plt.grid(True, alpha=0.3)

        plt.tight_layout()
        save_path = os.path.join(self.output_dir, 'backtest_results.png')
        plt.savefig(save_path, dpi=150)
        print(f"Backtest chart saved: {save_path}")
        plt.close()

if __name__ == "__main__":
    backtester = ExtremumBacktester(symbol="XAUUSD+", timeframe=mt5.TIMEFRAME_H1)
    backtester.run_backtest(bars=2000)
