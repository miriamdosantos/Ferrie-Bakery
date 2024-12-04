from django.db import models
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    name = models.CharField(max_length=254)
    friendly_name = models.CharField(max_length=254, null=True, blank=True)
    slug = models.SlugField(unique=True, max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.friendly_name


class Product(models.Model):
    PRICE_UNIT_CHOICES = [
        ("unit", _("Per Unit")),
        ("hundred", _("Per Hundred")),
        ("kilo", _("Per Kilo")),
    ]
    category = models.ForeignKey("Category", null=True, blank=True, on_delete=models.SET_NULL)
    sku = models.CharField(max_length=254, null=True, blank=True)
    name = models.CharField(max_length=254)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    price_unit = models.CharField(
        max_length=10,
        choices=PRICE_UNIT_CHOICES,
        default="unit"
    )
    rating = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    is_best_seller = models.BooleanField(default=False)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name

    def calculate_total_price(self, quantity):
        if self.price_unit == "unit":
            return self.price * quantity
        elif self.price_unit == "hundred":
            return self.price * (quantity / 100)
        elif self.price_unit == "kilo":
            return self.price * (quantity / 1000)
        return self.price
