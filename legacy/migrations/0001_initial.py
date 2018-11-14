# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import opal.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('opal', '0034_auto_20171214_1845'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActionLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(blank=True, null=True)),
                ('updated', models.DateTimeField(blank=True, null=True)),
                ('consistency_token', models.CharField(max_length=8)),
                ('employer', models.CharField(max_length=100, blank=True, null=True)),
                ('oh_provider', models.CharField(max_length=100, blank=True, null=True)),
                ('seen_by', models.CharField(max_length=100, blank=True, null=True)),
                ('clinicdate', models.DateField(blank=True, null=True)),
                ('date_first_appointment', models.DateField(blank=True, null=True)),
                ('attendance', models.NullBooleanField()),
                ('peak_flow', models.NullBooleanField()),
                ('immunology_oem', models.NullBooleanField()),
                ('histamine', models.NullBooleanField()),
                ('histamine_date', models.DateField(blank=True, null=True)),
                ('histamine_attendance', models.NullBooleanField()),
                ('lung_function', models.NullBooleanField()),
                ('lung_function_date', models.DateField(blank=True, null=True)),
                ('lung_function_attendance', models.NullBooleanField()),
                ('work_samples', models.NullBooleanField()),
                ('other_hospital_info', models.NullBooleanField()),
                ('other_oh_info', models.NullBooleanField()),
                ('other_gp_info', models.NullBooleanField()),
                ('other_rbh_bloods', models.NullBooleanField()),
                ('firefighter', models.NullBooleanField()),
                ('diagnosis_made', models.NullBooleanField()),
                ('follow_up_planned', models.NullBooleanField()),
                ('date_of_followup', models.DateField(blank=True, null=True)),
                ('active', models.NullBooleanField()),
                ('general_notes', models.TextField(blank=True, null=True)),
                ('letters', models.TextField(blank=True, null=True)),
                ('finaldays', models.IntegerField(blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, related_name='created_legacy_actionlog_subrecords', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('episode', models.ForeignKey(to='opal.Episode')),
                ('updated_by', models.ForeignKey(blank=True, null=True, related_name='updated_legacy_actionlog_subrecords', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(opal.models.UpdatesFromDictMixin, opal.models.ToDictMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ContactDetails',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(blank=True, null=True)),
                ('updated', models.DateTimeField(blank=True, null=True)),
                ('consistency_token', models.CharField(max_length=8)),
                ('mobile', models.CharField(max_length=100, blank=True, null=True)),
                ('phone', models.CharField(max_length=100, blank=True, null=True)),
                ('email', models.CharField(max_length=100, blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, related_name='created_legacy_contactdetails_subrecords', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('patient', models.ForeignKey(to='opal.Patient')),
                ('updated_by', models.ForeignKey(blank=True, null=True, related_name='updated_legacy_contactdetails_subrecords', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(opal.models.UpdatesFromDictMixin, opal.models.ToDictMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Referral',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(blank=True, null=True)),
                ('updated', models.DateTimeField(blank=True, null=True)),
                ('consistency_token', models.CharField(max_length=8)),
                ('referrer_title', models.CharField(max_length=100, blank=True, null=True)),
                ('referrer_name', models.CharField(max_length=100, blank=True, null=True)),
                ('date_of_referral', models.DateField(blank=True, null=True)),
                ('date_refferal_received', models.DateField(blank=True, null=True)),
                ('date_first_contact', models.DateField(blank=True, null=True)),
                ('comments', models.TextField(blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, related_name='created_legacy_referral_subrecords', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('episode', models.ForeignKey(to='opal.Episode')),
                ('updated_by', models.ForeignKey(blank=True, null=True, related_name='updated_legacy_referral_subrecords', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(opal.models.UpdatesFromDictMixin, opal.models.ToDictMixin, models.Model),
        ),
    ]
