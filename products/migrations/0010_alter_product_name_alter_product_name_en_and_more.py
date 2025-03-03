# Generated by Django 5.1.4 on 2025-03-03 09:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0009_alter_product_flavors_alter_product_name_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="name",
            field=models.CharField(max_length=254),
        ),
        migrations.AlterField(
            model_name="product",
            name="name_en",
            field=models.CharField(max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name="product",
            name="name_pt_br",
            field=models.CharField(max_length=254, null=True),
        ),
    ]
