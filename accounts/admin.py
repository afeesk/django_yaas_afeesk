from django.contrib import admin

# Register your models here.
from .models import EmailConfirmed,UserProfile
admin.site.register(EmailConfirmed)
admin.site.register(UserProfile)
