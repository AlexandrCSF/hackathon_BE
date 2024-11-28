from django.core.management import BaseCommand

from parsers.parser import Parser


class Command(BaseCommand):
    help = 'fill database'

    def handle(self, *args, **options):
        parser = Parser()
        parser.fill()