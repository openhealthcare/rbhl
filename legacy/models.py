"""
Models for the RBH legacy transition
"""
from django.db import models
from opal.models import PatientSubrecord, EpisodeSubrecord


"""
18 WEEK DB
"""


class ActionLog(EpisodeSubrecord):
    class Meta:
        verbose_name = 'General notes'
    # Now in rbhl.models.Employment
    # employer       = models.CharField(blank=True, null=True, max_length=100)
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
    occmendo = models.IntegerField(blank=True, null=True)


class GP(PatientSubrecord):
    _is_singleton = True

    name = models.TextField()
    address = models.TextField(null=True)
    post_code = models.TextField(null=True)


class PatientNumber(PatientSubrecord):
    _is_singleton = True

    value = models.TextField(null=True)


class Address(PatientSubrecord):
    _is_singleton = True

    address = models.TextField(null=True)
    telephone = models.TextField(null=True)
