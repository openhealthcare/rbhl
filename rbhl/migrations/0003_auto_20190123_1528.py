# Generated by Django 2.0.9 on 2019-01-23 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rbhl', '0002_auto_20190123_1505'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cliniclog',
            name='attendance',
        ),
        migrations.RemoveField(
            model_name='cliniclog',
            name='date_first_appointment',
        ),
        migrations.RemoveField(
            model_name='cliniclog',
            name='firefighter',
        ),
        migrations.AddField(
            model_name='referral',
            name='attendance',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='referral',
            name='date_first_appointment',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='referral',
            name='firefighter',
            field=models.NullBooleanField(),
        ),
    ]
