import pandas as pd
import itertools
from .strategies import MovingAverageCrossover
from .data_loader import load_data

def optimize_ma_crossover(data_path):
    df = load_data(data_path)
    
    # Define parameter ranges
    short_windows = range(10, 50, 5)  # 10, 15, 20...
    long_windows = range(50, 150, 10) # 50, 60, 70...
    
    results = []
    
    print(f"Starting Grid Search optimization on {data_path}...")
    
    # Iterate through all combinations
    for short_w, long_w in itertools.product(short_windows, long_windows):
        if short_w >= long_w:
            continue
            
        # Instantiate and Run
        # Quietly runs backtest without plotting
        strategy = MovingAverageCrossover(df.copy(), short_window=short_w, long_window=long_w)
        strategy.backtest()
        stats = strategy.evaluate_performance()
        
        results.append({
            'Short': short_w,
            'Long': long_w,
            'Return': stats['Total Return (%)'],
            'Sharpe': stats['Sharpe Ratio'],
            'Drawdown': stats['Max Drawdown (%)']
        })
    
    # Convert to DataFrame for easy sorting
    results_df = pd.DataFrame(results)
    
    # Sort by Sharpe Ratio
    best_sharpe = results_df.sort_values(by='Sharpe', ascending=False).iloc[0]
    best_return = results_df.sort_values(by='Return', ascending=False).iloc[0]
    
    print("\n" + "="*40)
    print("OPTIMIZATION RESULTS")
    print("="*40)
    
    print(f"Best SHARPE Configuration:")
    print(f"MA Windows: {int(best_sharpe['Short'])} / {int(best_sharpe['Long'])}")
    print(f"Sharpe: {best_sharpe['Sharpe']}")
    print(f"Return: {best_sharpe['Return']}%")
    print("-" * 30)
    
    print(f"Best RETURN Configuration:")
    print(f"MA Windows: {int(best_return['Short'])} / {int(best_return['Long'])}")
    print(f"Return: {best_return['Return']}%")
    print(f"Drawdown: {best_return['Drawdown']}%")

if __name__ == "__main__":
    # Run independent test if executed directly
    optimize_ma_crossover('data/synthetic_data.csv')