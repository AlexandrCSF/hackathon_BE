import os
import zipfile
from collections import Counter

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from rest_framework import generics, serializers, status
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

    def post(self, request):
        recommendations = recommend_channels_and_content(request.GET['client_id'])

        return Response({
            'client_id': request.GET['client_id'],
            'recommended_channels': recommendations['channels'],
            'recommended_packages': recommendations['packages'],
            'recommended_tv_shows': recommendations['tv_shows'],
        }, status=200)


class RecommendFileView(generics.GenericAPIView):
    class ClientRequestSerializer(serializers.Serializer):
        client_id = serializers.IntegerField()

    def create_csv(self, data, content_name, folder):
        content = content_name
        for item in data:
            content += '\n'
            content += str(item)
        with open(folder, 'w') as file:
            file.write(content)

    def create_csvs(self, request):
        folder_path = settings.STATICFILES_DIRS[0] / 'report'
        os.makedirs(folder_path, exist_ok=True)

        recommendations = recommend_channels_and_content(request.GET['client_id'])

        self.create_csv(recommendations['channels'], 'channels', folder_path / 'channels.csv')
        self.create_csv(recommendations['packages'], 'packages', folder_path / 'packages.csv')
        self.create_csv(recommendations['tv_shows'], 'tv_shows', folder_path / 'tv_shows.csv')

    def create_zip(self, request):
        self.create_csvs(request)
        folder_path = settings.STATICFILES_DIRS[0] / 'report'

        with zipfile.ZipFile(settings.STATICFILES_DIRS[0] / 'report.zip', 'w') as zip_file:
            zip_file.write(folder_path / 'channels.csv', 'channels.csv')
            zip_file.write(folder_path / 'packages.csv', 'packages.csv')
            zip_file.write(folder_path / 'tv_shows.csv', 'tv_shows.csv')

    def post(self, request):
        self.create_zip(request)

        return Response({'link': "https://freedom-lens.ru/static/report.zip"}, status=status.HTTP_200_OK)


class RecommendEmailView(RecommendFileView):
    def get_content(self, data, content_name):
        content = content_name
        for item in data:
            content += '\n'
            content += str(item)
        return content

    def post(self, request):
        recommendations = recommend_channels_and_content(request.GET['client_id'])
        email_message = EmailMultiAlternatives(
            f'Recommendations by client with id = {request.GET["client_id"]}',
            f'',
            settings.DEFAULT_FROM_EMAIL,
            [request.data['email']]
        )

        email_message.attach('channels.csv', self.get_content(recommendations['channels'], 'channels', ), 'text/csv')
        email_message.attach('packages.csv', self.get_content(recommendations['packages'], 'packages', ), 'text/csv')
        email_message.attach('tv_shows.csv', self.get_content(recommendations['tv_shows'], 'tv_shows', ), 'text/csv')
        email_message.send()
        return Response({}, status=status.HTTP_200_OK)
