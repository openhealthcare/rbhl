"""
Remove old episodes/patients/etc
"""
from django.core.management import BaseCommand

from opal.models import Patient, Episode

from rbhl.models import Demographics, Referral, ClinicLog, ContactDetails
from legacy.models import BloodBook, BloodBookResult, ActionLog


def flush():
    print("Deleting old episodes, referrals and actionlogs")
    Episode.objects.all().delete()
    Patient.objects.all().delete()
    Demographics.objects.all().delete()
    Referral.objects.all().delete()
    ContactDetails.objects.all().delete()
    ClinicLog.objects.all().delete()
    ActionLog.objects.all().delete()
    BloodBookResult.objects.all().delete()
    BloodBookResult.objects.all().delete()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        flush()
