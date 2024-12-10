# Generated by Django 5.1.4 on 2024-12-10 16:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0008_product_size"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="price",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=6),
        ),
        migrations.AlterField(
            model_name="product",
            name="size",
            field=models.CharField(
                blank=True,
                choices=[("small", "Small"), ("medium", "Medium"), ("large", "Large")],
                max_length=20,
                null=True,
                verbose_name="Size",
            ),
        ),
        migrations.CreateModel(
            name="Flavor",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=254, verbose_name="Flavor")),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="flavors",
                        to="products.category",
                    ),
                ),
            ],
            options={
                "verbose_name": "Flavor",
                "verbose_name_plural": "Flavors",
            },
        ),
        migrations.AddField(
            model_name="product",
            name="flavors",
            field=models.ManyToManyField(
                blank=True, to="products.flavor", verbose_name="Flavors"
            ),
        ),
    ]