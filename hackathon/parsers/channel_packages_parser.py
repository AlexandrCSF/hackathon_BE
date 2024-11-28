import pandas as pd
from django.conf import settings

from data.models import Client, AddressModel, ChannelPackege


class ChannelsPackagesParser:
    def fill(self):
        df = pd.read_csv(settings.FILES_DIR / 'package_channel.csv')
        package_channels = []
        for row in df.iterrows():
            package_channels.append(ChannelPackege(name=row[1][0].split(';')[0]))
        ChannelPackege.objects.bulk_create(package_channels)