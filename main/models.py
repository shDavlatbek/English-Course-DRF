import os
from django.db import models
from django.urls import reverse
from tinymce.models import HTMLField
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.contrib.auth.models import AbstractUser
from main.helpers import CustomUserManager


class User(AbstractUser):
    username = models.CharField(max_length=150, blank=True, null=True)  # make username optional
    email = models.EmailField(_('email address'), unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
