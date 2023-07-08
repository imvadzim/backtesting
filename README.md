# Backtesting for rodinicc

Golden dragon (long term and mid term)

The script and code for this strategy is done for the most part, their is still some minor
tweaks that need to be done.

Backtesting script
We need a backtesting script for the exact strategy.
It needs to be able to backtest: 1h, 4h, 1D and 1W.
It needs to backtest through Yahoo finance.
Its okay to have the backtest plotting different graphs so it's easier to see and analyze
and not gather all the information on one plot graph.
The backtesting plot graph needs to include:
- Profit/Loss (money)
- Profit/loss in %
- Positions value (money).
- Dates.
- Buy/sell dots on where it bought and sold on the stock graph.

- It needs to be able to backtest more than 1 stock at once.

- IF there is a period where the value (money) went to 0 the backtest still needs to
  keep running after that period even if the bot cant buy any more stocks.

- It needs to measure total capital that was measured during specific periods.
  Example: the bot bought 5 stocks and at another time additional 2 stocks. The value
  (Money) for this period is 60 then the value (money) increased to 80 because of the
  additional 2 stocks, you now have only 20 in value (money left) to buy stocks for. This
  measures how exposed/how much capital you used during certain periods its then
  easier to adjust the first buying value of stock.

Additional features that needs to be added to the strategy.
It needs to be able to buy on 1h - 1w graphs.

Additional features to add are:
STOP LOSS /sell signal (False/true).
If the stop loss is set to false, then the bot needs to hold the stock instead of selling it,
it then needs to use its "martingale" method to buy at the next buy signal instead. You
then average down on your value of the total stocks, But it cant take profit on
negative if the average down still is negative even if the bot wants to take profit. If
their is a positive amount on the average value of stocks after the second time it
bought and the bot got the sell signal as normal its fine.
Example you have 10 stocks you bought at 100. You then buy additional 20 stocks at
50. your average of stocks is = 66.


Output format is python. I am going to share the code itself with you and the included strategy, there are only some small changes in the strategy itself we want to implement as mentioned in the job description I sent. The main "job" is for creating the backtesting script for the strategy i am going to share. As mentioned in the paper all the functions we want the backtest to be able to backtest. I would like a easy way to run the backtest in the future is there any other program you can run the backtest with? for example spyder. The price is something you have to determined on how much work you think this will create. The code itself is already done, you only have to call to the functions to the backtest for be able to backtest. But we want to be able to backtest through yahoo finance


So for example. In most backtests the backtest will stop per defualt if the value (money) goes to 0. Becuse this is a backtest to not buy the underlying but for buying the real company (the stock) the backtest needs to continue even if the value goes to 0. You still own the stocks in that opinoion.



Request to ChatGPT:
could you please implement backtesting code in python against Golden dragon strategy (long term and mid term) using vectorbt. It needs to be able to backtest: 1h, 4h, 1D and 1W. It needs to backtest through Yahoo finance. Its okay to have the backtest plotting different graphs so it's easier to see and analyze and not gather all the information on one plot graph.
The backtesting plot graph needs to include:
- Profit/Loss (money)
- Profit/loss in %
- Positions value (money).
- Dates.
- Buy/sell dots on where it bought and sold on the stock graph.

- It needs to be able to backtest more than 1 stock at once.

- IF there is a period where the value (money) went to 0 the backtest still needs to
  keep running after that period even if the bot cant buy any more stocks. For example, in most backtests the backtest will stop per defualt if the value (money) goes to 0. Becuse this is a backtest to not buy the underlying but for buying the real company (the stock) the backtest needs to continue even if the value goes to 0. You still own the stocks in that opinoion.

- It needs to measure total capital that was measured during specific periods.
  Example: the bot bought 5 stocks and at another time additional 2 stocks. The value
  (Money) for this period is 60 then the value (money) increased to 80 because of the
  additional 2 stocks, you now have only 20 in value (money left) to buy stocks for. This
  measures how exposed/how much capital you used during certain periods its then
  easier to adjust the first buying value of stock.

Additional features that needs to be added to the strategy.
It needs to be able to buy on 1h - 1w graphs.

Additional features to add are:
STOP LOSS /sell signal (False/true).
If the stop loss is set to false, then the bot needs to hold the stock instead of selling it,
it then needs to use its "martingale" method to buy at the next buy signal instead. You
then average down on your value of the total stocks, But it cant take profit on
negative if the average down still is negative even if the bot wants to take profit. If
their is a positive amount on the average value of stocks after the second time it
bought and the bot got the sell signal as normal its fine.
Example you have 10 stocks you bought at 100. You then buy additional 20 stocks at
50. your average of stocks is = 66.

Initialisation:
jupytext --update-metadata '{"jupytext": {"cell_markers": "\"\"\""}}' main.py --to py:percent
