# Generated by Django 2.0.13 on 2019-08-12 16:17

from django.db import migrations
from rbhl import constants


def forwards(apps, schema_editor):
    Role = apps.get_model(
        'opal', 'Role'
    )
    Role.objects.create(name=constants.DOCTOR_ROLE)


def backwards(apps, schema_editor):
    Role = apps.get_model(
        'opal', 'Role'
    )
    Role.objects.filter(name=constants.DOCTOR_ROLE).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('rbhl', '0013_auto_20190812_1559'),
    ]

    operations = [
        migrations.RunPython(
            forwards, backwards
        )
    ]