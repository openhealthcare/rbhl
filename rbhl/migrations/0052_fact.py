# Generated by Django 2.2.16 on 2021-03-11 17:53

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('rbhl', '0051_referral_ocld'),
    ]

    operations = [
        migrations.CreateModel(
            name='Fact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('when', models.DateTimeField(default=django.utils.timezone.now)),
                ('label', models.CharField(db_index=True, max_length=100)),
                ('value_int', models.IntegerField(blank=True, null=True)),
                ('value_float', models.FloatField(blank=True, null=True)),
                ('value_str', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
    ]
