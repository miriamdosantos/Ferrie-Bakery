# Generated by Django 5.1.4 on 2025-02-27 13:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("checkout", "0004_alter_order_country"),
        ("profiles", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="user_profile",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="orders",
                to="profiles.userprofile",
            ),
        ),
    ]
