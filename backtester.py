import pandas as pd
import yfinance as yf
import numpy as np
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

class TradingAgentsBacktester:
    def __init__(self, ticker, start_date, end_date, initial_cash=100_000):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.initial_cash = initial_cash
        
        # Initialize TradingAgents with fast config for backtesting
        config = DEFAULT_CONFIG.copy()
        config["quick_think_llm"] = "gpt-4o-mini" 
        config["deep_think_llm"] = "gpt-4o-mini"
        config["max_debate_rounds"] = 1
        config["max_risk_discuss_rounds"] = 1
        
        self.ta_graph = TradingAgentsGraph(debug=False, config=config)
        
        # Load price data
        self.price_data = self._load_price_data()
        
        # Portfolio tracking
        self.cash = initial_cash
        self.shares = 0
        self.portfolio_history = []
        self.trades = []

    def _load_price_data(self):
        """Load historical price data from Yahoo Finance"""
        stock = yf.Ticker(self.ticker)
        df = stock.history(start=self.start_date, end=self.end_date)
        df.index = df.index.tz_localize(None)  # Remove timezone info
        return df

    def _get_closing_price(self, date):
        """Get closing price for a specific date"""
        try:
            return self.price_data.loc[date, 'Close']
        except KeyError:
            # Find nearest available date
            available_dates = self.price_data.index
            nearest_date = min(available_dates, key=lambda x: abs(x - pd.to_datetime(date)))
            return self.price_data.loc[nearest_date, 'Close']

    def _parse_decision(self, decision_text):
        """Convert TradingAgents text decision to actionable signal"""
        text = str(decision_text).lower()
        
        if any(word in text for word in ['buy', 'purchase', 'acquire']):
            return 'buy'
        elif any(word in text for word in ['sell', 'short']):
            return 'sell'
        else:
            return 'hold'

    def _execute_trade(self, action, price, date):
        """Execute buy/sell trades"""
        if action == 'buy' and self.cash > 0:
            # Buy as many shares as possible
            shares_to_buy = int(self.cash / price)
            if shares_to_buy > 0:
                cost = shares_to_buy * price
                self.cash -= cost
                self.shares += shares_to_buy
                
                self.trades.append({
                    'date': date,
                    'action': 'buy',
                    'shares': shares_to_buy,
                    'price': price,
                    'cost': cost
                })
                
        elif action == 'sell' and self.shares > 0:
            # Sell all shares
            proceeds = self.shares * price
            self.cash += proceeds
            
            self.trades.append({
                'date': date,
                'action': 'sell',
                'shares': self.shares,
                'price': price,
                'proceeds': proceeds
            })
            
            self.shares = 0

    def run_backtest(self, rebalance_frequency='weekly'):
        """Run the backtest"""
        print(f"Running backtest for {self.ticker} from {self.start_date} to {self.end_date}")
        
        # Create rebalancing dates
        if rebalance_frequency == 'weekly':
            dates = pd.date_range(self.start_date, self.end_date, freq='W')
        else:
            dates = pd.date_range(self.start_date, self.end_date, freq='D')
        
        for date in dates:
            date_str = date.strftime('%Y-%m-%d')
            price = self._get_closing_price(date)
            
            print(f"Processing {date_str}: ${price:.2f}")
            
            try:
                # Get TradingAgents decision
                _, decision = self.ta_graph.propagate(self.ticker, date_str)
                action = self._parse_decision(decision)
                
                print(f"  AI Decision: {action.upper()}")
                
                # Execute trade
                self._execute_trade(action, price, date)
                
            except Exception as e:
                print(f"  Error: {e}")
                action = 'hold'
            
            # Track portfolio value
            portfolio_value = self.cash + (self.shares * price)
            self.portfolio_history.append({
                'date': date,
                'price': price,
                'cash': self.cash,
                'shares': self.shares,
                'portfolio_value': portfolio_value,
                'action': action
            })
            
            print(f"  Portfolio: ${portfolio_value:,.2f} (Cash: ${self.cash:,.2f}, Shares: {self.shares})")

    def calculate_performance(self):
        """Calculate performance metrics"""
        df = pd.DataFrame(self.portfolio_history)
        df.set_index('date', inplace=True)
        
        # Calculate returns
        initial_value = self.initial_cash
        final_value = df['portfolio_value'].iloc[-1]
        total_return = (final_value / initial_value) - 1
        
        # Buy and hold benchmark
        initial_price = df['price'].iloc[0]
        final_price = df['price'].iloc[-1] 
        buy_hold_return = (final_price / initial_price) - 1
        
        # Calculate Sharpe ratio
        df['daily_returns'] = df['portfolio_value'].pct_change()
        sharpe = df['daily_returns'].mean() / df['daily_returns'].std() * np.sqrt(252)
        
        # Max drawdown
        df['cummax'] = df['portfolio_value'].cummax()
        df['drawdown'] = (df['portfolio_value'] - df['cummax']) / df['cummax']
        max_drawdown = df['drawdown'].min()
        
        return {
            'total_return': total_return,
            'buy_hold_return': buy_hold_return,
            'alpha': total_return - buy_hold_return,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'total_trades': len(self.trades),
            'final_portfolio_value': final_value,
            'portfolio_df': df,
            'trades_df': pd.DataFrame(self.trades)
        }

    def print_summary(self):
        """Print backtest summary"""
        results = self.calculate_performance()
        
        print(f"\n{'='*50}")
        print("BACKTEST RESULTS")
        print(f"{'='*50}")
        print(f"Ticker: {self.ticker}")
        print(f"Period: {self.start_date} to {self.end_date}")
        print(f"Initial Investment: ${self.initial_cash:,.2f}")
        print(f"Final Portfolio Value: ${results['final_portfolio_value']:,.2f}")
        print(f"")
        print(f"TradingAgents Return: {results['total_return']:.2%}")
        print(f"Buy & Hold Return: {results['buy_hold_return']:.2%}")
        print(f"Alpha (Excess Return): {results['alpha']:.2%}")
        print(f"")
        print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
        print(f"Max Drawdown: {results['max_drawdown']:.2%}")
        print(f"Total Trades: {results['total_trades']}")
        
        if results['alpha'] > 0:
            print(f"\n🎉 TradingAgents BEAT buy-and-hold by {results['alpha']:.2%}!")
        else:
            print(f"\n📉 TradingAgents underperformed buy-and-hold by {abs(results['alpha']):.2%}")

# Example usage:
# from backtester import TradingAgentsBacktester
# bt = TradingAgentsBacktester('AAPL', '2024-01-01', '2024-02-01', 50_000)
# bt.run_backtest()
# bt.print_summary()