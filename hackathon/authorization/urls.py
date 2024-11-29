from authorization.views import SendVerificationCodeView, VerifyVerificationCodeView
from django.urls import path

urlpatterns = [
    path('part1', SendVerificationCodeView.as_view()),
    path('part2', VerifyVerificationCodeView.as_view()),
]
