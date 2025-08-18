from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_products, name='products'),
    path('<int:product_id>/', views.product_detail, name= 'product_detail'),
    path('add/', views.add_product, name='add_product'),
    path('edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('category/<slug:slug>/', views.products_by_category, name='products_by_category'),
    path("personalized/<slug:product_slug>/", views.create_personalized_cake, name="create_personalized_cake"),
    path("personalized/order/<int:order_id>/", views.personalized_detail, name="personalized_detail"),

]