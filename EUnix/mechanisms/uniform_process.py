"""
MIT License

Copyright (c) 2019, Diego Kiedanki
Copyright (c) 2025, Godwin Okwuibe

This file includes modifications made by Godwin Okwuibe in 2025.
"""

import numpy as np
import pandas as pd




def demand_curve_from_bids(bids):
    """Creates a demand curve from buying bids."""
    buying = bids[bids.type].sort_values('energy_rate', ascending=False)
    buying['acum'] = buying.energy_qty.cumsum()
    demand_curve = np.vstack([buying[['acum', 'energy_rate']].values, [np.inf, 0]])
    return demand_curve, buying.index.values.astype('int64')


def supply_curve_from_bids(bids):
    """Creates a supply curve from selling bids."""
    selling = bids[~bids.type].sort_values('energy_rate')
    selling['acum'] = selling.energy_qty.cumsum()
    supply_curve = np.vstack([selling[['acum', 'energy_rate']].values, [np.inf, np.inf]])
    return supply_curve, selling.index.values.astype('int64')


def get_value_stepwise(x, f):
    """Returns value of a stepwise constant function f evaluated at x."""
    if x < 0:
        return None
    for step in f:
        if x <= step[0]:
            return step[1]


def intersect_stepwise(Buy, Sell):
    """
    Determines the market clearing point from stepwise demand and supply curves.
    Returns (quantity, price, buyer_index, seller_index)
    """
    if len(Buy) <= 2 and len(Sell) <= 2:
        buy_price, sell_price = Buy[0][1], Sell[0][1]
        if buy_price > sell_price:
            return min(Buy[0][0], Sell[0][0]), (buy_price + sell_price) / 2, 0, 0

    buy_cumsum = np.cumsum(Buy[:, 0])
    sell_cumsum = np.cumsum(Sell[:, 0])

    for b_, bq in enumerate(buy_cumsum):
        for s_, sq in enumerate(sell_cumsum):
            if bq >= sq and Buy[b_, 1] >= Sell[s_, 1]:
                return sq, (Buy[b_, 1] + Sell[s_, 1]) / 2, b_, s_

    return None, None, None, None
