from django.conf import settings
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


class BaseMostViewedTVShowsView(APIView):
    def get_data(self, request):
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
        return ResponseSerializer({'tv_shows': tv_shows[:50]}).data


class MostViewedTVShowsView(BaseMostViewedTVShowsView):

    def post(self, request, *args, **kwargs):
        return Response(self.get_data(request), status=status.HTTP_200_OK)


class MostViewedTVShowsFileView(BaseMostViewedTVShowsView):

    def post(self, request, *args, **kwargs):
        data = self.get_data(request)
        content = ';'.join(data['tv_shows'][0].keys())
        for tv_show in data['tv_shows']:
            content += '\n'
            content += ';'.join([str(v) for v in tv_show.values()])  # формат даты не как в исходных csv
        with open(settings.STATICFILES_DIRS[0] / '123.csv', 'w') as file:
            file.write(content)
        # return FileResponse(open('123.csv', 'rb'), as_attachment=True)
        return Response({'link': f"{settings.HOST}:8000/static/{'123.csv'}"}, status=status.HTTP_200_OK)
