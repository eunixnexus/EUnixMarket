# -*- coding: utf-8 -*-
"""
Implements processing techniques applied to bids before
mechanisms can use them
"""
import numpy as np
import pandas as pd
from .orders import OrderManager
from collections import OrderedDict


def new_player_id(index):
    """Helper function for merge_same_price.
    Creates a function that returns consecutive integers.

    Parameters
    -----------
    index: int
        First identifier to use for the
        new fake players

    Returns
    -------
    Callable : function
        Function that maps a list
        of user ids into a new user id.

    Examples
    ----------
    >>> id_gen = new_player_id(6)
    >>> id_gen([3])
    3
    >>> id_gen([5])
    5
    >>> id_gen([0, 1])
    6
    >>> id_gen([2, 4])
    7

    """
    new_player_id.index = index
    def new_id(users):
        """
        Generates a unique identifier for a
        list of users. If the list has
        only one user, then the id is mantained
        else, a new user id is created for the
        whole list.

        Parameters
        ----------
        users: list of int
            List of 1 or more user's identifiers.
            Precondition: all elements of users
            are smaller than index.
        Returns
        -------
        int
            The old identifier if in the list
            there was only one player
            and or the next new consecutive
            identifier if there where more
            than one.

        """

        #nonlocal index
        if len(users) > 1:
            new_index = new_player_id.index
            new_player_id.index += 1
        else:
            new_index = users[0]

        return new_index

    return new_id


def merge_same_price(df, prec=5):
    """
    Process a collection of bids by merging in each
    side (buying or selling) all players with the same
    price into a new user with their aggregated quantity

    Parameters
    ----------
    df : pd.DataFrame
        Collection of bids to process
    prec: float
        Number of digits to use after the comma



    """

    id_gen = new_player_id(df.user.max() + 1)
    columns = df.columns.copy()

    df = df.copy().reset_index().rename(columns={'index': 'bid'})

    buy = df.loc[df['buying'], :]
    sell = df.loc[~df['buying'], :]

    dataframes = [buy, sell]

    agg_fun = {
        'bid': list,
        'user': list,
        'quantity': sum,
        'buying': lambda x: x.sample(1),
        'time': lambda x: x.sample(1),
        'divisible': lambda x: x.sample(1),
    }

    dataframe_new = []
    user_to_bid = OrderedDict()
    for df_ in dataframes:
        rounded_prices = df_.price.apply(lambda x: np.round(x, prec))
        df_new = df_.groupby(rounded_prices).agg(agg_fun).reset_index()
        # print(df_new)
        df_new.user = df_new.user.apply(id_gen)
        #maping = df_new.set_index('user').bid.to_dict()
        # for k, v in maping.items():
        #    user_to_bid[k] = v

        dataframe_new.append(df_new)

    dataframe_new = pd.concat(dataframe_new).reset_index(drop=True)
    final_maping = dataframe_new.bid.to_dict()
    # print(final_maping)
    dataframe_new = dataframe_new[columns]
    # print('-------------')
    # print(dataframe_new)
    #index_to_user = dataframe_new.user.to_dict()

    #final_maping =
    # for k, v in index_to_user.items():
    #    final_maping[k] = user_to_bid[v]

    return dataframe_new, final_maping