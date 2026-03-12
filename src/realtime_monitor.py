"""
Real-time Monitoring & Multi-timeframe Resonance Alert
Monitors live MT5 feed for confirmed extremum points.
"""
import time
import pandas as pd
import MetaTrader5 as mt5
from mt5_extremum_analyzer import ExtremumAnalyzer
from datetime import datetime, timedelta
import os
import logging
import ctypes  # 用于 Windows 弹窗告警

class RealtimeMonitor:
    def __init__(self, symbol="XAUUSD+"):
        self.symbol = symbol
        self.analyzer_h1 = ExtremumAnalyzer(symbol, mt5.TIMEFRAME_H1)
        self.analyzer_m15 = ExtremumAnalyzer(symbol, mt5.TIMEFRAME_M15)
        self.last_h1_signal = None
        self.last_m15_signal = None
        self.last_h1_time = None
        self.last_m15_time = None
        
        # 设置日志
        self.output_dir = "output"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        self.alert_log_path = os.path.join(self.output_dir, "alerts.log")
        logging.basicConfig(
            filename=self.alert_log_path,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            encoding='utf-8'
        )
        self.logger = logging.getLogger()

    def _send_alert(self, message, is_resonance=False):
        """发送告警：日志 + 控制台 + (可选) 弹窗"""
        print(message)
        self.logger.info(message)
        
        if is_resonance:
            # Windows 弹窗告警 (MB_ICONEXCLAMATION | MB_OK)
            ctypes.windll.user32.MessageBoxW(0, message, "MT5 Extremum Resonance Alert", 0x30 | 0x0)

    def start(self, interval_sec=60, order=3):
        """
        Starts the monitoring loop.
        """
        self._send_alert(f"[{datetime.now().strftime('%H:%M:%S')}] Starting Real-time Monitoring for {self.symbol}...")
        self._send_alert(f"Checking every {interval_sec} seconds. Resonance window: 4 hours.")
        print("=" * 60)

        try:
            while True:
                now = datetime.now()
                
                # Check H1
                h1_signal = self._check_signals(self.analyzer_h1, order)
                if h1_signal:
                    self.last_h1_signal = h1_signal['type']
                    self.last_h1_time = now
                    msg = f"[H1] Signal Confirmed: {h1_signal['type'].upper()} at {h1_signal['price']}"
                    self._send_alert(f"[{now.strftime('%H:%M:%S')}] {msg}")
                
                # Check M15
                m15_signal = self._check_signals(self.analyzer_m15, order)
                if m15_signal:
                    self.last_m15_signal = m15_signal['type']
                    self.last_m15_time = now
                    msg = f"[M15] Signal Confirmed: {m15_signal['type'].upper()} at {m15_signal['price']}"
                    self._send_alert(f"[{now.strftime('%H:%M:%S')}] {msg}")
                
                # Check for Resonance
                self._check_resonance(now)
                
                time.sleep(interval_sec)
        except KeyboardInterrupt:
            self._send_alert("\nMonitoring stopped by user.")
        finally:
            mt5.shutdown()

    def _check_signals(self, analyzer, order):
        """
        Checks if an extremum was confirmed on the most recent bar.
        An extremum is confirmed at index (len-1) - order.
        """
        if not analyzer.connect_mt5():
            return None
            
        df = analyzer.get_historical_data(bars=order + 2)
        if df is None or len(df) < order + 1:
            return None
            
        # Check if the candle at (len-1) - order is an extremum
        # Simplified: Use existing argrelextrema but only look at the specific index
        extremums = analyzer.find_extremum_points(df, order)
        
        # We are looking for an extremum at index: (total bars) - 1 - order
        # Because that's the point where we now have enough bars to confirm it.
        target_idx = len(df) - 1 - order
        
        for e in extremums:
            if e['index'] == target_idx:
                return e
        
        return None

    def _check_resonance(self, now):
        """
        Checks if H1 and M15 have confirmed signals of the same type within 4 hours.
        """
        if self.last_h1_signal and self.last_m15_signal and self.last_h1_signal == self.last_m15_signal:
            h1_age = now - self.last_h1_time
            m15_age = now - self.last_m15_time
            
            if h1_age < timedelta(hours=4) and m15_age < timedelta(hours=4):
                msg = f"🔥 MULTI-TIMEFRAME RESONANCE DETECTED! 🔥\n" \
                      f"Symbol: {self.symbol}\n" \
                      f"Type: {self.last_h1_signal.upper()}\n" \
                      f"H1 confirmed {h1_age.seconds//60} mins ago\n" \
                      f"M15 confirmed {m15_age.seconds//60} mins ago"
                
                self._send_alert(f"[{now.strftime('%H:%M:%S')}] {msg}", is_resonance=True)
                
                # Reset signals to prevent repeated resonance alerts for the same events
                self.last_h1_signal = None
                self.last_m15_signal = None

if __name__ == "__main__":
    monitor = RealtimeMonitor(symbol="XAUUSD+")
    # For demonstration, we'll check every 10 seconds. In production, 60s is usually enough.
    monitor.start(interval_sec=10, order=5)
