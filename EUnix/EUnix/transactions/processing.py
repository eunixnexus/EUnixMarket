import pandas as pd
from EUnix.transactions.transactions import TransactionManager


def split_transactions_merged_players(transactions, bids, mapping, fees=None):
    """
    Splits aggregated transactions (from merged bids) proportionally into
    the original bids using their offered or requested energy quantities.

    Parameters
    ----------
    transactions : TransactionManager
        The transaction manager returned by the mechanism after clearing.
    bids : pd.DataFrame
        Original bid/offer dataframe. May contain repeated players that were merged.
    mapping : dict
        Maps merged transaction bid IDs to a list of original bid row indices.
        Example: {0: [0, 1]} means bid 0 in the transaction represents bids 0 and 1 in `bids`.
    fees : dict, optional
        A dictionary with transaction-level fees that should be split among original bids.

    Returns
    -------
    TransactionManager or (TransactionManager, dict)
        If `fees` is provided, returns a tuple of:
            - new TransactionManager with disaggregated transactions
            - updated fees dictionary, split proportionally across users
        If `fees` is None, returns only the new TransactionManager.

    Example
    -------
    >>> tm_split = split_transactions_merged_players(tm, bid_df, {0: [0, 1]})
    """
    new_trans = TransactionManager()

    for _, t in transactions.get_df().iterrows():
        bid_id = t.bid
        original_rows = mapping.get(bid_id, [])

        # Proportional share of quantity
        total_quantity = bids.iloc[original_rows]["quantity"].sum()
        proportions = bids.iloc[original_rows]["quantity"] / total_quantity if total_quantity > 0 else 0

        # Optional fee for the merged transaction
        fee_per_user = None
        if len(original_rows) > 1 and fees is not None:
            fee_per_user = fees.pop(t.user, None)

        for row_idx in original_rows:
            user_row = bids.iloc[row_idx]
            t_values = t.copy()

            # Update bid and quantity for disaggregated transaction
            t_values.bid = row_idx
            t_values.quantity *= proportions[row_idx]

            # Update fee per user if applicable
            if fee_per_user is not None:
                user_id = user_row.user
                fees[user_id] = fee_per_user * proportions[row_idx]

            new_trans.add_transaction(*t_values.values)

    return (new_trans, fees) if fees is not None else new_trans
