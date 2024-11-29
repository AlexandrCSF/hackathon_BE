from django.urls import path

from analytics.views import MostViewedTWShowsView

urlpatterns = [
    path('most_viewed_tw_shows/', MostViewedTWShowsView.as_view()),
]
