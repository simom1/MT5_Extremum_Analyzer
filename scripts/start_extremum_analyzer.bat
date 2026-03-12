@echo off
chcp 65001 >nul
echo ========================================
echo MT5极值点分析器
echo ========================================
echo.

python src/run_xauusd_extremum.py

echo.
echo 按任意键退出...
pause >nul
