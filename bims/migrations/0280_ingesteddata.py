# Generated by Django 2.2.12 on 2021-01-28 03:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('bims', '0279_requestlog'),
    ]

    operations = [
        migrations.CreateModel(
            name='IngestedData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('is_valid', models.BooleanField(default=False)),
                ('object_id', models.PositiveIntegerField()),
                ('data_key', models.CharField(blank=True, max_length=255, null=True)),
                ('category', models.TextField(blank=True, null=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name_plural': 'Ingested data',
            },
        ),
    ]
