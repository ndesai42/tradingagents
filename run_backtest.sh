#!/bin/bash

# TradingAgents Backtesting Script
# Tests the AI agents against historical data to validate performance

echo "🧪 TradingAgents Backtesting Suite"
echo "=================================="

# Activate virtual environment
source tradingagents_env/bin/activate

# Load API keys from .env file
if [ -f .env ]; then
    export $(cat .env | xargs)
else
    echo "⚠️ .env file not found. Please create one with your API keys."
    exit 1
fi

echo ""
echo "📊 Running backtest on AAPL..."
echo "Period: November 2024 (2 weeks)"
echo "Strategy: AI agents vs Buy & Hold"
echo ""

# Run the backtest
python -c "
from backtester import TradingAgentsBacktester

# Run backtest
backtester = TradingAgentsBacktester(
    ticker='AAPL',
    start_date='2024-11-01',
    end_date='2024-11-15',
    initial_cash=10_000
)

backtester.run_backtest(rebalance_frequency='weekly')
backtester.print_summary()
"

echo ""
echo "✅ Backtesting completed!"
echo ""
echo "💡 To run your own backtest:"
echo "   python -c \"from backtester import TradingAgentsBacktester; bt = TradingAgentsBacktester('TSLA', '2024-10-01', '2024-10-31'); bt.run_backtest(); bt.print_summary()\""