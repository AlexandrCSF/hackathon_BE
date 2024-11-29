from rest_framework import serializers

from data.models import Client, AddressModel


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressModel
        fields = ('lon', 'lat', 'address')


class ClientSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    color = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = "__all__"

    def get_color(self, client):
        category_colors = {
            "Познавательное": "#ffbf00",
            "Сериал": "#ff4500",
            "Досуг": "#32cd32",
            "Инфо": "#4682b4",
            "Фильм": "#8a2be2",
            "Остальное": "#808080",
            "Спорт": "#00bfff",
            "Детям": "#ff1493",
            "Для взрослых": "#800080",
        }

        categories = client.viewing_set.values_list('tv_show__categories__name', flat=True).distinct()

        for category in categories:
            if category in category_colors:
                return category_colors[category]

        return "#be2633"

class AllClientsSerializer(serializers.Serializer):
    clients = ClientSerializer(many=True)
