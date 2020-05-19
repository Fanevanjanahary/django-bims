# Generated by Django 2.0.4 on 2018-04-17 07:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bims', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BiologicalCollectionRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_species_name', models.CharField(blank=True, default='', max_length=100)),
                ('category', models.CharField(blank=True, choices=[('alien', 'Alien'), ('indigenous', 'Indigenous'), ('translocated', 'Translocated')], max_length=50)),
                ('present', models.BooleanField(default=True)),
                ('absent', models.BooleanField(default=True)),
                ('collection_date', models.DateField(default=django.utils.timezone.now)),
                ('collector', models.CharField(blank=True, default='', max_length=100)),
                ('notes', models.TextField(blank=True, default='')),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fish_collection_records', to='bims.LocationSite'))
            ],
        ),
    ]
