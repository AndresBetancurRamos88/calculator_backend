from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "balance", "status", "id")
    list_filter = ("username",)

    def save_model(self, request, obj, form, change):
        # Manually encode the password before saving the user object
        obj.set_password(obj.password)
        obj.save()


admin.site.register(User, UserAdmin)
