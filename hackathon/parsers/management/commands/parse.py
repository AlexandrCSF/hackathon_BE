from django.core.management import BaseCommand

from parsers.big_file_parse import BigFileParse
from parsers.channel_packages_parser import ChannelsPackagesParser
from parsers.clientparser import ClientParser


class Command(BaseCommand):
    help = 'fill database'

    def handle(self, *args, **options):
        ClientParser().fill()
        ChannelsPackagesParser().fill()
        BigFileParse().fill()
