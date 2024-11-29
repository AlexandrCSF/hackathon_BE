from sklearn.cluster import KMeans
import numpy as np
from collections import defaultdict
from tqdm import tqdm
from django.db import transaction
from data.models import Client, Category, SimilarClient


class SimilarClientParse:
    def fill(self):
        clients = list(Client.objects.prefetch_related('viewing_set__tv_show__categories')[:6000])
        categories = list(Category.objects.all())

        category_to_index = {category.name: idx for idx, category in enumerate(categories)}
        client_index_mapping = {client.id: idx for idx, client in enumerate(clients)}

        client_features = []

        for client in tqdm(clients, desc="Generating client features"):
            feature_vector = np.zeros(len(categories), dtype=np.float32)

            for viewing in client.viewing_set.all():
                for category in viewing.tv_show.categories.all():
                    category_idx = category_to_index.get(category.name)
                    if category_idx is not None:
                        feature_vector[category_idx] = 1

            client_features.append(feature_vector)

        client_features = np.array(client_features, dtype=np.float32)

        kmeans = KMeans(n_clusters=5, random_state=0)
        kmeans.fit(client_features)

        cluster_labels = kmeans.labels_

        cluster_to_clients = defaultdict(list)
        for client, cluster_label in zip(clients, cluster_labels):
            cluster_to_clients[cluster_label].append(client)

        SimilarClient.objects.all().delete()

        with transaction.atomic():
            for cluster_clients in tqdm(cluster_to_clients.values(), desc="Processing clusters"):
                cluster_indices = [client_index_mapping[client.id] for client in cluster_clients]

                cluster_feature_vectors = client_features[cluster_indices]

                norms = np.linalg.norm(cluster_feature_vectors, axis=1, keepdims=True)
                cluster_feature_vectors = cluster_feature_vectors / (norms + 1e-10)

                similarity_matrix = np.dot(cluster_feature_vectors, cluster_feature_vectors.T)

                similar_objects = []
                for i, client in enumerate(cluster_clients):
                    for j, similar_client in enumerate(cluster_clients):
                        if i != j:
                            similarity_score = similarity_matrix[i, j]
                            similar_objects.append(SimilarClient(
                                client=client,
                                similar_client=similar_client,
                                similarity_score=similarity_score,
                            ))
                SimilarClient.objects.bulk_create(similar_objects, batch_size=1000)