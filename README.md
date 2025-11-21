# AI-Trading-Backtester

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)]()
[![Architecture](https://img.shields.io/badge/architecture-event--driven-orange)]()
[![License](https://img.shields.io/badge/license-Proprietary-red)]()

> **Institutional-grade algorithmic trading architecture for High-Frequency Analysis and Trend Capture.**

---

## 🚀 Overview

**JACKBULL** is a high-performance quantitative trading engine designed to identify Alpha in volatile asset classes. Built on a vectorized Python kernel, it simulates institutional order flow with precision—accounting for transaction friction, slippage, and dynamic position management.

The core logic utilizes the proprietary **Jackbull Momentum Protocol**, a volatility-adaptive algorithm designed to capture "Fat Tail" distribution events (outlier trends) in Crypto, Forex, and Large-Cap Equities, while mathematically filtering out mean-reverting noise.

## ⚡ Technical Capabilities

Unlike retail backtesters that simplify execution, JACKBULL mimics a real exchange environment:

*   **Vectorized Signal Processing:** Exploits `numpy` and `pandas` specifically for nanosecond-latency data handling across large datasets (50,000+ data points).
*   **Friction Modeling:** Logic engine calculates PnL *net of fees* (default 10bps), ensuring realistic Expectancy (E) values.
*   **Multi-Asset Correlation:** Capable of running concurrent backtests across uncorrelated assets (e.g., BTC/USD vs. SPY) to analyze portfolio variance.
*   **Heikin-Ashi Smoothing Layer:** (Optional) Internal pre-processing to denoise HFT tick data before logic application.
*   **Risk Engine:** Embedded Drawdown limits and volatility-adjusted exit triggers.

## 📦 Installation & Usage

**Prerequisites:** Python 3.8+, Pip.

Follow these steps to install the dependencies, launch the engine, and start a trading session immediately.

1.  **Clone and Install:**
    ```bash
    git clone https://github.com/jay8patel/AI-Trading-Backtester.git
    cd jackbull-autotrader
    pip install -r requirements.txt
    ```

2.  **Run the Engine:**
    ```bash
    python main.py
    ```

3.  **Operation:**
    Once the CLI initializes, you will see the prompt below. Enter any ticker symbol to auto-ingest OHLCV data and generate the Equity Curve.
    ```text
    [JACKBULL] System Ready.
    > Enter Asset Symbol (e.g., BTC-USD, NVDA):
    ```

## 🛠️ Architecture

The codebase adheres to SOLID principles with a modular design pattern:

```text
AI-Trading-Backtester/
│
├── src/
│   ├── strategy_base.py      # Abstract Event Engine & Cash Management
│   ├── market_downloader.py  # Yahoo Finance API Connector / Data Sanitization
│   └── strategies.py         # Proprietary JACKBULL Logic Kernel (Obfuscated)
│
├── main.py                   # CLI Entry Point
├── requirements.txt          # Dependency List
└── README.md                 # Documentation
