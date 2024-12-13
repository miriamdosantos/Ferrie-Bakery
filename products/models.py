from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
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

class Flavor(models.Model):
    name = models.CharField(max_length=254, verbose_name=_("Flavor"))

    is_truffled = models.BooleanField(default=False, verbose_name=_("Is Truffled"))

    class Meta:
            verbose_name = _("Flavor")
            verbose_name_plural = _("Flavors")

    def __str__(self):
            return f"{self.name} ({'Truffled' if self.is_truffled else 'Traditional'})"
    
class Product(models.Model):
    PRICE_UNIT_CHOICES = [
        ("unit", _("Per Unit")),
        ("hundred", _("Per Hundred")),
        ("kilo", _("Per Kilo")),
        ("piece", _("Per Piece")),
        ("size", _("By Size (Small, Medium, Large)")),
    ]

    SIZE_CHOICES = [
        ("small", _("Small")),
        ("medium", _("Medium")),
        ("large", _("Large")),
    ]

    SIZE_PRICES = {
        "small": 7.00,
        "medium": 30.00,
        "large": 75.00,
    }

    category = models.ForeignKey("Category", null=True, blank=True, on_delete=models.SET_NULL)
    sku = models.CharField(max_length=254, null=True, blank=True)
    name = models.CharField(max_length=254, null=True, blank=True)
    custom_title = models.CharField(
        max_length=254,
        null=True,
        blank=True,
        verbose_name=_("Custom Title"),
    )
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    sale_option = models.CharField(
        max_length=20,
        choices=PRICE_UNIT_CHOICES,
        default="unit",
        verbose_name=_("Sale Option"),
    )
    size = models.CharField(
        max_length=20,
        choices=SIZE_CHOICES,
        null=True,
        blank=True,
        verbose_name=_("Size"),
    )
    shipping_info = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Shipping Information"),
    )
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    is_best_seller = models.BooleanField(default=False)
    image = models.ImageField(null=True, blank=True)
    flavors = models.ManyToManyField(Flavor, blank=True, verbose_name=_("Flavors"))

    class Meta:
        ordering = ["name"]
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def __str__(self):
        return self.name or self.custom_title or _("Unnamed Product")
    
    def get_average_rating(self):
        """Calcula a média das avaliações associadas."""
        reviews = self.reviews.all()
        if reviews.exists():
            return sum(review.rating for review in reviews) / reviews.count()
        return None


    def calculate_price_by_size(self, size):
        """Calcula o preço com base no tamanho selecionado."""
        return self.SIZE_PRICES.get(size, self.price)  # Retorna o preço baseado no tamanho ou o preço padrão se não encontrado

    def calculate_total_price(self, quantity, size=None, flavor=None):
        """Calcula o preço total com base no tipo de unidade, tamanho e sabor."""
        if flavor and flavor.is_truffled:
            base_price = 75.00  # Preço por quilo para sabores trufados
        else:
            base_price = 50.00  # Preço por quilo para sabores tradicionais

        # Se um tamanho foi escolhido, use o preço baseado no tamanho
        if size:
            price = self.calculate_price_by_size(size)
        else:
            price = base_price  # Use o preço padrão se nenhum tamanho for selecionado

        if self.sale_option == "unit":
            return price * quantity
        elif self.sale_option == "hundred":
            return price * (quantity / 100)
        elif self.sale_option == "kilo":
            return price * (quantity / 1000)
        return price


class Review(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_("Rating"),
    )
    comment = models.TextField(max_length=500, blank=True, null=True, verbose_name=_("Comment"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Review")
        verbose_name_plural = _("Reviews")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Review for {self.product.name} with rating {self.rating}"
