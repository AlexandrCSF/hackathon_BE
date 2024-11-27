from rest_framework import serializers


class SendVerificationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyVerificationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
