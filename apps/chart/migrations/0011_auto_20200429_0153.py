# Generated by Django 3.0.3 on 2020-04-29 01:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chart', '0010_remove_assetmilestone_percentage'),
    ]

    operations = [
        migrations.AddField(
            model_name='assetmilestone',
            name='max_price_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='assetmilestone',
            name='min_price_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
