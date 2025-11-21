import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class Strategy:
    def __init__(self, dataframe: pd.DataFrame, initial_capital=10000.0, position_size_pct=1.0, transaction_cost_pct=0.001):
        """
        Args:
            dataframe (pd.DataFrame): OHLCV data.
            initial_capital (float): Starting cash.
            position_size_pct (float): Max portfolio % to risk per trade (1.0 = 100%).
            transaction_cost_pct (float): Trading fee (0.001 = 0.1%).
        """
        self.data = dataframe.copy()
        self.initial_capital = initial_capital
        self.position_size_pct = position_size_pct
        self.transaction_cost_pct = transaction_cost_pct
        
        # Backtest state
        self.portfolio_value = []
        self.positions = []
        self.cash_history = []
        self.trade_log = []
        
    def generate_signals(self):
        raise NotImplementedError("Method generate_signals() must be implemented.")

    def backtest(self):
        # Ensure signals exist
        if 'Signal' not in self.data.columns:
            self.generate_signals()

        cash = self.initial_capital
        holding = 0 # Units held
        
        # --- FIX: REBRANDED PRINT STATEMENT ---
        # Old: print(f"Starting Backtest for {self.__class__.__name__}...")
        print(f"Initializing JACKBULL Logic Engine... (Fee: {self.transaction_cost_pct*100}%)")
        
        for i in range(len(self.data)):
            price = self.data.iloc[i]['Close']
            signal = self.data.iloc[i]['Signal']
            date = self.data.index[i]

            # EXECUTION LOGIC
            if signal == 1 and holding == 0:
                allocate_amt = cash * self.position_size_pct
                holding = allocate_amt / (price * (1 + self.transaction_cost_pct))
                cost = holding * price
                fee = cost * self.transaction_cost_pct
                cash -= (cost + fee)
                self.trade_log.append({'Date': date, 'Type': 'BUY', 'Price': price, 'Units': holding, 'Fee': fee})

            elif signal == -1 and holding > 0:
                revenue = holding * price
                fee = revenue * self.transaction_cost_pct
                cash += (revenue - fee)
                self.trade_log.append({'Date': date, 'Type': 'SELL', 'Price': price, 'Units': holding, 'Fee': fee})
                holding = 0
            
            current_val = cash + (holding * price)
            self.portfolio_value.append(current_val)
            self.positions.append(holding)
            self.cash_history.append(cash)

        self.data['Portfolio_Value'] = self.portfolio_value
        self.data['Position'] = self.positions

    def evaluate_performance(self):
        self.data['Returns'] = self.data['Portfolio_Value'].pct_change().fillna(0)
        total_return = (self.data['Portfolio_Value'].iloc[-1] - self.initial_capital) / self.initial_capital
        avg_return = self.data['Returns'].mean()
        std_return = self.data['Returns'].std()
        sharpe_ratio = np.sqrt(252 * 24) * (avg_return / std_return) if std_return != 0 else 0
        
        cumulative_returns = (1 + self.data['Returns']).cumprod()
        peak = cumulative_returns.cummax()
        drawdown = (cumulative_returns - peak) / peak
        max_drawdown = drawdown.min()

        results = {
            "Initial Capital": self.initial_capital,
            "Final Value": round(self.data['Portfolio_Value'].iloc[-1], 2),
            "Total Return (%)": round(total_return * 100, 2),
            "Sharpe Ratio": round(sharpe_ratio, 2),
            "Max Drawdown (%)": round(max_drawdown * 100, 2),
            "Total Trades": len(self.trade_log)
        }
        return results

    def plot_results(self):
        # Default plotter (Children often override this, but we keep it safe)
        plt.style.use('bmh')
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(self.data.index, self.data['Portfolio_Value'])
        plt.show()