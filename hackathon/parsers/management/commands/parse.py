from django.core.management import BaseCommand

from parsers.address_parser import AddressParser
from parsers.big_file_parse import BigFileParse
from parsers.channel_packages_parser import ChannelsPackagesParser
from parsers.clientparser import ClientParser
from parsers.similar_users import save_similar_clients


class Command(BaseCommand):
    help = 'fill database'

    def handle(self, *args, **options):
        AddressParser().fill()
        ClientParser().fill()
        ChannelsPackagesParser().fill()
        BigFileParse().fill()
        save_similar_clients()
