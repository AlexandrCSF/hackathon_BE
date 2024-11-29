import pandas as pd
from tqdm import tqdm
from django.conf import settings

from data.models import TVShow, Viewing, Category, Client


# class Category(models.Model):
#     name = models.CharField(max_length=64)
#
#
# class Viewing(models.Model):
#     start_time = models.DateField()
#     finish_time = models.DateField()
#     device = models.CharField(max_length=16)
#     tv_show = models.ForeignKey(TVShow, on_delete=models.CASCADE)
#     client = models.ForeignKey(Client, on_delete=models.CASCADE)
#     channel = models.ForeignKey(Channel, on_delete=models.CASCADE)

# class TVShow(models.Model):
#     start_time = models.DateField()
#     finish_time = models.DateField()
#     name = models.CharField(max_length=64)
#     main_category = models.CharField(max_length=64)
#     categories = models.ManyToManyField(Category, related_name='tv_shows')
#
#


class BigFileParse:
    def fill(self):
        df = pd.read_csv(settings.FILES_DIR / 'epg_stat_2024_10.csv', delimiter=';')
        ThroughModel = TVShow.categories.through
        categories = []
        tv_shows = []
        viewings = []
        tv_show_categories = []

        TVShow.objects.all().delete()
        Category.objects.all().delete()
        Viewing.objects.all().delete()
        ThroughModel.objects.all().delete()
        clients = {client.external_id: client.id for client in Client.objects.all()}
        i = 1

        for index, row in tqdm(df.iterrows()):
            client_external_id, device, time_channel, channel_id, TVshowname, TVshowtimestart, TVshowtimeend, TVshowwatchedduration, category, subcategory = row

            category_instance, created = Category.objects.get_or_create(name=category)
            if created:
                categories.append(category_instance)

            tv_show_instance, created = TVShow.objects.get_or_create(
                name=TVshowname,
                start_time=TVshowtimestart,
                finish_time=TVshowtimeend,
                main_category=category
            )
            if created:
                tv_shows.append(tv_show_instance)

            viewing_instance = Viewing(
                id = i,
                start_time=TVshowtimestart,
                finish_time=TVshowtimeend,
                device=device,
                tv_show=tv_show_instance,
                client_id=clients[client_external_id],
                channel_id=channel_id
            )
            viewings.append(viewing_instance)

            tv_show_categories.append(ThroughModel(tvshow_id=tv_show_instance.id, category_id=category_instance.id))
            i += 1
        Category.objects.bulk_create(categories, ignore_conflicts=True)
        TVShow.objects.bulk_create(tv_shows, ignore_conflicts=True)
        Viewing.objects.bulk_create(viewings, ignore_conflicts=True)

        ThroughModel.objects.bulk_create(tv_show_categories, ignore_conflicts=True)
