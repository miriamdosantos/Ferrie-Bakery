from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_bag, name='view_bag'),
    path('add/<item_id>/', views.add_to_bag, name='add_to_bag'),
    path('clear-bag/', views.clear_bag, name='clear_bag'),
    path('bag/adjust/<int:item_id>/', views.adjust_bag, name='adjust_bag'),

    path('remove/<item_key>/', views.remove_from_bag, name='remove_from_bag'),
    
]