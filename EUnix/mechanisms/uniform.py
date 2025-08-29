"""
MIT License

Copyright (c) 2019, Diego Kiedanki
Copyright (c) 2025, Godwin Okwuibe

This file includes modifications made by Godwin Okwuibe in 2025.
"""


import pandas as pd
import numpy as np
import uuid

from EUnix.transactions.transactions import TransactionManager
from EUnix.auctions.orders import OrderManager
from EUnix.mechanisms import Mechanism
from EUnix.mechanisms import uniform_process as dv


def uniform_price_mechanism(orders):
    trans = TransactionManager()

    buy, _ = dv.demand_curve_from_bids(orders)
    sell, _ = dv.supply_curve_from_bids(orders)
    q_, price, b_, s_ = dv.intersect_stepwise(buy, sell)

    if price is None:
        return trans, []

    bids = orders[orders.type].sort_values('energy_rate', ascending=False).iloc[:b_+1]
    offers = orders[~orders.type].sort_values('energy_rate').iloc[:s_+1]

    buying_qty = bids.energy_qty.sum()
    selling_qty = offers.energy_qty.sum()
    traded_qty = min(buying_qty, selling_qty)

    short_side = bids if buying_qty <= selling_qty else offers
    long_side = offers if buying_qty <= selling_qty else bids

    # Add all short side transactions (fully matched)
    for _, row in short_side.iterrows():
        trans.add_transaction(*create_transaction(row, price, row.energy_qty))

    # Add partial from long side until matched quantity is fulfilled
    quantity_added = 0
    for _, row in long_side.iterrows():
        if quantity_added >= traded_qty:
            break
        x_qty = min(row.energy_qty, traded_qty - quantity_added)
        trans.add_transaction(*create_transaction(row, price, x_qty))
        quantity_added += x_qty

    return trans, {
        'clearing quantity': q_,
        'clearing price': price
    }


def create_transaction(row, price, matched_qty):
    """Helper to generate a transaction tuple from a row."""
    tx_id = str(uuid.uuid4())
    if row.type:  # Buyer
        return (
            tx_id, row.User, row.User_id, row.Unit_area, row.Order_id,
            row.energy_qty, row.energy_rate, row.bid_offer_time,
            "", "", "", "", "", "", price, matched_qty, row.delivery_time, "Buying"
        )
    else:  # Seller
        return (
            tx_id, "", "", row.Unit_area, "", "", "", "",
            row.User, row.User_id, row.Order_id, row.energy_qty,
            row.energy_rate, row.bid_offer_time, price,
            matched_qty, row.delivery_time, "Selling"
        )


class UniformPrice(Mechanism):
    """Interface for uniform price mechanism."""

    def __init__(self, bids, *args, **kwargs):
        super().__init__(uniform_price_mechanism, bids, *args, **kwargs)
