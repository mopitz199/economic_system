# Generated by Django 3.0.3 on 2020-04-05 02:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('asset', '0008_auto_20200319_2059'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='asset',
            name='slugs',
        ),
    ]
