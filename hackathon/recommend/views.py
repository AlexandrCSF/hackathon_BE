# Create your views here.
from collections import Counter

from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, serializers
from rest_framework.response import Response
from tqdm import tqdm

from data.models import Client


def recommend_channels_and_content(client_id):
    client = Client.objects.get(id=client_id)

    similar_clients = Client.objects.filter(
        similar_to__client=client
    ).distinct()[:5]

    channel_counter = Counter()
    package_counter = Counter()
    tv_show_counter = Counter()
    for similar_client in tqdm(similar_clients):
        for viewing in similar_client.viewing_set.all()[:5]:
            channel_counter[viewing.channel] += 1
            tv_show_counter[viewing.tv_show] += 1

            for package in viewing.channel.packege.all()[:5]:
                package_counter[package] += 1

    recommended_channels = [channel for channel, count in channel_counter.most_common(5)]

    recommended_packages = [package for package, count in package_counter.most_common(5)]

    recommended_tv_shows = [tv_show for tv_show, count in tv_show_counter.most_common(5)]

    return {
        "channels": [channel.id for channel in recommended_channels],
        "packages": [package.name for package in recommended_packages],
        "tv_shows": [tv_show.name for tv_show in recommended_tv_shows],
    }

class RecommendView(generics.GenericAPIView):
    class ClientRequestSerializer(serializers.Serializer):
        client_id = serializers.IntegerField()

    @swagger_auto_schema(query_serializer=ClientRequestSerializer())
    def post(self, request):
        recommendations = recommend_channels_and_content(request.GET['client_id'])

        return Response({
            'client_id': request.GET['client_id'],
            'recommended_channels': recommendations['channels'],
            'recommended_packages': recommendations['packages'],
            'recommended_tv_shows': recommendations['tv_shows'],
        }, status=200)