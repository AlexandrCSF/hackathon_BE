import random
import string

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from authorization.models import User, CodeModel
from authorization.serializers import SendVerificationCodeSerializer


class SendVerificationCodeView(APIView):
    @swagger_auto_schema(request_body=SendVerificationCodeSerializer)
    def post(self, request, *args, **kwargs):
        serializer = SendVerificationCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        user, crated = User.objects.get_or_create(email=email, defaults={'username': 'name?'})

        code = ''.join(random.choice(string.digits) for _ in range(6))
        # user, created = User.objects.get_or_create(email=email, defaults={'username': 'name?'})

        code_model, _ = CodeModel.objects.update_or_create(update_defaults={'code': code}, email=email)

        email_message = EmailMultiAlternatives(
            'Your Activation Code',
            f'ваш код {code_model}',
            settings.DEFAULT_FROM_EMAIL,
            [email]
        )
        # email_message.attach_alternative(html_content, "text/html")
        email_message.send()

        return Response({"message": "Verification code sent to email"}, status=status.HTTP_200_OK)

# class VerifyVerificationCodeView(APIView):
#     @swagger_auto_schema(request_body=VerifyVerificationCodeSerializer)
#     def post(self, request, *args, **kwargs):
#         serializer = VerifyVerificationCodeSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         email = serializer.validated_data['email']
#         code = serializer.validated_data['code']
#
#         if email not in cache:
#             return Response({"error": "Verification code has expired."}, status=status.HTTP_400_BAD_REQUEST)
#         if cache[email] != code:
#             return Response({"error": "Invalid verification code."}, status=status.HTTP_400_BAD_REQUEST)
#
#         del cache[email]
#         return Response({"message": "Verification code is valid."}, status=status.HTTP_200_OK)
