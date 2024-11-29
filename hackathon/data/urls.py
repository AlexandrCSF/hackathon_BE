from django.urls import path

from data.views import ClientsView, UpdateAddressesView

urlpatterns = [
    path('clients/', ClientsView.as_view()),
    path('update_addresses/', UpdateAddressesView.as_view()),
]
