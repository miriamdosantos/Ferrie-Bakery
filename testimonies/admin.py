from django.contrib import admin
from .models import Testimony

@admin.register(Testimony)
class TestimonyAdmin(admin.ModelAdmin):  # Usando ModelAdmin padrão
    list_display = ('product', 'user', 'rating', 'created_at')
