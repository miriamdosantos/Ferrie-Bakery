from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import Category, Flavor, Product, Review
from . import translation

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
