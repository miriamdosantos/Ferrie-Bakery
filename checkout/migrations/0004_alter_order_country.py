# Generated by Django 5.1.4 on 2025-02-27 09:46

import django_countries.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("checkout", "0003_order_original_bag_order_stripe_pid"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="country",
            field=django_countries.fields.CountryField(max_length=2),
        ),
    ]
