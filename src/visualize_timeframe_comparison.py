"""
Visualize multi-timeframe comparison results
"""
import json
import matplotlib.pyplot as plt
import matplotlib
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

# 读取数据
json_path = os.path.join('output', 'multi_timeframe_comparison.json')
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

results = data['results']

# 提取数据
timeframes = [r['timeframe'] for r in results]
scores = [r['regularity_score'] for r in results]
extremum_counts = [r['extremum_count'] for r in results]
avg_intervals = [r['patterns']['avg_interval'] for r in results]
interval_stds = [r['patterns']['interval_std'] for r in results]
avg_ranges = [r['patterns']['avg_price_range'] for r in results]

# 创建图表
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle(f'XAUUSD+ 多周期极值点规律对比分析', fontsize=16, fontweight='bold')

# 1. Regularity Score
ax1 = axes[0, 0]
colors = ['#2ecc71' if s == max(scores) else '#3498db' for s in scores]
bars1 = ax1.bar(timeframes, scores, color=colors, alpha=0.7, edgecolor='black')
ax1.set_ylabel('Regularity Score', fontsize=11)
ax1.set_title('Regularity Score Comparison (Higher is Better)', fontsize=12, fontweight='bold')
ax1.set_ylim(0, 100)
ax1.axhline(y=50, color='red', linestyle='--', alpha=0.3, label='Pass Line (50)')
ax1.grid(axis='y', alpha=0.3)
ax1.legend()
for bar, score in zip(bars1, scores):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
             f'{score:.1f}', ha='center', va='bottom', fontsize=9)

# 2. Extremum Count
ax2 = axes[0, 1]
bars2 = ax2.bar(timeframes, extremum_counts, color='#e74c3c', alpha=0.7, edgecolor='black')
ax2.set_ylabel('Extremum Count', fontsize=11)
ax2.set_title('Extremum Count Comparison', fontsize=12, fontweight='bold')
ax2.grid(axis='y', alpha=0.3)
for bar, count in zip(bars2, extremum_counts):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
             f'{count}', ha='center', va='bottom', fontsize=9)

# 3. Average Interval
ax3 = axes[0, 2]
bars3 = ax3.bar(timeframes, avg_intervals, color='#9b59b6', alpha=0.7, edgecolor='black')
ax3.set_ylabel('Avg Interval (Bars)', fontsize=11)
ax3.set_title('Average Extremum Interval', fontsize=12, fontweight='bold')
ax3.grid(axis='y', alpha=0.3)
for bar, interval in zip(bars3, avg_intervals):
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height,
             f'{interval:.1f}', ha='center', va='bottom', fontsize=9)

# 4. Coefficient of Variation
ax4 = axes[1, 0]
cv = [std/avg if avg > 0 else 0 for std, avg in zip(interval_stds, avg_intervals)]
colors4 = ['#2ecc71' if c == min(cv) else '#f39c12' for c in cv]
bars4 = ax4.bar(timeframes, cv, color=colors4, alpha=0.7, edgecolor='black')
ax4.set_ylabel('Coefficient of Variation', fontsize=11)
ax4.set_title('Time Interval CV (Lower is More Regular)', fontsize=12, fontweight='bold')
ax4.grid(axis='y', alpha=0.3)
for bar, c in zip(bars4, cv):
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height,
             f'{c:.2f}', ha='center', va='bottom', fontsize=9)

# 5. Average Price Range
ax5 = axes[1, 1]
bars5 = ax5.bar(timeframes, avg_ranges, color='#1abc9c', alpha=0.7, edgecolor='black')
ax5.set_ylabel('Avg Range ($)', fontsize=11)
ax5.set_title('Average Price Range Between Extremums', fontsize=12, fontweight='bold')
ax5.grid(axis='y', alpha=0.3)
for bar, range_val in zip(bars5, avg_ranges):
    height = bar.get_height()
    ax5.text(bar.get_x() + bar.get_width()/2., height,
             f'${range_val:.1f}', ha='center', va='bottom', fontsize=9)

# 6. Summary Information
ax6 = axes[1, 2]
# Find best timeframe
best_idx = scores.index(max(scores))
best_tf = timeframes[best_idx]

# Display recommendation
ax6.axis('off')
info_text = f"""
ANALYSIS SUMMARY

Best Timeframe: {best_tf}
Regularity Score: {scores[best_idx]:.2f}/100

Key Metrics:
  - Extremum Count: {extremum_counts[best_idx]}
  - Avg Interval: {avg_intervals[best_idx]:.1f} bars
  - Interval StdDev: {interval_stds[best_idx]:.1f}
  - Avg Range: ${avg_ranges[best_idx]:.2f}

Trading Suggestions:
  1. Use {best_tf} timeframe
  2. Extremum every ~{int(avg_intervals[best_idx])} bars
  3. Set SL around ${avg_ranges[best_idx]:.0f}
   
5min Timeframe:
  - Most extremums ({extremum_counts[0]})
  - Smaller range (${avg_ranges[0]:.2f})
  - Good for scalping
  - Strong level: $5185.3
"""

ax6.text(0.1, 0.5, info_text, fontsize=10, verticalalignment='center',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

plt.tight_layout()
save_path = os.path.join('output', 'timeframe_comparison_chart.png')
plt.savefig(save_path, dpi=150, bbox_inches='tight')
print(f"Chart saved: {save_path}")
plt.close()

print("\nAnalysis complete!")
print(f"Best timeframe: {best_tf} (Score: {scores[best_idx]:.2f})")
