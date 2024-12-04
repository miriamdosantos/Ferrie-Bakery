from django.contrib import admin

# Register your models here.
from .models import StoreUpdate

@admin.register(StoreUpdate)
class StoreUpdateAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at", "is_active")
    list_filter = ("is_active", "created_at")
    search_fields = ("title", "description")