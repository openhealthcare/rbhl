# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('rbhl', '0005_auto_20171012_0829'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='allergies',
            options={'verbose_name_plural': 'Allergies'},
        ),
        migrations.AlterModelOptions(
            name='demographics',
            options={'verbose_name_plural': 'Demographics'},
        ),
        migrations.AlterModelOptions(
            name='diagnosis',
            options={'verbose_name_plural': 'Diagnoses'},
        ),
        migrations.AlterModelOptions(
            name='pastmedicalhistory',
            options={'verbose_name_plural': 'Past medical histories'},
        ),
        migrations.AlterModelOptions(
            name='symptomcomplex',
            options={'verbose_name_plural': 'Symptom complexes'},
        ),
        migrations.AddField(
            model_name='investigation',
            name='rhinovirus',
            field=models.CharField(max_length=20, blank=True, choices=[('pending', 'pending'), ('positive', 'positive'), ('negative', 'negative')]),
        ),
        migrations.AlterField(
            model_name='allergies',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, related_name='created_rbhl_allergies_subrecords', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='allergies',
            name='drug_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='opal.Drug'),
        ),
        migrations.AlterField(
            model_name='allergies',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, related_name='updated_rbhl_allergies_subrecords', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='demographics',
            name='birth_place_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='opal.Destination'),
        ),
        migrations.AlterField(
            model_name='demographics',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, related_name='created_rbhl_demographics_subrecords', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='demographics',
            name='ethnicity_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='opal.Ethnicity'),
        ),
        migrations.AlterField(
            model_name='demographics',
            name='marital_status_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='opal.MaritalStatus'),
        ),
        migrations.AlterField(
            model_name='demographics',
            name='sex_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='opal.Gender'),
        ),
        migrations.AlterField(
            model_name='demographics',
            name='title_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='opal.Title'),
        ),
        migrations.AlterField(
            model_name='demographics',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, related_name='updated_rbhl_demographics_subrecords', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='diagnosis',
            name='condition_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='opal.Condition'),
        ),
        migrations.AlterField(
            model_name='diagnosis',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, related_name='created_rbhl_diagnosis_subrecords', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='diagnosis',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, related_name='updated_rbhl_diagnosis_subrecords', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='diagnosisasthma',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, related_name='created_rbhl_diagnosisasthma_subrecords', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='diagnosisasthma',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, related_name='updated_rbhl_diagnosisasthma_subrecords', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='diagnosisrhinitis',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, related_name='created_rbhl_diagnosisrhinitis_subrecords', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='diagnosisrhinitis',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, related_name='updated_rbhl_diagnosisrhinitis_subrecords', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='investigation',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, related_name='created_rbhl_investigation_subrecords', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='investigation',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, related_name='updated_rbhl_investigation_subrecords', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='location',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, related_name='created_rbhl_location_subrecords', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='location',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, related_name='updated_rbhl_location_subrecords', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='occupation',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, related_name='created_rbhl_occupation_subrecords', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='occupation',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, related_name='updated_rbhl_occupation_subrecords', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='pastmedicalhistory',
            name='condition_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='opal.Condition'),
        ),
        migrations.AlterField(
            model_name='pastmedicalhistory',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, related_name='created_rbhl_pastmedicalhistory_subrecords', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='pastmedicalhistory',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, related_name='updated_rbhl_pastmedicalhistory_subrecords', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='patientconsultation',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, related_name='created_rbhl_patientconsultation_subrecords', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='patientconsultation',
            name='reason_for_interaction_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='opal.PatientConsultationReasonForInteraction'),
        ),
        migrations.AlterField(
            model_name='patientconsultation',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, related_name='updated_rbhl_patientconsultation_subrecords', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='peakflowday',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, related_name='created_rbhl_peakflowday_subrecords', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='peakflowday',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, related_name='updated_rbhl_peakflowday_subrecords', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='symptomcomplex',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, related_name='created_rbhl_symptomcomplex_subrecords', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='symptomcomplex',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, related_name='updated_rbhl_symptomcomplex_subrecords', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='treatment',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, related_name='created_rbhl_treatment_subrecords', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='treatment',
            name='drug_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='opal.Drug'),
        ),
        migrations.AlterField(
            model_name='treatment',
            name='frequency_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='opal.Drugfreq'),
        ),
        migrations.AlterField(
            model_name='treatment',
            name='route_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='opal.Drugroute'),
        ),
        migrations.AlterField(
            model_name='treatment',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, related_name='updated_rbhl_treatment_subrecords', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
