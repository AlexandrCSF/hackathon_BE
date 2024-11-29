from rest_framework import serializers

from data.models import Client, AddressModel


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressModel
        fields = ('lon', 'lat', 'address')


class ClientSerializer(serializers.ModelSerializer):
    address = AddressSerializer()

    class Meta:
        model = Client
        fields = "__all__"


class AllClientsSerializer(serializers.Serializer):
    clients = ClientSerializer(many=True)
