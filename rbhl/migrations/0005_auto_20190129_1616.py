# Generated by Django 2.0.9 on 2019-01-29 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rbhl', '0004_auto_20190129_1613'),
    ]

    operations = [
        migrations.AlterField(
            model_name='referral',
            name='date_first_appointment',
            field=models.DateField(blank=True, null=True, verbose_name='Date first appointment'),
        ),
        migrations.AlterField(
            model_name='referral',
            name='date_first_contact',
            field=models.DateField(blank=True, null=True, verbose_name='Date first contact'),
        ),
        migrations.AlterField(
            model_name='referral',
            name='date_of_referral',
            field=models.DateField(blank=True, null=True, verbose_name='Date of referral'),
        ),
        migrations.AlterField(
            model_name='referral',
            name='date_referral_received',
            field=models.DateField(blank=True, null=True, verbose_name='Date referral received'),
        ),
        migrations.AlterField(
            model_name='referral',
            name='referrer_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Referrer name'),
        ),
    ]
