# ---
# jupyter:
#   jupytext:
#     cell_markers: '"""'
#     cell_metadata_filter: -all
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.14.7
# ---

# %%
from datetime import datetime
import pytz
import vectorbt as vbt
import numpy as np
import pandas as pd
from numba import njit
from vectorbt.generic.nb import nanmean_nb
from vectorbt.portfolio.nb import order_nb, sort_call_seq_nb
from vectorbt.portfolio.enums import SizeType, Direction
from pypfopt import expected_returns
from pypfopt import risk_models
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import base_optimizer

# %%
# Define params
symbols = ['AMZN', 'NFLX', 'GOOG', 'AAPL']
start_date = datetime(2017, 1, 1, tzinfo=pytz.utc)
end_date = datetime(2020, 1, 1, tzinfo=pytz.utc)
num_tests = 2000

# %%
vbt.settings.array_wrapper['freq'] = 'days'
vbt.settings.returns['year_freq'] = '252 days'
vbt.settings.portfolio['seed'] = 42
vbt.settings.portfolio.stats['incl_unrealized'] = True

# %%
yfdata = vbt.YFData.download(symbols, start=start_date, end=end_date)
print(yfdata.symbols)

# %%
ohlcv = yfdata.concat()
print(ohlcv.keys())

# %%
price = ohlcv['Close']

# %%
# Plot normalized price series
(price / price.iloc[0]).vbt.plot().show_png()

# %%
returns = price.pct_change()
print(returns.mean())

# %%
print(returns.std())

# %%
print(returns.corr())

# %%
# vectorbt: random search
# One-time allocation
np.random.seed(42)
# Generate random weights, n times
weights = []
for i in range(num_tests):
    w = np.random.random_sample(len(symbols))
    w = w / np.sum(w)
    weights.append(w)
print(len(weights))

# %%
# Build column hierarchy such that one weight corresponds to one price series
_price = price.vbt.tile(num_tests, keys=pd.Index(np.arange(num_tests), name='symbol_group'))
_price = _price.vbt.stack_index(pd.Index(np.concatenate(weights), name='weights'))
print(_price.columns)

# %%
# Define order size
size = np.full_like(_price, np.nan)
size[0, :] = np.concatenate(weights)  # allocate at first timestamp, do nothing afterward
print(size.shape)

# %%
# Run simulation
pf = vbt.Portfolio.from_orders(
    close=_price,
    size=size,
    size_type='targetpercent',
    group_by='symbol_group',
    cash_sharing=True
)  # all weights sum to 1, no shorting, and 100% investment in risky assets
print(len(pf.orders))

# %%
# Plot annualized return against volatility, color by sharpe ratio
annualized_return = pf.annualized_return()
annualized_return.index = pf.annualized_volatility()
annualized_return.vbt.scatterplot(
    trace_kwargs=dict(
        mode='markers',
        marker=dict(
            color=pf.sharpe_ratio(),
            colorbar=dict(
                title='sharpe_ratio'
            ),
            size=5,
            opacity=0.7
        )
    ),
    xaxis_title='annualized_volatility',
    yaxis_title='annualized_return'
).show_png()

# %%
# Get index of the best group according to the target metric
best_symbol_group = pf.sharpe_ratio().idxmax()
print(best_symbol_group)

# %%
# Print best weights
print(weights[best_symbol_group])

# %%
# Compute default stats
print(pf.iloc[best_symbol_group].stats())

# %%
# Re-balance monthly
# Select the first index of each month
rb_mask = ~_price.index.to_period('m').duplicated()
print(rb_mask.sum())

# %%
rb_size = np.full_like(_price, np.nan)
rb_size[rb_mask, :] = np.concatenate(weights)  # allocate at mask
print(rb_size.shape)

# %%
# Run simulation, with re-balancing monthly
rb_pf = vbt.Portfolio.from_orders(
    close=_price,
    size=rb_size,
    size_type='targetpercent',
    group_by='symbol_group',
    cash_sharing=True,
    call_seq='auto'  # important: sell before buy
)
print(len(rb_pf.orders))

# %%
rb_best_symbol_group = rb_pf.sharpe_ratio().idxmax()
print(rb_best_symbol_group)

# %%
print(weights[rb_best_symbol_group])

# %%
print(rb_pf.iloc[rb_best_symbol_group].stats())


# %%
def plot_allocation(rb_pf):
    # Plot weights development of the portfolio
    rb_asset_value = rb_pf.asset_value(group_by=False)
    rb_value = rb_pf.value()
    rb_idxs = np.flatnonzero((rb_pf.asset_flow() != 0).any(axis=1))
    rb_dates = rb_pf.wrapper.index[rb_idxs]
    fig = (rb_asset_value.vbt / rb_value).vbt.plot(
        trace_names=symbols,
        trace_kwargs=dict(
            stackgroup='one'
        )
    )
    for rb_date in rb_dates:
        fig.add_shape(
            dict(
                xref='x',
                yref='paper',
                x0=rb_date,
                x1=rb_date,
                y0=0,
                y1=1,
                line_color=fig.layout.template.layout.plot_bgcolor
            )
        )
    fig.show_png()


# %%
plot_allocation(rb_pf.iloc[rb_best_symbol_group])  # best group


# %%
# # Search and re-balance every 30 days
"""
Utilize low-level API to dynamically search for best Sharpe ratio and re-balance accordingly. 
Compared to previous method, we won't utilize stacking, but do search in a loop instead. 
We also will use days instead of months, as latter may contain a various number of trading days.
"""

# %%
srb_sharpe = np.full(price.shape[0], np.nan)

# %%
ann_factor = returns.vbt.returns.ann_factor

# %%
@njit
def pre_sim_func_nb(c, every_nth):
    # Define re-balancing days
    c.segment_mask[:, :] = False
    c.segment_mask[every_nth::every_nth, :] = True
    return ()

# %%
@njit
def find_weights_nb(c, price, num_tests):
    # Find optimal weights based on best Sharpe ratio
    returns = (price[1:] - price[:-1]) / price[:-1]
    returns = returns[1:, :]  # cannot compute np.cov with NaN
    mean = nanmean_nb(returns)
    cov = np.cov(returns, rowvar=False)  # masked arrays not supported by Numba (yet)
    best_sharpe_ratio = -np.inf
    weights = np.full(c.group_len, np.nan, dtype=np.float_)

    for i in range(num_tests):
        # Generate weights
        w = np.random.random_sample(c.group_len)
        w = w / np.sum(w)

        # Compute annualized mean, covariance, and Sharpe ratio
        p_return = np.sum(mean * w) * ann_factor
        p_std = np.sqrt(np.dot(w.T, np.dot(cov, w))) * np.sqrt(ann_factor)
        sharpe_ratio = p_return / p_std
        if sharpe_ratio > best_sharpe_ratio:
            best_sharpe_ratio = sharpe_ratio
            weights = w

    return best_sharpe_ratio, weights

# %%
@njit
def pre_segment_func_nb(c, find_weights_nb, history_len, num_tests, srb_sharpe):
    if history_len == -1:
        # Look back at the entire time period
        close = c.close[:c.i, c.from_col:c.to_col]
    else:
        # Look back at a fixed time period
        if c.i - history_len <= 0:
            return (np.full(c.group_len, np.nan),)  # insufficient data
        close = c.close[c.i - history_len:c.i, c.from_col:c.to_col]

    # Find optimal weights
    best_sharpe_ratio, weights = find_weights_nb(c, close, num_tests)
    srb_sharpe[c.i] = best_sharpe_ratio

    # Update valuation price and reorder orders
    size_type = SizeType.TargetPercent
    direction = Direction.LongOnly
    order_value_out = np.empty(c.group_len, dtype=np.float_)
    for k in range(c.group_len):
        col = c.from_col + k
        c.last_val_price[col] = c.close[c.i, col]
    sort_call_seq_nb(c, weights, size_type, direction, order_value_out)

    return (weights,)

# %%
@njit
def order_func_nb(c, weights):
    col_i = c.call_seq_now[c.call_idx]
    return order_nb(
        weights[col_i],
        c.close[c.i, c.col],
        size_type=SizeType.TargetPercent
    )

# %%
# Run simulation using a custom order function
srb_pf = vbt.Portfolio.from_order_func(
    price,
    order_func_nb,
    pre_sim_func_nb=pre_sim_func_nb,
    pre_sim_args=(30,),
    pre_segment_func_nb=pre_segment_func_nb,
    pre_segment_args=(find_weights_nb, -1, ann_factor, num_tests, srb_sharpe),
    cash_sharing=True,
    group_by=True
)

# %%
# Plot the best Sharpe ratio at each re-balancing day
pd.Series(srb_sharpe, index=price.index).vbt.scatterplot(trace_kwargs=dict(mode='markers')).show_png()

# %%
print(srb_pf.stats())

# %%
plot_allocation(srb_pf)

# %%
# You can see how weights stabilize themselves with growing data.
# Run simulation, but now consider only the last 252 days of data
srb252_sharpe = np.full(price.shape[0], np.nan)

# %%
srb252_pf = vbt.Portfolio.from_order_func(
    price,
    order_func_nb,
    pre_sim_func_nb=pre_sim_func_nb,
    pre_sim_args=(30,),
    pre_segment_func_nb=pre_segment_func_nb,
    pre_segment_args=(find_weights_nb, 252, ann_factor, num_tests, srb252_sharpe),
    cash_sharing=True,
    group_by=True
)
pd.Series(srb252_sharpe, index=price.index).vbt.scatterplot(trace_kwargs=dict(mode='markers')).show_png()

# %%
print(srb252_pf.stats())

# %%
plot_allocation(srb252_pf)

# %%
# A much more volatile weight distribution.
# PyPortfolioOpt + vectorbt
# One-time allocation
# Calculate expected returns and sample covariance matrix
avg_returns = expected_returns.mean_historical_return(price)
cov_mat = risk_models.sample_cov(price)
# Get weights maximizing the Sharpe ratio
ef = EfficientFrontier(avg_returns, cov_mat)
weights = ef.max_sharpe()
clean_weights = ef.clean_weights()
pyopt_weights = np.array([clean_weights[symbol] for symbol in symbols])
print(pyopt_weights)

# %%
pyopt_size = np.full_like(price, np.nan)
pyopt_size[0, :] = pyopt_weights  # allocate at first timestamp, do nothing afterward
print(pyopt_size.shape)

# %%
# Run simulation with weights from PyPortfolioOpt
pyopt_pf = vbt.Portfolio.from_orders(
    close=price,
    size=pyopt_size,
    size_type='targetpercent',
    group_by=True,
    cash_sharing=True
)
print(len(pyopt_pf.orders))

# %%
print(pyopt_pf.stats())

# %%
# # Search and re-balance monthly
"""
You can’t use third-party optimization packages within Numba (yet).
Here you have two choices:
Use os.environ['NUMBA_DISABLE_JIT'] = '1' before all imports to disable Numba completely
Disable Numba for the function, but also for every other function in the stack that calls it
We will demonstrate the second option.
"""

# %%
def pyopt_find_weights(sc, price, num_tests):  # no @njit decorator = it's a pure Python function
    # Calculate expected returns and sample covariance matrix
    price = pd.DataFrame(price, columns=symbols)
    avg_returns = expected_returns.mean_historical_return(price)
    cov_mat = risk_models.sample_cov(price)

    # Get weights maximizing the Sharpe ratio
    ef = EfficientFrontier(avg_returns, cov_mat)
    weights = ef.max_sharpe()
    clean_weights = ef.clean_weights()
    weights = np.array([clean_weights[symbol] for symbol in symbols])
    best_sharpe_ratio = base_optimizer.portfolio_performance(weights, avg_returns, cov_mat)[2]

    return best_sharpe_ratio, weights


# %%
pyopt_srb_sharpe = np.full(price.shape[0], np.nan)

# %%
# Run simulation with a custom order function
pyopt_srb_pf = vbt.Portfolio.from_order_func(
    price,
    order_func_nb,
    pre_sim_func_nb=pre_sim_func_nb,
    pre_sim_args=(30,),
    pre_segment_func_nb=pre_segment_func_nb.py_func,  # run pre_segment_func_nb as pure Python function
    pre_segment_args=(pyopt_find_weights, -1, ann_factor, num_tests, pyopt_srb_sharpe),
    cash_sharing=True,
    group_by=True,
    use_numba=False  # run simulate_nb as pure Python function
)

# %%
pd.Series(pyopt_srb_sharpe, index=price.index).vbt.scatterplot(trace_kwargs=dict(mode='markers')).show_png()

# %%
print(pyopt_srb_pf.stats())


# %%
plot_allocation(pyopt_srb_pf)
