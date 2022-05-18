# Generated by Django 2.2.16 on 2022-05-18 11:44

from django.db import migrations

def is_populated(instance):
	fields = instance._meta.get_fields()
	for field in fields:
		field_name = field.name
		if field_name in ('id', 'episode', 'bloods'):
			continue
		if field.default and getattr(instance, field_name) == field.default:
			continue
		if getattr(instance, field_name):
			return True

def forwards(apps, schema_editor):
	"""
	Some clinic logs are populated but have no consistency token
	as they were populated via migrations.

	Add consistency tokens to these.
	"""
	ClinicLog = apps.get_model('rbhl', 'ClinicLog')
	Employment = apps.get_model('rbhl', 'Employment')
	Referral = apps.get_model('rbhl', 'Referral')
	SocialHistor = apps.get_model('rbhl', 'SocialHistory')

	clinic_logs = list(ClinicLog.objects.filter(consistency_token=''))
	employments = list(Employment.objects.filter(consistency_token=''))
	referrals = list(Referral.objects.filter(consistency_token=''))
	social_history = list(SocialHistor.objects.filter(consistency_token=''))
	for instance in clinic_logs + employments + referrals + social_history:
		if is_populated(instance):
			instance.set_consistency_token()
			instance.save()

class Migration(migrations.Migration):

    dependencies = [
        ('rbhl', '0064_auto_20220518_1141'),
    ]

    operations = [
        migrations.RunPython(
            forwards
        )
    ]
