# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import opal.models


class Migration(migrations.Migration):

    dependencies = [
        ('opal', '0029_auto_20170707_1337'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rbhl', '0002_occupation'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiagnosisAsthma',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(blank=True, null=True)),
                ('updated', models.DateTimeField(blank=True, null=True)),
                ('consistency_token', models.CharField(max_length=8)),
                ('asthma', models.CharField(max_length=200, blank=True, null=True)),
                ('exacerbated_by_work', models.CharField(max_length=200, blank=True, null=True)),
                ('irritant_induced_asthma', models.CharField(max_length=200, blank=True, null=True)),
                ('sensitisation', models.CharField(verbose_name='Occupational asthma caused by sensitisation', max_length=200, blank=True, null=True)),
                ('sensitising_agent', models.TextField(blank=True, null=True)),
                ('non_occupational_asthma', models.CharField(max_length=200, blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, related_name='created_rbhl_diagnosisasthma_subrecords', to=settings.AUTH_USER_MODEL)),
                ('episode', models.ForeignKey(to='opal.Episode')),
                ('updated_by', models.ForeignKey(blank=True, null=True, related_name='updated_rbhl_diagnosisasthma_subrecords', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(opal.models.UpdatesFromDictMixin, opal.models.ToDictMixin, models.Model),
        ),
        migrations.CreateModel(
            name='DiagnosisRhinitis',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(blank=True, null=True)),
                ('updated', models.DateTimeField(blank=True, null=True)),
                ('consistency_token', models.CharField(max_length=8)),
                ('rhinitis', models.CharField(max_length=200, blank=True, null=True)),
                ('work_exacerbated', models.CharField(verbose_name='Occupational asthma caused by sensitisation', max_length=200, blank=True, null=True)),
                ('sensitisation', models.CharField(verbose_name='Occupational rhinitis caused by sensitisation', max_length=200, blank=True, null=True)),
                ('cause', models.TextField(blank=True, null=True)),
                ('non_occupational_rhinitis', models.CharField(max_length=200, blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, related_name='created_rbhl_diagnosisrhinitis_subrecords', to=settings.AUTH_USER_MODEL)),
                ('episode', models.ForeignKey(to='opal.Episode')),
                ('updated_by', models.ForeignKey(blank=True, null=True, related_name='updated_rbhl_diagnosisrhinitis_subrecords', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(opal.models.UpdatesFromDictMixin, opal.models.ToDictMixin, models.Model),
        ),
    ]
