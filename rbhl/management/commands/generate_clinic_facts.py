"""
Generates the clinic activity facts
"""
import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from opal.models import Episode
from rbhl.models import ClinicLog, Fact
import logging
logger = logging.getLogger('commands')


class Command(BaseCommand):
    def get_five_year_episodes(self):
        today = datetime.date.today()
        if today.month > 9:
            five_year_range = (
                datetime.date(today.year-5, 10, 1),
                datetime.date(today.year, 10, 1),
            )
        else:
            five_year_range = (
                datetime.date(today.year-6, 10, 1),
                datetime.date(today.year-1, 10, 1)
            )
        return Episode.objects.filter(
            referral__occld=True
        ).filter(
            cliniclog__clinic_date__gte=five_year_range[0]
        ).filter(
            cliniclog__clinic_date__lt=five_year_range[1]
        ).distinct().prefetch_related(
            "cliniclog_set",
        )

    def handle(self, *args, **kwargs):
        try:
            self.process(*args, **kwargs)
        except Exception:
            logger.error(f"Unable to generate clinic facts on {datetime.date.today()}")
            raise

    @transaction.atomic
    def save_facts(self, mean_clinic_patients_per_year, mean_known_diagnosis):
        Fact.objects.filter(
            label__in=[
                Fact.MEAN_CLINIC_PATIENTS_PER_YEAR,
                Fact.FIVE_YEAR_MEAN_KNOWN_DIAGNOSIS
            ]
        ).delete()
        Fact.objects.create(
            label=Fact.MEAN_CLINIC_PATIENTS_PER_YEAR,
            value_int=mean_clinic_patients_per_year
        )
        Fact.objects.create(
            label=Fact.FIVE_YEAR_MEAN_KNOWN_DIAGNOSIS,
            value_int=mean_known_diagnosis
        )

    def process(self, *args, **options):
        five_year_episodes = self.get_five_year_episodes()
        episode_count = five_year_episodes.count()

        referral_mean = round(episode_count/5)
        diagnosed_count = 0

        # Diagnosis % is calclated by the
        # number of clinic log with diagnosis
        # Known
        for episode in five_year_episodes:
            clinic_log = episode.cliniclog_set.all()[0]
            if clinic_log.diagnosis_outcome == ClinicLog.KNOWN:
                diagnosed_count += 1

        mean_diagnosis_percent = round(diagnosed_count/episode_count * 100)
        self.save_facts(referral_mean, mean_diagnosis_percent)
