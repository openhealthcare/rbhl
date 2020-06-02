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
    age = models.IntegerField(blank=True, null=True)


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
    referral_reason = models.TextField(blank=True, null=True)
    fire_service_applicant = models.TextField(null=True, blank=True)
    systems_presenting_compliant = models.TextField(null=True, blank=True)
    referral_disease = models.TextField(null=True, blank=True)
    geographical_area = models.TextField(null=True, blank=True)
    geographical_area_other = models.TextField(null=True, blank=True)
    site_of_clinic = models.TextField(null=True, blank=True)
    other_clinic_site = models.TextField(null=True, blank=True)
    clinic_status = models.TextField(null=True, blank=True)
    previous_atopic_disease = models.TextField(null=True, blank=True)
    has_asthma = models.NullBooleanField(null=True, blank=True)
    has_hayfever = models.NullBooleanField(null=True, blank=True)
    has_eczema = models.NullBooleanField(null=True, blank=True)
    is_smoker = models.TextField(null=True, blank=True)
    smokes_per_day = models.IntegerField(null=True, blank=True)


class SuspectOccupationalCategory(PatientSubrecord):
    _is_singleton = True

    # UI Field: Currently Employed?
    is_currently_employed = models.NullBooleanField(null=True, blank=True)
    # UI Field: Suspect occupation Category
    suspect_occupational_category = models.TextField(null=True, blank=True)
    # UI Field: Job Title
    job_title = models.TextField(null=True, blank=True)
    # UI Field: Exposures
    exposures = models.TextField(null=True, blank=True)
    # UI Field: Name of Employer
    employer_name = models.TextField(null=True, blank=True)
    # UI Field: Currently employed in suspect occupation
    is_employed_in_suspect_occupation = models.TextField(null=True, blank=True)
    # UI Field: Date started Exposure -> Month
    year_started_exposure = models.TextField(null=True, blank=True)
    # UI Field: Date started Exposure -> Year
    month_started_exposure = models.TextField(null=True, blank=True)
    # UI Field: Date finished exposure -> Month
    year_finished_exposure = models.TextField(null=True, blank=True)
    # UI Field: Date finished exposure -> Year
    month_finished_exposure = models.TextField(null=True, blank=True)


class DiagnosticTesting(PatientSubrecord):
    _is_singleton = True

    # UI Field: Antihistimines
    antihistimines = models.NullBooleanField(null=True, blank=True)
    # UI Field: SkinPrick test
    skin_prick_test = models.NullBooleanField(null=True, blank=True)
    # UI Field: Atopic
    atopic = models.TextField(null=True, blank=True)
    # UI Field: SpecificSkinPrick
    specific_skin_prick = models.NullBooleanField(null=True, blank=True)
    # UI Field: Serum antibodies
    serum_antibodies = models.NullBooleanField(null=True, blank=True)
    # UI Field: BronchialProvTest
    bronchial_prov_test = models.NullBooleanField(null=True, blank=True)
    # UI Field: ChangePC20
    change_pc_20 = models.TextField(null=True, blank=True)
    # UI Field: NasalProvTest
    nasal_prov_test = models.NullBooleanField(null=True, blank=True)
    # UI Field: PositiveReaction
    positive_reaction = models.NullBooleanField(null=True, blank=True)
    # UI Field: Height
    height = models.TextField(null=True, blank=True)
    # UI Field: FEV1
    fev_1 = models.FloatField(null=True, blank=True)
    # UI Field: FEV1PostVentolin
    fev_1_post_ventolin = models.FloatField(null=True, blank=True)
    # UI Field: FEV1 %predicted
    fev_1_percentage_protected = models.IntegerField(null=True, blank=True)
    # UI Field: FVC
    fvc = models.FloatField(null=True, blank=True)
    # UI Field: FVCPostVentolin
    fvc_post_ventolin = models.FloatField(null=True, blank=True)
    # UI Field: FVC &predicted
    fvc_percentage_protected = models.IntegerField(null=True, blank=True)
    # UI Field: Serail peak flows requested?
    is_serial_peak_flows_requested = models.NullBooleanField(
        null=True, blank=True,
    )
    # UI Field: SPEFR Variability?
    has_spefr_variability = models.TextField(null=True, blank=True)
    # UI Field: Returned?
    is_returned = models.TextField(null=True, blank=True)
    # UI Field: SPEFR work related?
    is_spefr_work_related = models.TextField(null=True, blank=True)

    # TODO: combine?
    # UI Field: CTChestScan
    ct_chest_scan = models.NullBooleanField(null=True, blank=True)
    # UI Field: Date
    ct_chest_scan_date = models.DateTimeField(null=True, blank=True)

    # TODO: combine?
    # UI Field: Full lung function
    full_lung_function = models.NullBooleanField(null=True, blank=True)
    # UI Field: Date
    full_lung_function_date = models.DateTimeField(null=True, blank=True)


class DiagnosticOutcome(PatientSubrecord):
    _is_singleton = True

    # UI Field: Diagnosis
    diagnosis = models.TextField(null=True, blank=True)
    # UI Field: Date of Diagnosis
    diagnosis_date = models.DateTimeField(null=True, blank=True)
    # UI Field: If referred, who to?
    referred_to = models.TextField(null=True, blank=True)


class DiagnosticAsthma(PatientSubrecord):
    _is_singleton = True

    # UI Field: Asthma
    asthma = models.NullBooleanField(null=True, blank=True)
    # UI Field: Exacerbated by work
    is_exacerbated_by_work = models.NullBooleanField(null=True, blank=True)
    # UI Field: Irritant induced asthma
    has_infant_induced_asthma = models.NullBooleanField(null=True, blank=True)
    # UI Field: Occupational asthma caused by sensitisation
    occupational_asthma_caused_by_sensitisation = models.NullBooleanField(
        null=True, blank=True
    )
    # UI Field: Sensitising agent
    sensitising_agent = models.TextField(null=True, blank=True)
    # UI Field: Non-Occupational Asthma
    has_non_occupational_asthma = models.NullBooleanField(
        null=True, blank=True
    )


class DiagnosticRhinitis(PatientSubrecord):
    _is_singleton = True

    # Rhinitis
    rhinitis = models.NullBooleanField(null=True, blank=True)
    # Work exacerbated
    work_exacerbated = models.NullBooleanField(null=True, blank=True)
    # Occupation rhinitis caused by sensitization
    occupational_rhinitis_caused_by_sensitisation = models.NullBooleanField(
        null=True, blank=True,
    )
    # RhinitisOccSenCause
    rhinitis_occupational_sensitisation_cause = models.TextField(
        null=True, blank=True,
    )
    # Non-Occupational Rhinitis
    has_non_occupational_rhinitis = models.NullBooleanField(
        null=True, blank=True,
    )


class DiagnosticOther(PatientSubrecord):
    _is_singleton = True

    # UI Field: COPD
    copd = models.NullBooleanField(null=True, blank=True)
    # UI Field: Emphysema
    emphysema = models.NullBooleanField(null=True, blank=True)
    # UI Field: COPD with emphysema
    copd_with_emphysema = models.NullBooleanField(null=True, blank=True)
    # UI Field: Occupational
    copd_is_occupational = models.NullBooleanField(null=True, blank=True)
    # UI Field: Malignancy
    malignancy = models.NullBooleanField(null=True, blank=True)
    # UI Field: Occupational
    malignancy_is_occupational = models.NullBooleanField(null=True, blank=True)
    # UI Field: Type of malignancy
    malignancy_type = models.TextField(null=True, blank=True)
    # UI Field: If other, please specify
    malignancy_type_other = models.TextField(null=True, blank=True)
    # UI Field: NAD
    NAD = models.NullBooleanField(null=True, blank=True)
    # UI Field: Diffuse lung disease
    diffuse_lung_disease = models.NullBooleanField(null=True, blank=True)
    # UI Field: Occupational
    diffuse_lung_disease_is_occupational = models.NullBooleanField(
        null=True, blank=True
    )
    # UI Field: Type of disease
    diffuse_lung_disease_type = models.TextField(null=True, blank=True)
    # UI Field: If other, please specify
    diffuse_lung_disease_type_other = models.TextField(null=True, blank=True)
    # UI Field: Benign pleural disease
    benign_pleural_disease = models.NullBooleanField(null=True, blank=True)
    # UI Field: Type of disease
    benign_pleural_disease_type = models.TextField(null=True, blank=True)
    # UI Field: Other diagnosis
    other_diagnosis = models.NullBooleanField(null=True, blank=True)
    # UI Field: Occupational
    other_diagnosis_is_occupational = models.NullBooleanField(
        null=True, blank=True,
    )
    # UI Field: Type of disease
    other_diagnosis_type = models.TextField(null=True, blank=True)
    # UI Field: If other, please specify
    other_diagnosis_type_other = models.TextField(null=True, blank=True)


class LegacySkinPrickTest(PatientSubrecord):
    specific_sp_testnum = models.IntegerField(null=True, blank=True)
    spt = models.TextField(null=True, blank=True)
    wheal = models.FloatField(null=True, blank=True)
    test_date = models.DateTimeField(null=True, blank=True)


class OtherFields(PatientSubrecord):
    _is_singleton = True

    other_det_num = models.TextField(null=True, blank=True)
    attendance_date = models.TextField(null=True, blank=True)
    referral = models.TextField(null=True, blank=True)
    reason_other = models.TextField(null=True, blank=True)
    occupation_other = models.TextField(null=True, blank=True)
    asthma_relate_work = models.TextField(null=True, blank=True)
    chronic_air_flow = models.TextField(null=True, blank=True)
    chronic_air_flow_choice = models.TextField(null=True, blank=True)
    chronic_obstructive_brinchitis = models.TextField(null=True, blank=True)


class LegacyBronchialTest(PatientSubrecord):
    # UI Field: ???
    bronchial_num = models.IntegerField(null=True, blank=True)
    # UI Field: Substance
    substance = models.TextField(null=True, blank=True)
    # UI Field: Last_exposed
    last_exposed = models.DateTimeField(null=True, blank=True)
    # UI Field: Duration_exposure
    duration_exposed = models.TextField(null=True, blank=True)
    # UI Field: Date Challenge started
    date_of_challenge = models.DateTimeField(null=True, blank=True)
    # UI Field: Type
    foo = models.TextField(null=True, blank=True)
    # UI Field: Response (?)
    other_type = models.TextField(null=True, blank=True)
    # UI Field: Other
    other = models.TextField(null=True, blank=True)
    # UI Field: BaselinePC20
    baseline_pc290 = models.TextField(null=True, blank=True)
    # UI Field: LowestPC20
    lowest_pc20 = models.TextField(null=True, blank=True)


class RoutineSPT(PatientSubrecord):
    neg_control = models.FloatField(null=True, blank=True)
    pos_control = models.FloatField(null=True, blank=True)
    asp_fumigatus = models.FloatField(null=True, blank=True)
    grass_pollen = models.FloatField(null=True, blank=True)
    cat = models.FloatField(null=True, blank=True)
    d_pter = models.FloatField(null=True, blank=True)
