# Generated by Django 3.0.3 on 2020-05-01 04:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asset', '0010_assetportfolio'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='currency',
            field=models.CharField(blank=True, max_length=3, null=True),
        ),
    ]