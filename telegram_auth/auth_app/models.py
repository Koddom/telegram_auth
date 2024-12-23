# auth_app/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    telegram_id = models.CharField(max_length=255, blank=True, null=True, unique=True)  # размер и тип поля желательно согласовать
    telegram_username = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return self.username or self.telegram_username
