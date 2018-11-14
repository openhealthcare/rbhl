# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import opal.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('opal', '0029_auto_20170707_1337'),
        ('rbhl', '0003_diagnosisasthma_diagnosisrhinitis'),
    ]

    operations = [
        migrations.CreateModel(
            name='PeakFlowDay',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(blank=True, null=True)),
                ('updated', models.DateTimeField(blank=True, null=True)),
                ('consistency_token', models.CharField(max_length=8)),
                ('date', models.DateField(blank=True, null=True)),
                ('treatment_taken', models.CharField(max_length=200, blank=True, null=True)),
                ('work_start', models.DateTimeField(blank=True, null=True)),
                ('work_end', models.DateTimeField(blank=True, null=True)),
                ('flow_0600', models.IntegerField(blank=True, null=True)),
                ('flow_0700', models.IntegerField(blank=True, null=True)),
                ('flow_0800', models.IntegerField(blank=True, null=True)),
                ('flow_0900', models.IntegerField(blank=True, null=True)),
                ('flow_1000', models.IntegerField(blank=True, null=True)),
                ('flow_1100', models.IntegerField(blank=True, null=True)),
                ('flow_1200', models.IntegerField(blank=True, null=True)),
                ('flow_1300', models.IntegerField(blank=True, null=True)),
                ('flow_1400', models.IntegerField(blank=True, null=True)),
                ('flow_1500', models.IntegerField(blank=True, null=True)),
                ('flow_1600', models.IntegerField(blank=True, null=True)),
                ('flow_1700', models.IntegerField(blank=True, null=True)),
                ('flow_1800', models.IntegerField(blank=True, null=True)),
                ('flow_1900', models.IntegerField(blank=True, null=True)),
                ('flow_2000', models.IntegerField(blank=True, null=True)),
                ('flow_2100', models.IntegerField(blank=True, null=True)),
                ('flow_2200', models.IntegerField(blank=True, null=True)),
                ('flow_2300', models.IntegerField(blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, related_name='created_rbhl_peakflowday_subrecords', to=settings.AUTH_USER_MODEL)),
                ('episode', models.ForeignKey(to='opal.Episode')),
                ('updated_by', models.ForeignKey(blank=True, null=True, related_name='updated_rbhl_peakflowday_subrecords', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(opal.models.UpdatesFromDictMixin, opal.models.ToDictMixin, models.Model),
        ),
    ]
