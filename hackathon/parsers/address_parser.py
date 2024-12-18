import contextlib
import re

import pandas as pd
from dadata import Dadata
from django.conf import settings
from httpx import HTTPStatusError
from rest_framework import status
from rest_framework.response import Response

from data.models import AddressModel


class AddressParser:
    def fill(self):
        file_name = settings.FILES_DIR / 'address.csv'
        with open(file_name, 'r', encoding='utf-8') as file:
            content = file.read()
        modified_content = re.sub(r'".*"', '', content)
        modified_content = modified_content.replace('\r\n', '\n')

        # Записываем измененное содержимое обратно в файл
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(modified_content)
        data = pd.read_csv(file_name, delimiter=';')
        new_addresses = []
        update_addresses = []
        existing_addresses = {a.address: a for a in AddressModel.objects.all()}
        with contextlib.suppress(HTTPStatusError):
            for index, row in data.iterrows():
                try:
                    row['floors'] = int(row['floors'])
                except Exception:
                    row['floors'] = 0

                if address_model := existing_addresses.get(row['address']):
                    if address_model.flats != row['flats'] or address_model.entrances != row[
                        'entrances'] or address_model.floors != row['floors']:
                        address_model.flats = row['flats']
                        address_model.entrances = row['entrances']
                        address_model.floors = row['floors']
                        update_addresses.append(address_model)
                else:
                    new_addresses.append(AddressModel(**{**self.get_geo_by_address(row['address']), **row}))
                if index == 10:
                    break

        AddressModel.objects.bulk_create(new_addresses, batch_size=10000)
        AddressModel.objects.bulk_update(update_addresses, batch_size=10000, fields=['flats', 'entrances', 'floors'])

        return Response({}, status=status.HTTP_200_OK)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dadata = Dadata(settings.DADATA_TOKEN, settings.DADATA_SECRET)

    def get_geo_by_address(self, address):
        result = self.dadata.clean("address", f'г. Воронеж, {address}')
        return {'lon': result['geo_lon'], 'lat': result['geo_lat']}
