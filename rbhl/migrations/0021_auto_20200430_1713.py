# Generated by Django 2.0.13 on 2020-04-30 17:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import opal.models


class Migration(migrations.Migration):

    dependencies = [
        ('opal', '0037_auto_20181114_1445'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rbhl', '0020_merge_20200430_1136'),
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
            name='GeographicArea',
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
            name='ReferralDisease',
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
            name='ReferralReason',
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
            name='SocialHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True, null=True)),
                ('updated', models.DateTimeField(blank=True, null=True)),
                ('consistency_token', models.CharField(max_length=8)),
                ('smoker', models.CharField(blank=True, choices=[('Currently', 'Currently'), ('Ex-smoker', 'Ex-smoker'), ('Never', 'Never')], max_length=256, null=True)),
                ('cigerettes_per_day', models.IntegerField(blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_rbhl_socialhistory_subrecords', to=settings.AUTH_USER_MODEL)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opal.Patient')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_rbhl_socialhistory_subrecords', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(opal.models.UpdatesFromDictMixin, opal.models.ToDictMixin, models.Model),
        ),
        migrations.AddField(
            model_name='cliniclog',
            name='clinic_site',
            field=models.CharField(blank=True, default='OCLD', max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='contactdetails',
            name='address',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='employment',
            name='employed_in_suspect_occupation',
            field=models.NullBooleanField(),
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
            model_name='referral',
            name='geographic_area_ft',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='referral',
            name='referral_disease_ft',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='referral',
            name='referral_reason_ft',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='referralreason',
            unique_together={('code', 'system')},
        ),
        migrations.AlterUniqueTogether(
            name='referraldisease',
            unique_together={('code', 'system')},
        ),
        migrations.AlterUniqueTogether(
            name='jobtitle',
            unique_together={('code', 'system')},
        ),
        migrations.AlterUniqueTogether(
            name='geographicarea',
            unique_together={('code', 'system')},
        ),
        migrations.AlterUniqueTogether(
            name='employmentcategory',
            unique_together={('code', 'system')},
        ),
        migrations.AddField(
            model_name='employment',
            name='employment_category_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rbhl.EmploymentCategory'),
        ),
        migrations.AddField(
            model_name='referral',
            name='geographic_area_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rbhl.GeographicArea'),
        ),
        migrations.AddField(
            model_name='referral',
            name='referral_disease_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rbhl.ReferralDisease'),
        ),
        migrations.AddField(
            model_name='referral',
            name='referral_reason_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rbhl.ReferralReason'),
        ),
    ]