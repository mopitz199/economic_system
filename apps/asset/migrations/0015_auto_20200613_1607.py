# Generated by Django 3.0.3 on 2020-06-13 16:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('asset', '0014_auto_20200613_1451'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='portfolio',
            name='user',
        ),
        migrations.DeleteModel(
            name='AssetPortfolio',
        ),
        migrations.DeleteModel(
            name='Portfolio',
        ),
    ]