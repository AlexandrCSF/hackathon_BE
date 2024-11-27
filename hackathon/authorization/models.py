from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"


class CodeModel(models.Model):
    code = models.CharField(max_length=6)
    mail = models.EmailField()
    date_joined = models.DateTimeField(default=timezone.now)
