import pandas as pd


class OrderManager:
    """A class used to store and organize a collection
    of all the bids and offers in the market.

    Attributes
    -----------
    col_names : :obj:`list` of :obj:`str`
        Column names for the different attributes in the dataframe
        to be created. Currently and in order: .
    n_orders : int
        Number of bids and offers currently stored. Used as a unique identifier
        for each bid within a BidManager.
    orders : :obj:`list` of :obj:`tuple`
        A list where all the recieved orders are stored.
    """

    col_names = [
        'User',
        'User_id',
        'Unit_area',
        'Order_id',
        'energy_qty',
        'energy_rate',
        'bid_offer_time',
        'delivery_time',
        'type',
        'attributes',
        'requirements',
        'power[kW]',
        'area',
        'direction',
    ]

    def __init__(self):
        self.n_orders = 0
        self.orders = []

        
    def add_order(
        self,
        User,
        User_id,
        Unit_area,
        Order_id,
        energy_qty,
        energy_rate,
        bid_offer_time,
        delivery_time,
        type,
        attributes = None,
        requirements = None,
        power = 0,
        area = None,
        direction = None
    ):
        """Appends an order to the order list

        Parameters
        ----------

        0
        """


        new_order = (User, User_id, Unit_area, Order_id, energy_qty, energy_rate, bid_offer_time, delivery_time,
                    type, attributes, requirements, power, area, direction)
        self.orders.append(new_order)
        self.n_orders += 1
        return self.n_orders - 1

    def get_df(self):
        """Creates a dataframe with the bids

        Parameters
        ----------

        Returns

        """

        df = pd.DataFrame(self.orders, columns=self.col_names)
        return df
