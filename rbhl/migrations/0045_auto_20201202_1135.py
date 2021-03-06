# Generated by Django 2.2.16 on 2020-12-02 11:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rbhl', '0044_auto_20200908_1010'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asthmadetails',
            name='consistency_token',
            field=models.CharField(max_length=8, verbose_name='Consistency Token'),
        ),
        migrations.AlterField(
            model_name='asthmadetails',
            name='created',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Created'),
        ),
        migrations.AlterField(
            model_name='asthmadetails',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_rbhl_asthmadetails_subrecords', to=settings.AUTH_USER_MODEL, verbose_name='Created By'),
        ),
        migrations.AlterField(
            model_name='asthmadetails',
            name='episode',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opal.Episode', verbose_name='Episode'),
        ),
        migrations.AlterField(
            model_name='asthmadetails',
            name='updated',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Updated'),
        ),
        migrations.AlterField(
            model_name='asthmadetails',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_rbhl_asthmadetails_subrecords', to=settings.AUTH_USER_MODEL, verbose_name='Updated By'),
        ),
        migrations.AlterField(
            model_name='cliniclog',
            name='consistency_token',
            field=models.CharField(max_length=8, verbose_name='Consistency Token'),
        ),
        migrations.AlterField(
            model_name='cliniclog',
            name='created',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Created'),
        ),
        migrations.AlterField(
            model_name='cliniclog',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_rbhl_cliniclog_subrecords', to=settings.AUTH_USER_MODEL, verbose_name='Created By'),
        ),
        migrations.AlterField(
            model_name='cliniclog',
            name='episode',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opal.Episode', verbose_name='Episode'),
        ),
        migrations.AlterField(
            model_name='cliniclog',
            name='updated',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Updated'),
        ),
        migrations.AlterField(
            model_name='cliniclog',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_rbhl_cliniclog_subrecords', to=settings.AUTH_USER_MODEL, verbose_name='Updated By'),
        ),
        migrations.AlterField(
            model_name='contactdetails',
            name='consistency_token',
            field=models.CharField(max_length=8, verbose_name='Consistency Token'),
        ),
        migrations.AlterField(
            model_name='contactdetails',
            name='created',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Created'),
        ),
        migrations.AlterField(
            model_name='contactdetails',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_rbhl_contactdetails_subrecords', to=settings.AUTH_USER_MODEL, verbose_name='Created By'),
        ),
        migrations.AlterField(
            model_name='contactdetails',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opal.Patient', verbose_name='Patient'),
        ),
        migrations.AlterField(
            model_name='contactdetails',
            name='updated',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Updated'),
        ),
        migrations.AlterField(
            model_name='contactdetails',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_rbhl_contactdetails_subrecords', to=settings.AUTH_USER_MODEL, verbose_name='Updated By'),
        ),
        migrations.AlterField(
            model_name='demographics',
            name='consistency_token',
            field=models.CharField(max_length=8, verbose_name='Consistency Token'),
        ),
        migrations.AlterField(
            model_name='demographics',
            name='created',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Created'),
        ),
        migrations.AlterField(
            model_name='demographics',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_rbhl_demographics_subrecords', to=settings.AUTH_USER_MODEL, verbose_name='Created By'),
        ),
        migrations.AlterField(
            model_name='demographics',
            name='death_indicator',
            field=models.BooleanField(default=False, help_text='This field will be True if the patient is deceased.', verbose_name='Death Indicator'),
        ),
        migrations.AlterField(
            model_name='demographics',
            name='first_name',
            field=models.CharField(blank=True, max_length=255, verbose_name='First Name'),
        ),
        migrations.AlterField(
            model_name='demographics',
            name='hospital_number',
            field=models.CharField(blank=True, help_text='The unique identifier for this patient at the hospital.', max_length=255, verbose_name='Demographics'),
        ),
        migrations.AlterField(
            model_name='demographics',
            name='middle_name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Middle Name'),
        ),
        migrations.AlterField(
            model_name='demographics',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opal.Patient', verbose_name='Patient'),
        ),
        migrations.AlterField(
            model_name='demographics',
            name='post_code',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Post Code'),
        ),
        migrations.AlterField(
            model_name='demographics',
            name='surname',
            field=models.CharField(blank=True, max_length=255, verbose_name='Surname'),
        ),
        migrations.AlterField(
            model_name='demographics',
            name='updated',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Updated'),
        ),
        migrations.AlterField(
            model_name='demographics',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_rbhl_demographics_subrecords', to=settings.AUTH_USER_MODEL, verbose_name='Updated By'),
        ),
        migrations.AlterField(
            model_name='diagnosis',
            name='consistency_token',
            field=models.CharField(max_length=8, verbose_name='Consistency Token'),
        ),
        migrations.AlterField(
            model_name='diagnosis',
            name='created',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Created'),
        ),
        migrations.AlterField(
            model_name='diagnosis',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_rbhl_diagnosis_subrecords', to=settings.AUTH_USER_MODEL, verbose_name='Created By'),
        ),
        migrations.AlterField(
            model_name='diagnosis',
            name='episode',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opal.Episode', verbose_name='Episode'),
        ),
        migrations.AlterField(
            model_name='diagnosis',
            name='updated',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Updated'),
        ),
        migrations.AlterField(
            model_name='diagnosis',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_rbhl_diagnosis_subrecords', to=settings.AUTH_USER_MODEL, verbose_name='Updated By'),
        ),
        migrations.AlterField(
            model_name='diagnosisasthma',
            name='consistency_token',
            field=models.CharField(max_length=8, verbose_name='Consistency Token'),
        ),
        migrations.AlterField(
            model_name='diagnosisasthma',
            name='created',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Created'),
        ),
        migrations.AlterField(
            model_name='diagnosisasthma',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_rbhl_diagnosisasthma_subrecords', to=settings.AUTH_USER_MODEL, verbose_name='Created By'),
        ),
        migrations.AlterField(
            model_name='diagnosisasthma',
            name='episode',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opal.Episode', verbose_name='Episode'),
        ),
        migrations.AlterField(
            model_name='diagnosisasthma',
            name='updated',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Updated'),
        ),
        migrations.AlterField(
            model_name='diagnosisasthma',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_rbhl_diagnosisasthma_subrecords', to=settings.AUTH_USER_MODEL, verbose_name='Updated By'),
        ),
        migrations.AlterField(
            model_name='diagnosisrhinitis',
            name='consistency_token',
            field=models.CharField(max_length=8, verbose_name='Consistency Token'),
        ),
        migrations.AlterField(
            model_name='diagnosisrhinitis',
            name='created',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Created'),
        ),
        migrations.AlterField(
            model_name='diagnosisrhinitis',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_rbhl_diagnosisrhinitis_subrecords', to=settings.AUTH_USER_MODEL, verbose_name='Created By'),
        ),
        migrations.AlterField(
            model_name='diagnosisrhinitis',
            name='episode',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opal.Episode', verbose_name='Episode'),
        ),
        migrations.AlterField(
            model_name='diagnosisrhinitis',
            name='updated',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Updated'),
        ),
        migrations.AlterField(
            model_name='diagnosisrhinitis',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_rbhl_diagnosisrhinitis_subrecords', to=settings.AUTH_USER_MODEL, verbose_name='Updated By'),
        ),
        migrations.AlterField(
            model_name='employer',
            name='code',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Code'),
        ),
        migrations.AlterField(
            model_name='employer',
            name='name',
            field=models.CharField(max_length=255, unique=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='employer',
            name='system',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='System'),
        ),
        migrations.AlterField(
            model_name='employer',
            name='version',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Version'),
        ),
        migrations.AlterField(
            model_name='employment',
            name='consistency_token',
            field=models.CharField(max_length=8, verbose_name='Consistency Token'),
        ),
        migrations.AlterField(
            model_name='employment',
            name='created',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Created'),
        ),
        migrations.AlterField(
            model_name='employment',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_rbhl_employment_subrecords', to=settings.AUTH_USER_MODEL, verbose_name='Created By'),
        ),
        migrations.AlterField(
            model_name='employment',
            name='episode',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opal.Episode', verbose_name='Episode'),
        ),
        migrations.AlterField(
            model_name='employment',
            name='updated',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Updated'),
        ),
        migrations.AlterField(
            model_name='employment',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_rbhl_employment_subrecords', to=settings.AUTH_USER_MODEL, verbose_name='Updated By'),
        ),
        migrations.AlterField(
            model_name='employmentcategory',
            name='code',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Code'),
        ),
        migrations.AlterField(
            model_name='employmentcategory',
            name='name',
            field=models.CharField(max_length=255, unique=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='employmentcategory',
            name='system',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='System'),
        ),
        migrations.AlterField(
            model_name='employmentcategory',
            name='version',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Version'),
        ),
        migrations.AlterField(
            model_name='geographicalarea',
            name='code',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Code'),
        ),
        migrations.AlterField(
            model_name='geographicalarea',
            name='name',
            field=models.CharField(max_length=255, unique=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='geographicalarea',
            name='system',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='System'),
        ),
        migrations.AlterField(
            model_name='geographicalarea',
            name='version',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Version'),
        ),
        migrations.AlterField(
            model_name='importedfrompeakflowdatabase',
            name='consistency_token',
            field=models.CharField(max_length=8, verbose_name='Consistency Token'),
        ),
        migrations.AlterField(
            model_name='importedfrompeakflowdatabase',
            name='created',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Created'),
        ),
        migrations.AlterField(
            model_name='importedfrompeakflowdatabase',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_rbhl_importedfrompeakflowdatabase_subrecords', to=settings.AUTH_USER_MODEL, verbose_name='Created By'),
        ),
        migrations.AlterField(
            model_name='importedfrompeakflowdatabase',
            name='episode',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opal.Episode', verbose_name='Episode'),
        ),
        migrations.AlterField(
            model_name='importedfrompeakflowdatabase',
            name='updated',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Updated'),
        ),
        migrations.AlterField(
            model_name='importedfrompeakflowdatabase',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_rbhl_importedfrompeakflowdatabase_subrecords', to=settings.AUTH_USER_MODEL, verbose_name='Updated By'),
        ),
        migrations.AlterField(
            model_name='jobtitle',
            name='code',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Code'),
        ),
        migrations.AlterField(
            model_name='jobtitle',
            name='name',
            field=models.CharField(max_length=255, unique=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='jobtitle',
            name='system',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='System'),
        ),
        migrations.AlterField(
            model_name='jobtitle',
            name='version',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Version'),
        ),
        migrations.AlterField(
            model_name='letter',
            name='consistency_token',
            field=models.CharField(max_length=8, verbose_name='Consistency Token'),
        ),
        migrations.AlterField(
            model_name='letter',
            name='created',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Created'),
        ),
        migrations.AlterField(
            model_name='letter',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_rbhl_letter_subrecords', to=settings.AUTH_USER_MODEL, verbose_name='Created By'),
        ),
        migrations.AlterField(
            model_name='letter',
            name='episode',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opal.Episode', verbose_name='Episode'),
        ),
        migrations.AlterField(
            model_name='letter',
            name='updated',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Updated'),
        ),
        migrations.AlterField(
            model_name='letter',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_rbhl_letter_subrecords', to=settings.AUTH_USER_MODEL, verbose_name='Updated By'),
        ),
        migrations.AlterField(
            model_name='occupation',
            name='consistency_token',
            field=models.CharField(max_length=8, verbose_name='Consistency Token'),
        ),
        migrations.AlterField(
            model_name='occupation',
            name='created',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Created'),
        ),
        migrations.AlterField(
            model_name='occupation',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_rbhl_occupation_subrecords', to=settings.AUTH_USER_MODEL, verbose_name='Created By'),
        ),
        migrations.AlterField(
            model_name='occupation',
            name='episode',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opal.Episode', verbose_name='Episode'),
        ),
        migrations.AlterField(
            model_name='occupation',
            name='updated',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Updated'),
        ),
        migrations.AlterField(
            model_name='occupation',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_rbhl_occupation_subrecords', to=settings.AUTH_USER_MODEL, verbose_name='Updated By'),
        ),
        migrations.AlterField(
            model_name='ohprovider',
            name='code',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Code'),
        ),
        migrations.AlterField(
            model_name='ohprovider',
            name='name',
            field=models.CharField(max_length=255, unique=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='ohprovider',
            name='system',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='System'),
        ),
        migrations.AlterField(
            model_name='ohprovider',
            name='version',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Version'),
        ),
        migrations.AlterField(
            model_name='patientsource',
            name='peak_flow_database',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='peakflowday',
            name='consistency_token',
            field=models.CharField(max_length=8, verbose_name='Consistency Token'),
        ),
        migrations.AlterField(
            model_name='peakflowday',
            name='created',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Created'),
        ),
        migrations.AlterField(
            model_name='peakflowday',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_rbhl_peakflowday_subrecords', to=settings.AUTH_USER_MODEL, verbose_name='Created By'),
        ),
        migrations.AlterField(
            model_name='peakflowday',
            name='episode',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opal.Episode', verbose_name='Episode'),
        ),
        migrations.AlterField(
            model_name='peakflowday',
            name='updated',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Updated'),
        ),
        migrations.AlterField(
            model_name='peakflowday',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_rbhl_peakflowday_subrecords', to=settings.AUTH_USER_MODEL, verbose_name='Updated By'),
        ),
        migrations.AlterField(
            model_name='rbhreferrer',
            name='code',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Code'),
        ),
        migrations.AlterField(
            model_name='rbhreferrer',
            name='name',
            field=models.CharField(max_length=255, unique=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='rbhreferrer',
            name='system',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='System'),
        ),
        migrations.AlterField(
            model_name='rbhreferrer',
            name='version',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Version'),
        ),
        migrations.AlterField(
            model_name='referral',
            name='consistency_token',
            field=models.CharField(max_length=8, verbose_name='Consistency Token'),
        ),
        migrations.AlterField(
            model_name='referral',
            name='created',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Created'),
        ),
        migrations.AlterField(
            model_name='referral',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_rbhl_referral_subrecords', to=settings.AUTH_USER_MODEL, verbose_name='Created By'),
        ),
        migrations.AlterField(
            model_name='referral',
            name='episode',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opal.Episode', verbose_name='Episode'),
        ),
        migrations.AlterField(
            model_name='referral',
            name='updated',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Updated'),
        ),
        migrations.AlterField(
            model_name='referral',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_rbhl_referral_subrecords', to=settings.AUTH_USER_MODEL, verbose_name='Updated By'),
        ),
        migrations.AlterField(
            model_name='rhinitisdetails',
            name='consistency_token',
            field=models.CharField(max_length=8, verbose_name='Consistency Token'),
        ),
        migrations.AlterField(
            model_name='rhinitisdetails',
            name='created',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Created'),
        ),
        migrations.AlterField(
            model_name='rhinitisdetails',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_rbhl_rhinitisdetails_subrecords', to=settings.AUTH_USER_MODEL, verbose_name='Created By'),
        ),
        migrations.AlterField(
            model_name='rhinitisdetails',
            name='episode',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opal.Episode', verbose_name='Episode'),
        ),
        migrations.AlterField(
            model_name='rhinitisdetails',
            name='updated',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Updated'),
        ),
        migrations.AlterField(
            model_name='rhinitisdetails',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_rbhl_rhinitisdetails_subrecords', to=settings.AUTH_USER_MODEL, verbose_name='Updated By'),
        ),
        migrations.AlterField(
            model_name='socialhistory',
            name='consistency_token',
            field=models.CharField(max_length=8, verbose_name='Consistency Token'),
        ),
        migrations.AlterField(
            model_name='socialhistory',
            name='created',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Created'),
        ),
        migrations.AlterField(
            model_name='socialhistory',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_rbhl_socialhistory_subrecords', to=settings.AUTH_USER_MODEL, verbose_name='Created By'),
        ),
        migrations.AlterField(
            model_name='socialhistory',
            name='episode',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opal.Episode', verbose_name='Episode'),
        ),
        migrations.AlterField(
            model_name='socialhistory',
            name='updated',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Updated'),
        ),
        migrations.AlterField(
            model_name='socialhistory',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_rbhl_socialhistory_subrecords', to=settings.AUTH_USER_MODEL, verbose_name='Updated By'),
        ),
    ]
