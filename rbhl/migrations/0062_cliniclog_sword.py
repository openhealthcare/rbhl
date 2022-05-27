# Generated by Django 2.2.16 on 2022-05-09 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rbhl', '0061_auto_20220509_1240'),

    ]

    operations = [
        migrations.AddField(
            model_name='cliniclog',
            name='sword',
            field=models.CharField(blank=True, choices=[('No relevant', 'No relevant'), ('Needs to be reported', 'Needs to be reported'), ('Reported', 'Reported')], max_length=256, null=True, verbose_name='SWORD'),
        ),
    ]
