# Generated by Django 3.0.3 on 2020-04-12 03:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chart', '0005_assetmilestone_milestone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='milestone',
            name='end',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]