import json
from datetime import datetime

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q, Count, F
from django.db.models import Sum
from rest_framework import generics
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from analytics.models import Template
from data.models import TVShow, Client, Channel, Viewing


class RequestSerializer(serializers.Serializer):
    start_time = serializers.TimeField(required=False)
    finish_time = serializers.TimeField(required=False)
    age_max = serializers.IntegerField(required=False)
    age_min = serializers.IntegerField(required=False)
    categories = serializers.ListSerializer(child=serializers.CharField(), required=False)
    sort_by_choices = [
        ('most_watched', 'Most Watched'),
        ('watch_time', 'Watch Time'),
        ('start_time', 'Start Time'),
        ('name', 'Name')
    ]
    sort_by = serializers.ChoiceField(choices=sort_by_choices, required=False)


class TVShowSerializer(serializers.ModelSerializer):
    view_count = serializers.IntegerField()

    class Meta:
        model = TVShow
        exclude = ("categories",)


class ResponseSerializer(serializers.Serializer):
    tv_shows = TVShowSerializer(many=True)


class BaseMostViewedTVShowsView(APIView):
    serializer = RequestSerializer

    def get_data(self, request):
        serializer = self.serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        tv_shows = TVShow.objects.all()

        q = Q()
        if data.get('start_time') or data.get('finish_time'):
            q &= Q(viewing__start_time__day=F('viewing__finish_time__day'))

        if data.get('start_time'):
            start_time_str = data.get('start_time')
            start_time = datetime.strptime(start_time_str, '%H:%M:%S').time()
            q &= Q(viewing__start_time__hour__gt=start_time.hour) | Q(viewing__start_time__hour=start_time.hour,
                                                                      viewing__start_time__minute__gte=start_time.minute)

        if data.get('finish_time'):
            finish_time_str = data.get('finish_time')
            finish_time = datetime.strptime(finish_time_str, '%H:%M:%S').time()
            q &= Q(viewing__finish_time__hour__lt=finish_time.hour) | Q(viewing__finish_time__hour=finish_time.hour,
                                                                        viewing__finish_time__minute__lte=finish_time.minute)

        if data.get('age_min') is not None and data.get('age_max') is not None:
            q &= Q(viewing__client__age_min__gte=data.get('age_min')) & Q(
                viewing__client__age_max__lte=data.get('age_max'))

        if data.get('categories'):
            category_names = data.get('categories')
            q &= Q(categories__name__in=category_names)

        tv_shows = tv_shows.annotate(view_count=Count('viewing', filter=q))

        sort_by = data.get('sort_by')
        if sort_by == 'most_watched':
            tv_shows = tv_shows.order_by('-view_count')
        elif sort_by == 'watch_time':
            tv_shows = tv_shows.order_by('viewing__duration')
        elif sort_by == 'start_time':
            tv_shows = tv_shows.order_by('viewing__start_time')
        else:
            tv_shows = tv_shows.order_by('-view_count')

        tv_shows = tv_shows[:50]

        return ResponseSerializer({'tv_shows': tv_shows}).data


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
        return Response({'link': "https://freedom-lens.ru/static/123.csv"}, status=status.HTTP_200_OK)


class RequestEmailSerializer(RequestSerializer):
    email = serializers.CharField()


class MostViewedTVShowsEmailView(BaseMostViewedTVShowsView):
    serializer = RequestEmailSerializer

    def post(self, request, *args, **kwargs):
        data = self.get_data(request)
        content = ';'.join(data['tv_shows'][0].keys())
        for tv_show in data['tv_shows']:
            content += '\n'
            content += ';'.join([str(v) for v in tv_show.values()])  # формат даты не как в исходных csv

        email_message = EmailMultiAlternatives(
            'Your most viewed TV shows report',
            f'',
            settings.DEFAULT_FROM_EMAIL,
            [request.data['email']]
        )
        email_message.attach('report.csv', content, 'text/csv')
        email_message.send()

        return Response({}, status=status.HTTP_200_OK)


class UserWatchedChannelView(generics.GenericAPIView):
    def post(self, request):
        client_id = request.GET["client_id"]
        channel_id = request.GET["channel_id"]

        client = Client.objects.filter(id=client_id).first()
        channel = Channel.objects.filter(id=channel_id).first()

        if not client or not channel:
            return Response(data={"error": "Invalid id"}, status=404)

        total_viewing_time = Viewing.objects.filter(client=client, channel=channel).aggregate(
            total_time=Sum(F('finish_time') - F('start_time'))
        )['total_time']

        if not total_viewing_time:
            total_viewing_time = 0

        return Response(
            data={
                "client_id": client_id,
                "channel_id": channel_id,
                "total_viewing_time": str(total_viewing_time)
            },
            status=200
        )


class TemplatesView(generics.GenericAPIView):
    def get(self, request):
        templates = Template.objects.values_list('template', flat=True)
        templates = [json.loads(t) for t in templates]

        return Response({'templates': RequestSerializer(templates, many=True).data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = RequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data

        Template.objects.get_or_create(template=json.dumps(data))
        return Response({}, status=status.HTTP_200_OK)
