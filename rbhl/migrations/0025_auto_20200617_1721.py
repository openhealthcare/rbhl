# Generated by Django 2.0.13 on 2020-06-17 17:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rbhl', '0024_auto_20200617_1548'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmploymentCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('system', models.CharField(blank=True, max_length=255, null=True)),
                ('code', models.CharField(blank=True, max_length=255, null=True)),
                ('version', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GeographicalArea',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('system', models.CharField(blank=True, max_length=255, null=True)),
                ('code', models.CharField(blank=True, max_length=255, null=True)),
                ('version', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='JobTitle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('system', models.CharField(blank=True, max_length=255, null=True)),
                ('code', models.CharField(blank=True, max_length=255, null=True)),
                ('version', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PresentingComplaint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('system', models.CharField(blank=True, max_length=255, null=True)),
                ('code', models.CharField(blank=True, max_length=255, null=True)),
                ('version', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='cliniclog',
            name='clinic_site',
            field=models.CharField(blank=True, default='OCLD', max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='cliniclog',
            name='diagnosis_outcome',
            field=models.CharField(blank=True, choices=[('Known', 'Known'), ('Investigations continuing', 'Investigations continuing'), ('Not established lost to follow-up', 'Not established lost to follow-up'), ('Not reached despite investigation', 'Not reached despite investigation'), ('Not established referred to someone else', 'Not established referred to someone else'), ('Not established patient withdrew', 'Not established patient withdrew')], max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='cliniclog',
            name='presenting_complaint_ft',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='cliniclog',
            name='referred_to',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='employment',
            name='employed_in_suspect_occupation',
            field=models.CharField(blank=True, choices=[('Yes-employed in suspect occupation', 'Yes-employed in suspect occupation'), ('Yes', 'Yes'), ('Yes-other occupation', 'Yes-other occupation'), ('No', 'No')], max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='employment',
            name='employment_category_ft',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='employment',
            name='exposures',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='employment',
            name='job_title_ft',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='referral',
            name='geographical_area_ft',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='referral',
            name='referral_disease',
            field=models.CharField(blank=True, choices=[('Asthma', 'Asthma'), ('Asthma/Rhinitis', 'Asthma/Rhinitis'), ('Inhalation injury', 'Inhalation injury'), ('Malignancy', 'Malignancy'), ('Other / Unclear', 'Other / Unclear'), ('Pulmonary fibrosis(eg: Asbestos related disease)', 'Pulmonary fibrosis(eg: Asbestos related disease)')], max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='referral',
            name='referral_reason',
            field=models.CharField(blank=True, choices=[('Environmental', 'Environmental'), ('Fit to work', 'Fit to work'), ('Occupational', 'Occupational'), ('Other', 'Other')], max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='employment',
            name='firefighter',
            field=models.NullBooleanField(verbose_name='Firefighter pre-employment'),
        ),
        migrations.AlterUniqueTogether(
            name='presentingcomplaint',
            unique_together={('code', 'system')},
        ),
        migrations.AlterUniqueTogether(
            name='jobtitle',
            unique_together={('code', 'system')},
        ),
        migrations.AlterUniqueTogether(
            name='geographicalarea',
            unique_together={('code', 'system')},
        ),
        migrations.AlterUniqueTogether(
            name='employmentcategory',
            unique_together={('code', 'system')},
        ),
        migrations.AddField(
            model_name='cliniclog',
            name='presenting_complaint_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rbhl.PresentingComplaint'),
        ),
        migrations.AddField(
            model_name='employment',
            name='employment_category_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rbhl.EmploymentCategory'),
        ),
        migrations.AddField(
            model_name='employment',
            name='job_title_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rbhl.JobTitle'),
        ),
        migrations.AddField(
            model_name='referral',
            name='geographical_area_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rbhl.GeographicalArea'),
        ),
    ]
