# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-02-05 12:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sass', '0030_auto_20190205_0517'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitevisit',
            name='comments_or_observations',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='sitevisit',
            name='other_biota',
            field=models.TextField(blank=True, null=True),
        ),
    ]
