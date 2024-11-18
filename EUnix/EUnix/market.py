from .auctions.orders import OrderManager
from EUnix.mechanisms import *
#from pymarket.transactions import TransactionManager
#from collections import OrderedDict

MECHANISM = {
    'uniform': UniformPrice,
    'p2p': P2PTrading,
}




class Market():

    """General interface for calling the different
    market mechanisms

    Parameters
    ----------
    bm: BidManager
        All bids are stored in the bid manager
    transactions: TransactionManager
        The set of all tranasactions in the Market.
        This argument get updated after the market ran.
    extra: dict
        Extra information provided by the mechanisms.
        Gets updated after an execution of the run.

    Returns
    -------


    Examples
    ---------

    If everyone is buying, the transaction
    dataframe is returned empty as well as the extra
    dictionary.

    >>> mar = pm.Market()
    >>> mar.accept_bid(1, 2, 0, True)
    0
    >>> mar.accept_bid(2, 3, 1, True)
    1
    >>> trans, extra = mar.run('huang')
    >>> extra
    OrderedDict()
    >>> trans.get_df()
    Empty DataFrame
    Columns: [bid, quantity, price, source, active]
    Index: []

    If everyone is buying, the transaction
    dataframe is returned empty as well as the extra
    dictionary.

    >>> mar = pm.Market()
    >>> mar.accept_bid(1, 2, 0, False)
    0
    >>> mar.accept_bid(2, 3, 1, False)
    1
    >>> trans, extra = mar.run('huang')
    >>> extra
    OrderedDict()
    >>> trans.get_df()
    Empty DataFrame
    Columns: [bid, quantity, price, source, active]
    Index: []

    A very simple auction where nobody trades

    >>> mar = pm.Market()
    >>> mar.accept_bid(1, 3, 0, True)
    0
    >>> mar.accept_bid(1, 2, 1, False)
    1
    >>> trans, extra = mar.run('huang')
    >>> extra
    OrderedDict([('price_sell', 2.0), ('price_buy', 3.0), ('quantity_traded', 0)])
    >>> trans.get_df()
    Empty DataFrame
    Columns: [bid, quantity, price, source, active]
    Index: []

    """
 
    def __init__(self):
        """TODO: to be defined."""
        self.bm = OrderManager()
        
        

        #self.transactions = TransactionManager()
        #self.extra = OrderedDict()

    def accept_order(self, *args):
       
        """Adds a bid to the bid manager

        Parameters
        ----------           
        *args :
            List of parameters requried to create a bid.
            See `BidManager` documentation.

        Returns
        -------
        bid_id: int
            The id of the new created bid in the Auction
        
        """
        order_id = self.bm.add_order(*args)
        return order_id



    def get_oders(self):
        """get the bids and offers

        

        
        """
        df = self.bm.get_df()
        return df



    def run(self, algo, *args, **kwargs):
        """Runs a given mechanism with the current
        bids

        Parameters
        ----------
        algo : str
            One of:
                * 'p2p'
                * 'huang'
                * 'muda'
            
        *args :
            Extra arguments to pass to the algorithm.

        **kwargs :
            Extra keyworded arguments to pass to the algorithm


        Returns
        -------
        transactions: TransactionManager
            The transaction manager holding all the transactions
            returned by the mechanism.
        extra: dict
            Dictionary with extra information returned by the
            executed method.

        
        """
        df = self.bm.get_df()
        mec = MECHANISM[algo](df, *args, **kwargs)
        transactions, extra = mec.run()
        self.transactions = transactions
        self.extra = extra
        return transactions, extra

    