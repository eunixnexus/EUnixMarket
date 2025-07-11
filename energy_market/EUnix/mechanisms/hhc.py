import numpy as np
import pandas as pd
import scipy.cluster.hierarchy as sch
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist
from sklearn.cluster import AgglomerativeClustering

# Step 1: Generate synthetic bid and offer data
np.random.seed(42)
n_buyers = 10
n_sellers = 10


def generate_market_data(n, role):
    data = {
        'ID': [f'{role}_{i}' for i in range(n)],
        'Price': np.random.uniform(20, 50, n),  # Price in $/MWh
        'Quantity': np.random.uniform(5, 20, n),  # Quantity in MWh
        'Location': np.random.uniform(0, 100, n)  # Location index (0 to 100)
    }
    return pd.DataFrame(data)

buyers = generate_market_data(n_buyers, 'Buyer')
sellers = generate_market_data(n_sellers, 'Seller')



# Step 2: Hierarchical Clustering based on Price and Location
market_data = pd.concat([buyers, sellers]).reset_index(drop=True)
feature_matrix = market_data[['Price', 'Location']]



# Perform hierarchical clustering
distance_matrix = cdist(feature_matrix, feature_matrix, metric='euclidean')
linkage_matrix = sch.linkage(distance_matrix, method='ward')




# Plot dendrogram
plt.figure(figsize=(10, 5))
sch.dendrogram(linkage_matrix, labels=market_data['ID'].values, leaf_rotation=90)
plt.title('Hierarchical Clustering Dendrogram')
plt.show()
plt.savefig("hierarchical_clustering_dendrogram.pdf", format="pdf", bbox_inches="tight")


# Choose number of clusters (e.g., 3 groups)
n_clusters = 3
clustering = AgglomerativeClustering(n_clusters=n_clusters, affinity='euclidean', linkage='ward')
market_data['Cluster'] = clustering.fit_predict(feature_matrix)




# Step 3: Match bids and offers within each cluster
def match_bids_offers(cluster_id):
    cluster_data = market_data[market_data['Cluster'] == cluster_id]
    buyers_cluster = cluster_data[cluster_data['ID'].str.startswith('Buyer')].sort_values(by='Price', ascending=False)
    sellers_cluster = cluster_data[cluster_data['ID'].str.startswith('Seller')].sort_values(by='Price', ascending=True)
    
    matches = []
    for _, buyer in buyers_cluster.iterrows():
        for _, seller in sellers_cluster.iterrows():
            if buyer['Price'] >= seller['Price'] and buyer['Quantity'] > 0 and seller['Quantity'] > 0:
                trade_quantity = min(buyer['Quantity'], seller['Quantity'])
                matches.append((buyer['ID'], seller['ID'], seller['Price'], trade_quantity))
                
                # Update remaining quantities
                buyer['Quantity'] -= trade_quantity
                seller['Quantity'] -= trade_quantity
    
    return matches

# Apply matching to each cluster
all_matches = []
for cluster in range(n_clusters):
    all_matches.extend(match_bids_offers(cluster))

# Step 4: Compare results with uniform clearing
uniform_price = np.mean(market_data['Price'])  # Simple uniform clearing price
market_data['Cleared'] = market_data['Price'] <= uniform_price

# Print results
print("Hierarchical Clustering Market Matches:")
for match in all_matches:
    print(f"Buyer {match[0]} matched with Seller {match[1]} at {match[2]:.2f} $/MWh for {match[3]:.1f} MWh")

print("\nTraditional Uniform Clearing:")
cleared_buyers = market_data[(market_data['ID'].str.startswith('Buyer')) & (market_data['Cleared'])]
cleared_sellers = market_data[(market_data['ID'].str.startswith('Seller')) & (market_data['Cleared'])]
print(f"{len(cleared_buyers)} buyers and {len(cleared_sellers)} sellers cleared at uniform price {uniform_price:.2f} $/MWh")


