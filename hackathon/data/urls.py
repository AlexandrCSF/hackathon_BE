from django.urls import path

from data.views import TestView

urlpatterns = [
    path('test/',TestView.as_view())
]