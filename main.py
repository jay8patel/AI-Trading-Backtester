import os
import sys
import pandas as pd
from src.data_loader import load_data
from src.market_downloader import download_market_data
# We use the rebranded logic now (even though under the hood it is Donchian)
from src.strategies import DonchianStrategy 

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def analyze_ticker(ticker):
    print(f"\n[JACKBULL] Processing {ticker}...")
    
    data_file = f'data/{ticker}_1h_data.csv'
    
    if not os.path.exists(data_file):
        download_market_data(ticker)
        
    if not os.path.exists(data_file):
        print(f"ERROR: Could not fetch data for '{ticker}'.")
        return

    try:
        df = load_data(data_file)
    except Exception as e:
        print(f"ERROR loading data: {e}")
        return

    # --- BRANDED OUTPUT ---
    print(f"Loading JACKBULL Auto Trading Logic...")
    
    strategy = DonchianStrategy(
        df, 
        entry_window=168,   # Variables hidden from user print
        exit_window=72,     
        initial_capital=10000, 
        transaction_cost_pct=0.001
    )

    strategy.backtest()
    stats = strategy.evaluate_performance()
    
    print("\n" + "="*40)
    print(f"JACKBULL RESULTS FOR {ticker}")
    print("="*40)
    print(f"{'Metric':<25} {'Value'}")
    print("-" * 40)
    for k, v in stats.items():
        print(f"{k:<25} {v}")
    print("="*40)

    print("Opening JACKBULL Charts... (Close chart window to continue)")
    strategy.plot_results()

def run_interactive_mode():
    while True:
        clear_screen()
        print("="*50)
        print("   JACKBULL AUTO TRADER v1.0")
        print("="*50)
        print("Supported Assets:")
        print("  - Crypto: BTC-USD, ETH-USD, SOL-USD, DOGE-USD")
        print("  - Stocks: AAPL, NVDA, TSLA, SPY, QQQ")
        print("  - Forex:  EURUSD=X, GBPUSD=X")
        print("-" * 50)
        
        user_input = input("Enter Asset Symbol (or 'q' to quit): ").strip().upper()
        
        if user_input == 'Q':
            print("Exiting JACKBULL System...")
            sys.exit()
            
        if not user_input:
            continue
            
        analyze_ticker(user_input)
        
        input("\nPress Enter to scan another asset...")

if __name__ == "__main__":
    try:
        run_interactive_mode()
    except KeyboardInterrupt:
        print("\nGoodbye!")