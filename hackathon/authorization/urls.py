from authorization.views import SendVerificationCodeView
from django.urls import path

urlpatterns = [
    path('part1', SendVerificationCodeView.as_view()),
]
