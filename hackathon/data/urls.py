from django.urls import path

from data.views import TestView, UpdateAddressesView

urlpatterns = [
    path('test/',TestView.as_view()),
    path('update_addresses/',UpdateAddressesView.as_view()),
]