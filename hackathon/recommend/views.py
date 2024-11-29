from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, serializers
from rest_framework.response import Response
from sklearn.neighbors import NearestNeighbors
import numpy as np
from collections import Counter
from data.models import Client, Viewing, Channel, Category


def recommend_channels(client_id):
    client = Client.objects.get(id=client_id)

    similar_clients = Client.objects.filter(
        similar_clients__client=client
    ).distinct()

    channel_counter = Counter()

    for similar_client in similar_clients:
        for viewing in similar_client.viewing_set.all():
            channel_counter[viewing.channel] += 1

    recommended_channels = [channel for channel, count in channel_counter.most_common(5)]

    recommended_channel_names = [channel.name for channel in recommended_channels]

    return recommended_channel_names


class RecommendView(generics.GenericAPIView):
    class ClientRequestSerializer(serializers.Serializer):
        client_id = serializers.IntegerField()

    @swagger_auto_schema(query_serializer=ClientRequestSerializer())
    def post(self, request):
        recommended_channels = recommend_channels(request.GET['client_id'])

        return Response({
            'client_id': request.GET['client_id'],
            'recommended_channels': recommended_channels
        }, status=200)
