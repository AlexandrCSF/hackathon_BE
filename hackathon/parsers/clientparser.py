import pandas as pd
from django.conf import settings
from django.db.models import Min
from tqdm import tqdm

from data.models import Client, AddressModel, Viewing


class ClientParser:
    def fill(self):
        df = pd.read_csv(settings.FILES_DIR / 'client.csv',delimiter=';')
        addresses = {address.address: address for address in AddressModel.objects.all()}

        clients_to_update = []
        clients_to_create = []
        existing_external_ids = set(Client.objects.values_list('external_id', flat=True))

        for row in tqdm(df.iterrows()):
            data = row[1]
            external_id = data[0]

            gender = False if data[2] == 'Ж' else True
            age_min, age_max = data[3].split('-')
            address = addresses.get(str(data[1]), None)

            if external_id in existing_external_ids:
                client = Client.objects.get(external_id=external_id)
                client.address = address
                client.gender = gender
                clients_to_update.append(client)
            else:
                clients_to_create.append(Client(
                    external_id=external_id,
                    gender=gender,
                    age_min=age_min,
                    age_max=age_max,
                    address=address
                ))

        Client.objects.bulk_update(clients_to_update, ['address','gender'])
        Client.objects.bulk_create(clients_to_create)
        print('parsed clients: ' + str(len(clients_to_create)))
        print('updated clients: ' + str(len(clients_to_update)))