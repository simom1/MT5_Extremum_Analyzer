# MT5 Extremum Analyzer

🔍 A powerful tool for analyzing price extremum points (highs and lows) in MT5 trading data to discover market patterns and identify optimal trading timeframes.

## 📋 Features

- **Extremum Point Detection** - Automatically identifies local highs and lows in price data
- **Multi-Timeframe Analysis** - Compares patterns across 5min, 15min, 30min, 1H, 4H, and Daily timeframes
- **Pattern Recognition** - Analyzes time intervals, price ranges, volume characteristics, and reversal signals
- **Support/Resistance Identification** - Automatically detects strong support and resistance levels
- **Regularity Scoring** - Rates each timeframe's pattern consistency (0-100 score)
- **Visual Reports** - Generates charts and detailed analysis reports
- **Real-time MT5 Connection** - Connects directly to your local MT5 terminal

## 🚀 Quick Start

### Prerequisites

```bash
pip install MetaTrader5 pandas numpy scipy matplotlib
```

### Installation

1. Clone this repository
2. Ensure MT5 is running on your system
3. Run the analyzer

### Usage

#### Single Timeframe Analysis

```bash
cd src
python run_xauusd_extremum.py
```

#### Multi-Timeframe Comparison

```bash
cd src
python multi_timeframe_extremum_finder.py
```

#### Check Available Symbols

```bash
cd src
python check_mt5_symbols.py
```

## 📁 Project Structure

```
MT5_Extremum_Analyzer/
├── src/                                    # Source code
│   ├── mt5_extremum_analyzer.py           # Core analyzer class
│   ├── multi_timeframe_extremum_finder.py # Multi-timeframe comparison
│   ├── visualize_timeframe_comparison.py  # Visualization tools
│   ├── run_xauusd_extremum.py            # Quick run script for XAUUSD+
│   └── check_mt5_symbols.py              # Symbol checker utility
├── docs/                                   # Documentation
│   └── EXTREMUM_ANALYZER_README.md        # Detailed usage guide
├── output/                                 # Analysis results
│   ├── *.txt                              # Text reports
│   ├── *.json                             # JSON data
│   └── *.png                              # Charts
├── scripts/                                # Helper scripts
│   └── start_extremum_analyzer.bat        # Windows batch launcher
├── extremum_config.json                   # Configuration file
└── README.md                              # This file
```

## 📊 Analysis Results

### Regularity Ranking (XAUUSD+ Example)

| Rank | Timeframe | Score | Extremum Count | Avg Interval | Avg Range |
|------|-----------|-------|----------------|--------------|-----------|
| 🥇 1 | 1 Hour    | 54.97 | 133            | 7.5 bars     | $105.95   |
| 🥈 2 | 30 Min    | 50.16 | 121            | 8.3 bars     | $60.26    |
| 🥉 3 | 4 Hour    | 42.40 | 93             | 8.4 bars     | $157.84   |
| 4    | 5 Min     | 42.22 | 252            | 7.9 bars     | $29.73    |
| 5    | 15 Min    | 41.35 | 198            | 7.5 bars     | $42.47    |
| 6    | Daily     | 26.20 | 57             | 8.7 bars     | $250.30   |

### Key Findings

- **Best Timeframe**: 1 Hour (highest regularity score)
- **Extremum Frequency**: Approximately every 7-8 bars
- **5 Min Characteristics**: Most extremum points (252), suitable for scalping
- **Strong Support Level**: $5185.3 (appeared 3+ times)

## 🎯 Trading Applications

1. **Entry Points** - Price near strong support/resistance + extremum formation
2. **Stop Loss** - Set based on average price range for the timeframe
3. **Take Profit** - Use historical extremum intervals to set targets
4. **Trend Strength** - Analyze extremum point spacing and progression

## 📈 Regularity Score Calculation

The score (0-100) is based on:
- **Time Interval Consistency** (30%) - Lower variance = higher score
- **Extremum Density** (20%) - Optimal density: 5-15% of total bars
- **Reversal Signal Quality** (20%) - Strength of price reversals
- **Support/Resistance Strength** (15%) - Number of strong levels
- **Volume Consistency** (15%) - Volume spike at extremum points

## 🔧 Configuration

Edit `extremum_config.json` to customize:

```json
{
  "default_settings": {
    "symbol": "XAUUSD+",
    "timeframe": "H1",
    "bars": 1000,
    "order": 5
  },
  "analysis_parameters": {
    "support_resistance_threshold": 3,
    "high_volume_ratio": 1.5,
    "price_precision": 0.1
  }
}
```

## 📝 Parameters

- **symbol**: Trading symbol (e.g., XAUUSD+, EURUSD)
- **timeframe**: M5, M15, M30, H1, H4, D1
- **bars**: Number of historical bars to analyze (500-2000 recommended)
- **order**: Sensitivity (3=very sensitive, 10=only major extremums)

## 🐛 Troubleshooting

### MT5 Connection Failed
- Ensure MT5 is running
- Enable "Allow automated trading" in MT5 settings

### Symbol Not Found
- Check symbol name (may include suffix like +, .m, etc.)
- Run `check_mt5_symbols.py` to see available symbols
- Ensure symbol is visible in Market Watch

### No Extremum Points Found
- Reduce the `order` parameter (try 3-4)
- Increase the number of bars analyzed
- Check if sufficient historical data is available

## 📄 License

MIT License - Feel free to use and modify

## 🤝 Contributing

Contributions welcome! Please feel free to submit pull requests.

## 📧 Contact

For questions or suggestions, please open an issue on GitHub.

---

**Note**: This tool is for analysis purposes only. Always test strategies thoroughly before live trading.
