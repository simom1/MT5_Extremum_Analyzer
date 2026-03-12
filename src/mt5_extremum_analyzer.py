"""
MT5极值点分析器
分析市场高低点的形成规律，识别支撑阻力位
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from scipy.signal import argrelextrema
import matplotlib.pyplot as plt
from collections import defaultdict

# 设置中文字体
import matplotlib
import matplotlib.font_manager as fm
# 尝试查找系统中可用的中文字体
available_fonts = [f.name for f in fm.fontManager.ttflist]
chinese_fonts = ['SimHei', 'Microsoft YaHei', 'SimSun', 'STHeiti', 'Arial Unicode MS']
selected_fonts = [f for f in chinese_fonts if f in available_fonts]
if not selected_fonts:
    selected_fonts = ['sans-serif']

matplotlib.rcParams['font.sans-serif'] = selected_fonts + ['sans-serif']
matplotlib.rcParams['axes.unicode_minus'] = False
matplotlib.rcParams['font.family'] = 'sans-serif'

import os

class ExtremumAnalyzer:
    def __init__(self, symbol="XAUUSD", timeframe=mt5.TIMEFRAME_H1):
        self.symbol = symbol
        self.timeframe = timeframe
        self.extremum_data = []
        self.output_dir = "output"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
    def connect_mt5(self):
        """连接到MT5"""
        if not mt5.initialize():
            print(f"MT5初始化失败，错误代码: {mt5.last_error()}")
            return False
        
        print(f"MT5版本: {mt5.version()}")
        
        # 检查品种是否可用
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            print(f"品种 {self.symbol} 不存在")
            # 尝试显示可用的品种
            symbols = mt5.symbols_get()
            if symbols:
                print(f"\n可用品种示例（前20个）:")
                for i, s in enumerate(symbols[:20]):
                    print(f"  {s.name}")
            return False
        
        # 确保品种可见
        if not symbol_info.visible:
            print(f"品种 {self.symbol} 不可见，尝试启用...")
            if not mt5.symbol_select(self.symbol, True):
                print(f"无法启用品种 {self.symbol}")
                return False
        
        print(f"连接成功！品种: {self.symbol}")
        return True
    
    def get_historical_data(self, bars=1000):
        """获取历史数据"""
        rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, bars)
        
        if rates is None:
            print(f"获取数据失败: {mt5.last_error()}")
            return None
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df
    
    def find_extremum_points(self, df, order=5):
        """
        识别极值点
        order: 用于比较的相邻K线数量
        """
        # 找高点
        high_indices = argrelextrema(df['high'].values, np.greater, order=order)[0]
        # 找低点
        low_indices = argrelextrema(df['low'].values, np.less, order=order)[0]
        
        extremums = []
        
        # 处理高点
        for idx in high_indices:
            extremums.append({
                'index': idx,
                'time': df.iloc[idx]['time'],
                'price': df.iloc[idx]['high'],
                'type': 'high',
                'volume': df.iloc[idx]['tick_volume'],
                'close': df.iloc[idx]['close'],
                'open': df.iloc[idx]['open']
            })
        
        # 处理低点
        for idx in low_indices:
            extremums.append({
                'index': idx,
                'time': df.iloc[idx]['time'],
                'price': df.iloc[idx]['low'],
                'type': 'low',
                'volume': df.iloc[idx]['tick_volume'],
                'close': df.iloc[idx]['close'],
                'open': df.iloc[idx]['open']
            })
        
        # 按时间排序
        extremums.sort(key=lambda x: x['index'])
        return extremums
    
    def analyze_extremum_patterns(self, df, extremums):
        """分析极值点的规律"""
        patterns = {
            'time_intervals': [],  # 极值点之间的时间间隔
            'price_ranges': [],    # 极值点之间的价格波动
            'volume_analysis': [], # 极值点处的成交量特征
            'reversal_signals': [], # 反转信号
            'support_resistance': defaultdict(int)  # 支撑阻力位
        }
        
        for i in range(1, len(extremums)):
            prev = extremums[i-1]
            curr = extremums[i]
            
            # 时间间隔（K线数量）
            time_interval = curr['index'] - prev['index']
            patterns['time_intervals'].append(time_interval)
            
            # 价格波动
            price_range = abs(curr['price'] - prev['price'])
            patterns['price_ranges'].append({
                'range': price_range,
                'from_type': prev['type'],
                'to_type': curr['type'],
                'percentage': (price_range / prev['price']) * 100
            })
            
            # 成交量分析
            avg_volume = df.iloc[prev['index']:curr['index']]['tick_volume'].mean()
            patterns['volume_analysis'].append({
                'extremum_volume': curr['volume'],
                'avg_volume': avg_volume,
                'volume_ratio': curr['volume'] / avg_volume if avg_volume > 0 else 0,
                'type': curr['type']
            })
            
            # 识别反转信号
            if prev['type'] != curr['type']:
                reversal_strength = self._calculate_reversal_strength(df, prev, curr)
                patterns['reversal_signals'].append({
                    'from': prev['type'],
                    'to': curr['type'],
                    'strength': reversal_strength,
                    'price_change': price_range,
                    'time_bars': time_interval
                })
            
            # 统计支撑阻力位（价格聚类）
            price_level = round(curr['price'], 1)  # 精确到0.1
            patterns['support_resistance'][price_level] += 1
        
        return patterns
    
    def _calculate_reversal_strength(self, df, prev_extremum, curr_extremum):
        """计算反转强度"""
        start_idx = prev_extremum['index']
        end_idx = curr_extremum['index']
        
        if end_idx <= start_idx:
            return 0
        
        # 计算价格变化幅度
        price_change = abs(curr_extremum['price'] - prev_extremum['price'])
        price_change_pct = (price_change / prev_extremum['price']) * 100
        
        # 计算成交量变化
        volume_change = df.iloc[start_idx:end_idx]['tick_volume'].mean()
        
        # 综合评分
        strength = price_change_pct * (1 + volume_change / 1000)
        return strength
    
    def find_pattern_rules(self, patterns):
        """总结极值点规律"""
        rules = {}
        
        # 1. 时间间隔规律
        intervals = patterns['time_intervals']
        if intervals:
            rules['avg_interval'] = np.mean(intervals)
            rules['median_interval'] = np.median(intervals)
            rules['interval_std'] = np.std(intervals)
        
        # 2. 价格波动规律
        price_ranges = [p['range'] for p in patterns['price_ranges']]
        if price_ranges:
            rules['avg_price_range'] = np.mean(price_ranges)
            rules['median_price_range'] = np.median(price_ranges)
            
        # 3. 成交量特征
        volume_ratios = [v['volume_ratio'] for v in patterns['volume_analysis']]
        if volume_ratios:
            rules['avg_volume_ratio'] = np.mean(volume_ratios)
            rules['high_volume_extremums'] = sum(1 for r in volume_ratios if r > 1.5)
        
        # 4. 反转信号统计
        if patterns['reversal_signals']:
            rules['total_reversals'] = len(patterns['reversal_signals'])
            rules['avg_reversal_strength'] = np.mean([r['strength'] for r in patterns['reversal_signals']])
        
        # 5. 支撑阻力位（出现3次以上的价格位）
        strong_levels = {price: count for price, count in patterns['support_resistance'].items() if count >= 3}
        rules['strong_support_resistance'] = sorted(strong_levels.items(), key=lambda x: x[1], reverse=True)
        
        return rules
    
    def generate_report(self, df, extremums, patterns, rules):
        """生成分析报告"""
        report = []
        report.append("=" * 60)
        report.append(f"极值点分析报告 - {self.symbol}")
        report.append(f"时间框架: {self._get_timeframe_name()}")
        report.append(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 60)
        report.append("")
        
        report.append(f"数据范围: {df.iloc[0]['time']} 至 {df.iloc[-1]['time']}")
        report.append(f"总K线数: {len(df)}")
        report.append(f"识别的极值点数量: {len(extremums)}")
        report.append(f"  - 高点: {sum(1 for e in extremums if e['type'] == 'high')}")
        report.append(f"  - 低点: {sum(1 for e in extremums if e['type'] == 'low')}")
        report.append("")
        
        report.append("【规律总结】")
        report.append(f"1. 极值点平均间隔: {rules.get('avg_interval', 0):.1f} 根K线")
        report.append(f"   中位数间隔: {rules.get('median_interval', 0):.1f} 根K线")
        report.append(f"   标准差: {rules.get('interval_std', 0):.1f}")
        report.append("")
        
        report.append(f"2. 价格波动特征:")
        report.append(f"   平均波动: ${rules.get('avg_price_range', 0):.2f}")
        report.append(f"   中位数波动: ${rules.get('median_price_range', 0):.2f}")
        report.append("")
        
        report.append(f"3. 成交量特征:")
        report.append(f"   极值点平均成交量比: {rules.get('avg_volume_ratio', 0):.2f}x")
        report.append(f"   高成交量极值点: {rules.get('high_volume_extremums', 0)} 个")
        report.append("")
        
        report.append(f"4. 反转信号:")
        report.append(f"   总反转次数: {rules.get('total_reversals', 0)}")
        report.append(f"   平均反转强度: {rules.get('avg_reversal_strength', 0):.2f}")
        report.append("")
        
        report.append("5. 强支撑/阻力位 (出现3次以上):")
        for price, count in rules.get('strong_support_resistance', [])[:10]:
            report.append(f"   ${price:.1f} - 触及 {count} 次")
        report.append("")
        
        # 最近的极值点
        report.append("【最近10个极值点】")
        for extremum in extremums[-10:]:
            report.append(f"{extremum['time'].strftime('%Y-%m-%d %H:%M')} | "
                         f"{'高点' if extremum['type'] == 'high' else '低点'} | "
                         f"价格: ${extremum['price']:.2f} | "
                         f"成交量: {extremum['volume']}")
        
        return "\n".join(report)
    
    def _get_timeframe_name(self):
        """获取时间框架名称"""
        timeframes = {
            mt5.TIMEFRAME_M1: "1分钟",
            mt5.TIMEFRAME_M5: "5分钟",
            mt5.TIMEFRAME_M15: "15分钟",
            mt5.TIMEFRAME_M30: "30分钟",
            mt5.TIMEFRAME_H1: "1小时",
            mt5.TIMEFRAME_H4: "4小时",
            mt5.TIMEFRAME_D1: "日线",
        }
        return timeframes.get(self.timeframe, "未知")
    
    def visualize_extremums(self, df, extremums, save_path=None):
        """可视化极值点"""
        if save_path is None:
            save_path = os.path.join(self.output_dir, 'extremum_analysis.png')
        plt.figure(figsize=(15, 8))
        
        # 绘制价格线
        plt.plot(df['time'], df['close'], label='Close Price', alpha=0.5, linewidth=1)
        
        # 标记高点
        highs = [e for e in extremums if e['type'] == 'high']
        if highs:
            high_times = [e['time'] for e in highs]
            high_prices = [e['price'] for e in highs]
            plt.scatter(high_times, high_prices, color='red', marker='v', s=100, label='High', zorder=5)
        
        # 标记低点
        lows = [e for e in extremums if e['type'] == 'low']
        if lows:
            low_times = [e['time'] for e in lows]
            low_prices = [e['price'] for e in lows]
            plt.scatter(low_times, low_prices, color='green', marker='^', s=100, label='Low', zorder=5)
        
        plt.title(f'{self.symbol} Extremum Analysis - {self._get_timeframe_name()}', fontsize=14)
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        plt.savefig(save_path, dpi=150)
        print(f"Chart saved: {save_path}")
        plt.close()
    
    def save_results(self, extremums, patterns, rules, filename=None):
        """保存分析结果"""
        if filename is None:
            filename = os.path.join(self.output_dir, 'extremum_results.json')
        def convert_to_json_serializable(obj):
            """转换numpy类型为Python原生类型"""
            if isinstance(obj, (np.integer, np.int64, np.int32)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64, np.float32)):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: convert_to_json_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_json_serializable(item) for item in obj]
            return obj
        
        # 转换extremums
        extremums_serializable = []
        for e in extremums:
            e_copy = e.copy()
            e_copy['time'] = e_copy['time'].isoformat()
            e_copy['index'] = int(e_copy['index'])
            e_copy['volume'] = int(e_copy['volume'])
            extremums_serializable.append(e_copy)
        
        results = {
            'symbol': self.symbol,
            'timeframe': self._get_timeframe_name(),
            'analysis_time': datetime.now().isoformat(),
            'extremums': extremums_serializable,
            'rules': convert_to_json_serializable(rules),
            'patterns_summary': {
                'total_intervals': len(patterns['time_intervals']),
                'total_reversals': len(patterns['reversal_signals']),
                'support_resistance_levels': len(patterns['support_resistance'])
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"结果已保存到: {filename}")
    
    def run_analysis(self, bars=1000, order=5):
        """运行完整分析"""
        print("开始极值点分析...")
        
        # 连接MT5
        if not self.connect_mt5():
            return
        
        try:
            # 获取数据
            print(f"获取 {bars} 根K线数据...")
            df = self.get_historical_data(bars)
            if df is None:
                return
            
            print(f"数据获取成功: {len(df)} 根K线")
            
            # 识别极值点
            print(f"识别极值点 (order={order})...")
            extremums = self.find_extremum_points(df, order)
            print(f"识别到 {len(extremums)} 个极值点")
            
            # 分析规律
            print("分析极值点规律...")
            patterns = self.analyze_extremum_patterns(df, extremums)
            
            # 总结规律
            print("总结规律...")
            rules = self.find_pattern_rules(patterns)
            
            # 生成报告
            report = self.generate_report(df, extremums, patterns, rules)
            print("\n" + report)
            
            # 保存报告
            report_file = os.path.join(self.output_dir, f'extremum_report_{self.symbol}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"\n报告已保存到: {report_file}")
            
            # 可视化
            print("生成可视化图表...")
            self.visualize_extremums(df, extremums)
            
            # 保存JSON结果
            self.save_results(extremums, patterns, rules)
            
            print("\n分析完成！")
            
        finally:
            mt5.shutdown()
            print("MT5连接已关闭")

def main():
    """主函数"""
    print("MT5极值点分析器")
    print("=" * 60)
    
    # 使用默认参数
    symbol = "XAUUSD"
    timeframe = mt5.TIMEFRAME_H1
    bars = 1000
    order = 5
    
    print(f"使用默认参数运行: 品种={symbol}, 时间框架=1小时, K线数量={bars}, 敏感度={order}")
    
    # 创建分析器并运行
    analyzer = ExtremumAnalyzer(symbol=symbol, timeframe=timeframe)
    analyzer.run_analysis(bars=bars, order=order)

if __name__ == "__main__":
    main()
