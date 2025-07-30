from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True)
    stage = models.ForeignKey('website.Stage', on_delete=models.SET_NULL, null=True, blank=True, related_name='stage')

    def __str__(self):
        return self.username