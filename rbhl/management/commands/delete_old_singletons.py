from django.db import transaction
from rbhl.models import Referral, Employment
from django.core.management.base import BaseCommand


def is_empty_employment(employment):
    empty_fields = [
        "employer",
        "job_title",
        "employment_category",
        "employed_in_suspect_occupation",
        "exposures",
        "oh_provider",
        "firefighter",
        "created",
        "updated"
    ]
    empty = True

    for field in empty_fields:
        if getattr(employment, field):
            empty = False
    return empty


def is_empty_referral(referral):
    empty_fields = [
        "referrer_title",
        "referrer_name",
        "reference_number",
        "date_of_referral",
        "date_referral_received",
        "date_first_contact",
        "comments",
        "attendance",
        "date_first_appointment",
        "referral_source",
        "referral_reason",
        "referral_disease",
        "geographical_area",
    ]
    empty = True

    for field in empty_fields:
        if getattr(referral, field):
            empty = False
    return empty


class Command(BaseCommand):
    """
    Referrals and employments used to be singletons.

    Usually we would used created/updated timestamps to
    detect if they are singletons however not all the
    old data import scripts populated created/updated.

    This checks all fields on the model and sees if they are
    populated and deletes them if they have not been touched.
    """
    @transaction.atomic
    def handle(self, *args, **options):
        deleted_employment = 0
        deleted_referral = 0
        for employment in Employment.objects.all():
            if is_empty_employment(employment):
                employment.delete()
                deleted_employment += 1

        deleted_referral = 0
        for referral in Referral.objects.all():
            if is_empty_referral(referral):
                referral.delete()
                deleted_referral += 1

        self.stdout.write(f"Deleleted {deleted_employment} employment models")
        self.stdout.write(f"Deleleted {deleted_referral} referral models")
