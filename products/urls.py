from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_products, name='products'),
    path('<product_id>', views.product_detail, name= 'product_detail'),
    path('category/<slug:slug>/', views.products_by_category, name='products_by_category'),
]