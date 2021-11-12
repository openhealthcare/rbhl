"""
rbhl models.
"""
import datetime
import math
from django.db import models as fields
from django.utils import timezone
from decimal import Decimal
from django.db.models.signals import (
    pre_save, post_save, post_delete
)
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from opal import models
from opal.core.fields import enum
from opal.core import lookuplists

YN = enum('Yes', 'No')
User = get_user_model()

"""
Core Opal models - these inherit from the abstract data models in
opal.models but can be customised here with extra / altered fields.
"""


def calculate_peak_expiratory_flow(height, age, sex):
    """
    For males
    PEF = e (0.544 loge*age – 0.0151age – 74.7/height + 5.48)

    For females
    PEF = e (0.376 loge*age – 0.0121 age – 58.8/height + 5.63)

    Reference

    AJ Nunn, I Gregg New regression equations for predicting peak
    expiratory flow in adults Br Med J 1989; 298:1068-70
    """
    if sex == Demographics.MALE:
        PEF = 0.544 * (math.log(age)) - (0.0151*age) - 74.7/height + 5.48
    if sex == Demographics.FEMALE:
        PEF = 0.376 * (math.log(age)) - (0.0121*age) - 58.8/height + 5.63

    return round(math.exp(PEF))


def get_peak_expiratory_flow(date, episode, trial_num):
    demographics = episode.patient.demographics()
    height = demographics.height
    sex = demographics.sex
    age = demographics.get_age(date)

    if height and sex and age:
        return calculate_peak_expiratory_flow(height, age, sex)

    if not height or not sex:
        return

    imported = ImportedFromPeakFlowDatabase.objects.filter(
        episode=episode, trial_number=trial_num
    ).first()

    if imported and imported.age:
        return calculate_peak_expiratory_flow(
            height, imported.age, sex
        )


class RBHLSubrecord(fields.Model):
    """
    Changes models titles and field display names
    to be sentence case rather than title case,
    the opal default.
    """
    class Meta:
        abstract = True

    @classmethod
    def _get_field_title(cls, name):
        field = cls._get_field(name)
        if isinstance(field, fields.ManyToOneRel):
            field_name = field.related_model._meta.verbose_name_plural
        else:
            field_name = field.verbose_name

        if field_name.islower():
            field_name = field_name.capitalize()

        return field_name

    @classmethod
    def get_display_name(cls):
        if cls._meta.verbose_name.islower():
            return cls._meta.verbose_name.capitalize()
        return cls._meta.verbose_name


class Demographics(RBHLSubrecord, models.Demographics):
    height = fields.IntegerField(
        blank=True, null=True, verbose_name='Height (cm)'
    )
    MALE = "Male"
    FEMALE = "Female"

    def get_age(self, date=None):
        if date is None:
            date = datetime.date.today()

        if self.date_of_birth:
            born = self.date_of_birth
            return date.year - born.year - (
                (date.month, date.day) < (born.month, born.day)
            )


"""
End Opal core models
"""


class SocialHistory(RBHLSubrecord, models.EpisodeSubrecord):
    _is_singleton = True
    _icon = 'fa fa-clock-o'

    SMOKING_CHOICES = enum("Currently", "Ex-smoker", "Never")
    smoker = fields.CharField(
        blank=True, null=True, max_length=256, choices=SMOKING_CHOICES
    )
    cigarettes_per_day = fields.IntegerField(null=True, blank=True)


class ContactDetails(RBHLSubrecord, models.PatientSubrecord):
    _is_singleton = True
    _icon         = 'fa fa-phone'

    mobile = fields.CharField(blank=True, null=True, max_length=100)
    phone  = fields.CharField(blank=True, null=True, max_length=100)
    email  = fields.CharField(blank=True, null=True, max_length=100)
    email_consent = fields.BooleanField(default=False)


class RBHReferrer(lookuplists.LookupList):
    pass


class GeographicalArea(lookuplists.LookupList):
    pass


class Referral(RBHLSubrecord, models.EpisodeSubrecord):
    _icon         = 'fa fa-level-up'

    REASONS = enum(
        "Environmental",
        "Fit to work",
        "Occupational",
        "Other"
    )

    DISEASE = enum(
        "Asthma",
        "Asthma / Rhinitis",
        "Inhalation injury",
        "Malignancy",
        "Other / Unclear",
        "Pulmonary fibrosis(eg: Asbestos related disease)"
    )

    SOURCE = enum(
        'GP',
        'RBH doctor',
        'Other hospital doctor',
        'Occupational health doctor or nurse',
        'Medico legal',
        'Self',
        'Other'
    )

    # Deprecated
    referrer_title         = models.ForeignKeyOrFreeText(models.Title)
    referrer_name = fields.CharField(
        blank=True, null=True, max_length=100, verbose_name="Referrer name"
    )
    reference_number = fields.CharField(
        blank=True, null=True, max_length=200, verbose_name="Their reference number"
    )
    date_of_referral       = fields.DateField(
        blank=True, null=True
    )

    # Process tracking for admin staff
    date_referral_received = fields.DateField(
        blank=True, null=True, verbose_name="Date referral received"
    )
    # ??
    date_first_contact     = fields.DateField(
        blank=True, null=True, verbose_name="Date of first contact"
    )
    # Used by admin staff
    comments               = fields.TextField(blank=True, null=True)

    date_first_appointment = fields.DateField(
        blank=True, null=True, verbose_name="Date of first appointment offered"
    )
    referral_source = fields.TextField(
        blank=True, null=True, choices=SOURCE, verbose_name="Referral source",
    )
    referral_reason = fields.CharField(
        blank=True, null=True, max_length=256, choices=REASONS
    )
    referral_disease = fields.CharField(
        blank=True, null=True, max_length=256, choices=DISEASE
    )
    geographical_area = models.ForeignKeyOrFreeText(GeographicalArea)
    occld = fields.BooleanField(default=True, verbose_name="OCCLD")

    @classmethod
    def get_recent_occld_referral_for_episode(cls, episode):
        """
        """
        clinic_log = episode.cliniclog_set.all()[0]
        clinc_log_date = clinic_log.clinic_date
        if not clinc_log_date:
            return
        referrals = episode.referral_set.all()
        recent_referral = None
        max_referral_date = None

        for referral in referrals:
            referral_date = referral.date_of_referral
            occld = referral.occld
            if occld and referral_date and referral_date <= clinc_log_date:
                if not max_referral_date or max_referral_date < referral_date:
                    max_referral_date = referral_date
                    recent_referral = referral
        return recent_referral


class Employer(lookuplists.LookupList):
    pass


class OHProvider(lookuplists.LookupList):
    pass


class EmploymentCategory(lookuplists.LookupList):
    pass


class JobTitle(lookuplists.LookupList):
    pass


class Employment(RBHLSubrecord, models.EpisodeSubrecord):
    _icon         = 'fa fa-building-o'

    employer = fields.CharField(blank=True, null=True, max_length=100)
    job_title = models.ForeignKeyOrFreeText(JobTitle)
    employment_category = models.ForeignKeyOrFreeText(
        EmploymentCategory, verbose_name="category"
    )
    employed_in_suspect_occupation = fields.BooleanField(
        default=False, verbose_name="Currently employed in suspect occupation"
    )
    exposures = fields.TextField(blank=True, default="")
    oh_provider = fields.CharField(
        blank=True, null=True, max_length=100, verbose_name="OH provider"
    )
    firefighter = fields.NullBooleanField(
        verbose_name="Firefighter pre-employment"
    )


class ClinicLog(RBHLSubrecord, models.EpisodeSubrecord):
    _icon         = 'fa fa-hospital-o'
    _is_singleton = True

    class Meta:
        verbose_name = "Clinic details"

    KNOWN = 'Known'

    OUTCOMES = enum(
        KNOWN,
        'Investigations continuing',
        'Not established lost to follow-up',
        'Not reached despite investigation',
        'Not established referred to someone else',
        'Not established patient withdrew'
    )

    seen_by           = fields.CharField(
        null=True, blank=True, default="", max_length=100
    )
    cns               = fields.CharField(
        null=True,
        blank=True,
        default="",
        max_length=100,
        verbose_name="CNS",
        help_text="Clinical nurse specialist"
    )
    clinic_date        = fields.DateField(blank=True, null=True)
    clinic_site        = fields.CharField(
        blank=True, null=True, max_length=256, default="OCLD"
    )
    follow_up_planned = fields.NullBooleanField()
    date_of_followup  = fields.DateField(
        blank=True, null=True, verbose_name="Date of follow up"
    )

    lung_function       = fields.NullBooleanField()
    lung_function_date  = fields.DateField(blank=True, null=True)
    lung_function_attendance = fields.NullBooleanField()

    histamine           = fields.NullBooleanField()
    histamine_date      = fields.DateField(blank=True, null=True)
    histamine_attendance = fields.NullBooleanField()

    peak_flow           = fields.NullBooleanField()

    other_rbh_bloods    = fields.NullBooleanField(
        verbose_name="Other RBH bloods"
    )
    immunology_oem      = fields.NullBooleanField(
        verbose_name="Immunology OEM"
    )

    other_hospital_info = fields.NullBooleanField()
    other_oh_info       = fields.NullBooleanField(
        verbose_name="Other OH info"
    )
    other_gp_info       = fields.NullBooleanField(
        verbose_name="Other GP info"
    )
    work_samples        = fields.NullBooleanField()

    outstanding_tests_required = fields.BooleanField(
        default=False
    )

    active              = fields.NullBooleanField()

    diagnosis_outcome = fields.CharField(
        blank=True, null=True, max_length=256, choices=OUTCOMES
    )
    referred_to = fields.CharField(
        blank=True, null=True, max_length=256
    )

    def days_since_first_attended(self):
        if not self.clinic_date:
            return None
        today = datetime.date.today()
        diff = today - self.clinic_date
        return diff.days


class Letter(models.EpisodeSubrecord):
    _icon = 'fa fa-envelope'

    text = fields.TextField(blank=True, null=True)


class PeakFlowDay(RBHLSubrecord, models.EpisodeSubrecord):
    _sort = '-date'

    date = fields.DateField(blank=True, null=True)
    treatment_taken = fields.CharField(max_length=200, blank=True, null=True)
    note = fields.TextField()

    day_num = fields.IntegerField(blank=True, null=True)
    trial_num = fields.IntegerField(blank=True, null=True)

    work_day = fields.BooleanField(default=False)

    flow_0000 = fields.IntegerField(
        blank=True, null=True, verbose_name="00:00"
    )
    flow_0100 = fields.IntegerField(
        blank=True, null=True, verbose_name="01:00"
    )
    flow_0200 = fields.IntegerField(
        blank=True, null=True, verbose_name="02:00"
    )
    flow_0300 = fields.IntegerField(
        blank=True, null=True, verbose_name="03:00"
    )
    flow_0400 = fields.IntegerField(
        blank=True, null=True, verbose_name="04:00"
    )
    flow_0500 = fields.IntegerField(
        blank=True, null=True, verbose_name="05:00"
    )
    flow_0600 = fields.IntegerField(
        blank=True, null=True, verbose_name="06:00"
    )
    flow_0700 = fields.IntegerField(
        blank=True, null=True, verbose_name="07:00"
    )
    flow_0800 = fields.IntegerField(
        blank=True, null=True, verbose_name="08:00"
    )
    flow_0900 = fields.IntegerField(
        blank=True, null=True, verbose_name="09:00"
    )
    flow_1000 = fields.IntegerField(
        blank=True, null=True, verbose_name="10:00"
    )
    flow_1100 = fields.IntegerField(
        blank=True, null=True, verbose_name="11:00"
    )
    flow_1200 = fields.IntegerField(
        blank=True, null=True, verbose_name="12:00"
    )
    flow_1300 = fields.IntegerField(
        blank=True, null=True, verbose_name="13:00"
    )
    flow_1400 = fields.IntegerField(
        blank=True, null=True, verbose_name="14:00"
    )
    flow_1500 = fields.IntegerField(
        blank=True, null=True, verbose_name="15:00"
    )
    flow_1600 = fields.IntegerField(
        blank=True, null=True, verbose_name="16:00"
    )
    flow_1700 = fields.IntegerField(
        blank=True, null=True, verbose_name="17:00"
    )
    flow_1800 = fields.IntegerField(
        blank=True, null=True, verbose_name="18:00"
    )
    flow_1900 = fields.IntegerField(
        blank=True, null=True, verbose_name="19:00"
    )
    flow_2000 = fields.IntegerField(
        blank=True, null=True, verbose_name="20:00"
    )
    flow_2100 = fields.IntegerField(
        blank=True, null=True, verbose_name="21:00"
    )
    flow_2200 = fields.IntegerField(
        blank=True, null=True, verbose_name="22:00"
    )
    flow_2300 = fields.IntegerField(
        blank=True, null=True, verbose_name="23:00"
    )

    class Meta:
        unique_together = [['day_num', 'trial_num', 'episode']]

    def get_flow_values(self):
        db_fields = self._meta.get_fields()
        fields = [
            i.attname for i in db_fields if i.attname.startswith("flow_")
        ]
        flow_values = []
        for field in fields:
            value = getattr(self, field)
            if value:
                flow_values.append(value)
        return flow_values

    def get_aggregate_data(self):
        flow_values = self.get_flow_values()

        if flow_values:
            min_flow = min(flow_values)
            max_flow = max(flow_values)
            variabilty = Decimal(max_flow - min_flow)/Decimal(max_flow)
            variabilty_perc = round(variabilty * 100)
            num_entries = len(flow_values)
            mean_flow = round(
                Decimal(sum(flow_values))/Decimal(len(flow_values))
            )
            return {
                "min_flow": min_flow,
                "max_flow": max_flow,
                "mean_flow": mean_flow,
                "variabilty": variabilty_perc,
                "num_entries": num_entries
            }


class AsthmaDetails(RBHLSubrecord, models.EpisodeSubrecord):
    """
    This model has an implicit fk to Diagnosis, based on a
    diagnosis of Asthma and a date.

    When this model is saved we create a diagnosis of Asthma for the date.
    When we update this model we update the diagnosis for the date.
    When it is deleted we remove the diagnosis of Asthma for the date.
    """
    _icon = "fa fa-stethoscope"

    OCCUPATIONAL_CAUSED_BY_SENSITISATION = "Occupational caused by sensitisation"
    EXACERBATED_BY_WORK = "Exacerbated by work"
    IRRITANT_INDUCED = "Irritant induced"
    NON_OCCUPATIONAL = "Non occupational"

    ASTHMA_CHOICES = enum(
        OCCUPATIONAL_CAUSED_BY_SENSITISATION,
        EXACERBATED_BY_WORK,
        IRRITANT_INDUCED,
        NON_OCCUPATIONAL,
    )
    date = fields.DateField(blank=True, null=True)
    trigger = fields.CharField(
        blank=True, null=True, max_length=256, choices=ASTHMA_CHOICES
    )
    sensitivities = fields.TextField(blank=True, default="")

    class Meta:
        verbose_name = "Asthma"


@receiver(post_delete, sender=AsthmaDetails)
def delete_related_asthma_diagnosis(
    sender, instance, **kwargs
):
    instance.episode.diagnosis_set.filter(
        category=Diagnosis.ASTHMA,
        date=instance.date
    ).delete()


@receiver(pre_save, sender=AsthmaDetails)
def create_related_asthma_diagnosis(
    sender, instance, **kwargs
):
    """
    If its new create a diagnosis.

    If its an update that updates the date,
    update the diagnosis date.
    """
    if not instance.id:
        Diagnosis.objects.create(
            episode=instance.episode,
            category=Diagnosis.ASTHMA,
            condition=Diagnosis.ASTHMA,
            date=instance.date
        )
    else:
        existing_instance = instance.__class__.objects.get(
            id=instance.id
        )
        if not existing_instance.date == instance.date:
            Diagnosis.objects.filter(
                episode=instance.episode,
                category=Diagnosis.ASTHMA,
                condition=Diagnosis.ASTHMA,
                date=existing_instance.date
            ).update(
                date=instance.date
            )


class RhinitisDetails(RBHLSubrecord, models.EpisodeSubrecord):
    """
    This model has an implicit fk to Diagnosis, based on a
    diagnosis of Rhinitis and a date.

    When this model is saved we create a diagnosis of Rhinitis for the date.
    When we update this model we update the diagnosis for the date.
    When it is deleted we remove the diagnosis of Rhinitis for the date.
    """
    _icon = "fa fa-stethoscope"

    OCCUPATIONAL_CAUSED_BY_SENSITISATION = "Occupational caused by sensitisation"
    EXACERBATED_BY_WORK = "Exacerbated by work"
    NON_OCCUPATIONAL = "Non occupational"

    RHINITIS_CHOICES = enum(
        OCCUPATIONAL_CAUSED_BY_SENSITISATION,
        EXACERBATED_BY_WORK,
        NON_OCCUPATIONAL,
    )
    date = fields.DateField(blank=True, null=True)
    trigger = fields.CharField(
        blank=True, null=True, max_length=256, choices=RHINITIS_CHOICES
    )
    sensitivities = fields.TextField(blank=True, default="")

    class Meta:
        verbose_name = "Rhinitis"


@receiver(post_delete, sender=RhinitisDetails)
def delete_related_rhinitis_diagnosis(
    sender, instance, **kwargs
):
    instance.episode.diagnosis_set.filter(
        category=Diagnosis.RHINITIS,
        date=instance.date
    ).delete()


@receiver(pre_save, sender=RhinitisDetails)
def create_related_rhinits_diagnosis(
    sender, instance, **kwargs
):
    """
    If its new create a diagnosis.

    If its an update that updates the date,
    update the diagnosis date.
    """
    if not instance.id:
        Diagnosis.objects.create(
            episode=instance.episode,
            category=Diagnosis.RHINITIS,
            condition=Diagnosis.RHINITIS,
            date=instance.date
        )
    else:
        existing_instance = instance.__class__.objects.get(
            id=instance.id
        )
        if not existing_instance.date == instance.date:
            Diagnosis.objects.filter(
                episode=instance.episode,
                category=Diagnosis.RHINITIS,
                condition=Diagnosis.RHINITIS,
                date=existing_instance.date
            ).update(
                date=instance.date
            )


class Diagnosis(RBHLSubrecord, models.EpisodeSubrecord):
    ASTHMA = "Asthma"
    RHINITIS = "Rhinitis"
    CHRONIC_AIR_FLOW_LIMITATION = "Chronic air flow limitation"
    MALIGNANCY = "Malignancy"
    BENIGN_PLEURAL_DISEASE = "Benign pleural disease"
    DIFFUSE_LUNG_DISEASE = "Diffuse lung disease"
    BREATHING_PATTERN_DYSFUNCTION = "Breathing pattern dysfunction"
    IRRITANT_SYMPTOMS_ONLY = "Irritant symptoms only"
    UPPER_AIRWAY_DYSFUNCTION = "Upper airway dysfunction"

    NAD = "NAD"  # no abnormality detected
    OTHER = "Other"

    CONDITON_CATEGORIES = enum(
        ASTHMA, RHINITIS, CHRONIC_AIR_FLOW_LIMITATION,
        MALIGNANCY, BENIGN_PLEURAL_DISEASE, DIFFUSE_LUNG_DISEASE,
        BREATHING_PATTERN_DYSFUNCTION, IRRITANT_SYMPTOMS_ONLY,
        UPPER_AIRWAY_DYSFUNCTION, OTHER
    )

    CONDITION_OPTIONS = {
        "asthma": [ASTHMA],
        "rhinitis": [RHINITIS],
        "chronic_air_flow_limitation": [
            "COPD", "Emphysema"
        ],
        "NAD": [NAD],
        # Free text is also possible for all of the below
        "malignancy": [
            'Mesothelioma',
            'Bronchus with asbestos exposure',
        ],
        "benign_pleural_disease": [
            "Predominantly plaques",
            "Diffuse"
        ],
        "diffuse_lung_disease": [
            "Asbestosis",
            "Hypersensitivity pneumonitis",
            "ILD Other",
            "Berylliosis",
            "Ideopathic Pulmonary Fibrosis",
            "Sarcodisis",
            "Silicosis",
        ],
        "other": [
            "Humidifier fever",
            "Polymer fume fever",
            "Infection",
            "Chemical pneumonitis",
            "Building related symptoms",
            "Breathing pattern disorder ",
            "Induced laryngeal obstruction",
            "Air travel related symptoms",
            "Medically unexplained symptoms",
            "Cough due to irritant symptoms"
        ]
    }

    date = fields.DateField(blank=True, null=True)
    category = fields.CharField(
        blank=True, null=True, max_length=256, choices=CONDITON_CATEGORIES
    )
    condition = fields.CharField(blank=True, null=True, max_length=256)
    occupational = fields.BooleanField(default=False)


@receiver(post_save, sender=Diagnosis)
def handle_NAD_diagnosis(
    sender, instance, **kwargs
):
    """
    If an episode is marked as NAD then they have no
    other diagnosis. Remove the other diagnosis.

    If an episode is given a diagnosis, delete any
    previous diagnosis of NAD that they have.
    """
    if instance.category == instance.NAD:
        instance.episode.rhinitisdetails_set.all().delete()
        instance.episode.asthmadetails_set.all().delete()
        instance.episode.diagnosis_set.exclude(id=instance.id).delete()
    else:
        instance.episode.diagnosis_set.filter(
            category=instance.NAD
        ).delete()


"""
Begin exploratory models during testing
"""


class Occupation(models.EpisodeSubrecord):
    _is_singleton = True
    _exclude_from_extract = True
    _advanced_searchable = False
    currently_employed = fields.CharField(
        max_length=200, choices=YN, blank=True, null=True
    )
    job_title = fields.CharField(max_length=200, blank=True, null=True)
    name_of_employer = fields.CharField(max_length=200, blank=True, null=True)
    exposures = fields.TextField(blank=True, null=True)


class DiagnosisAsthma(models.EpisodeSubrecord):
    _is_singleton = True
    _exclude_from_extract = True
    _advanced_searchable = False

    asthma = fields.CharField(max_length=200, blank=True, null=True)
    exacerbated_by_work = fields.CharField(
        max_length=200, blank=True, null=True
    )
    irritant_induced_asthma = fields.CharField(
        max_length=200, blank=True, null=True, choices=YN
    )
    sensitisation = fields.CharField(
        max_length=200, blank=True, null=True,
        choices=YN,
        verbose_name="Occupational asthma caused by sensitisation"
    )
    sensitising_agent = fields.TextField(blank=True, null=True)
    non_occupational_asthma = fields.CharField(
        max_length=200, blank=True, null=True, choices=YN
    )


class DiagnosisRhinitis(models.EpisodeSubrecord):
    _is_singleton = True
    _exclude_from_extract = True
    _advanced_searchable = False

    rhinitis = fields.CharField(max_length=200, blank=True, null=True)
    work_exacerbated = fields.CharField(
        max_length=200, blank=True, null=True,
        choices=YN,
        verbose_name="Occupational asthma caused by sensitisation"
    )
    sensitisation = fields.CharField(
        max_length=200, blank=True, null=True,
        choices=YN,
        verbose_name="Occupational rhinitis caused by sensitisation"
    )
    cause = fields.TextField(blank=True, null=True)
    non_occupational_rhinitis = fields.CharField(
        max_length=200, blank=True, null=True,
        choices=YN
    )


class ImportedFromPeakFlowDatabase(models.EpisodeSubrecord):
    """
    The occupational lung database was the database before
    Indigo that was used to store peak flows
    """
    _exclude_from_extract = True
    _advanced_searchable = False
    age = fields.IntegerField(blank=True, null=True)
    trial_number = fields.IntegerField(blank=True, null=True)


class PatientSource(fields.Model):
    _exclude_from_extract = True
    _advanced_searchable = False
    patient = fields.OneToOneField(models.Patient, on_delete=fields.CASCADE)
    peak_flow_database = fields.BooleanField(
        default=False, blank=True
    )


class SetUpTwoFactor(fields.Model):
    """
    Instances of this model gives the user permission to setup
    2 factor auth for themselves provided they
    do it within ALLOWED_TIME minutes of the object creation
    """
    user = fields.OneToOneField(User, on_delete=fields.CASCADE)
    created = fields.DateTimeField(auto_now=True)

    # how long in minutes the user is allowed after the object
    # is created
    ALLOWED_TIME = 10

    @classmethod
    def time_left(cls, user):
        instance = cls.objects.filter(user=user).first()
        if instance:
            threshold = instance.created + datetime.timedelta(
                minutes=cls.ALLOWED_TIME
            )
            if threshold > timezone.now():
                diff = threshold - timezone.now()
                return int(diff.seconds/60)

    @classmethod
    def allowed(cls, user):
        if cls.time_left(user):
            return True


class Fact(fields.Model):
    """
    A model to store various performance monitoring data
    """
    FIVE_YEAR_MEAN_REFERRAL_TO_DIAGNOSIS = "Five year mean referral to diagnosis"
    FIVE_YEAR_MEAN_KNOWN_DIAGNOSIS = "Five year mean known diagnosis"

    MEAN_CLINIC_PATIENTS_PER_YEAR = "Mean number of clinic patients per year"

    when        = fields.DateTimeField(default=timezone.now)
    label       = fields.CharField(max_length=100, db_index=True)
    value_int   = fields.IntegerField(blank=True, null=True)
    value_float = fields.FloatField(blank=True, null=True)
    value_str   = fields.CharField(max_length=255, blank=True, null=True)

    def val(self):
        if self.value_int is not None:
            return self.value_int
        if self.value_float is not None:
            return self.value_float
        if self.value_str is not None:
            return self.value_str
        raise ValueError('No value set')
