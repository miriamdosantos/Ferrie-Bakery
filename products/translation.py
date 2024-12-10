from modeltranslation.translator import register, TranslationOptions
from .models import Product, Category, Flavor

@register(Product)
class ProductTranslationOptions(TranslationOptions):
    """
    Specifies which fields of the Product model will support translations.
    """
    fields = ('name', 'custom_title', 'description', 'shipping_info')

@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    """
    Specifies which fields of the Category model will support translations.
    """
    fields = ('name', 'friendly_name')

@register(Flavor)
class FlavorTranslationOptions(TranslationOptions):
    """
    Specifies which fields of the Flavor model will support translations.
    """
    fields = ('name',)
