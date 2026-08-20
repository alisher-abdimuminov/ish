from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import User


# Register your models here.
@admin.register(User)
class UserModelAdmin(UserAdmin, admin.ModelAdmin):
    list_display = ["phone", "first_name", "last_name"]
    add_form = UserCreationForm
    form = UserChangeForm
    search_fields = ["phone", "full_name"]
