# Generated by Django 3.0.3 on 2020-06-10 01:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio_optimization', '0003_portfoliooptimization_optimism'),
    ]

    operations = [
        migrations.AddField(
            model_name='assetoptimization',
            name='amount_to_invest',
            field=models.DecimalField(blank=True, decimal_places=10, max_digits=30, null=True),
        ),
    ]