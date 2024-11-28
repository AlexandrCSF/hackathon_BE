from django.core.management import BaseCommand

from parsers.channel_packages_parser import ChannelsPackagesParser
from parsers.clientparser import ClientParser


class Command(BaseCommand):
    help = 'fill database'

    def handle(self, *args, **options):
        parser_client = ClientParser()
        parser_client.fill()
        parser_channel = ChannelsPackagesParser()
        parser_channel.fill()