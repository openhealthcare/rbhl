# Generated by Django 2.2.16 on 2021-01-21 20:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rbhl', '0045_auto_20201202_1135'),
    ]

    operations = [
        migrations.RenameField(
            model_name='socialhistory',
            old_name='cigerettes_per_day',
            new_name='cigarettes_per_day',
        ),
    ]
