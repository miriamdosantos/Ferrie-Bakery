from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_bag, name='view_bag'),
    path('add/<item_id>/', views.add_to_bag, name='add_to_bag'),
    path('clear-bag/', views.clear_bag, name='clear_bag'),
    path('adjust/<str:item_key>/', views.adjust_bag, name='adjust_bag'),
    path('remove/<str:item_key>/', views.remove_from_bag, name='remove_item'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),

    
]