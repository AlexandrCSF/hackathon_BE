from django.core.management import BaseCommand

from parsers.clientparser import ClientParser


class Command(BaseCommand):
    help = 'fill database'

    def handle(self, *args, **options):
        parser = ClientParser()
        parser.fill()