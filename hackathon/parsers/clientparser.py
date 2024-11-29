import pandas as pd
from django.conf import settings
from django.db.models import Min
from tqdm import tqdm

from data.models import Client, AddressModel, Viewing


class ClientParser:
    def fill(self):
        df = pd.read_csv(settings.FILES_DIR / 'client.csv')
        addresses = {address.address: address for address in AddressModel.objects.all()}

        clients_to_update = []
        clients_to_create = []
        existing_external_ids = set(Client.objects.values_list('external_id', flat=True))
        unique_external_ids = Client.objects.values_list('external_id', flat=True).distinct()

        for external_id in tqdm(unique_external_ids):
            clients = Client.objects.filter(external_id=external_id)

            if clients.count() > 1:
                min_id_client = clients.aggregate(Min('id'))['id__min']
                clients.exclude(id=min_id_client).delete()

        for row in df.iterrows():
            data1 = row[1][0].split(';')
            data2 = row[0].split(';')
            external_id = data2[0]

            gender = False if data1[1] == 'F' else True
            age_min, age_max = data1[2].split('-')
            address = addresses.get(data2[1] + data1[0], None)

            if external_id in existing_external_ids:
                client = Client.objects.get(external_id=external_id)
                if client.address != address:
                    client.address = address
                    clients_to_update.append(client)
            else:
                clients_to_create.append(Client(
                    external_id=external_id,
                    gender=gender,
                    age_min=age_min,
                    age_max=age_max,
                    address=address
                ))

        Client.objects.bulk_update(clients_to_update, ['address'])
        Client.objects.bulk_create(clients_to_create)
        print('parsed clients: ' + str(len(clients_to_create)))
        print('updated clients: ' + str(len(clients_to_update)))