from django.shortcuts import render
from rest_framework import generics

from data.models import Client


# Create your views here.
class TestView(generics.ListAPIView):
    queryset = Client.objects.all()
