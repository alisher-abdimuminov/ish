from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from typing_extensions import final

from .models import User


@admin.register(User)
class UserModelAdmin(UserAdmin, admin.ModelAdmin):
    list_display = ["phone", "first_name", "last_name"]
    add_form = UserCreationForm
    form = UserChangeForm
    search_fields = ["phone", "first_name", "last_name"]
    fieldsets = (
        (
            "Foydalanuvchini tahrirlash",
            {
                "fields": (
                    "phone",
                    "first_name",
                    "last_name",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            "Yangi foydalanuvchi qo'shish",
            {
                "fields": (
                    "phone",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                )
            },
        ),
    )
