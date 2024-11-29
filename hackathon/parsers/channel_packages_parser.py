import pandas as pd
from django.conf import settings

from data.models import Client, AddressModel, ChannelPackege, Channel


class ChannelsPackagesParser:
    def fill(self):
        df = pd.read_csv(settings.FILES_DIR / 'package_channel.csv')
        ThroughModel = Channel.packege.through
        package_channels = []
        channels = []
        throughs = []

        Channel.objects.all().delete()
        ChannelPackege.objects.all().delete()
        ThroughModel.objects.all().delete()

        for index, row in df.iterrows():
            package_name, channel_id = row[0].split(';')
            channel_id = int(channel_id)

            channel, created = Channel.objects.get_or_create(id=channel_id)
            if created:
                channels.append(channel)

            package, created = ChannelPackege.objects.get_or_create(name=package_name)
            if created:
                package_channels.append(package)

            throughs.append(ThroughModel(channel_id=channel_id, channelpackege_id=package.id))

        ChannelPackege.objects.bulk_create(package_channels, ignore_conflicts=True)
        Channel.objects.bulk_create(channels, ignore_conflicts=True)

        ThroughModel.objects.bulk_create(throughs, ignore_conflicts=True)