from django.db.models import Q, Count
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from data.models import TVShow, Channel


class RequestSerializer(serializers.Serializer):
    start_time = serializers.DateField(required=False)
    finish_time = serializers.DateField(required=False)


class MostViewedTWShowsView(APIView):
    serializer_class = None

    def post(self, request, *args, **kwargs):
        serializer = RequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        # viewing = Viewing.objects.all()
        tw_shows = TVShow.objects.all()
        q = Q()
        if data.get('start_time'):
            q = q & Q(viewing__start_time__gte=data.get('start_time'))
        if data.get('finish_time'):
            q = q & Q(viewing__finish_time__lte=data.get('finish_time'))

        aggregate = tw_shows.annotate(view_count=Count('viewing', filter=q))
        aggregate = aggregate.order_by('view_count')

        return Response(self.serializer_class({}).data, status=status.HTTP_200_OK)


class MostViewedChannelsView(APIView):
    serializer_class = None

    def post(self, request, *args, **kwargs):
        serializer = RequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        q = Q()
        if data.get('start_time'):
            q = q & Q(viewing__start_time__gte=data.get('start_time'))
        if data.get('finish_time'):
            q = q & Q(viewing__finish_time__lte=data.get('finish_time'))

        channels = Channel.objects.all()
        aggregate = channels.annotate(view_count=Count('viewing', filter=q))
        aggregate = aggregate.order_by('view_count')

        return Response(self.serializer_class({}).data, status=status.HTTP_200_OK)
