# Generated by Django 5.2.3 on 2025-06-24 07:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0002_producthistory'),
    ]

    operations = [
        migrations.AddField(
            model_name='producthistory',
            name='rating',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='producthistory',
            name='review_count',
            field=models.IntegerField(default=3),
            preserve_default=False,
        ),
    ]
