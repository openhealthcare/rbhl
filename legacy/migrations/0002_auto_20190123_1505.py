# Generated by Django 2.0.9 on 2019-01-23 15:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('legacy', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='actionlog',
            name='active',
        ),
        migrations.RemoveField(
            model_name='actionlog',
            name='attendance',
        ),
        migrations.RemoveField(
            model_name='actionlog',
            name='date_first_appointment',
        ),
        migrations.RemoveField(
            model_name='actionlog',
            name='firefighter',
        ),
    ]