# Backtesting

Todo (requirements):
1. Backtesting script (.py)
2. Golden dragon (long term and mid term)
3. Backtest: 1h, 4h, 1D and 1W.
4. Backtest through Yahoo finance.
5. Backtest more than 1 stock at once
6. Implement separated backtesting graphs:
- Profit/Loss (money)
- Profit/loss in %
- Positions value (money).
- Dates.
- Buy/sell dots on where it bought and sold on the stock graph.
7. IF there is a period where the value (money) went to 0 the backtest still needs to
  keep running after that period even if the bot cant buy any more stocks. 
(In most backtests the backtest will stop per default if the value (money) goes to 0. 
Because this is a backtest to not buy the underlying but for buying the real company (the stock) the backtest needs 
8. to continue even if the value goes to 0. You still own the stocks in that option)
8. It needs to measure total capital that was measured during specific periods.
  Example: the bot bought 5 stocks and at another time additional 2 stocks. The value
  (Money) for this period is 60 then the value (money) increased to 80 because of the
  additional 2 stocks, you now have only 20 in value (money left) to buy stocks for. This
  measures how exposed/how much capital you used during certain periods its then
  easier to adjust the first buying value of stock.
9. (Additional, to be added to the strategy) It needs to be able to buy on 1h - 1w graphs.
10. (Additional) STOP LOSS /sell signal (False/true).
If the stop loss is set to false, then the bot needs to hold the stock instead of selling it,
it then needs to use its "martingale" method to buy at the next buy signal instead. You
then average down on your value of the total stocks, But it cant take profit on
negative if the average down still is negative even if the bot wants to take profit. If
their is a positive amount on the average value of stocks after the second time it
bought and the bot got the sell signal as normal its fine.
Example you have 10 stocks you bought at 100. You then buy additional 20 stocks at 50. 
Your average of stocks is = 66.


Initialisation:
jupytext --update-metadata '{"jupytext": {"cell_markers": "\"\"\""}}' main.py --to py:percent
jupytext --opt notebook_metadata_filter=kernelspec,jupytext --opt cell_metadata_filter=-all main.py
