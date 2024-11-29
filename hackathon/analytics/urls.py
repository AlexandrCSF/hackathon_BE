from django.urls import path

from analytics.views import MostViewedTVShowsView

urlpatterns = [
    path('most_viewed_tw_shows/', MostViewedTVShowsView.as_view()),
]
