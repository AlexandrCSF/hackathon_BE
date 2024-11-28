import pandas as pd
from django.conf import settings

from data.models import Client


class Parser:
    def fill(self):
        df = pd.read_csv(settings.FILES_DIR / 'client.csv')
        clients = []
        for row in df.iterrows():
            data1 = row[1][0].split(';')
            data2 = row[0].split(';')
            clients.append(Client(external_id=data2[0],gender=data1[1],age_min=data1[2].split('-')[0],age_max=data1[2].split('-')[1],address=data2[1] + data1[0]))