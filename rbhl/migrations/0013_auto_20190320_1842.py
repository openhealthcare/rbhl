# Generated by Django 2.0.9 on 2019-02-13 19:21
from django.db import migrations


def forwards(apps, schema_editor):
    PeakFlowDay = apps.get_model(
        'rbhl', 'PeakFlowDay'
    )
    PeakFlowDay.objects.exclude(
        work_end=0
    ).exclude(
        work_end=None
    ).exclude(
        work_start=0
    ).exclude(
        work_start=None
    ).update(work_day=True)


def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('rbhl', '0012_peakflowday_work_day'),
    ]

    operations = [
        migrations.RunPython(
            forwards, backwards
        )
    ]
