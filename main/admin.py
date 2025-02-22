from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from django.contrib.auth.admin import UserAdmin
from main import models
# Register your models here.
admin.site.register(models.User, UserAdmin)