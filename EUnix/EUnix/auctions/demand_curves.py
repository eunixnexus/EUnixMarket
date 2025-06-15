import numpy as np
import pandas as pd
from .orders import OrderManager


def demand_curve_from_bids(bids):
    """
    Creates a demand curve from a set of buying bids.


    """
    buying = bids[bids.type]
    buying = buying.sort_values('energy_rate', ascending=False)
    buying['acum'] = buying.energy_qty.cumsum()
    demand_curve = buying[['acum', 'energy_rate']].values
    demand_curve = np.vstack([demand_curve, [np.inf, 0]])
    index = buying.index.values.astype('int64')
    return demand_curve, index


def supply_curve_from_bids(bids):
    """
    Creates a supply curve from a set of selling bids.
    It is the cumulative distribution of quantity
    as a function of price.

    Parameters
    ----------
    bids: pd.DataFrame
        Collection of all the bids in the market. The algorithm
        filters only the selling bids.

    Returns
    ---------
    supply_curve: np.ndarray
       Stepwise constant demand curve represented as a collection
       of the N rightmost points of each interval (N-1 bids). It is stored
       as a (N, 2) matrix where the first column is the x-coordinate
       and the second column is the y-coordinate.
       An extra point is added with x coordinate at infinity and
       price at infinity to represent the end of the curve.

    index : np.ndarray
        The order of the identifier of each bid in the supply
        curve.

    Examples
    ---------

    A minimal example, selling bid is ignored:

    >>> bm = pm.BidManager()
    >>> bm.add_bid(1, 3, 0, False)
    0
    >>> bm.add_bid(2.1, 3, 3, True)
    1
    >>> sc, index = pm.supply_curve_from_bids(bm.get_df())
    >>> sc
    array([[ 1.,  3.],
           [inf, inf]])
    >>> index
    array([0])

    A larger example with reordering:

    >>> bm = pm.BidManager()
    >>> bm.add_bid(1, 3, 0, False)
    0
    >>> bm.add_bid(2.1, 3, 3, True)
    1
    >>> bm.add_bid(0.2, 1, 3, False)
    2
    >>> bm.add_bid(1.7, 6, 4, False)
    3
    >>> sc, index = pm.supply_curve_from_bids(bm.get_df())
    >>> sc
    array([[0.2, 1. ],
           [1.2, 3. ],
           [2.9, 6. ],
           [inf, inf]])
    >>> index
    array([2, 0, 3])


    """
    selling = bids[bids.type == False]
    selling = selling.sort_values('energy_rate')
    selling['acum'] = selling.energy_qty.cumsum()
    supply_curve = selling[['acum', 'energy_rate']].values
    supply_curve = np.vstack([supply_curve, [np.inf, np.inf]])
    index = selling.index.values.astype('int64')
    return supply_curve, index


def get_value_stepwise(x, f):
    """
    Returns the value of a stepwise constant
    function defined by the right extrems
    of its interval
    Functions are assumed to be defined
    in (0, inf).

    Parameters
    ----------
    x: float
        Value in which the function is to be
        evaluated
    f: np.ndarray
        Stepwise function represented as a 2 column
        matrix. Each row is the rightmost extreme
        point of each constant interval. The first column
        contains the x coordinate and is sorted increasingly.
        f is assumed to be defined only in the interval
        :math: (0, \infty)
    Returns
    --------
    float or None
        The image of x under f: `f(x)`. If `x` is negative,
        then None is returned instead. If x is outside
        the range of the function (greater than `f[-1, 0]`),
        then the method returns None.

    Examples
    ---------
    >>> f = np.array([
    ...     [1, 1],
    ...     [3, 4]])
    >>> [pm.get_value_stepwise(x, f)
    ...     for x in [-1, 0, 0.5, 1, 2, 3, 4]]
    [None, 1, 1, 1, 4, 4, None]

    """
    if x < 0:
        return None

    for step in f:
        if x <= step[0]:
            return step[1]


def intersect_stepwise(Buy, Sell):
    """
    Determines the equilibrium point for supply and demand.
    
    Parameters:
        Buy (ndarray): 2D array containing buy quantities and prices (descending price order).
        Sell (ndarray): 2D array containing sell quantities and prices (ascending price order).
        
    Returns:
        q_ (float): Quantity at which supply and demand meet.
        price (float): Price at which supply and demand meet.
        b_ (int): Index of the buyer at that position.
        s_ (int): Index of the seller at that position.
        If no equilibrium is found, returns None for all values.
    """
    # Check if there's only one buy and one sell row
    if len(Buy) <= 2 and len(Sell) <= 2:

        buy_price = Buy[0][1]
        sell_price = Sell[0][1]
        if buy_price > sell_price:  # Buyer willing to pay more than seller's ask
            # Equilibrium quantity is the minimum of the two quantities
            q_ = min(Buy[0][0], Sell[0][0])
            # Equilibrium price is the average of the buy and sell price
            price = (buy_price + sell_price) / 2
            return q_, price, 0, 0  # Indices are both 0 since there's only one row
    
    
    # Accumulate the Buy and Sell quantities
    buy_cumulative = np.cumsum(Buy[:, 0])  # Cumulative quantities for buyers
    sell_cumulative = np.cumsum(Sell[:, 0])  # Cumulative quantities for sellers
    
    for b_, buy_qty in enumerate(buy_cumulative):
        for s_, sell_qty in enumerate(sell_cumulative):
            # Check if there's an overlap between supply and demand
            if buy_qty >= sell_qty and Buy[b_, 1] >= Sell[s_, 1]:  # Prices and quantities match
                q_ = sell_qty  # Quantity at equilibrium is the supply
                price = (Buy[b_, 1] + Sell[s_, 1]) / 2  # Midpoint of buyer and seller price
                return q_, price, b_, s_
    
    # If no equilibrium is found, return None
    return None, None, None, None
        
""""
    # Example input data
    Buy = np.array([
        [252.194, 21.57],
        [411.076, 19.5],
        [695.387, 17.73],
        [818.158, 10.89],
        [np.inf, 0]
    ])

    Sell = np.array([
        [252.194, 15],
        [360.171, 20.36],
        [523.87, 21.37],
        [1096.814, 21.74],
        [1228.232, 23.12],
        [np.inf, np.inf]
    ])

    # Call the function
    q_, price, b_, s_ = find_market_equilibrium(Buy, Sell)

    # Output the results
    if q_ is not None:
        print(f"Equilibrium found at quantity: {q_}, price: {price}, buyer index: {b_}, seller index: {s_}")
    else:
        print("No equilibrium found.")


    return x_ast, f_ast, g_ast, v
"""
