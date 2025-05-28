from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User
from products.models import Product  # Importa o modelo de produto

class Testimony(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='testimonies')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    rating = models.IntegerField(default=5)  # Opcional: nota de 1 a 5
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.product.name}'
