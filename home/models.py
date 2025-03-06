from django.db import models
from django.utils.translation import gettext_lazy as _
from cloudinary.models import CloudinaryField


# Create your models here.

class StoreUpdate(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    image = CloudinaryField('image', default='noimage.jpg', blank=True, null=True)

    class Meta:
        verbose_name = _("Store Update")
        verbose_name_plural = _("Store Updates")
        ordering = ["-created_at"]

    def __str__(self):
        return self.title