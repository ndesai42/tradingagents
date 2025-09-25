#!/bin/bash

# TradingAgents Convenience Script
# This script activates the virtual environment, sets up API keys, and runs the CLI

# Activate virtual environment
source tradingagents_env/bin/activate

# Set up API keys
export FINNHUB_API_KEY=d3aodopr01qrtc0d40s0d3aodopr01qrtc0d40sg
export OPENAI_API_KEY=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

# Run TradingAgents CLI
echo "🚀 Starting TradingAgents CLI..."
echo "📊 Ready to analyze stocks!"
echo ""

python -m cli.main