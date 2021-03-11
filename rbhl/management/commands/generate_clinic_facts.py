"""
Generates the clinic activity facts
"""
from collections import defaultdict
from django.core.management.base import BaseCommand
from rbhl.models import ClinicLog, Diagnosis, Fact
from rbhl.views import ClinicActivityOverview


class Command(BaseCommand):
    def handle(self, *args, **options):
        five_year_referrals = ClinicActivityOverview.get_five_year_referrals()
        episode_id_to_referrals = defaultdict(list)
        for i in five_year_referrals:
            episode_id_to_referrals[i.episode_id].append(i)

        clinic_log = ClinicLog.objects.filter(
            episode_id__in=episode_id_to_referrals.keys()
        ).filter(
            diagnosis_outcome=ClinicLog.KNOWN
        )
        episode_id_to_clinic_log = defaultdict(list)
        for i in clinic_log:
            episode_id_to_clinic_log[i.episode_id].append(i)

        diagnosis = Diagnosis.objects.filter(
            episode_id__in=episode_id_to_referrals.keys()
        ).exclude(
            date=None
        ).order_by("date")
        episode_id_to_diagnosis = defaultdict(list)
        for i in diagnosis:
            episode_id_to_diagnosis[i.episode_id].append(i)

        total_referrals = five_year_referrals.count()
        diagnosed_count = 0

        # Diagnosis % is calclated by the number of clinic log with diagnosis
        # Known
        for episode_id, referrals in episode_id_to_referrals.items():
            for _ in referrals:
                clinic_log = episode_id_to_clinic_log[episode_id]
                if clinic_log:
                    diagnosed_count += 1

        mean_diagnosis_percent = round(diagnosed_count/total_referrals * 100)
        Fact.objects.filter(label=Fact.FIVE_YEAR_MEAN_KNOWN_DIAGNOSIS).delete()
        Fact.objects.create(
            label=Fact.FIVE_YEAR_MEAN_KNOWN_DIAGNOSIS,
            value_int=mean_diagnosis_percent
        )

        # Diagnosis time is calculated the time from our first diagnosis
        # after the referral date
        total_days = 0
        count_with_diagnosis = 0
        for episode_id, referrals in episode_id_to_referrals.items():
            for referral in referrals:
                diagnoses = episode_id_to_diagnosis[episode_id]
                diagnosis_after_referral = [
                    i for i in diagnoses if i.date > referral.date_of_referral
                ]
                if diagnosis_after_referral:
                    diagnosis = diagnosis_after_referral[0]
                    days_to_diagnosis = diagnosis.date - referral.date_of_referral
                    total_days += days_to_diagnosis.days
                    count_with_diagnosis += 1

        mean_diagnosis_time = round(total_days/count_with_diagnosis)
        Fact.objects.filter(label=Fact.FIVE_YEAR_MEAN_REFERRAL_TO_DIAGNOSIS).delete()
        Fact.objects.create(
            label=Fact.FIVE_YEAR_MEAN_REFERRAL_TO_DIAGNOSIS,
            value_int=mean_diagnosis_time
        )
