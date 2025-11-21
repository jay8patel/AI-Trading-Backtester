import numpy as np
import pandas as pd
from .strategy_base import Strategy

# 1. MOVING AVERAGE CROSSOVER
class MovingAverageCrossover(Strategy):
    def __init__(self, dataframe, short_window=50, long_window=200, initial_capital=10000, transaction_cost_pct=0.001):
        super().__init__(dataframe, initial_capital, transaction_cost_pct=transaction_cost_pct)
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self):
        self.data['SMA_Short'] = self.data['Close'].rolling(window=self.short_window).mean()
        self.data['SMA_Long'] = self.data['Close'].rolling(window=self.long_window).mean()
        self.data['Signal_State'] = np.where(self.data['SMA_Short'] > self.data['SMA_Long'], 1.0, 0.0)
        self.data['Signal'] = self.data['Signal_State'].diff().fillna(0)

# 2. RSI REVERSAL
class RSIReversal(Strategy):
    def __init__(self, dataframe, period=14, rsi_lower=30, rsi_upper=70, initial_capital=10000, transaction_cost_pct=0.001):
        super().__init__(dataframe, initial_capital, transaction_cost_pct=transaction_cost_pct)
        self.period = period
        self.lower = rsi_lower
        self.upper = rsi_upper

    def calculate_rsi(self):
        delta = self.data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).ewm(alpha=1/self.period, adjust=False).mean()
        loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/self.period, adjust=False).mean()
        rs = gain / loss
        self.data['RSI'] = 100 - (100 / (1 + rs))

    def generate_signals(self):
        self.calculate_rsi()
        self.data['Signal'] = 0
        in_position = False
        signals = []
        for rsi in self.data['RSI']:
            if rsi < self.lower and not in_position:
                signals.append(1)
                in_position = True
            elif rsi > self.upper and in_position:
                signals.append(-1)
                in_position = False
            else:
                signals.append(0)
        self.data['Signal'] = signals

# 3. MULTI-TIMEFRAME MA
class MultiTimeframeMA(Strategy):
    def __init__(self, dataframe, fast_ma=20, slow_ma=50, trend_ma=50, initial_capital=10000, transaction_cost_pct=0.001):
        super().__init__(dataframe, initial_capital, transaction_cost_pct=transaction_cost_pct)
        self.fast_ma = fast_ma   
        self.slow_ma = slow_ma   
        self.trend_ma = trend_ma 
        
    def generate_signals(self):
        self.data['SMA_Fast'] = self.data['Close'].rolling(window=self.fast_ma).mean()
        self.data['SMA_Slow'] = self.data['Close'].rolling(window=self.slow_ma).mean()
        df_4h = self.data.resample('4h').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'})
        df_4h['Trend_SMA'] = df_4h['Close'].rolling(window=self.trend_ma).mean()
        self.data['HTF_Trend_SMA'] = df_4h['Trend_SMA'].reindex(self.data.index, method='ffill')
        crossover_bullish = self.data['SMA_Fast'] > self.data['SMA_Slow']
        crossover_bearish = self.data['SMA_Fast'] < self.data['SMA_Slow']
        trend_bullish = self.data['Close'] > self.data['HTF_Trend_SMA']
        signal_col = np.where(crossover_bullish & trend_bullish, 1.0, 0.0)
        signal_col = np.where(crossover_bearish, -1.0, signal_col)
        self.data['Signal_State'] = signal_col
        self.data['Signal'] = self.data['Signal_State'].diff().fillna(0)

# 4. BOLLINGER BREAKOUT
class BollingerBreakout(Strategy):
    def __init__(self, dataframe, period=20, std_dev=2.0, initial_capital=10000, transaction_cost_pct=0.001):
        super().__init__(dataframe, initial_capital, transaction_cost_pct=transaction_cost_pct)
        self.period = period
        self.std_dev = std_dev

    def generate_signals(self):
        self.data['SMA'] = self.data['Close'].rolling(window=self.period).mean()
        self.data['STD'] = self.data['Close'].rolling(window=self.period).std()
        self.data['Upper'] = self.data['SMA'] + (self.data['STD'] * self.std_dev)
        signals = []
        in_position = False
        for i in range(len(self.data)):
            price = self.data['Close'].iloc[i]
            upper = self.data['Upper'].iloc[i]
            sma = self.data['SMA'].iloc[i]
            if price > upper and not in_position:
                signals.append(1)
                in_position = True
            elif price < sma and in_position:
                signals.append(-1)
                in_position = False
            else:
                signals.append(0)
        self.data['Signal'] = signals

# 5. SUPERTREND (HEIKIN-ASHI)
class SuperTrendStrategy(Strategy):
    def __init__(self, dataframe, atr_period=10, factor=3.0, initial_capital=10000, transaction_cost_pct=0.001):
        super().__init__(dataframe, initial_capital, transaction_cost_pct=transaction_cost_pct)
        self.atr_period = atr_period
        self.factor = factor

    def generate_signals(self):
        ha_close = (self.data['Open'] + self.data['High'] + self.data['Low'] + self.data['Close']) / 4
        ha_open = np.zeros(len(self.data))
        ha_open[0] = self.data['Open'].iloc[0]
        for i in range(1, len(self.data)):
            ha_open[i] = (ha_open[i-1] + ha_close.iloc[i-1]) / 2
        
        self.data['HA_Close'] = ha_close
        self.data['HA_High'] = self.data[['High', 'HA_Close']].max(axis=1)
        self.data['HA_Low']  = self.data[['Low', 'HA_Close']].min(axis=1)
        
        tr1 = self.data['HA_High'] - self.data['HA_Low']
        tr2 = (self.data['HA_High'] - self.data['HA_Close'].shift(1)).abs()
        tr3 = (self.data['HA_Low'] - self.data['HA_Close'].shift(1)).abs()
        self.data['ATR'] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1).ewm(alpha=1/self.atr_period).mean()

        hl2 = (self.data['HA_High'] + self.data['HA_Low']) / 2
        upper = hl2 + (self.factor * self.data['ATR'])
        lower = hl2 - (self.factor * self.data['ATR'])
        trend = np.zeros(len(self.data))
        final_upper = np.zeros(len(self.data))
        final_lower = np.zeros(len(self.data))
        vals = self.data['HA_Close'].values
        u_vals = upper.values
        l_vals = lower.values

        for i in range(1, len(self.data)):
            if u_vals[i] < final_upper[i-1] or vals[i-1] > final_upper[i-1]:
                final_upper[i] = u_vals[i]
            else:
                final_upper[i] = final_upper[i-1]
            if l_vals[i] > final_lower[i-1] or vals[i-1] < final_lower[i-1]:
                final_lower[i] = l_vals[i]
            else:
                final_lower[i] = final_lower[i-1]
            prev = trend[i-1]
            if prev == -1 and vals[i] > final_upper[i]:
                trend[i] = 1
            elif prev == 1 and vals[i] < final_lower[i]:
                trend[i] = -1
            else:
                trend[i] = prev
            if trend[i] == 0: trend[i] = 1

        self.data['Trend'] = trend
        self.data['SuperTrend_Line'] = np.where(trend==1, final_lower, final_upper)
        diff = pd.Series(trend, index=self.data.index).diff().fillna(0)
        self.data['Signal'] = np.where(diff > 0, 1, np.where(diff < 0, -1, 0))

    def plot_results(self):
        import matplotlib.pyplot as plt
        plt.style.use('bmh')
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [2, 1]})
        
        ax1.plot(self.data.index, self.data['Close'], color='gray', alpha=0.5, label='Price')
        ax1.plot(self.data.index, self.data['SuperTrend_Line'], color='orange', linestyle='--', label='Jackbull Trend Line')
        ax1_eq = ax1.twinx()
        ax1_eq.plot(self.data.index, self.data['Portfolio_Value'], color='blue', linewidth=2, label='Equity Curve')
        
        buys = self.data[self.data['Signal'] == 1]
        sells = self.data[self.data['Signal'] == -1]
        if not buys.empty: ax1.scatter(buys.index, buys['Close'], marker='^', color='green', s=100)
        if not sells.empty: ax1.scatter(sells.index, sells['Close'], marker='v', color='red', s=100)
        
        ax1.set_title("JACKBULL Auto Trading Strategy") 
        # FIX: Combine legends from Ax1 (Left) and Ax1_Eq (Right)
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax1_eq.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        cum = (1+self.data['Returns']).cumprod()
        dd = (cum - cum.cummax()) / cum.cummax()
        ax2.fill_between(dd.index, dd, color='red', alpha=0.3)
        ax2.set_title("Risk Analysis (Drawdown)")
        plt.tight_layout()
        plt.show()

# 6. DONCHIAN STRATEGY (THIS IS THE ACTIVE JACKBULL LOGIC)
class DonchianStrategy(Strategy):
    def __init__(self, dataframe, entry_window=168, exit_window=72, initial_capital=10000, transaction_cost_pct=0.001):
        super().__init__(dataframe, initial_capital, transaction_cost_pct=transaction_cost_pct)
        self.entry_window = entry_window
        self.exit_window = exit_window

    def generate_signals(self):
        self.data['Donchian_High'] = self.data['High'].rolling(window=self.entry_window).max().shift(1)
        self.data['Donchian_Low'] = self.data['Low'].rolling(window=self.exit_window).min().shift(1)
        
        signals = []
        in_position = False
        for i in range(len(self.data)):
            close = self.data['Close'].iloc[i]
            high_bound = self.data['Donchian_High'].iloc[i]
            low_bound = self.data['Donchian_Low'].iloc[i]
            if close > high_bound and not in_position:
                signals.append(1)
                in_position = True
            elif close < low_bound and in_position:
                signals.append(-1)
                in_position = False
            else:
                signals.append(0)
        self.data['Signal'] = signals

    def plot_results(self):
        import matplotlib.pyplot as plt
        plt.style.use('bmh')
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [2, 1]})
        
        ax1.plot(self.data.index, self.data['Close'], color='gray', alpha=0.5, label='Price')
        
        # Indicators
        ax1.plot(self.data.index, self.data['Donchian_High'], color='green', linestyle='--', alpha=0.8, label='Jackbull Buy Zone')
        ax1.plot(self.data.index, self.data['Donchian_Low'], color='red', linestyle='--', alpha=0.8, label='Jackbull Sell Zone')
        
        # Equity Curve (Right Axis)
        ax1_eq = ax1.twinx()
        ax1_eq.plot(self.data.index, self.data['Portfolio_Value'], color='blue', linewidth=2, label='Jackbull Equity (Blue)')
        
        # Markers
        buys = self.data[self.data['Signal'] == 1]
        sells = self.data[self.data['Signal'] == -1]
        if not buys.empty: ax1.scatter(buys.index, buys['Close'], marker='^', color='green', s=100)
        if not sells.empty: ax1.scatter(sells.index, sells['Close'], marker='v', color='red', s=100)
        
        ax1.set_title("JACKBULL Auto Trading Strategy") 
        
        # --- FIX: LEGEND COMBINATION ---
        # Get labels from Left Y-Axis
        lines1, labels1 = ax1.get_legend_handles_labels()
        # Get labels from Right Y-Axis (Equity)
        lines2, labels2 = ax1_eq.get_legend_handles_labels()
        # Combine them so Blue Line shows up
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        cum = (1+self.data['Returns']).cumprod()
        dd = (cum - cum.cummax()) / cum.cummax()
        ax2.fill_between(dd.index, dd, color='red', alpha=0.3)
        ax2.set_title("Drawdown") 
        plt.tight_layout()
        plt.show()