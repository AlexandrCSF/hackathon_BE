from django.urls import path

from recommend.views import RecommendView, RecommendFileView, RecommendEmailView

urlpatterns = [
    path('recommend/', RecommendView.as_view()),
    path('recommend_file/', RecommendFileView.as_view()),
    path('recommend_email/', RecommendEmailView.as_view()),
]
