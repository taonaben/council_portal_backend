import django.contrib.auth.models
from django.contrib import admin

from portal.models import User

admin.site.register(User)