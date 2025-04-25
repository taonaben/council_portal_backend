import django.contrib.auth.models
from django.contrib import admin

from portal.models import User, Account

admin.site.register(User)
admin.site.register(Account)
