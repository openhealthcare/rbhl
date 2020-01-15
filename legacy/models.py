"""
Models for the RBH legacy transition
"""
from django.db import models
from opal.models import PatientSubrecord, EpisodeSubrecord, Patient


"""
18 WEEK DB
"""


class ActionLog(EpisodeSubrecord):
    class Meta:
        verbose_name = 'General notes'
    # Now in rbhl.models.Employment
    # employer       = models.CharField( max_length=100)
    # oh_provider    = models.CharField(blank=True, null=True, max_length=100)

    # Now in rbhl.models.ClinicLog
    # seen_by        = models.CharField(blank=True, null=True, max_length=100)
    # clinicdate = models.DateField(blank=True, null=True)
    # diagnosis_made      = models.NullBooleanField()
    # follow_up_planned   = models.NullBooleanField()
    # date_of_followup    = models.DateField(blank=True, null=True)
    # lung_function       = models.NullBooleanField()
    # lung_function_date  = models.DateField(blank=True, null=True)
    # lung_function_attendance = models.NullBooleanField()
    # histamine           = models.NullBooleanField()
    # histamine_date      = models.DateField(blank=True, null=True)
    # histamine_attendance = models.NullBooleanField()
    # peak_flow           = models.NullBooleanField()
    # other_rbh_bloods    = models.NullBooleanField()
    # immunology_oem      = models.NullBooleanField()
    # other_hospital_info = models.NullBooleanField()
    # other_oh_info       = models.NullBooleanField()
    # other_gp_info       = models.NullBooleanField()
    # work_samples        = models.NullBooleanField()

    # Now in rbhl.models.Letter
    # Second comment box RHS [Comments1]
    # letters             = models.TextField(blank=True, null=True)

    # LHS

    # First comment box RHS [Other]
    general_notes       = models.TextField(blank=True, null=True)

    finaldays           = models.IntegerField(blank=True, null=True)


class BloodBook(EpisodeSubrecord):
    reference_number   = models.CharField(blank=True, null=True,
                                          max_length=200)
    employer           = models.CharField(blank=True, null=True,
                                          max_length=200)
    oh_provider        = models.CharField(blank=True, null=True,
                                          max_length=100)
    blood_date         = models.DateField(blank=True, null=True)
    blood_number       = models.CharField(blank=True, null=True,
                                          max_length=200)
    method             = models.CharField(blank=True, null=True,
                                          max_length=200)
    blood_collected    = models.CharField(
        verbose_name='EDTA blood collected',
        blank=True, null=True,
        max_length=200)
    date_dna_extracted = models.CharField(blank=True, null=True,
                                          max_length=200)
    information        = models.CharField(blank=True, null=True,
                                          max_length=200)
    assayno            = models.CharField(blank=True, null=True,
                                          max_length=200)
    assay_date         = models.DateField(blank=True, null=True)
    blood_taken        = models.DateField(blank=True, null=True)
    blood_tm           = models.DateField(blank=True, null=True)
    report_dt          = models.DateField(blank=True, null=True)
    report_st          = models.DateField(blank=True, null=True)
    store              = models.CharField(blank=True, null=True,
                                          max_length=200)
    exposure           = models.CharField(blank=True, null=True,
                                          max_length=200)
    antigen_date       = models.DateField(blank=True, null=True)
    antigen_type       = models.CharField(blank=True, null=True,
                                          max_length=200)
    comment            = models.TextField(blank=True, null=True)
    batches            = models.TextField(blank=True, null=True)
    room               = models.TextField(blank=True, null=True)
    freezer            = models.TextField(blank=True, null=True)
    shelf              = models.TextField(blank=True, null=True)
    tray               = models.TextField(blank=True, null=True)
    vials              = models.TextField(blank=True, null=True)


class BloodBookResult(EpisodeSubrecord):
    result = models.CharField(blank=True, null=True, max_length=200)
    allergen   = models.CharField(blank=True, null=True, max_length=200)
    antigenno  = models.CharField(blank=True, null=True, max_length=200)
    kul        = models.CharField(blank=True, null=True, max_length=200)
    klass      = models.CharField(blank=True, null=True, max_length=200)
    rast       = models.CharField(blank=True, null=True, max_length=200)
    precipitin = models.CharField(blank=True, null=True, max_length=200)
    igg        = models.CharField(blank=True, null=True, max_length=200)
    iggclass   = models.CharField(blank=True, null=True, max_length=200)


"""
Existing form/fields:

[SURNAME]        [FIRSTNAME]
[BIRTH]          [Hosp_no]
[Referrername]   [Referrerttl]        [REFERENCE NO]
[Employer]       [INFORMATION]        [STORE]
[OH Provider]

[BLOODNO]        [BLOODDAT]           [ANTIGENDAT]
[ASSAYNO]        [BLOODTK]
[ASSAYDATE]      [BLOODTM]
[EXPOSURE]       [METHOD]
[ANTIGENTYP]

[ALLERGEN1..10]			Text (100),
[ANTIGENNO1..10]			Text (100),
[KUL1..10]			Text (100),
[CLASS1..10]			Text (100),
[RAST1..10]			Double,
[precipitin1..10]			Text (100),
[igg1..10]			Text (100),
[iggclass1..10]			Text (100),

    [RESULT1]			Text (200),
    [RESULT2]			Text (200),
    [RESULT3]			Text (200),
    [RESULT4]			Text (200),
    [RESULT5]			Text (200),
    [RESULT6]			Text (200),
    [RESULT7]			Text (100),
    [RESULT8]			Text (100),
    [RESULT9]			Text (100),
    [RESULT10]			Text (100),


# Unknown fields

    [EDTA blood collected]			Text (100),
    [Date DNA extracted]			Double,
    [REPORTDT]			DateTime,
    [REPORTST]			DateTime,
    [Comment]			Text (510),
    [Batches]			Text (510),
    [Room]			Text (510),
    [Freezer]			Text (510),
    [Shelf]			Text (510),
    [Tray]			Text (510),
    [Vials]			Text (510)

"""

"""

Peak Flow DB

"""


class PeakFlowIdentifier(PatientSubrecord):
    MALE = "Male"
    FEMALE = "Female"

    SEX = (
        (MALE, MALE,), (FEMALE, FEMALE,),
    )
    patient = models.ForeignKey(
        Patient, blank=True, null=True, on_delete=models.CASCADE
    )
    occmedno = models.IntegerField(unique=True, blank=True, null=True)
    height = models.IntegerField()
    sex = models.CharField(max_length=256, choices=SEX)
    name = models.CharField(max_length=256)
    company = models.CharField(max_length=256)
    hospital_number = models.CharField(max_length=256, blank=True, null=True)

    def trials(self):
        return OccTrial.objects.filter(occmedno=self.occmedno)

    def trial_days(self):
        return OccTrialDay.objects.filter(occmedno=self.occmedno)


class OccTrialDay(models.Model):
    DRUG_MAPPING = {
        0: None,
        1: "Only",
        2: "Beta",
        3: "Oral Steroid",
        4: "Other"
    }

    patient = models.ForeignKey(
        Patient, blank=True, null=True, on_delete=models.CASCADE
    )
    occmedno = models.IntegerField()
    trial_num = models.IntegerField()
    drug_code = models.IntegerField()
    work_start = models.IntegerField()
    work_finish = models.IntegerField()
    day_num = models.IntegerField()
    published = models.BooleanField()
    flow_0000 = models.IntegerField(verbose_name="00:00")
    flow_0100 = models.IntegerField(verbose_name="01:00")
    flow_0200 = models.IntegerField(verbose_name="02:00")
    flow_0300 = models.IntegerField(verbose_name="03:00")
    flow_0400 = models.IntegerField(verbose_name="04:00")
    flow_0500 = models.IntegerField(verbose_name="05:00")
    flow_0600 = models.IntegerField(verbose_name="06:00")
    flow_0700 = models.IntegerField(verbose_name="07:00")
    flow_0800 = models.IntegerField(verbose_name="08:00")
    flow_0900 = models.IntegerField(verbose_name="09:00")
    flow_1000 = models.IntegerField(verbose_name="10:00")
    flow_1100 = models.IntegerField(verbose_name="11:00")
    flow_1200 = models.IntegerField(verbose_name="12:00")
    flow_1300 = models.IntegerField(verbose_name="13:00")
    flow_1400 = models.IntegerField(verbose_name="14:00")
    flow_1500 = models.IntegerField(verbose_name="15:00")
    flow_1600 = models.IntegerField(verbose_name="16:00")
    flow_1700 = models.IntegerField(verbose_name="17:00")
    flow_1800 = models.IntegerField(verbose_name="18:00")
    flow_1900 = models.IntegerField(verbose_name="19:00")
    flow_2000 = models.IntegerField(verbose_name="20:00")
    flow_2100 = models.IntegerField(verbose_name="21:00")
    flow_2200 = models.IntegerField(verbose_name="22:00")
    flow_2300 = models.IntegerField(verbose_name="23:00")

    class Meta:
        unique_together = (
            ('trial_num', 'occmedno', 'day_num', 'published',),
        )

    @property
    def drug(self):
        return self.DRUG_MAPPING.get(self.drug_code)

    @property
    def is_work_day(self):
        if self.work_start and self.work_finish:
            return True
        return False

    def save(self, *args, **kwargs):
        if not self.patient_id:
            pfi = PeakFlowIdentifier.objects.filter(
                occmedno=self.occmedno
            ).first()
            if pfi:
                self.patient = pfi.patient
        super().save(*args, **kwargs)


class OccTrial(models.Model):
    patient = models.ForeignKey(
        Patient, blank=True, null=True, on_delete=models.CASCADE
    )
    trial_id = models.IntegerField()
    occmedno = models.IntegerField()
    trial_num = models.IntegerField()
    trial_days = models.IntegerField()
    start_date = models.DateField()
    trial_deleted = models.BooleanField()

    class Meta:
        unique_together = (
            ('trial_id', 'occmedno', 'trial_num', 'trial_deleted',),
        )

    def save(self, *args, **kwargs):
        if not self.patient_id:
            pfi = PeakFlowIdentifier.objects.filter(
                occmedno=self.occmedno
            ).first()
            if pfi:
                self.patient = pfi.patient
        super().save(*args, **kwargs)
