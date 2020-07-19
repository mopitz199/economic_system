# Generated by Django 3.0.3 on 2020-05-20 01:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chart', '0014_remove_milestone_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssetMilestoneComparision',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('correlation', models.FloatField(blank=True, null=True)),
                ('asset_milestone_1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comparisions_1', to='chart.AssetMilestone')),
                ('asset_milestone_2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comparisions_2', to='chart.AssetMilestone')),
            ],
        ),
    ]