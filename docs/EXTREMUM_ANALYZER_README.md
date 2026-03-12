# MT5极值点分析器使用说明

## 功能概述

这个程序连接到本地MT5，分析市场的高低点（极值点），找出它们形成的规律，帮助识别支撑阻力位和市场反转信号。

## 主要功能

1. **极值点识别** - 自动识别价格的局部高点和低点
2. **时间规律分析** - 分析极值点之间的时间间隔规律
3. **价格波动分析** - 统计极值点之间的价格波动特征
4. **成交量特征** - 分析极值点处的成交量异常
5. **反转信号识别** - 识别和量化市场反转信号
6. **支撑阻力位** - 自动识别强支撑/阻力价格位
7. **可视化展示** - 生成图表直观展示极值点分布

## 安装依赖

```bash
pip install MetaTrader5 pandas numpy scipy matplotlib
```

## 使用方法

### 方法1: 交互式运行

```bash
python mt5_extremum_analyzer.py
```

按提示输入：
- 交易品种（如：XAUUSD, EURUSD）
- 时间框架（1分钟到日线）
- 分析K线数量
- 极值点敏感度（3-10，数值越小越敏感）

### 方法2: 代码调用

```python
from mt5_extremum_analyzer import ExtremumAnalyzer
import MetaTrader5 as mt5

# 创建分析器
analyzer = ExtremumAnalyzer(
    symbol="XAUUSD",
    timeframe=mt5.TIMEFRAME_H1
)

# 运行分析
analyzer.run_analysis(bars=1000, order=5)
```

## 参数说明

### symbol (交易品种)
- XAUUSD - 黄金
- EURUSD - 欧美
- GBPUSD - 镑美
- 等MT5支持的所有品种

### timeframe (时间框架)
- M1 - 1分钟
- M5 - 5分钟
- M15 - 15分钟
- M30 - 30分钟
- H1 - 1小时
- H4 - 4小时
- D1 - 日线

### bars (K线数量)
- 建议: 500-2000
- 数量越多，分析越全面，但计算时间越长

### order (极值点敏感度)
- 范围: 3-10
- 3 - 非常敏感，识别更多极值点
- 5 - 平衡（推荐）
- 10 - 不敏感，只识别主要极值点

## 输出结果

### 1. 文本报告
文件名: `extremum_report_XAUUSD_20260312_HHMMSS.txt`

包含：
- 极值点统计
- 时间间隔规律
- 价格波动特征
- 成交量分析
- 强支撑/阻力位
- 最近极值点列表

### 2. 可视化图表
文件名: `extremum_analysis.png`

展示：
- 价格走势
- 高点标记（红色倒三角）
- 低点标记（绿色正三角）

### 3. JSON数据
文件名: `extremum_results.json`

包含完整的分析数据，可用于进一步处理

## 分析结果解读

### 时间间隔规律
```
平均间隔: 15.3 根K线
中位数间隔: 12.0 根K线
标准差: 8.5
```
- 说明极值点大约每12-15根K线出现一次
- 标准差较大说明间隔不规律

### 价格波动特征
```
平均波动: $25.50
中位数波动: $20.30
```
- 极值点之间平均波动约25美元
- 可用于设置止损止盈

### 成交量特征
```
极值点平均成交量比: 1.85x
高成交量极值点: 23 个
```
- 极值点处成交量通常是平均值的1.85倍
- 高成交量极值点更可靠

### 强支撑/阻力位
```
$2650.5 - 触及 5 次
$2635.2 - 触及 4 次
```
- 这些价格位多次成为极值点
- 可作为重要的支撑/阻力位参考

## 实战应用

### 1. 识别入场点
- 价格接近强支撑位 + 低点形成 → 考虑做多
- 价格接近强阻力位 + 高点形成 → 考虑做空

### 2. 设置止损止盈
- 根据平均价格波动设置合理的止损距离
- 参考历史极值点间距设置止盈目标

### 3. 判断趋势强度
- 极值点间隔变短 → 市场波动加剧
- 连续高点抬高 → 上升趋势
- 连续低点降低 → 下降趋势

### 4. 预测反转时机
- 高成交量 + 极值点 → 可能反转
- 触及强支撑/阻力位 → 关注反转信号

## 注意事项

1. **MT5必须运行** - 程序需要连接到本地MT5终端
2. **品种可用性** - 确保MT5中该品种可交易
3. **历史数据** - 确保MT5已下载足够的历史数据
4. **计算时间** - 大量K线分析需要较长时间
5. **参数调优** - 不同品种和时间框架可能需要不同的order参数

## 高级用法

### 多时间框架分析

```python
import MetaTrader5 as mt5
from mt5_extremum_analyzer import ExtremumAnalyzer

timeframes = [
    (mt5.TIMEFRAME_M15, "15分钟"),
    (mt5.TIMEFRAME_H1, "1小时"),
    (mt5.TIMEFRAME_H4, "4小时")
]

for tf, name in timeframes:
    print(f"\n分析 {name} 时间框架...")
    analyzer = ExtremumAnalyzer("XAUUSD", tf)
    analyzer.run_analysis(bars=500, order=5)
```

### 批量品种分析

```python
symbols = ["XAUUSD", "EURUSD", "GBPUSD"]

for symbol in symbols:
    print(f"\n分析 {symbol}...")
    analyzer = ExtremumAnalyzer(symbol, mt5.TIMEFRAME_H1)
    analyzer.run_analysis(bars=1000, order=5)
```

## 故障排除

### 问题1: MT5初始化失败
- 确保MT5正在运行
- 检查MT5是否允许自动交易
- 重启MT5和程序

### 问题2: 获取数据失败
- 检查品种名称是否正确
- 确保MT5中该品种可见
- 检查历史数据是否已下载

### 问题3: 识别的极值点太少/太多
- 调整order参数
- order越小，识别的极值点越多
- order越大，只识别主要极值点

## 更新日志

- v1.0 (2026-03-12) - 初始版本
  - 基础极值点识别
  - 规律分析功能
  - 可视化展示
  - 报告生成
