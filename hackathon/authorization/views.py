import random
import string

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from authorization.models import User, CodeModel
from authorization.serializers import SendVerificationCodeSerializer, VerifyVerificationCodeSerializer


class SendVerificationCodeView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = SendVerificationCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        if email not in ['vadim.egorov.02@mail.ru', 'z3firniy@yandex.ru', 'Kotov.Sasho204@yandex.ru']:
            return Response(status=status.HTTP_403_FORBIDDEN)

        code = ''.join(random.choice(string.digits) for _ in range(6))

        code_model, _ = CodeModel.objects.update_or_create(defaults={'code': code}, mail=email)

        email_message = EmailMultiAlternatives(
            'Your Activation Code',
            f'ваш код {code}',
            settings.DEFAULT_FROM_EMAIL,
            [email]
        )
        email_message.send()

        return Response({"message": "Verification code sent to email"}, status=status.HTTP_200_OK)


class VerifyVerificationCodeView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = VerifyVerificationCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        # user, created = User.objects.get_or_create(email=email, defaults={'username': email.split('@')[0]})

        if not CodeModel.objects.filter(mail=email, code=code).first():
            return Response({'error': 'Код неверный'}, status=status.HTTP_403_FORBIDDEN)

        CodeModel.objects.filter(mail=email, code=code).delete()

        return Response({"message": "Verification code is valid."}, status=status.HTTP_200_OK)
