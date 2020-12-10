# Generated by Django 2.2.12 on 2020-12-10 08:03

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bims', '0277_auto_20201203_0429'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseMapLayer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(db_index=True, editable=False, verbose_name='order')),
                ('title', models.CharField(max_length=256, unique=True)),
                ('source_type', models.CharField(choices=[('xyz', 'XYZ'), ('bing', 'BingMaps'), ('osm', 'OSM'), ('stamen', 'Stamen')], max_length=100)),
                ('layer_name', models.CharField(blank=True, default='', help_text='Only for Stamen base layer', max_length=100)),
                ('attributions', models.TextField(blank=True, default='')),
                ('url', models.URLField(blank=True, null=True)),
                ('key', models.CharField(blank=True, default='', help_text='Key is required if the source of the map is Bing', max_length=256)),
                ('additional_params', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('default_basemap', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('order',),
            },
        ),
    ]
