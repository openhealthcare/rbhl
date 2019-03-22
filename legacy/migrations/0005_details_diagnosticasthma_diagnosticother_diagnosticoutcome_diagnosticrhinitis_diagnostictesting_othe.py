# Generated by Django 2.0.13 on 2019-03-22 09:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import opal.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('opal', '0037_auto_20181114_1445'),
        ('legacy', '0004_address_gp_patientnumber'),
    ]

    operations = [
        migrations.CreateModel(
            name='Details',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True, null=True)),
                ('updated', models.DateTimeField(blank=True, null=True)),
                ('consistency_token', models.CharField(max_length=8)),
                ('hospital_number', models.TextField(blank=True, null=True)),
                ('date_first_attended', models.TextField(blank=True, null=True)),
                ('referring_doctor', models.TextField(blank=True, null=True)),
                ('date_referral_received', models.TextField(blank=True, null=True)),
                ('referral_type', models.TextField(blank=True, null=True)),
                ('fire_service_applicant', models.TextField(blank=True, null=True)),
                ('systems_presenting_compliant', models.TextField(blank=True, null=True)),
                ('referral_disease', models.TextField(blank=True, null=True)),
                ('geographical_area', models.TextField(blank=True, null=True)),
                ('geographical_area_other', models.TextField(blank=True, null=True)),
                ('site_of_clinic', models.TextField(blank=True, null=True)),
                ('other_clinic_site', models.TextField(blank=True, null=True)),
                ('clinic_status', models.TextField(blank=True, null=True)),
                ('seen_by_dr', models.TextField(blank=True, null=True)),
                ('previous_atopic_disease', models.TextField(blank=True, null=True)),
                ('has_asthma', models.TextField(blank=True, null=True)),
                ('has_hayfever', models.TextField(blank=True, null=True)),
                ('has_eczema', models.TextField(blank=True, null=True)),
                ('is_smoker', models.TextField(blank=True, null=True)),
                ('smokes_per_day', models.TextField(blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_legacy_details_subrecords', to=settings.AUTH_USER_MODEL)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opal.Patient')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_legacy_details_subrecords', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(opal.models.UpdatesFromDictMixin, opal.models.ToDictMixin, models.Model),
        ),
        migrations.CreateModel(
            name='DiagnosticAsthma',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True, null=True)),
                ('updated', models.DateTimeField(blank=True, null=True)),
                ('consistency_token', models.CharField(max_length=8)),
                ('asthma', models.TextField(blank=True, null=True)),
                ('is_exacerbated_by_work', models.TextField(blank=True, null=True)),
                ('has_infant_induced_asthma', models.TextField(blank=True, null=True)),
                ('occupational_asthma_caused_by_sensitisation', models.TextField(blank=True, null=True)),
                ('sensitising_agent', models.TextField(blank=True, null=True)),
                ('has_non_occupational_asthma', models.TextField(blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_legacy_diagnosticasthma_subrecords', to=settings.AUTH_USER_MODEL)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opal.Patient')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_legacy_diagnosticasthma_subrecords', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(opal.models.UpdatesFromDictMixin, opal.models.ToDictMixin, models.Model),
        ),
        migrations.CreateModel(
            name='DiagnosticOther',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True, null=True)),
                ('updated', models.DateTimeField(blank=True, null=True)),
                ('consistency_token', models.CharField(max_length=8)),
                ('copd', models.TextField(blank=True, null=True)),
                ('emphysema', models.TextField(blank=True, null=True)),
                ('copd_with_emphysema', models.TextField(blank=True, null=True)),
                ('copd_is_occupational', models.TextField(blank=True, null=True)),
                ('malignancy', models.TextField(blank=True, null=True)),
                ('malignancy_is_occupational', models.TextField(blank=True, null=True)),
                ('malignancy_type', models.TextField(blank=True, null=True)),
                ('malignancy_type_other', models.TextField(blank=True, null=True)),
                ('NAD', models.TextField(blank=True, null=True)),
                ('diffuse_lung_disease', models.TextField(blank=True, null=True)),
                ('diffuse_lung_disease_is_occupational', models.TextField(blank=True, null=True)),
                ('diffuse_lung_disease_type', models.TextField(blank=True, null=True)),
                ('diffuse_lung_disease_type_other', models.TextField(blank=True, null=True)),
                ('benign_pleural_disease', models.TextField(blank=True, null=True)),
                ('benign_pleural_disease_type', models.TextField(blank=True, null=True)),
                ('other_diagnosis', models.TextField(blank=True, null=True)),
                ('other_diagnosis_is_occupational', models.TextField(blank=True, null=True)),
                ('other_diagnosis_type', models.TextField(blank=True, null=True)),
                ('other_diagnosis_type_other', models.TextField(blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_legacy_diagnosticother_subrecords', to=settings.AUTH_USER_MODEL)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opal.Patient')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_legacy_diagnosticother_subrecords', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(opal.models.UpdatesFromDictMixin, opal.models.ToDictMixin, models.Model),
        ),
        migrations.CreateModel(
            name='DiagnosticOutcome',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True, null=True)),
                ('updated', models.DateTimeField(blank=True, null=True)),
                ('consistency_token', models.CharField(max_length=8)),
                ('diagnosis', models.TextField(blank=True, null=True)),
                ('diagnosis_date', models.TextField(blank=True, null=True)),
                ('referred_to', models.TextField(blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_legacy_diagnosticoutcome_subrecords', to=settings.AUTH_USER_MODEL)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opal.Patient')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_legacy_diagnosticoutcome_subrecords', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(opal.models.UpdatesFromDictMixin, opal.models.ToDictMixin, models.Model),
        ),
        migrations.CreateModel(
            name='DiagnosticRhinitis',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True, null=True)),
                ('updated', models.DateTimeField(blank=True, null=True)),
                ('consistency_token', models.CharField(max_length=8)),
                ('rhinitis', models.TextField(blank=True, null=True)),
                ('work_exacerbated', models.TextField(blank=True, null=True)),
                ('occupational_rhinitis_caused_by_sensitisation', models.TextField(blank=True, null=True)),
                ('rhinitis_occupational_sensitisation_cause', models.TextField(blank=True, null=True)),
                ('has_non_occupational_rhinitis', models.TextField(blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_legacy_diagnosticrhinitis_subrecords', to=settings.AUTH_USER_MODEL)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opal.Patient')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_legacy_diagnosticrhinitis_subrecords', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(opal.models.UpdatesFromDictMixin, opal.models.ToDictMixin, models.Model),
        ),
        migrations.CreateModel(
            name='DiagnosticTesting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True, null=True)),
                ('updated', models.DateTimeField(blank=True, null=True)),
                ('consistency_token', models.CharField(max_length=8)),
                ('antihistimines', models.TextField(blank=True, null=True)),
                ('skin_prick_test', models.TextField(blank=True, null=True)),
                ('atopic', models.TextField(blank=True, null=True)),
                ('specific_skin_prick', models.TextField(blank=True, null=True)),
                ('serum_antibodies', models.TextField(blank=True, null=True)),
                ('bronchial_prov_test', models.TextField(blank=True, null=True)),
                ('change_pc_20', models.TextField(blank=True, null=True)),
                ('nasal_prov_test', models.TextField(blank=True, null=True)),
                ('positive_reaction', models.TextField(blank=True, null=True)),
                ('height', models.TextField(blank=True, null=True)),
                ('fev_1', models.TextField(blank=True, null=True)),
                ('fev_1_post_ventolin', models.TextField(blank=True, null=True)),
                ('fev_1_percentage_protected', models.TextField(blank=True, null=True)),
                ('fvc', models.TextField(blank=True, null=True)),
                ('fvc_post_ventolin', models.TextField(blank=True, null=True)),
                ('fvc_percentage_protected', models.TextField(blank=True, null=True)),
                ('is_serial_peak_flows_requested', models.TextField(blank=True, null=True)),
                ('has_spefr_variability', models.TextField(blank=True, null=True)),
                ('is_returned', models.TextField(blank=True, null=True)),
                ('is_spefr_work_related', models.TextField(blank=True, null=True)),
                ('ct_chest_scan', models.TextField(blank=True, null=True)),
                ('ct_chest_scan_date', models.TextField(blank=True, null=True)),
                ('full_lung_function', models.TextField(blank=True, null=True)),
                ('full_lung_function_date', models.TextField(blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_legacy_diagnostictesting_subrecords', to=settings.AUTH_USER_MODEL)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opal.Patient')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_legacy_diagnostictesting_subrecords', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(opal.models.UpdatesFromDictMixin, opal.models.ToDictMixin, models.Model),
        ),
        migrations.CreateModel(
            name='OtherFields',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True, null=True)),
                ('updated', models.DateTimeField(blank=True, null=True)),
                ('consistency_token', models.CharField(max_length=8)),
                ('other_det_num', models.TextField(blank=True, null=True)),
                ('attendance_date', models.TextField(blank=True, null=True)),
                ('specialist_doctor', models.TextField(blank=True, null=True)),
                ('referral', models.TextField(blank=True, null=True)),
                ('reason_other', models.TextField(blank=True, null=True)),
                ('occupation_other', models.TextField(blank=True, null=True)),
                ('ige_results', models.TextField(blank=True, null=True)),
                ('serum_results_num', models.TextField(blank=True, null=True)),
                ('ssp_test_num', models.TextField(blank=True, null=True)),
                ('serial_perf', models.TextField(blank=True, null=True)),
                ('perf_variability', models.TextField(blank=True, null=True)),
                ('perf_work_relate', models.TextField(blank=True, null=True)),
                ('outcome_num', models.TextField(blank=True, null=True)),
                ('full_pul_fun_test', models.TextField(blank=True, null=True)),
                ('lft_date', models.TextField(blank=True, null=True)),
                ('asthma_relate_work', models.TextField(blank=True, null=True)),
                ('chronic_air_flow', models.TextField(blank=True, null=True)),
                ('chronic_air_flow_choice', models.TextField(blank=True, null=True)),
                ('chronic_obstructive_brinchitis', models.TextField(blank=True, null=True)),
                ('exposure_dates', models.TextField(blank=True, null=True)),
                ('bronch_prov_test_type', models.TextField(blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_legacy_otherfields_subrecords', to=settings.AUTH_USER_MODEL)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opal.Patient')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_legacy_otherfields_subrecords', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(opal.models.UpdatesFromDictMixin, opal.models.ToDictMixin, models.Model),
        ),
        migrations.CreateModel(
            name='SkinPrickTest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True, null=True)),
                ('updated', models.DateTimeField(blank=True, null=True)),
                ('consistency_token', models.CharField(max_length=8)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_legacy_skinpricktest_subrecords', to=settings.AUTH_USER_MODEL)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opal.Patient')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_legacy_skinpricktest_subrecords', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(opal.models.UpdatesFromDictMixin, opal.models.ToDictMixin, models.Model),
        ),
        migrations.CreateModel(
            name='SuspectOccupationalCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True, null=True)),
                ('updated', models.DateTimeField(blank=True, null=True)),
                ('consistency_token', models.CharField(max_length=8)),
                ('is_currently_employed', models.TextField(blank=True, null=True)),
                ('suspect_occupational_category', models.TextField(blank=True, null=True)),
                ('job_title', models.TextField(blank=True, null=True)),
                ('exposures', models.TextField(blank=True, null=True)),
                ('employer_name', models.TextField(blank=True, null=True)),
                ('is_employed_in_suspect_occupation', models.TextField(blank=True, null=True)),
                ('year_started_exposure', models.TextField(blank=True, null=True)),
                ('month_started_exposure', models.TextField(blank=True, null=True)),
                ('year_finished_exposure', models.TextField(blank=True, null=True)),
                ('month_finished_exposure', models.TextField(blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_legacy_suspectoccupationalcategory_subrecords', to=settings.AUTH_USER_MODEL)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opal.Patient')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_legacy_suspectoccupationalcategory_subrecords', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(opal.models.UpdatesFromDictMixin, opal.models.ToDictMixin, models.Model),
        ),
    ]