from django.urls import path

from analytics.views import MostViewedTVShowsView, MostViewedTVShowsFileView, UserWatchedChannelView

urlpatterns = [
    path('most_viewed_tw_shows/', MostViewedTVShowsView.as_view()),
    path('most_viewed_tw_shows_file/', MostViewedTVShowsFileView.as_view()),
    path('user_channel/', UserWatchedChannelView.as_view()),
]
