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


class Details(PatientSubrecord):
    _is_singleton = True

    date_referral_received = models.DateTimeField(null=True, blank=True)
    referral_type = models.TextField(null=True, blank=True)
    fire_service_applicant = models.TextField(null=True, blank=True)
    systems_presenting_compliant = models.TextField(null=True, blank=True)
    referral_disease = models.TextField(null=True, blank=True)
    geographical_area = models.TextField(null=True, blank=True)
    geographical_area_other = models.TextField(null=True, blank=True)
    site_of_clinic = models.TextField(null=True, blank=True)
    other_clinic_site = models.TextField(null=True, blank=True)
    clinic_status = models.TextField(null=True, blank=True)
    seen_by_dr = models.TextField(null=True, blank=True)
    previous_atopic_disease = models.TextField(null=True, blank=True)
    has_asthma = models.NullBooleanField(null=True, blank=True)
    has_hayfever = models.NullBooleanField(null=True, blank=True)
    has_eczema = models.NullBooleanField(null=True, blank=True)
    is_smoker = models.TextField(null=True, blank=True)
    smokes_per_day = models.IntegerField(null=True, blank=True)


class SuspectOccupationalCategory(PatientSubrecord):
    _is_singleton = True

    is_currently_employed = models.NullBooleanField(null=True, blank=True)
    suspect_occupational_category = models.TextField(null=True, blank=True)
    job_title = models.TextField(null=True, blank=True)
    exposures = models.TextField(null=True, blank=True)
    employer_name = models.TextField(null=True, blank=True)
    is_employed_in_suspect_occupation = models.TextField(null=True, blank=True)
    year_started_exposure = models.TextField(null=True, blank=True)
    month_started_exposure = models.TextField(null=True, blank=True)
    year_finished_exposure = models.TextField(null=True, blank=True)
    month_finished_exposure = models.TextField(null=True, blank=True)


class DiagnosticTesting(PatientSubrecord):
    _is_singleton = True

    antihistimines = models.NullBooleanField(null=True, blank=True)
    skin_prick_test = models.NullBooleanField(null=True, blank=True)
    atopic = models.TextField(null=True, blank=True)
    specific_skin_prick = models.NullBooleanField(null=True, blank=True)
    serum_antibodies = models.NullBooleanField(null=True, blank=True)
    bronchial_prov_test = models.NullBooleanField(null=True, blank=True)
    change_pc_20 = models.TextField(null=True, blank=True)
    nasal_prov_test = models.NullBooleanField(null=True, blank=True)
    positive_reaction = models.NullBooleanField(null=True, blank=True)
    height = models.TextField(null=True, blank=True)
    fev_1 = models.FloatField(null=True, blank=True)
    fev_1_post_ventolin = models.FloatField(null=True, blank=True)
    fev_1_percentage_protected = models.IntegerField(null=True, blank=True)
    fvc = models.FloatField(null=True, blank=True)
    fvc_post_ventolin = models.FloatField(null=True, blank=True)
    fvc_percentage_protected = models.IntegerField(null=True, blank=True)
    is_serial_peak_flows_requested = models.TextField(null=True, blank=True)
    has_spefr_variability = models.TextField(null=True, blank=True)
    is_returned = models.TextField(null=True, blank=True)
    is_spefr_work_related = models.TextField(null=True, blank=True)

    # TODO: combine?
    ct_chest_scan = models.NullBooleanField(null=True, blank=True)
    ct_chest_scan_date = models.DateTimeField(null=True, blank=True)

    # TODO: combine?
    full_lung_function = models.NullBooleanField(null=True, blank=True)
    full_lung_function_date = models.TextField(null=True, blank=True)


class DiagnosticOutcome(PatientSubrecord):
    _is_singleton = True

    diagnosis = models.TextField(null=True, blank=True)
    diagnosis_date = models.DateTimeField(null=True, blank=True)
    referred_to = models.TextField(null=True, blank=True)


class DiagnosticAsthma(PatientSubrecord):
    _is_singleton = True

    asthma = models.NullBooleanField(null=True, blank=True)
    is_exacerbated_by_work = models.NullBooleanField(null=True, blank=True)
    has_infant_induced_asthma = models.NullBooleanField(null=True, blank=True)
    occupational_asthma_caused_by_sensitisation = models.NullBooleanField(
        null=True, blank=True
    )
    sensitising_agent = models.TextField(null=True, blank=True)
    has_non_occupational_asthma = models.NullBooleanField(
        null=True, blank=True
    )


class DiagnosticRhinitis(PatientSubrecord):
    _is_singleton = True

    rhinitis = models.NullBooleanField(null=True, blank=True)
    work_exacerbated = models.NullBooleanField(null=True, blank=True)
    occupational_rhinitis_caused_by_sensitisation = models.NullBooleanField(
        null=True, blank=True,
    )
    rhinitis_occupational_sensitisation_cause = models.TextField(
        null=True, blank=True,
    )
    has_non_occupational_rhinitis = models.NullBooleanField(
        null=True, blank=True,
    )


class DiagnosticOther(PatientSubrecord):
    _is_singleton = True

    copd = models.NullBooleanField(null=True, blank=True)
    emphysema = models.NullBooleanField(null=True, blank=True)
    copd_with_emphysema = models.NullBooleanField(null=True, blank=True)
    copd_is_occupational = models.NullBooleanField(null=True, blank=True)
    malignancy = models.NullBooleanField(null=True, blank=True)
    malignancy_is_occupational = models.NullBooleanField(null=True, blank=True)
    malignancy_type = models.TextField(null=True, blank=True)
    malignancy_type_other = models.TextField(null=True, blank=True)
    NAD = models.NullBooleanField(null=True, blank=True)
    diffuse_lung_disease = models.NullBooleanField(null=True, blank=True)
    diffuse_lung_disease_is_occupational = models.NullBooleanField(
        null=True, blank=True
    )
    diffuse_lung_disease_type = models.TextField(null=True, blank=True)
    diffuse_lung_disease_type_other = models.TextField(null=True, blank=True)
    benign_pleural_disease = models.NullBooleanField(null=True, blank=True)
    benign_pleural_disease_type = models.TextField(null=True, blank=True)
    other_diagnosis = models.NullBooleanField(null=True, blank=True)
    other_diagnosis_is_occupational = models.NullBooleanField(
        null=True, blank=True,
    )
    other_diagnosis_type = models.TextField(null=True, blank=True)
    other_diagnosis_type_other = models.TextField(null=True, blank=True)


class SkinPrickTest(PatientSubrecord):
    specific_sp_testnum = models.IntegerField(null=True, blank=True)
    spt = models.TextField(null=True, blank=True)
    wheal = models.FloatField(null=True, blank=True)
    test_date = models.DateTimeField(null=True, blank=True)


class OtherFields(PatientSubrecord):
    _is_singleton = True

    other_det_num = models.TextField(null=True, blank=True)
    attendance_date = models.TextField(null=True, blank=True)
    specialist_doctor = models.TextField(null=True, blank=True)
    referral = models.TextField(null=True, blank=True)
    reason_other = models.TextField(null=True, blank=True)
    occupation_other = models.TextField(null=True, blank=True)
    ige_results = models.TextField(null=True, blank=True)
    serum_results_num = models.TextField(null=True, blank=True)
    ssp_test_num = models.TextField(null=True, blank=True)
    serial_perf = models.TextField(null=True, blank=True)
    perf_variability = models.TextField(null=True, blank=True)
    perf_work_relate = models.TextField(null=True, blank=True)
    outcome_num = models.TextField(null=True, blank=True)
    full_pul_fun_test = models.TextField(null=True, blank=True)
    lft_date = models.TextField(null=True, blank=True)
    asthma_relate_work = models.TextField(null=True, blank=True)
    chronic_air_flow = models.TextField(null=True, blank=True)
    chronic_air_flow_choice = models.TextField(null=True, blank=True)
    chronic_obstructive_brinchitis = models.TextField(null=True, blank=True)
    exposure_dates = models.TextField(null=True, blank=True)
    bronch_prov_test_type = models.TextField(null=True, blank=True)


class BronchialTest(PatientSubrecord):
    bronchial_num = models.IntegerField(null=True, blank=True)
    substance = models.TextField(null=True, blank=True)
    last_exposed = models.DateTimeField(null=True, blank=True)
    duration_exposed = models.TextField(null=True, blank=True)
    date_of_challenge = models.DateTimeField(null=True, blank=True)
    foo = models.TextField(null=True, blank=True)
    other_type = models.TextField(null=True, blank=True)
    other = models.TextField(null=True, blank=True)
    baseline_pc290 = models.TextField(null=True, blank=True)
    lowest_pc20 = models.TextField(null=True, blank=True)


class RoutineSPT(PatientSubrecord):
    neg_control = models.FloatField(null=True, blank=True)
    pos_control = models.FloatField(null=True, blank=True)
    asp_fumigatus = models.FloatField(null=True, blank=True)
    grass_pollen = models.FloatField(null=True, blank=True)
    cat = models.FloatField(null=True, blank=True)
    d_pter = models.FloatField(null=True, blank=True)
