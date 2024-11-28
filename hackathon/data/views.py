import contextlib
import re

import pandas as pd
from dadata import Dadata
from django.conf import settings
from httpx import HTTPStatusError
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from data.models import AddressModel
from data.models import Client
from data.serializer import ClientSerializer


class TestView(generics.ListAPIView):
    serializer_class = ClientSerializer
    queryset = Client.objects.all()[:50]


class UpdateAddressesView(APIView):

    def init(self, *args, kwargs):
        super().__init__(*args, **kwargs)
        self.dadata = Dadata(settings.DADATA_TOKEN, settings.DADATA_SECRET)

    def get_geo_by_address(self, address):
        result = self.dadata.clean("address", f'г. Воронеж, {address}')
        return {'lon': result['geo_lon'], 'lat': result['geo_lat']}

    def post(self, request, *args, **kwargs):
        with open('address.csv', 'r', encoding='utf-8') as file:
            content = file.read()

        # Замена найденных строк на пустую строку
        modified_content = re.sub(r'".*"', '', content)

        # Записываем измененное содержимое обратно в файл
        with open('address.csv', 'w', encoding='utf-8') as file:
            file.write(modified_content)
        data = pd.read_csv('address.csv', delimiter=';')
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
                    new_addresses.append(AddressModel({**self.get_geo_by_address(row['address']), **row}))
                if index == 10:
                    break

        AddressModel.objects.bulk_create(new_addresses, batch_size=10000)
        AddressModel.objects.bulk_update(update_addresses, batch_size=10000, fields=['flats', 'entrances', 'floors'])

        return Response({}, status=status.HTTP_200_OK)
