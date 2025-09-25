#!/bin/bash

# TradingAgents Convenience Script
# This script activates the virtual environment, sets up API keys, and runs the CLI

# Activate virtual environment
source tradingagents_env/bin/activate

# Load API keys from .env file
if [ -f .env ]; then
    export $(cat .env | xargs)
else
    echo "⚠️ .env file not found. Please create one with your API keys."
    exit 1
fi

# Run TradingAgents CLI
echo "🚀 Starting TradingAgents CLI..."
echo "📊 Ready to analyze stocks!"
echo ""

python -m cli.main