# Generated by Django 2.0.13 on 2020-06-04 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rbhl', '0020_merge_20200427_1936'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cliniclog',
            options={},
        ),
        migrations.AlterModelOptions(
            name='contactdetails',
            options={},
        ),
        migrations.AlterField(
            model_name='cliniclog',
            name='diagnosis_made',
            field=models.NullBooleanField(),
        ),
        migrations.AlterField(
            model_name='cliniclog',
            name='follow_up_planned',
            field=models.NullBooleanField(),
        ),
        migrations.AlterField(
            model_name='cliniclog',
            name='histamine_attendance',
            field=models.NullBooleanField(),
        ),
        migrations.AlterField(
            model_name='cliniclog',
            name='histamine_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='cliniclog',
            name='lung_function',
            field=models.NullBooleanField(),
        ),
        migrations.AlterField(
            model_name='cliniclog',
            name='lung_function_attendance',
            field=models.NullBooleanField(),
        ),
        migrations.AlterField(
            model_name='cliniclog',
            name='lung_function_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='cliniclog',
            name='other_hospital_info',
            field=models.NullBooleanField(),
        ),
        migrations.AlterField(
            model_name='cliniclog',
            name='peak_flow',
            field=models.NullBooleanField(),
        ),
        migrations.AlterField(
            model_name='cliniclog',
            name='seen_by',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='cliniclog',
            name='work_samples',
            field=models.NullBooleanField(),
        ),
        migrations.AlterField(
            model_name='referral',
            name='date_of_referral',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='referral',
            name='date_referral_received',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='referral',
            name='referrer_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
