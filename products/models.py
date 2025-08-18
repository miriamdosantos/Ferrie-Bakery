from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from cloudinary.models import CloudinaryField
from django.conf import settings




from django.utils.encoding import force_str
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
        # Força a conversão para string
        return force_str(self.name)


from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _

class Flavor(models.Model):
    name = models.CharField(max_length=254, verbose_name=_("Flavor"))
    is_truffled = models.BooleanField(default=False, verbose_name=_("Is Truffled"))

    class Meta:
        verbose_name = _("Flavor")
        verbose_name_plural = _("Flavors")

    def __str__(self):
        # Converte cada parte para string
        label = 'Truffled' if self.is_truffled else 'Traditional'
        return f"{force_str(self.name)} ({label})"

    
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
    name = models.CharField(max_length=254, )
    custom_title = models.CharField(
        max_length=254,
        null=True,
        blank=True,
        verbose_name=_("Custom Title"),
    )
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, )
    sale_option = models.CharField(
        max_length=20,
        choices=PRICE_UNIT_CHOICES,
        verbose_name=_("Sale Option"),
    )  # Obrigatório
    size = models.CharField(
        max_length=20,
        choices=SIZE_CHOICES,
        null=True,
        blank=True,
        verbose_name=_("Size"),
    ) # Opcional, usado somente para alguns produtos
    shipping_info = models.TextField(blank=True, default="Shipping information ")
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    is_best_seller = models.BooleanField(default=False)
    has_topper = models.BooleanField(default=False, verbose_name=_("Has Topper"))
    has_roses = models.BooleanField(default=False, verbose_name=_("Has Roses"))
    image = CloudinaryField('image', default='noimage.jpg', blank=True, null=True)

    flavors = models.ManyToManyField("Flavor",  verbose_name=_("Flavors"))

    class Meta:
        ordering = ["name"]
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def __str__(self):
        # Força a conversão para string em todas as opções
        if self.name:
            return force_str(self.name)
        elif self.custom_title:
            return force_str(self.custom_title)
        else:
            return force_str(_("Unnamed Product"))
    
    def get_average_rating(self):
        """Calcula a média das avaliações associadas."""
        reviews = self.reviews.all()
        if reviews.exists():
            return sum(review.rating for review in reviews) / reviews.count()
        return None


    def calculate_price_by_size(self, size):
        """Calcula o preço com base no tamanho selecionado."""
        return self.SIZE_PRICES.get(size, self.price)  # Retorna o preço baseado no tamanho ou o preço padrão se não encontrado

    def calculate_total_price(self, quantity, quantity_kilo=0, size=None, flavor=None, topper_text=None, roses_quantity=0, is_truffled=False):
        base_price = Decimal(self.price)
        print(f"Base price: {base_price}")

        # Ajusta o preço base de acordo com o tamanho, se aplicável
        if self.sale_option == "size" and size:
            if self.category.name == "Pies":
                base_price = Decimal(self.SIZE_PRICES.get(size, self.price))
            else:
                base_price = self.calculate_price_by_size(size)
        print(f"Adjusted base price: {base_price}")

        # Ajusta o preço para sabores trufados, se aplicável
        if flavor and flavor.is_truffled:
            base_price = Decimal('75.00')  # Preço por quilo para sabores trufados
        print(f"Final base price: {base_price}")

        # Calcula o preço total
        if quantity == 1:
            # Se há apenas uma unidade, use o maior entre o preço da unidade e o preço por quilo
            unit_price = base_price
            kilo_price = base_price * Decimal(quantity_kilo)
            total_price = max(unit_price, kilo_price)
            print(f"Single unit price: {unit_price}")
            print(f"Single unit kilo price: {kilo_price}")
        else:
            # Se há mais de uma unidade, calcule tanto o preço por unidade quanto por quilo
            unit_price = base_price * quantity
            kilo_price = base_price * Decimal(quantity_kilo)
            total_price = unit_price + kilo_price
            print(f"Unit price: {quantity} x {base_price} = {unit_price}")
            print(f"Kilo price: {quantity_kilo} x {base_price} = {kilo_price}")

        print(f"Total before extras: {total_price}")

        # Adiciona o preço do topper, se aplicável
        if self.has_topper and topper_text:
            topper_price = Decimal('08.00')
            total_price += topper_price
            print(f"Added topper price: {topper_price}")

        # Adiciona o preço das rosas, se aplicável
        if self.has_roses:
            rose_price = Decimal('5.00') * Decimal(roses_quantity)
            total_price += rose_price
            print(f"Added roses price: {rose_price}")

        print(f"Final total price: {total_price}")
        return total_price.quantize(Decimal('0.01'))  # Arredonda para 2 casas decimais
    def get_topper_price(self):
        """Retorna o preço do topper, se aplicável."""
        if self.has_topper:
            return Decimal('8.00')  # Preço do topper
        return Decimal('0.00')  # Sem topper
    
     

    def get_roses_price(self, roses_quantity, return_individual=False):
        """Retorna o preço das rosas com base na quantidade e, opcionalmente, o valor individual por rosa."""
        individual_price = Decimal('5.00')  # Preço por rosa
        if self.has_roses:
            if return_individual:
                return individual_price  # Retorna o preço individual
            return individual_price * Decimal(roses_quantity)  # Preço total
        return Decimal('0.00')

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
class PersonalizedCakeOrder(models.Model):
    SIZE_CHOICES = [
        ("small", _("Small")),
        ("medium", _("Medium")),
        ("large", _("Large")),
    ]

    

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="personalized_cakes")
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="personalized_orders")

    size = models.CharField(max_length=20, choices=SIZE_CHOICES)
    flavor = models.ForeignKey("Flavor", on_delete=models.SET_NULL, null=True, blank=True)
    message = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Message on cake"))
    topper_text = models.CharField(max_length=60, blank=True, null=True, verbose_name=_("Topper text"))
    roses_quantity = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])

    reference_image = CloudinaryField('cake_reference', blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Personalized Cake Order")
        verbose_name_plural = _("Personalized Cake Orders")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} • {self.product.name} • {self.size}"
    def calculate_price(self) -> Decimal:
        """
        Reusa a lógica do Product (calculate_total_price).
        Considera topper/roses conforme flags do Product.
        """
        total = self.product.calculate_total_price(
            quantity=self.quantity,
            size=self.size,
            flavor=self.flavor,
            topper_text=self.topper_text,
            roses_quantity=self.roses_quantity,
            is_truffled=getattr(self.flavor, "is_truffled", False),
        )
        return Decimal(total)