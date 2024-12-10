from django.contrib import admin
from .models import Product, Category, Review, Flavor

# Inline for associating flavors with products
class FlavorInline(admin.TabularInline):
    """
    Allows flavors to be associated directly with products in the admin interface.
    """
    model = Product.flavors.through  # Connects the many-to-many relationship
    extra = 1  # Allows adding a new row for flavors
    verbose_name = "Flavor"  # Label for the inline in the admin
    verbose_name_plural = "Flavors"  # Plural label

class ProductAdmin(admin.ModelAdmin):
    """
    Customizes the admin interface for managing products.
    """
    # Fields displayed in the product list view
    list_display = (
        'sku',
        'name',
        'category',
        'price',
        'sale_option',
        'size',
        'get_average_rating',
        'is_best_seller',
        'image',
    )

    # Fields to filter by in the admin panel
    list_filter = ('category', 'sale_option', 'size', 'is_best_seller')

    # Fields searchable in the admin search bar
    search_fields = ('name', 'sku', 'description')

    # Ordering of products in the admin list view
    ordering = ('sku',)

    # Inline configuration for flavors
    inlines = [FlavorInline]

    # Allows selecting multiple flavors with a user-friendly interface
    filter_horizontal = ('flavors',)

    # Organizes fields in sections for better user experience
    fieldsets = (
        (None, {
            'fields': ('name', 'custom_title', 'category', 'description', 'price', 'sale_option', 'size', 'flavors', 'shipping_info', 'image', 'is_best_seller')
        }),
        ('Additional Information', {
            'classes': ('collapse',),
            'fields': ('sku', 'image_url'),
        }),
    )

class CategoryAdmin(admin.ModelAdmin):
    """
    Customizes the admin interface for managing categories.
    """
    list_display = (
        'friendly_name',
        'name',
    )
    search_fields = ('name', 'friendly_name')  # Allows searching categories by name or friendly name

class ReviewAdmin(admin.ModelAdmin):
    """
    Customizes the admin interface for managing reviews.
    """
    list_display = ('product', 'rating', 'created_at', 'comment')
    list_filter = ('rating', 'created_at')  # Filter reviews by rating or creation date
    search_fields = ('product__name', 'comment')  # Search by product name or review comment

class FlavorAdmin(admin.ModelAdmin):
    """
    Customizes the admin interface for managing flavors.
    """
    list_display = ('name', 'category')  # Displays flavor name and associated category
    search_fields = ('name', 'category__name')  # Allows searching by flavor name or category name

# Registering models with their respective admin configurations
admin.site.register(Flavor, FlavorAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
