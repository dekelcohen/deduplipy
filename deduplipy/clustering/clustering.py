import pandas as pd
import numpy as np
import networkx as nx
from scipy.cluster.hierarchy import linkage, fcluster
import scipy.spatial.distance as ssd


def hierarchical_clustering(scored_pairs_table, col_names, cluster_threshold=0.5):
    """
    Apply hierarchical clustering to scored_pairs_table and perform the actual deduplication by adding a cluster id to
    each record

    Args:
        scored_pairs_table: Pandas dataframe containg all pairs and the similarity probability score
        col_names: name to use for deduplication
        cluster_threshold: threshold to apply in hierarchical clustering

    Returns:
        Pandas dataframe containing records with cluster id

    """
    graph = nx.Graph()
    for j, row in scored_pairs_table.iterrows():
        graph.add_node(row['row_number_1'], **{col: row[f'{col}_1'] for col in col_names})
        graph.add_node(row['row_number_2'], **{col: row[f'{col}_2'] for col in col_names})
        graph.add_edge(row['row_number_1'], row['row_number_2'], score=row['score'])

    components = nx.connected_components(graph)

    clustering = {}
    cluster_counter = 0
    for component in components:
        subgraph = graph.subgraph(component)
        if len(subgraph.nodes) > 1:
            adjacency = nx.to_numpy_matrix(subgraph, weight='score')
            condensed_distance = ssd.pdist(adjacency)
            z = linkage(condensed_distance, method='centroid')
            clusters = fcluster(z, t=cluster_threshold, criterion='distance')
        else:
            clusters = np.array([1])
        clustering.update(dict(zip(subgraph.nodes(), clusters + cluster_counter)))
        cluster_counter += len(component)
    df_clusters = pd.DataFrame.from_dict(clustering, orient='index', columns=['cluster_id'])
    df_clusters.sort_values('cluster_id', inplace=True)
    df_clusters['row_number'] = df_clusters.index
    return df_clusters
