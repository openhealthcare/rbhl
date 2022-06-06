# Generated by Django 2.2.16 on 2022-05-27 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rbhl', '0062_cliniclog_sword'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cliniclog',
            name='sword',
            field=models.CharField(blank=True, choices=[('Not relevant', 'Not relevant'), ('Needs to be reported', 'Needs to be reported'), ('Reported', 'Reported')], max_length=256, null=True, verbose_name='SWORD'),
        ),
    ]