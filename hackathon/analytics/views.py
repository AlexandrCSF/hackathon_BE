from django.db.models import Q, Count
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from data.models import TVShow


class RequestSerializer(serializers.Serializer):
    start_time = serializers.DateField(required=False)
    finish_time = serializers.DateField(required=False)


class TVShowSerializer(serializers.ModelSerializer):
    view_count = serializers.IntegerField()

    class Meta:
        model = TVShow
        exclude = ("categories",)


class ResponseSerializer(serializers.Serializer):
    tv_shows = TVShowSerializer(many=True)


class MostViewedTVShowsView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = RequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        tv_shows = TVShow.objects.all()
        q = Q()
        if data.get('start_time'):
            q = q & Q(viewing__start_time__gte=data.get('start_time'))
        if data.get('finish_time'):
            q = q & Q(viewing__finish_time__lte=data.get('finish_time'))

        tv_shows = tv_shows.annotate(view_count=Count('viewing', filter=q))
        tv_shows = tv_shows.order_by('-view_count')

        return Response(ResponseSerializer({'tv_shows': tv_shows[:50]}).data, status=status.HTTP_200_OK)
