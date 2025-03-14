from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('password-reset/', views.password_reset, name='password_reset'),
    
]