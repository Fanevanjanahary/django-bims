# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-08-01 06:04
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bims', '0029_auto_20180801_0403'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Author',
        ),
        migrations.DeleteModel(
            name='AuthorEntryRank',
        ),
        migrations.DeleteModel(
            name='Collection',
        ),
        migrations.DeleteModel(
            name='Editor',
        ),
        migrations.DeleteModel(
            name='Entry',
        ),
        migrations.DeleteModel(
            name='Journal',
        ),
        migrations.DeleteModel(
            name='Publisher',
        ),
    ]
