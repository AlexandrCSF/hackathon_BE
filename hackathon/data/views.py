from django.shortcuts import render
from rest_framework import generics

from data.models import Client
from data.serializer import ClientSerializer


# Create your views here.
class TestView(generics.ListAPIView):
    serializer_class = ClientSerializer
    queryset = Client.objects.all()[:50]
