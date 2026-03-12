# Quick Start Guide

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Run Multi-Timeframe Analysis

```bash
cd src
python multi_timeframe_extremum_finder.py
```

This will analyze all timeframes (5min, 15min, 30min, 1H, 4H, Daily) and recommend the best one.

## 3. Run Single Timeframe Analysis

```bash
cd src
python run_xauusd_extremum.py
```

## 4. Check Available Symbols

```bash
cd src
python check_mt5_symbols.py
```

## Output Files

- `output/multi_timeframe_report_*.txt` - Detailed analysis report
- `output/multi_timeframe_comparison.json` - JSON data for further processing
- `output/timeframe_comparison_chart.png` - Visual comparison chart
- `output/*.png` - Individual timeframe analysis charts

## Next Steps

1. Review the analysis report to find the best timeframe
2. Use the recommended timeframe for your trading strategy
3. Monitor the identified support/resistance levels
4. Adjust the `order` parameter for more/less sensitivity
