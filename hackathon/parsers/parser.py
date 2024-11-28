import csv
from pathlib import Path

from django.conf import settings
import requests


class Parser:
    def __init__(self, clients_url=None, address_url=None, package_channel_url=None, activities_url=None):
        clients_url = clients_url if clients_url else settings.CLIENTS_URL

        response = requests.get(clients_url)
        #self.address = requests.get(address_url if address_url else settings.ADDRESS_URL)
        #self.package_channel = requests.get(
        #    package_channel_url if package_channel_url else settings.PACKAGE_CHANNEL_URL)
        #self.activities = requests.get(activities_url if activities_url else settings.ACTIVITIES_URL)
        if response.status_code == 200:
            decoded_content = response.content.decode('utf-8-sig')
            rows = [row.split(',') for row in decoded_content.splitlines()]

            output_path = Path(settings.FILES_DIR) / 'clients.csv'
            with open(output_path, mode='w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                writer.writerows(rows)
        else:
            print(f"Ошибка при загрузке файла: {response.status_code}")

    def init_data(self):
        123
    def fill(self):
        123