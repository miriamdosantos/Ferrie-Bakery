# Generated by Django 5.1.4 on 2025-03-05 14:59

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0012_alter_product_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="image",
            field=cloudinary.models.CloudinaryField(
                blank=True,
                default="noimage.jpg",
                max_length=255,
                null=True,
                verbose_name="image",
            ),
        ),
    ]
