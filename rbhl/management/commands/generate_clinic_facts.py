"""
Generates the clinic activity facts
"""
import datetime
from collections import defaultdict
from django.core.management.base import BaseCommand
from django.db import transaction
from opal.models import Episode
from rbhl.models import ClinicLog, Diagnosis, Fact, Referral
import logging
logger = logging.getLogger('commands')


class Command(BaseCommand):
    def get_five_year_episodes(cls):
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
            "referral_set",
            "diagnosis_set"
        )

    def handle(self, *args, **kwargs):
        try:
            self.process(*args, **kwargs)
        except Exception:
            logger.error(f"Unable to generate clinic facts on {datetime.date.today()}")
            raise

    @transaction.atomic
    def process(self, *args, **options):
        five_year_episodes = self.get_five_year_episodes()
        episode_count = five_year_episodes.count()

        referral_mean = round(episode_count/5)
        Fact.objects.create(
            label=Fact.MEAN_CLINIC_PATIENTS_PER_YEAR,
            value_int=referral_mean
        )
        episode_ids = set(five_year_episodes.values_list('id', flat=True))
        diagnosis = Diagnosis.objects.filter(
            episode_id__in=episode_ids
        ).exclude(
            date=None
        ).order_by("date")
        episode_id_to_diagnosis = defaultdict(list)
        for i in diagnosis:
            episode_id_to_diagnosis[i.episode_id].append(i)
        diagnosed_count = 0

        # Diagnosis % is calclated by the
        # number of clinic log with diagnosis
        # Known
        for episode in five_year_episodes:
            clinic_log = episode.cliniclog_set.all()[0]
            if clinic_log.diagnosis_outcome == ClinicLog.KNOWN:
                diagnosed_count += 1

        mean_diagnosis_percent = round(diagnosed_count/episode_count * 100)
        Fact.objects.filter(label=Fact.FIVE_YEAR_MEAN_KNOWN_DIAGNOSIS).delete()
        Fact.objects.create(
            label=Fact.FIVE_YEAR_MEAN_KNOWN_DIAGNOSIS,
            value_int=mean_diagnosis_percent
        )

        # Diagnosis time is calculated the time from our first diagnosis
        # after the referral date
        total_days = 0
        count_with_diagnosis = 0
        for episode in five_year_episodes:
            referral = Referral.get_recent_occld_referral_for_episode(episode)
            if referral and referral.date_of_referral:
                diagnoses = episode.diagnosis_set.all()
                diagnoses = [i for i in diagnoses if i.date]
                diagnosis_after_referral = [
                    i for i in diagnoses if i.date > referral.date_of_referral
                ]
                if diagnosis_after_referral:
                    diagnosis = diagnosis_after_referral[0]
                    days_to_diagnosis = diagnosis.date - referral.date_of_referral
                    total_days += days_to_diagnosis.days
                    count_with_diagnosis += 1
