from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import Category, Flavor, Product, Review, PersonalizedCakeOrder
from . import translation
from django.contrib import admin
from .models import PersonalizedCakeOrder, Product, Flavor, Category


@admin.register(Category)
class CategoryAdmin(TranslationAdmin):
    list_display = ('name', )

@admin.register(Flavor)
class FlavorAdmin(TranslationAdmin):
    list_display = ('name',)

@admin.register(Product)
class ProductAdmin(TranslationAdmin):
    list_display = ('name', 'category', 'price', 'sale_option', 'is_best_seller','has_topper', 'has_roses')
    list_filter = ('category', 'has_topper', 'has_roses')
    filter_horizontal = ('flavors', )

@admin.register(Review)
class ReviewAdmin(TranslationAdmin):
    list_display = ('product', 'rating', 'created_at')



@admin.register(PersonalizedCakeOrder)
class PersonalizedCakeOrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'flavor',  'quantity_kilo', 'total_price', 'created_at'
    )
    list_filter = ('created_at', 'flavor', 'user')
    search_fields = ('user__username', 'flavor__name', 'topper_text', 'message')