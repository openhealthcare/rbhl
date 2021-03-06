# Generated by Django 2.0.13 on 2020-06-23 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rbhl', '0034_auto_20200623_1455'),
    ]

    operations = [
        migrations.AlterField(
            model_name='referral',
            name='date_referral_received',
            field=models.DateField(blank=True, null=True, verbose_name='Received'),
        ),
        migrations.AlterField(
            model_name='referral',
            name='referral_type',
            field=models.TextField(blank=True, null=True, verbose_name='Type'),
        ),
        migrations.AlterField(
            model_name='referral',
            name='referrer_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Referrer name'),
        ),
    ]
