# Generated by Django 2.0.13 on 2020-03-26 14:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import opal.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('opal', '0037_auto_20181114_1445'),
        ('rbhl', '0017_cliniclog_outstanding_tests_required'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImportedFromPeakFlowDatabase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True, null=True)),
                ('updated', models.DateTimeField(blank=True, null=True)),
                ('consistency_token', models.CharField(max_length=8)),
                ('age', models.IntegerField(blank=True, null=True)),
                ('trial_number', models.IntegerField(blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_rbhl_importedfrompeakflowdatabase_subrecords', to=settings.AUTH_USER_MODEL)),
                ('episode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opal.Episode')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_rbhl_importedfrompeakflowdatabase_subrecords', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(opal.models.UpdatesFromDictMixin, opal.models.ToDictMixin, models.Model),
        ),
        migrations.CreateModel(
            name='PatientSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('peak_flow_database', models.BooleanField(default=False)),
                ('patient', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='opal.Patient')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='peakflowday',
            unique_together={('day_num', 'trial_num', 'episode')},
        ),
    ]
