from django.urls import path

from recommend.views import RecommendView, RecommendFileView

urlpatterns = [
    path('recommend/', RecommendView.as_view()),
    path('recommend_file/', RecommendFileView.as_view()),
]
