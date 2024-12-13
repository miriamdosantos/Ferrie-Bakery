from modeltranslation.translator import register, TranslationOptions
from .models import Category, Flavor, Product, Review

@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'friendly_name')

@register(Flavor)
class FlavorTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('name', 'custom_title', 'description', 'shipping_info')

@register(Review)
class ReviewTranslationOptions(TranslationOptions):
    fields = ('comment',)
