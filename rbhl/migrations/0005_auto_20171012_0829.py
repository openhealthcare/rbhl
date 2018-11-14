# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rbhl', '0004_peakflowday'),
    ]

    operations = [
        migrations.AddField(
            model_name='peakflowday',
            name='note',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='diagnosisasthma',
            name='irritant_induced_asthma',
            field=models.CharField(max_length=200, blank=True, null=True, choices=[('Yes', 'Yes'), ('No', 'No')]),
        ),
        migrations.AlterField(
            model_name='diagnosisasthma',
            name='non_occupational_asthma',
            field=models.CharField(max_length=200, blank=True, null=True, choices=[('Yes', 'Yes'), ('No', 'No')]),
        ),
        migrations.AlterField(
            model_name='diagnosisasthma',
            name='sensitisation',
            field=models.CharField(verbose_name='Occupational asthma caused by sensitisation', max_length=200, blank=True, null=True, choices=[('Yes', 'Yes'), ('No', 'No')]),
        ),
        migrations.AlterField(
            model_name='diagnosisrhinitis',
            name='non_occupational_rhinitis',
            field=models.CharField(max_length=200, blank=True, null=True, choices=[('Yes', 'Yes'), ('No', 'No')]),
        ),
        migrations.AlterField(
            model_name='diagnosisrhinitis',
            name='sensitisation',
            field=models.CharField(verbose_name='Occupational rhinitis caused by sensitisation', max_length=200, blank=True, null=True, choices=[('Yes', 'Yes'), ('No', 'No')]),
        ),
        migrations.AlterField(
            model_name='diagnosisrhinitis',
            name='work_exacerbated',
            field=models.CharField(verbose_name='Occupational asthma caused by sensitisation', max_length=200, blank=True, null=True, choices=[('Yes', 'Yes'), ('No', 'No')]),
        ),
        migrations.AlterField(
            model_name='peakflowday',
            name='flow_0600',
            field=models.IntegerField(verbose_name='06:00', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='peakflowday',
            name='flow_0700',
            field=models.IntegerField(verbose_name='07:00', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='peakflowday',
            name='flow_0800',
            field=models.IntegerField(verbose_name='08:00', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='peakflowday',
            name='flow_0900',
            field=models.IntegerField(verbose_name='09:00', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='peakflowday',
            name='flow_1000',
            field=models.IntegerField(verbose_name='10:00', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='peakflowday',
            name='flow_1100',
            field=models.IntegerField(verbose_name='11:00', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='peakflowday',
            name='flow_1200',
            field=models.IntegerField(verbose_name='12:00', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='peakflowday',
            name='flow_1300',
            field=models.IntegerField(verbose_name='13:00', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='peakflowday',
            name='flow_1400',
            field=models.IntegerField(verbose_name='14:00', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='peakflowday',
            name='flow_1500',
            field=models.IntegerField(verbose_name='15:00', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='peakflowday',
            name='flow_1600',
            field=models.IntegerField(verbose_name='16:00', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='peakflowday',
            name='flow_1700',
            field=models.IntegerField(verbose_name='17:00', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='peakflowday',
            name='flow_1800',
            field=models.IntegerField(verbose_name='18:00', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='peakflowday',
            name='flow_1900',
            field=models.IntegerField(verbose_name='19:00', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='peakflowday',
            name='flow_2000',
            field=models.IntegerField(verbose_name='20:00', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='peakflowday',
            name='flow_2100',
            field=models.IntegerField(verbose_name='21:00', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='peakflowday',
            name='flow_2200',
            field=models.IntegerField(verbose_name='22:00', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='peakflowday',
            name='flow_2300',
            field=models.IntegerField(verbose_name='23:00', blank=True, null=True),
        ),
    ]
