# Generated by Django 2.0.13 on 2020-06-12 10:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rbhl', '0021_auto_20200604_0943'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='diagnosis',
            name='condition_fk',
        ),
        migrations.RemoveField(
            model_name='diagnosis',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='diagnosis',
            name='episode',
        ),
        migrations.RemoveField(
            model_name='diagnosis',
            name='updated_by',
        ),
        migrations.DeleteModel(
            name='Diagnosis',
        ),
    ]
