from django.urls import path

from analytics.views import MostViewedTWShowsView, MostViewedChannelsView

urlpatterns = [
    path('most_viewed_tw_shows/', MostViewedTWShowsView.as_view()),
    path('most_viewed_channels/', MostViewedChannelsView.as_view()),
]
