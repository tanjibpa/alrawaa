# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-10-17 06:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0006_cartline_package_offer_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='has_package_offer',
            field=models.BooleanField(default=False),
        ),
    ]
