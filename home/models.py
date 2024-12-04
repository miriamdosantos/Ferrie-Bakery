from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.

class StoreUpdate(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)

    class Meta:
        verbose_name = _("Store Update")
        verbose_name_plural = _("Store Updates")
        ordering = ["-created_at"]

    def __str__(self):
        return self.title