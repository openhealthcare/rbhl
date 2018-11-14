# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import opal.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('opal', '0029_auto_20170707_1337'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rbhl', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Occupation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(blank=True, null=True)),
                ('updated', models.DateTimeField(blank=True, null=True)),
                ('consistency_token', models.CharField(max_length=8)),
                ('currently_employed', models.CharField(max_length=200, blank=True, null=True, choices=[('Yes', 'Yes'), ('No', 'No')])),
                ('job_title', models.CharField(max_length=200, blank=True, null=True)),
                ('name_of_employer', models.CharField(max_length=200, blank=True, null=True)),
                ('exposures', models.TextField(blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, related_name='created_rbhl_occupation_subrecords', to=settings.AUTH_USER_MODEL)),
                ('episode', models.ForeignKey(to='opal.Episode')),
                ('updated_by', models.ForeignKey(blank=True, null=True, related_name='updated_rbhl_occupation_subrecords', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(opal.models.UpdatesFromDictMixin, opal.models.ToDictMixin, models.Model),
        ),
    ]
