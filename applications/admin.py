from django.contrib import admin

from .models import Application


@admin.register(Application)
class ApplicationModelAdmin(admin.ModelAdmin):
    list_display = ["user", "status", "created_at"]
