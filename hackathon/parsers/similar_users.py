from collections import Counter
import numpy as np
from sklearn.neighbors import NearestNeighbors

from data.models import Client, Category, SimilarClient
from tqdm import tqdm

def save_similar_clients():
    clients = Client.objects.prefetch_related('viewing_set__tv_show__categories')

    categories = Category.objects.all()
    category_to_index = {category.name: idx for idx, category in enumerate(categories)}

    client_features = []

    for client in tqdm(clients):
        feature_vector = np.zeros(len(categories))

        for viewing in client.viewing_set.all():
            for category in viewing.tv_show.categories.all():
                category_idx = category_to_index.get(category.name)
                if category_idx is not None:
                    feature_vector[category_idx] = 1

        client_features.append(feature_vector)

    client_features = np.array(client_features)

    knn = NearestNeighbors(n_neighbors=5, metric='cosine')
    knn.fit(client_features)

    for client_idx, client in tqdm(enumerate(clients)):
        target_client_vector = client_features[client_idx]

        distances, indices = knn.kneighbors([target_client_vector])

        for idx in indices[0]:
            if idx != client_idx:
                similar_client = clients[idx]
                similarity_score = 1 - distances[0][np.where(indices[0] == idx)[0][0]]

                SimilarClient.objects.update_or_create(
                    client=client,
                    similar_client=similar_client,
                    defaults={'similarity_score': similarity_score},
                )