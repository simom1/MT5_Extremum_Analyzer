"""
多周期极值点规律对比分析
找出规律最明显的时间周期
"""
from mt5_extremum_analyzer import ExtremumAnalyzer
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import json

import os

class MultiTimeframeExtremumFinder:
    def __init__(self, symbol="XAUUSD+"):
        self.symbol = symbol
        self.results = []
        self.output_dir = "output"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
    def analyze_all_timeframes(self, min_timeframe="M5"):
        """分析所有时间周期"""
        # 定义要分析的时间周期（从5分钟开始）
        timeframes = [
            (mt5.TIMEFRAME_M5, "5分钟", 2000, 5),
            (mt5.TIMEFRAME_M15, "15分钟", 1500, 5),
            (mt5.TIMEFRAME_M30, "30分钟", 1000, 5),
            (mt5.TIMEFRAME_H1, "1小时", 1000, 5),
            (mt5.TIMEFRAME_H4, "4小时", 800, 5),
            (mt5.TIMEFRAME_D1, "日线", 500, 5),
        ]
        
        print("=" * 80)
        print(f"多周期极值点规律分析 - {self.symbol}")
        print("=" * 80)
        print()
        
        for tf, name, bars, order in timeframes:
            print(f"\n{'='*80}")
            print(f"正在分析: {name} 周期")
            print(f"{'='*80}")
            
            try:
                analyzer = ExtremumAnalyzer(symbol=self.symbol, timeframe=tf)
                
                # 连接MT5
                if not analyzer.connect_mt5():
                    print(f"❌ {name} - 连接失败")
                    continue
                
                # 获取数据
                df = analyzer.get_historical_data(bars)
                if df is None or len(df) == 0:
                    print(f"❌ {name} - 数据获取失败")
                    mt5.shutdown()
                    continue
                
                # 识别极值点
                extremums = analyzer.find_extremum_points(df, order)
                if len(extremums) < 10:
                    print(f"❌ {name} - 极值点太少 ({len(extremums)}个)")
                    mt5.shutdown()
                    continue
                
                # 分析规律
                patterns = analyzer.analyze_extremum_patterns(df, extremums)
                rules = analyzer.find_pattern_rules(patterns)
                
                # 计算规律性评分
                regularity_score = self._calculate_regularity_score(rules, patterns, extremums, len(df))
                
                # 保存结果
                result = {
                    'timeframe': name,
                    'timeframe_code': tf,
                    'total_bars': len(df),
                    'extremum_count': len(extremums),
                    'high_count': sum(1 for e in extremums if e['type'] == 'high'),
                    'low_count': sum(1 for e in extremums if e['type'] == 'low'),
                    'regularity_score': regularity_score,
                    'rules': rules,
                    'patterns': {
                        'avg_interval': rules.get('avg_interval', 0),
                        'interval_std': rules.get('interval_std', 0),
                        'avg_price_range': rules.get('avg_price_range', 0),
                        'avg_volume_ratio': rules.get('avg_volume_ratio', 0),
                        'total_reversals': rules.get('total_reversals', 0),
                        'strong_levels_count': len(rules.get('strong_support_resistance', []))
                    }
                }
                
                self.results.append(result)
                
                # 显示简要结果
                print(f"✓ {name} 分析完成")
                print(f"  极值点数量: {len(extremums)}")
                print(f"  平均间隔: {rules.get('avg_interval', 0):.1f} 根K线")
                print(f"  间隔标准差: {rules.get('interval_std', 0):.1f}")
                print(f"  规律性评分: {regularity_score:.2f}")
                
                mt5.shutdown()
                
            except Exception as e:
                print(f"❌ {name} - 分析出错: {str(e)}")
                mt5.shutdown()
                continue
        
        return self.results
    
    def _calculate_regularity_score(self, rules, patterns, extremums, total_bars):
        """
        计算规律性评分（0-100分）
        分数越高，规律性越强
        """
        score = 0
        
        # 1. 时间间隔规律性 (30分)
        avg_interval = rules.get('avg_interval', 0)
        interval_std = rules.get('interval_std', 0)
        if avg_interval > 0:
            # 变异系数越小，规律性越强
            cv = interval_std / avg_interval
            interval_score = max(0, 30 - cv * 30)
            score += interval_score
        
        # 2. 极值点密度 (20分)
        extremum_density = len(extremums) / total_bars
        # 理想密度在 0.05-0.15 之间
        if 0.05 <= extremum_density <= 0.15:
            density_score = 20
        elif extremum_density < 0.05:
            density_score = extremum_density / 0.05 * 20
        else:
            density_score = max(0, 20 - (extremum_density - 0.15) * 100)
        score += density_score
        
        # 3. 反转信号质量 (20分)
        total_reversals = rules.get('total_reversals', 0)
        if total_reversals > 0:
            avg_reversal_strength = rules.get('avg_reversal_strength', 0)
            # 反转强度在20-50之间较理想
            if 20 <= avg_reversal_strength <= 50:
                reversal_score = 20
            elif avg_reversal_strength < 20:
                reversal_score = avg_reversal_strength / 20 * 20
            else:
                reversal_score = max(0, 20 - (avg_reversal_strength - 50) / 10)
            score += reversal_score
        
        # 4. 支撑阻力位强度 (15分)
        strong_levels = len(rules.get('strong_support_resistance', []))
        # 有3-10个强支撑阻力位较理想
        if 3 <= strong_levels <= 10:
            sr_score = 15
        elif strong_levels < 3:
            sr_score = strong_levels / 3 * 15
        else:
            sr_score = max(0, 15 - (strong_levels - 10))
        score += sr_score
        
        # 5. 成交量一致性 (15分)
        avg_volume_ratio = rules.get('avg_volume_ratio', 0)
        # 极值点处成交量应该明显高于平均
        if avg_volume_ratio >= 1.3:
            volume_score = 15
        else:
            volume_score = (avg_volume_ratio - 1) / 0.3 * 15
        score += max(0, volume_score)
        
        return min(100, max(0, score))
    
    def generate_comparison_report(self):
        """生成对比报告"""
        if not self.results:
            return "没有分析结果"
        
        # 按规律性评分排序
        sorted_results = sorted(self.results, key=lambda x: x['regularity_score'], reverse=True)
        
        report = []
        report.append("=" * 80)
        report.append(f"多周期极值点规律对比报告 - {self.symbol}")
        report.append(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)
        report.append("")
        
        report.append("【规律性排名】（分数越高，规律越明显）")
        report.append("")
        
        for i, result in enumerate(sorted_results, 1):
            report.append(f"{i}. {result['timeframe']} - 规律性评分: {result['regularity_score']:.2f}/100")
            report.append(f"   极值点数量: {result['extremum_count']} (高点:{result['high_count']}, 低点:{result['low_count']})")
            report.append(f"   平均间隔: {result['patterns']['avg_interval']:.1f} 根K线")
            report.append(f"   间隔标准差: {result['patterns']['interval_std']:.1f}")
            report.append(f"   平均波动: ${result['patterns']['avg_price_range']:.2f}")
            report.append(f"   强支撑/阻力位: {result['patterns']['strong_levels_count']} 个")
            report.append("")
        
        # 推荐最佳周期
        best = sorted_results[0]
        report.append("=" * 80)
        report.append("【推荐使用周期】")
        report.append("")
        report.append(f"🏆 最佳周期: {best['timeframe']}")
        report.append(f"   规律性评分: {best['regularity_score']:.2f}/100")
        report.append("")
        report.append("【推荐理由】")
        
        # 分析推荐理由
        if best['patterns']['interval_std'] / best['patterns']['avg_interval'] < 0.5:
            report.append(f"✓ 时间间隔规律性强（变异系数: {best['patterns']['interval_std'] / best['patterns']['avg_interval']:.2f}）")
        
        if 0.05 <= best['extremum_count'] / best['total_bars'] <= 0.15:
            report.append(f"✓ 极值点密度适中（{best['extremum_count']}/{best['total_bars']} = {best['extremum_count']/best['total_bars']:.2%}）")
        
        if best['patterns']['strong_levels_count'] >= 3:
            report.append(f"✓ 有明显的支撑阻力位（{best['patterns']['strong_levels_count']}个）")
        
        if best['patterns']['avg_volume_ratio'] >= 1.2:
            report.append(f"✓ 极值点处成交量明显放大（{best['patterns']['avg_volume_ratio']:.2f}x）")
        
        report.append("")
        report.append("【交易建议】")
        report.append(f"1. 使用 {best['timeframe']} 周期识别极值点")
        report.append(f"2. 极值点大约每 {best['patterns']['avg_interval']:.0f} 根K线出现一次")
        report.append(f"3. 平均波动约 ${best['patterns']['avg_price_range']:.2f}，可据此设置止损止盈")
        
        if best['patterns']['strong_levels_count'] > 0:
            report.append(f"4. 关注强支撑/阻力位，这些位置容易形成极值点")
        
        report.append("")
        
        # 详细数据表格
        report.append("=" * 80)
        report.append("【详细对比数据】")
        report.append("")
        report.append(f"{'周期':<10} {'评分':<8} {'极值点':<8} {'平均间隔':<10} {'标准差':<10} {'强支撑位':<10}")
        report.append("-" * 80)
        
        for result in sorted_results:
            report.append(
                f"{result['timeframe']:<10} "
                f"{result['regularity_score']:<8.2f} "
                f"{result['extremum_count']:<8} "
                f"{result['patterns']['avg_interval']:<10.1f} "
                f"{result['patterns']['interval_std']:<10.1f} "
                f"{result['patterns']['strong_levels_count']:<10}"
            )
        
        return "\n".join(report)
    
    def save_comparison_results(self, filename=None):
        """保存对比结果"""
        if filename is None:
            filename = os.path.join(self.output_dir, 'multi_timeframe_comparison.json')
        data = {
            'symbol': self.symbol,
            'analysis_time': datetime.now().isoformat(),
            'results': self.results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"对比结果已保存到: {filename}")
    
    def run(self):
        """运行完整分析"""
        # 分析所有周期
        self.analyze_all_timeframes()
        
        if not self.results:
            print("\n❌ 没有成功分析的周期")
            return
        
        # 生成报告
        print("\n\n")
        report = self.generate_comparison_report()
        print(report)
        
        # 保存报告
        report_file = os.path.join(self.output_dir, f'multi_timeframe_report_{self.symbol}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n报告已保存到: {report_file}")
        
        # 保存JSON
        self.save_comparison_results()
        
        print("\n✓ 多周期分析完成！")

def main():
    """主函数"""
    symbol = "XAUUSD+"
    
    print("=" * 80)
    print("多周期极值点规律分析器")
    print("自动分析 5分钟、15分钟、30分钟、1小时、4小时、日线")
    print("找出规律最明显的时间周期")
    print("=" * 80)
    print()
    
    finder = MultiTimeframeExtremumFinder(symbol=symbol)
    finder.run()

if __name__ == "__main__":
    main()
