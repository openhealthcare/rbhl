"""
rbhl models.
"""
import datetime
import math
from django.db import models as fields
from decimal import Decimal

from opal import models
from opal.core.fields import enum
from opal.core import lookuplists

YN = enum('Yes', 'No')

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


class RbhlSubrecord(fields.Model):
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


class Demographics(models.Demographics):
    height = fields.IntegerField(
        blank=True, null=True, verbose_name='Height(cm)'
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


class Location(models.Location):
    pass


class Allergies(models.Allergies):
    pass


class Diagnosis(models.Diagnosis):
    _title = 'Diagnosis'


class PastMedicalHistory(models.PastMedicalHistory):
    pass


class Treatment(models.Treatment):
    pass


class Investigation(models.Investigation):
    pass


class SymptomComplex(models.SymptomComplex):
    pass


class PatientConsultation(models.PatientConsultation):
    pass

# we commonly need a referral route, ie how the patient
# came to the service, but not always.
# class ReferralRoute(models.ReferralRoute): pass


"""
End Opal core models
"""


class ContactDetails(models.PatientSubrecord):
    _is_singleton = True
    _icon         = 'fa fa-phone'

    mobile = fields.CharField(blank=True, null=True, max_length=100)
    phone  = fields.CharField(blank=True, null=True, max_length=100)
    email  = fields.CharField(blank=True, null=True, max_length=100)
    address = fields.TextField(blank=True, default="")

    class Meta:
        verbose_name = "Contact details"


class RBHReferrer(lookuplists.LookupList):
    pass


class ReferralReason(lookuplists.LookupList):
    pass


class ReferralDisease(lookuplists.LookupList):
    pass


class GeographicalArea(lookuplists.LookupList):
    pass


class Referral(RbhlSubrecord, models.EpisodeSubrecord):
    _icon         = 'fa fa-level-up'
    _is_singleton = True

    # Deprecated
    referrer_title         = models.ForeignKeyOrFreeText(models.Title)
    referrer_name = fields.CharField(blank=True, null=True, max_length=100)
    date_of_referral       = fields.DateField(blank=True, null=True)

    # Process tracking for admin staff
    date_referral_received = fields.DateField(blank=True, null=True)
    # ??
    date_first_contact     = fields.DateField(
        blank=True, null=True, verbose_name="Date of first contact"
    )
    # Used by admin staff
    comments               = fields.TextField(blank=True, null=True)

    attendance = fields.NullBooleanField()
    date_first_appointment = fields.DateField(
        blank=True, null=True, verbose_name="Date of first appointment offered"
    )
    referral_type = models.ForeignKeyOrFreeText(models.ReferralType)
    referral_reason = models.ForeignKeyOrFreeText(ReferralReason)
    referral_disease = models.ForeignKeyOrFreeText(ReferralDisease)
    geographical_area = models.ForeignKeyOrFreeText(GeographicalArea)


class SocialHistory(RbhlSubrecord, models.EpisodeSubrecord):
    _is_singleton = True
    _icon = 'fa fa-clock-o'

    SMOKING_CHOICES = enum("Currently", "Ex-smoker", "Never")
    smoker = fields.CharField(
        blank=True, null=True, max_length=256, choices=SMOKING_CHOICES
    )
    cigerettes_per_day = fields.IntegerField(null=True, blank=True)


class Employer(lookuplists.LookupList):
    pass


class OHProvider(lookuplists.LookupList):
    pass


class EmploymentCategory(lookuplists.LookupList):
    pass


class JobTitle(lookuplists.LookupList):
    pass


class Employment(RbhlSubrecord, models.EpisodeSubrecord):
    _icon         = 'fa fa-building-o'
    _is_singleton = True

    employer = fields.CharField(blank=True, null=True, max_length=100)
    job_title = models.ForeignKeyOrFreeText(JobTitle)
    employment_category = models.ForeignKeyOrFreeText(
        EmploymentCategory
    )
    employed_in_suspect_occupation = fields.NullBooleanField()
    exposures = fields.TextField(blank=True, default="")
    oh_provider = fields.CharField(
        blank=True, null=True, max_length=100, verbose_name="OH provider"
    )
    firefighter = fields.NullBooleanField()


class RbhlDiagnosticTesting(RbhlSubrecord, models.EpisodeSubrecord):
    _is_singleton = True
    _icon = "fa fa-hand-paper-o"

    ATOPIC_CHOICES = enum("Yes", "No", "Dermatographic")
    antihistimines = fields.NullBooleanField(null=True, blank=True)

    skin_prick_test = fields.NullBooleanField(null=True, blank=True)
    atopic = fields.TextField(null=True, blank=True, choices=ATOPIC_CHOICES)
    specific_skin_prick = fields.NullBooleanField(null=True, blank=True)

    immunology_oem = fields.NullBooleanField(
        null=True, blank=True, verbose_name="Immunology OEM"
    )

    # TODO seperate section
    # bronchial_prov_test = models.NullBooleanField(null=True, blank=True)

    fev_1 = fields.FloatField(
        null=True, blank=True, verbose_name="FEV1"
    )
    fev_1_post_ventolin = fields.FloatField(
        null=True, blank=True, verbose_name="FEV1 post Ventolin"
    )
    fev_1_percentage_protected = fields.IntegerField(
        null=True, blank=True, verbose_name="FEV1 predicted %"
    )
    fvc = fields.FloatField(
        null=True, blank=True, verbose_name="FVC"
    )
    fvc_post_ventolin = fields.FloatField(
        null=True, blank=True, verbose_name="FVC post Ventolin"
    )
    fvc_percentage_protected = fields.IntegerField(
        null=True, blank=True, verbose_name="FVC predicted %"
    )
    ct_chest_scan = fields.NullBooleanField(
        null=True, blank=True, verbose_name="CT chest scan"
    )
    ct_chest_scan_date = fields.DateField(
        null=True, blank=True, verbose_name="CT chest scan date"
    )
    full_lung_function = fields.NullBooleanField(null=True, blank=True)
    full_lung_function_date = fields.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Diagnostic testing"


class MalignancyType(lookuplists.LookupList):
    pass


class DiffuseLungDisease(lookuplists.LookupList):
    pass


class BenignPleuralDisease(lookuplists.LookupList):
    pass


class OtherDiagnosisType(lookuplists.LookupList):
    pass


class Asthma(RbhlSubrecord, models.EpisodeSubrecord):
    _is_singleton = True
    _icon = "fa fa-hand-paper-o"
    occupational_caused_by_sensitisation = fields.BooleanField(
        default=False
    )
    exacerbated_by_work = fields.BooleanField(
        default=False
    )
    irritant_induced = fields.BooleanField(
        default=False
    )
    non_occupational = fields.BooleanField(
        default=False
    )
    # we are using this for if they tick asthma but
    # nothing else
    other = fields.BooleanField(
        default=False
    )


class Rhinitis(RbhlSubrecord, models.EpisodeSubrecord):
    _is_singleton = True
    _icon = "fa fa-hand-paper-o"
    occupational_caused_by_sensitisation = fields.BooleanField(default=False)
    exacerbated_by_work = fields.BooleanField(default=False)
    non_occupational = fields.BooleanField(default=False)
    # we are using this for if they tick rhinitis but
    # nothing else
    other = fields.BooleanField(default=False)


class ChronicAirFlowLimitation(RbhlSubrecord, models.EpisodeSubrecord):
    _is_singleton = True
    _icon = "fa fa-hand-paper-o"
    copd = fields.BooleanField(
        default=False, verbose_name="COPD"
    )
    emphysema = fields.BooleanField(
        default=False
    )
    occupational = fields.BooleanField(default=False)


class Disease(RbhlSubrecord, models.EpisodeSubrecord):
    _is_singleton = True
    _icon = "fa fa-hand-paper-o"
    malignancy = models.ForeignKeyOrFreeText(MalignancyType)
    malignancy_occupational = fields.BooleanField(default=False)
    diffuse_lung_disease = models.ForeignKeyOrFreeText(DiffuseLungDisease)
    diffuse_lung_disease_occupational = fields.BooleanField(default=False)
    benign_pleural_disease = models.ForeignKeyOrFreeText(BenignPleuralDisease)


class OtherDiagnostic(RbhlSubrecord, models.EpisodeSubrecord):
    _is_singleton = True
    _icon = "fa fa-hand-paper-o"
    other_diagnosis = models.ForeignKeyOrFreeText(OtherDiagnosisType)
    other_diagnosis_occupational = fields.BooleanField(default=False)
    nad = fields.BooleanField(default=False, verbose_name="NaD")


class Sensitivities(RbhlSubrecord, models.EpisodeSubrecord):
    _is_singleton = True
    _icon = "fa fa-hand-paper-o"
    sensitivities = fields.TextField(blank=True, default="")


class PresentingComplaint(lookuplists.LookupList):
    pass


class DiagnosisOutcome(lookuplists.LookupList):
    pass


class ClinicLog(RbhlSubrecord, models.EpisodeSubrecord):
    _icon         = 'fa fa-hospital-o'
    _is_singleton = True

    seen_by           = fields.CharField(
        null=True, blank=True, default="", max_length=100
    )
    clinic_date        = fields.DateField(blank=True, null=True)
    clinic_site        = fields.CharField(
        blank=True, null=True, max_length=256, default="OCLD"
    )
    presenting_complaint = models.ForeignKeyOrFreeText(PresentingComplaint)
    diagnosis_made    = fields.NullBooleanField()
    diagnosis_outcome = models.ForeignKeyOrFreeText(
        DiagnosisOutcome
    )
    referred_to = fields.CharField(blank=True, null=True, max_length=256)
    follow_up_planned = fields.NullBooleanField()
    date_of_followup  = fields.DateField(blank=True, null=True)

    lung_function       = fields.NullBooleanField()
    lung_function_date  = fields.DateField(blank=True, null=True)
    lung_function_attendance = fields.NullBooleanField()

    histamine           = fields.NullBooleanField()
    histamine_date      = fields.DateField(blank=True, null=True)
    histamine_attendance = fields.NullBooleanField()

    peak_flow           = fields.NullBooleanField()

    other_rbh_bloods    = fields.NullBooleanField()
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

    class Meta:
        verbose_name = "Clinic log"

    def days_since_first_attended(self):
        if not self.clinic_date:
            return None
        today = datetime.date.today()
        diff = today - self.clinic_date
        return diff.days


class Letter(models.EpisodeSubrecord):
    _icon = 'fa fa-envelope'

    text = fields.TextField(blank=True, null=True)


class PeakFlowDay(models.EpisodeSubrecord):
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


"""
Begin exploratory models during testing
"""


class Occupation(models.EpisodeSubrecord):
    _is_singleton = True
    currently_employed = fields.CharField(
        max_length=200, choices=YN, blank=True, null=True
    )
    job_title = fields.CharField(max_length=200, blank=True, null=True)
    name_of_employer = fields.CharField(max_length=200, blank=True, null=True)
    exposures = fields.TextField(blank=True, null=True)


class DiagnosisAsthma(models.EpisodeSubrecord):
    _is_singleton = True

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
    age = fields.IntegerField(blank=True, null=True)
    trial_number = fields.IntegerField(blank=True, null=True)


class PatientSource(fields.Model):
    patient = fields.OneToOneField(models.Patient, on_delete=fields.CASCADE)
    peak_flow_database = fields.BooleanField(
        default=False, blank=True
    )
