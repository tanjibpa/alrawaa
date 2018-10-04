# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-03-28 11:19
from __future__ import unicode_literals

from django.db import migrations
import django_prices.models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0052_packageoffer_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='packageoffer',
            name='price',
            field=django_prices.models.PriceField(blank=True, currency='AED', decimal_places=2, max_digits=12, null=True, verbose_name='price'),
        ),
    ]
