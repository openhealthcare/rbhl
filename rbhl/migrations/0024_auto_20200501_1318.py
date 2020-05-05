# Generated by Django 2.0.13 on 2020-05-01 13:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rbhl', '0023_auto_20200501_1059'),
    ]

    operations = [
        migrations.AddField(
            model_name='employment',
            name='job_title_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rbhl.JobTitle'),
        ),
        migrations.AddField(
            model_name='employment',
            name='job_title_ft',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
    ]