import pandas as pd
import uuid

from scipy.spatial.distance import cdist
from sklearn.cluster import AgglomerativeClustering
from EUnix.transactions.transactions import TransactionManager
from EUnix.mechanisms import Mechanism

def hhc_clearing_mechanism(orders, n_cluster = 3):
    #Initial declaration
    n_clusters = n_cluster
    price = orders 
    q_ = orders
    
    
    trans = TransactionManager()

    bids  = orders.loc[orders['type']]
    offers = orders.loc[~orders['type']]


# Step 2: Hierarchical Clustering based on Price and Location
    market_data = pd.concat([bids, offers]).reset_index(drop=True)
    feature_matrix = market_data[['energy_rate']]
    #feature_matrix = market_data[['Price', 'area']]


# Choose number of clusters (e.g., 3 groups)
    clustering = AgglomerativeClustering(n_clusters=n_clusters, metric='euclidean', linkage='ward')
    market_data['Cluster'] = clustering.fit_predict(feature_matrix)


    # Step 3: Match bids and offers within each cluster
    def match_bids_offers(cluster_id):
        cluster_data = market_data[market_data['Cluster'] == cluster_id]
        bid_clusters  = cluster_data.loc[cluster_data['type']].sort_values('energy_rate', ascending=False)
        offer_clusters = cluster_data.loc[~cluster_data['type']].sort_values('energy_rate', ascending=True)

        for _, buyer in bid_clusters.iterrows():
            for _, seller in offer_clusters.iterrows():
                if buyer['energy_rate'] >= seller['energy_rate'] and buyer['energy_qty'] > 0 and seller['energy_qty'] > 0:
                    trade_quantity = min(buyer['energy_qty'], seller['energy_qty'])
                    
                    #matches.append((buyer['ID'], seller['ID'], seller['Price'], trade_quantity))
                    trx_id = str(uuid.uuid4())
                    trans_b = (trx_id, buyer.User, buyer.User_id, buyer.Unit_area, buyer.Order_id, buyer.energy_qty, buyer.energy_rate, buyer.bid_offer_time,
                 seller.User, seller.User_id, seller.Order_id, seller.energy_qty, seller.energy_rate, seller.bid_offer_time,seller['energy_rate'],trade_quantity, buyer.delivery_time, "Buying")
                    trans_s = (trx_id, buyer.User, buyer.User_id, seller.Unit_area, buyer.Order_id, buyer.energy_qty, buyer.energy_rate, buyer.bid_offer_time,
                 seller.User, seller.User_id, seller.Order_id, seller.energy_qty, seller.energy_rate, seller.bid_offer_time,seller['energy_rate'],trade_quantity, buyer.delivery_time, "Selling")


                  
                    # Update remaining quantities
                    buyer['energy_qty'] -= trade_quantity
                    seller['energy_qty'] -= trade_quantity
                    trans.add_transaction(*trans_b)
                    trans.add_transaction(*trans_s)
        
        return 

    # Apply matching to each cluster

    for cluster in range(n_clusters):
        match_bids_offers(cluster)


    extra = {
        'clearing quantity': q_,
        'clearing price': price
    }



    return trans, extra



# Observe that we add as the second argument of init the algorithm just coded
class hhcMechanism(Mechanism):
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
        Mechanism.__init__(self, hhc_clearing_mechanism, bids, *args, **kwargs)
        
        
