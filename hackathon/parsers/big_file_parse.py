from datetime import datetime

import pandas as pd
from django.conf import settings
from tqdm import tqdm

from data.models import TVShow, Viewing, Category, Client, Channel


class BigFileParse:
    def fill(self):
        df = pd.read_csv(settings.FILES_DIR / 'epg_stat_2024_10.csv', delimiter=';')
        ThroughModel = TVShow.categories.through
        categories = []
        tv_shows = []
        viewings = []
        tv_show_categories = []

        clients = {client.external_id: client.id for client in Client.objects.all()}
        existing_categories = {category.name: category for category in Category.objects.all()}
        existing_tv_shows = {(tv_show.name, tv_show.start_time, tv_show.finish_time, tv_show.main_category): tv_show for
                             tv_show in TVShow.objects.all()}
        existing_views = {(v.start_time,
                           v.finish_time,
                           v.device,
                           v.tv_show_id,
                           v.client_id,
                           v.channel_id): v for
                          v in Viewing.objects.all()}
        channels = set(Channel.objects.values_list('id', flat=True))
        new_channels = []
        max_tv_show_id = TVShow.objects.all().order_by('-id').first().id
        max_category_id = Category.objects.all().order_by('-id').first().id

        for index, row in tqdm(df.iterrows()):
            client_external_id, device, time_channel, channel_id, TVshowname, TVshowtimestart, TVshowtimeend, TVshowwatchedduration, category, subcategory = row

            category_instance = existing_categories.get(category)
            if not category_instance:
                max_category_id += 1
                category_instance = Category(id=max_category_id, name=category)
                categories.append(category_instance)
                existing_categories[category] = category_instance

            tv_show_key = (TVshowname,
                           datetime.strptime(TVshowtimestart, '%Y-%m-%d %H:%M:%S'),
                           datetime.strptime(TVshowtimeend, '%Y-%m-%d %H:%M:%S'),
                           category)
            tv_show_instance = existing_tv_shows.get(tv_show_key)
            max_tv_show_id += 1
            if not tv_show_instance:
                tv_show_instance = TVShow(
                    id=max_tv_show_id,
                    name=TVshowname,
                    start_time=TVshowtimestart,
                    finish_time=TVshowtimeend,
                    main_category=category
                )
                tv_shows.append(tv_show_instance)
                existing_tv_shows[tv_show_key] = tv_show_instance

            if channel_id not in channels:
                new_channels.append(Channel(id=channel_id))
                channels.add(channel_id)

            view_key = (datetime.strptime(TVshowtimestart, '%Y-%m-%d %H:%M:%S'),
                        datetime.strptime(TVshowtimeend, '%Y-%m-%d %H:%M:%S'),
                        device,
                        tv_show_instance.id,
                        clients[client_external_id],
                        channel_id)
            if view_key not in existing_views:
                viewing_instance = Viewing(
                    start_time=TVshowtimestart,
                    finish_time=TVshowtimeend,
                    device=device,
                    tv_show_id=tv_show_instance.id,
                    client_id=clients[client_external_id],
                    channel_id=channel_id
                )
                viewings.append(viewing_instance)

                tv_show_categories.append(ThroughModel(tvshow_id=tv_show_instance.id, category_id=category_instance.id))

        Category.objects.bulk_create(categories, batch_size=2000)
        TVShow.objects.bulk_create(tv_shows, batch_size=2000)
        Channel.objects.bulk_create(new_channels, batch_size=2000)
        Viewing.objects.bulk_create(viewings, batch_size=20000)

        ThroughModel.objects.bulk_create(tv_show_categories, ignore_conflicts=True)
