
import pandas as pd
import networkx as nx
import numpy as np

from EUnix.transactions.transactions import TransactionManager
from EUnix.auctions.orders import OrderManager
from EUnix.mechanisms import Mechanism
from EUnix.auctions import demand_curves as dv


def uniform_price_mechanism(orders):

    trans = TransactionManager()

    buy, _ = dv.demand_curve_from_bids(orders) # Creates demand curve from bids
    sell, _ = dv.supply_curve_from_bids(orders) # Creates supply curve from bids



    # q_ is the quantity at which supply and demand meet
    # price is the price at which that happens
    # b_ is the index of the buyer in that position
    # s_ is the index of the seller in that position
    q_, b_, s_, price = dv.intersect_stepwise(buy, sell)


    bids  = orders.loc[orders['type']].sort_values('energy_rate', ascending=False)
    offers = orders.loc[~orders['type']].sort_values('energy_rate', ascending=True)


    ## Filter only the trading bids.
    bids = bids.iloc[: b_ + 1, :]
    offers = offers.iloc[: s_ + 1, :]



    # Find the long side of the market
    buying_quantity = bids.energy_qty.sum()
    selling_quantity = offers.energy_qty.sum()




    if buying_quantity > selling_quantity:
        long_side = bids
        short_side = offers
    else:
        long_side = offers
        short_side = bids

    traded_quantity = short_side.energy_qty.sum()


    ## All the short side will trade at `price`
    ## The -1 is there because there is no clear 1 to 1 trade.
    for i, x in short_side.iterrows():
        t = (i, x.energy_qty, price, -1, True)

        trans.add_transaction(*t)
    

    ## The long side has to trade only up to the short side
    quantity_added = 0
    for i, x in long_side.iterrows():

        if x.energy_qty + quantity_added <= traded_quantity:
            x_quantity = x.energy_qty
        else:
            x_quantity = traded_quantity - quantity_added
        t = (i, x_quantity, price, -1, False)
        trans.add_transaction(*t)
        quantity_added += x.energy_qty

    extra = {
        'clearing quantity': q_,
        'clearing price': price
    }



    return trans, extra



# Observe that we add as the second argument of init the algorithm just coded
class UniformPrice(Mechanism):
    """
    Interface for our new uniform price mechanism.

    Parameters
    -----------
    bids
        Collection of bids to run the mechanism
        with.
    """

    def __init__(self, bids, *args, **kwargs):
        """TODO: to be defined1. """
        Mechanism.__init__(self, uniform_price_mechanism, bids, *args, **kwargs)
        
        
        
#pm.market.MECHANISM['TPC'] = UniformPrice        
        
        
        
        
        

