from django.db import models
from django.db.models import Sum
from django.conf import settings
from django_countries.fields import CountryField
from products.models import Product, Flavor
from profiles.models import UserProfile
import uuid


class Order(models.Model):
    order_number = models.CharField(max_length=32, null=False, editable=False)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.SET_NULL,
                                     null=True, blank=True, related_name='orders')
    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    country = CountryField(blank_label='Country *', null=False, blank=False)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    town_or_city = models.CharField(max_length=40, null=False, blank=False)
    street_address1 = models.CharField(max_length=80, null=False, blank=False)
    street_address2 = models.CharField(max_length=80, null=True, blank=True)
    county = models.CharField(max_length=80, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    delivery_cost = models.DecimalField(max_digits=6, decimal_places=2, null=False, default=0)
    order_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)
    original_bag = models.TextField(null=False, blank=False, default='')
    stripe_pid = models.CharField(max_length=254, null=False, blank=False, default='')

    def _generate_order_number(self):
        """Generate a random, unique order number using UUID."""
        return uuid.uuid4().hex.upper()

    def update_total(self):
        """Update grand total each time a line item is added, accounting for delivery costs."""
        self.order_total = self.lineitems.aggregate(Sum('lineitem_total'))['lineitem_total__sum'] or 0
        if self.order_total < settings.FREE_DELIVERY_THRESHOLD:
            self.delivery_cost = self.order_total * settings.STANDARD_DELIVERY_PERCENTAGE / 100
        else:
            self.delivery_cost = 0
        self.grand_total = self.order_total + self.delivery_cost
        self.save(update_fields=['order_total', 'delivery_cost', 'grand_total'])

    def save(self, *args, **kwargs):
        """Override the original save method to set the order number if it hasn't been set already."""
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)
        # Call update_total() only if it's a new instance
        if kwargs.get('force_insert', False):
            self.update_total()
    
    def __str__(self):
        return self.order_number


class OrderLineItem(models.Model):
    order = models.ForeignKey(Order, related_name="lineitems", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    quantity_kilo = models.DecimalField(max_digits=6, decimal_places=3, default=0)  # Novo campo
    size = models.CharField(max_length=20, choices=Product.SIZE_CHOICES, null=True, blank=True)
    flavor = models.ForeignKey(Flavor, null=True, blank=True, on_delete=models.SET_NULL)
    is_truffled = models.BooleanField(default=False)  # Novo campo
    topper_text = models.CharField(max_length=255, null=True, blank=True)
    roses_quantity = models.PositiveIntegerField(default=0)
    lineitem_total = models.DecimalField(max_digits=6, decimal_places=2, null=False, blank=False, editable=False)

    def save(self, *args, **kwargs):
        """Override the original save method to set the lineitem total and update the order total."""
        self.lineitem_total = self.product.calculate_total_price(
            self.quantity, 
            quantity_kilo=self.quantity_kilo,
            size=self.size, 
            flavor=self.flavor, 
            topper_text=self.topper_text, 
            roses_quantity=self.roses_quantity,
            is_truffled=self.is_truffled
        )
        super().save(*args, **kwargs)
        if self.order:
            self.order.update_total()


    


    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
