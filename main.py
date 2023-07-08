import yfinance as yf
import numpy as np
import pandas as pd
import vectorbt as vbt


# Define the Golden Dragon strategy
def golden_dragon_strategy(close: pd.Series) -> pd.Series:
    ema50 = close.rolling(50).mean()
    ema200 = close.rolling(200).mean()
    golden_cross = np.where(ema50 > ema200, 1, 0)
    return pd.Series(golden_cross.squeeze())


# Define the stocks to backtest
stocks = ['AAPL', 'MSFT']  # Add more symbols as desired

# Download OHLCV data using yfinance
ohlcv = yf.download(stocks, start='2022-01-01', end='2022-12-31')

# Extract 'Close' prices
close = ohlcv['Close']

# Apply the strategy on different timeframes
strategies = {}
timeframes = ['1h', '4h', '1D', '1W']
for timeframe in timeframes:
    resampled_close = close.resample(timeframe).last()
    strategies[timeframe] = golden_dragon_strategy(resampled_close)

# Create DataFrame from strategies
strategies_df = pd.DataFrame(strategies, index=close.index)

# Create signals DataFrame
signals_df = vbt.signals.generate_signals(strategies_df, close)

# Create portfolio
portfolio = vbt.Portfolio.from_signals(signals_df, close)

# Plot the backtest results
portfolio.plot(title='Golden Dragon Strategy Backtest')

# Add additional plots for specific metrics
portfolio.total_profit.plot(title='Total Profit')
portfolio.total_return.plot(title='Total Return')
portfolio.positions_value.plot(title='Positions Value')
portfolio.orders.plot_orders(close, title='Buy/Sell Signals')

# Calculate and plot capital allocation during specific periods
capital_allocation = portfolio.capital_used.groupby(portfolio.total_profit > 0).sum()
capital_allocation.plot(kind='bar', title='Capital Allocation')

# Calculate and print strategy statistics
print('--- Strategy Statistics ---')
print('Total Trades:', portfolio.total_trades())
print('Winning Trades:', portfolio.winning_trades())
print('Losing Trades:', portfolio.losing_trades())
print('Profitable Trades Ratio:', portfolio.profitable_trades_ratio())
print('Largest Winning Trade:', portfolio.largest_winning_trade())
print('Largest Losing Trade:', portfolio.largest_losing_trade())
print('Max Drawdown:', portfolio.max_drawdown())

# Save the backtest results to a CSV file
portfolio.to_csv('backtest_results.csv')
