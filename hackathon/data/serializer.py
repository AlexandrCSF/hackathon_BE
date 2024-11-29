from rest_framework import serializers

from data.models import Client


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = "__all__"


class TestSerializer(serializers.Serializer):
    clients = ClientSerializer(many=True)
