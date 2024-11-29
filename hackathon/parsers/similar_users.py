from collections import Counter
import numpy as np
from sklearn.cluster import KMeans
from sklearn.neighbors import NearestNeighbors

from data.models import Client, Category, SimilarClient
from tqdm import tqdm


class SimilarClientParse:
    def fill(self):
        clients = Client.objects.prefetch_related('viewing_set__tv_show__categories')[:6000]

        categories = Category.objects.all()

        category_to_index = {category.name: idx for idx, category in enumerate(categories)}

        client_features = []

        for client in tqdm(clients.iterator(chunk_size=200)):
            feature_vector = np.zeros(len(categories))

            for viewing in client.viewing_set.all():
                for category in viewing.tv_show.categories.all():
                    category_idx = category_to_index.get(category.name)
                    if category_idx is not None:
                        feature_vector[category_idx] = 1

            client_features.append(feature_vector)

        client_features = np.array(client_features)

        kmeans = KMeans(n_clusters=5, random_state=0)
        kmeans.fit(client_features)

        cluster_labels = kmeans.labels_

        cluster_to_clients = {i: [] for i in range(kmeans.n_clusters)}
        for client_idx, cluster_label in enumerate(cluster_labels):
            cluster_to_clients[cluster_label].append(clients[client_idx])

        for cluster_label, cluster_clients in cluster_to_clients.items():
            for client in cluster_clients:
                for similar_client in cluster_clients:
                    if client != similar_client:
                        similarity_score = np.dot(client_features[clients.index(client)],
                                                  client_features[clients.index(similar_client)]) / (np.linalg.norm(
                            client_features[clients.index(client)]) * np.linalg.norm(
                            client_features[clients.index(similar_client)]))

                        SimilarClient.objects.update_or_create(
                            client=client,
                            similar_client=similar_client,
                            defaults={'similarity_score': similarity_score},
                        )