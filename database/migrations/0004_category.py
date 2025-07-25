# Generated by Django 5.2.3 on 2025-06-24 08:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0003_producthistory_rating_producthistory_review_count'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('preset_id', models.CharField(max_length=30, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('level', models.IntegerField(default=0)),
                ('slug', models.CharField(blank=True, max_length=255)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='database.category')),
            ],
        ),
    ]
