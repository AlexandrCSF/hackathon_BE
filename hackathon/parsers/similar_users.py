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

        kmeans = KMeans(n_clusters=len(categories), random_state=0)
        kmeans.fit(client_features)

        cluster_labels = kmeans.labels_

        for client, cluster_label in zip(clients, cluster_labels):
            client.kmeans_label = cluster_label
            client.save()

        client_to_cluster = {client.id: cluster_label for client, cluster_label in zip(clients, cluster_labels)}

        cluster_centroids = kmeans.cluster_centers_

        for client in clients:
            cluster_label = client_to_cluster[client.id]
            centroid = cluster_centroids[cluster_label]

            best_categories = np.argsort(centroid)[::-1][:3]
            client.preferred_category = categories[best_categories[0]].name
            client.save()
            print(f"Client {client.id} is most interested in categories: {', '.join([categories[i].name for i in best_categories])}")
