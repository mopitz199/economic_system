# Generated by Django 3.0.3 on 2020-05-16 21:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asset', '0012_asset_health'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='health',
            field=models.FloatField(default=0),
        ),
    ]
