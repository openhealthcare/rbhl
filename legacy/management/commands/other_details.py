import csv
from django.core.management import BaseCommand
from django.db import transaction
from django.utils import timezone

from opal import models as opal_models
from rbhl import models
from plugins.lab import models as lab_models

from legacy.models import (
    Details,
    DiagnosticAsthma,
    DiagnosticOther,
    DiagnosticOutcome,
    DiagnosticRhinitis,
    DiagnosticTesting,
    OtherFields,
    PatientNumber,
    SuspectOccupationalCategory,
)

from ..utils import to_bool, to_date, to_float, to_int, to_upper


sensitivies_translation = {
    ("Rats",): (
        "animals (rats)", "rat", 'animals - rats', '(rats)', 'animals rats',
        'rats'
    ),
    ("Mice",): (
        "mouse", 'animals mice', 'animals (mice)', 'animals - mice', '(mice)',
        'animals- mice', '(mouse)', 'animals (mouse)', 'animals (mice)',
        'mice'
    ),
    ("Rats", "Mice",): (
        'animals rats & mice', 'rats & mice', 'animals - rats & mice',
        'rat /mouse', 'animals rats and mice', '-rats & mice', 'rats and dogs',
        '(rats & mice)', 'mice/rat', 'animals - rat and mouse',
        'animals (rats & mice)', 'animals rat & mouse',
        'animals- mice and rats', 'rat and  mouse', 'rat/mouse',
        'mouse & rat', '(rat & mouse)', 'animals (rat or mouse)'
        'rat and mouse', 'animals rats and mice', 'animals rats & mice',
        'rats and mice'
    ),
    ("Amylase",): [
        'enzymes - alpha amylase',
        'enzymes - other (alpha amylase)',
        'enzymes - other - alpha amylase',
        'enzymes -alpha amylase',
        'enzymes - (alpha amylase)',
        'enzymes - other(alpha amylase)',
        'enzymes - other alpha amylase',
        '(alpha amylase)',
        'enzymes  (alpha amylase)',
        'enzymes - other, alpha amylase',
        'enzymes alpha amylase',
        "enzymes - other (amylase)",
        "enzymes - amylase",
        "(amylase)",
        "enzymes - (amylase)",
        '(bakers amylase)',
        'enzymes - (bakers amylase)',
        '( bakers amylase)',
        'enzymes -(bakers amylase)',
        'enzymes -bakers amylase',
        'enzymes - bakers amylase',
        "enzymes - other (bakers amylase)",
        'enzymes - bakers amylase'
        'amylase',
    ],
    ("Morphine",): [
        '-morphine',
        '(morphine)',
        'pharmaceuticals - morphine',
        'morphine'
    ],
    ('Grain / Flour',): [
        "grain/flour"
    ]
}


def clean_sensitivies(sensitivities):
    stripped = [
        i.strip() for i in sensitivities.split("\n") if i.strip()
    ]

    cleaned = []

    for row in stripped:
        translated = sensitivies_translation.get(row.lower())
        if translated:
            cleaned.extend(translated)
        else:
            cleaned.append(row)

    return "\n".join(sorted(cleaned))


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("file_name", help="Specify import file")

    def build_details(self, patientLUT, rows):

        for row in rows:

            patient = patientLUT.get(row["Patient_details.Patient_num"], None)

            if patient is None:
                continue

            date_referral_received = to_date(row["Date referral written"])

            yield Details(
                patient=patient,
                created=timezone.now(),
                date_referral_received=date_referral_received,
                referral_type=row["referral"],
                referral_reason=row["Referral_reason"],
                fire_service_applicant=row["Fireapplicant"],
                systems_presenting_compliant=row["reason_other"],
                referral_disease=row["Referral_disease"],
                geographical_area=row["Geographical_area"],
                geographical_area_other=row["Geographical_other"],
                site_of_clinic=row["Site of Clinic"],
                other_clinic_site=row["Other Clinic Site"],
                clinic_status=row["Clinic_status"],
                previous_atopic_disease=row["AtopicDisease"],
                has_asthma=to_bool(row["Asthma"]),
                has_hayfever=to_bool(row["Hayfever"]),
                has_eczema=to_bool(row["Eczema"]),
                is_smoker=row["Smoker"],
                smokes_per_day=to_int(row["No_cigarettes"]),
            )

    def convert_details(self, patient):
        """
        Maps
        Details.date_referral_received" -> Referral.date_referral_received
        OtherFields.attendance_date -> Referral.date_first_appointment
        Details.referral_type -> Referral.referral_type
        Details.referral_reason -> Referral.referral_reason
        Details.fire_service_applicant -> Employment.firefighter
        Details.systems_presenting_compliant ->     Referral.referral_reason
        Details.referral_disease -> Referral.referral_disease
        Details.specialist_doctor -> ClinicLog.seen_by
        Details.geographical_area or Details.geographical_area_other ->
            Referral.geographical_area
        Details.is_smoker = SocialHistory.smoker
        Details.smokes_per_day = SocialHistory.cigarettes_per_day
        """
        episode = patient.episode_set.first()
        details = patient.details_set.all()[0]
        if not details:
            return
        clinic_log = episode.cliniclog_set.all()[0]

        if details and details.site_of_clinic:
            if details.site_of_clinic == "Other":
                clinic_log.clinic_site = details.site_of_clinic
            else:
                clinic_log.clinic_site = details.other_clinic_site
            clinic_log.save()

        referral = episode.referral_set.all()[0]
        referral_received = referral.date_referral_received

        # agreed with the client, as there are patients that
        # have rereferrals, always use the most recent.
        if referral_received:
            if details.date_referral_received:
                referral.date_referral_received = max(
                    referral_received, details.date_referral_received.date()
                )
        else:
            referral.date_referral_received = details.date_referral_received

        referral.referral_reason = details.systems_presenting_compliant

        if not referral.referral_reason:
            referral.referral_reason = details.referral_reason

        referral_disease = details.referral_disease
        # this is a strangely common error
        if referral_disease == "Pulmonary fibrosis(eg: Asbestos related disease":
            referral_disease = "Pulmonary fibrosis(e.g.: Asbestos related disease)"
        if referral_disease == "Pulmonary fibrosis(eg: Asbestos related disease)":
            referral_disease = "Pulmonary fibrosis(e.g.: Asbestos related disease)"

        if referral_disease == "Asthma/Rhinitis":
            referral_disease = "Asthma / Rhinitis"
        referral.referral_disease = referral_disease

        if not referral.referral_source and details.referral_type:
            remap = {
                'Company or Group OHS doctor': 'Occupational health doctor or nurse',
                'GP': 'GP',
                'Hospital Doctor(Brompton)': 'RBH doctor',
                'Dept social security': 'Other',
                'Medico-legal': 'Medico legal',
                'Hospital Doctor(Other)': 'Other hospital doctor',
                'Employment medical advisory service':
                    'Occupational health doctor or nurse',
                'Other doctor': 'Other hospital doctor',
                'self': 'Self',
                'Occ Health': 'Occupational health doctor or nurse',
                'Other (self)': 'Self',
                'Company or Group OHS nurse': 'Occupational health doctor or nurse',
                'Self': 'Self',
                'resp nurse community': 'Other',
                'Other doctor- GP': 'GP',
            }

            referral_source = details.referral_type
            if referral_source:
                referral.referral_source  = remap[referral_source]

        area = details.geographical_area
        if area:
            if area == "SouthThames":
                area = "South Thames"
            elif area == "North thames":
                area = "North Thames"
            elif area.lower() == "other" and details.geographical_area_other:
                area = details.geographical_area_other
            referral.geographical_area = area

        if not referral.date_first_appointment:
            other_fields = patient.otherfields_set.all()[0]
            if other_fields.attendance_date_as_date():
                referral.date_first_appointment = other_fields.attendance_date_as_date()

        referral.save()

        employment = episode.employment_set.all()[0]
        if employment.firefighter is None:
            fsa = details.fire_service_applicant
            if fsa:
                fire_service_lut = {"no": False, "yes": True}
                employment.firefighter = fire_service_lut.get(fsa.lower())
                employment.save()

        social_history = episode.socialhistory_set.all()[0]
        if not social_history.smoker:
            if details.is_smoker:
                if details.is_smoker == "Current":
                    social_history.smoker = "Currently"
                else:
                    social_history.smoker = details.is_smoker

        if not social_history.cigarettes_per_day:
            if details.smokes_per_day:
                social_history.cigarettes_per_day = details.smokes_per_day
        social_history.save()

    def build_suspect_occupational_category(self, patientLUT, rows):
        for row in rows:
            patient = patientLUT.get(row["Patient_details.Patient_num"], None)

            if patient is None:
                continue

            def get_year(some_str):
                if some_str and len(some_str) == 2:
                    as_int = int(some_str)
                    if as_int < 21:
                        return "20{}".format(some_str)
                    else:
                        return "19{}".format(some_str)
                return some_str

            def none_if_0(some_str):
                if some_str == 0:
                    return
                return some_str

            yield SuspectOccupationalCategory(
                patient=patient,
                created=timezone.now(),
                is_currently_employed=to_bool(row["Employed"]),
                suspect_occupational_category=row["Occupation_category"],
                job_title=row["Occupation_other"],
                exposures=row["Exposures"],
                is_employed_in_suspect_occupation=row["Current_employment"],
                month_started_exposure=none_if_0(row["Date started"]),
                year_started_exposure=get_year(none_if_0(row["Dates_st_Exposure_Y"])),
                month_finished_exposure=none_if_0(row["Date Finished"]),
                year_finished_exposure=get_year(none_if_0(row["Dates_f_Exposure_Y"])),
            )

    def convert_suspect_occupational_category(self, patient):
        """
        Maps
        SuspectOccupationalCategory.job_title
            -> Employment.job_title
        SuspectOccupationalCategory.employer_name
            -> Employment.employer
        SuspectOccupationalCategory.suspect_occupational_category
            -> Employment.employment_category
        SuspectOccupationalCategory.is_employed_in_suspect_occupation
            -> Employment.employed_in_suspect_occupation
        SuspectOccupationalCategory.exposures
            -> Employment.exposures
        """
        suspect_occupational_category = patient.suspectoccupationalcategory_set.all()[0]
        episode = patient.episode_set.first()
        employment = episode.employment_set.all()[0]
        employment.job_title = suspect_occupational_category.job_title
        emp_cat = suspect_occupational_category.suspect_occupational_category
        employment.employment_category = emp_cat

        if not employment.employer:
            emp_name = suspect_occupational_category.employer_name
            employment.employment_category = emp_name

        sus = suspect_occupational_category.is_employed_in_suspect_occupation
        if sus and sus in [
                'Yes-employed in suspect occupation',
                'Yes'
        ]:
            employment.employed_in_suspect_occupation = True

        # exposures like sensitities contain a lot of synonyms
        # that we can clean
        exposures = clean_sensitivies(
            suspect_occupational_category.exposures
        )
        exposures = exposures.replace("Christmas trees", "")
        exposures = exposures.replace("gluteraldehyde", "")
        exposures = exposures.replace("Christmas trees", "")
        exposures = exposures.replace("Tea bloom", "")
        exposures = "\n".join([i.strip() for i in exposures.split("\n") if i.strip()])
        exposures = exposures.strip()
        employment.save()

    def build_diagnostic_testing(self, patientLUT, rows):
        for row in rows:
            patient = patientLUT.get(row["Patient_details.Patient_num"], None)

            if patient is None:
                continue

            yield DiagnosticTesting(
                patient=patient,
                created=timezone.now(),
                antihistamines=to_bool(row["Antihistimines"]),
                skin_prick_test=to_bool(row["SkinPrick_test"]),
                atopic=row["Atopic"],
                specific_skin_prick=to_bool(row["SpecificSkinPrick"]),
                serum_antibodies=to_bool(row["Serum_antibodies"]),
                bronchial_prov_test=to_bool(row["BronchialProvTest"]),
                change_pc_20=row["ChangePC20"],
                nasal_prov_test=to_bool(row["NasalProvTest"]),
                positive_reaction=to_bool(row["PositiveReaction"]),
                height=row["Height"],
                fev_1=to_float(row["FEV1"]),
                fev_1_post_ventolin=to_float(row["FEV1PostVentolin"]),
                fev_1_percentage_protected=to_int(row["FEV1%pred"]),
                fvc=to_float(row["FVCpPreVentolin"]),
                fvc_post_ventolin=to_float(row["FVCPostVentolin"]),
                fvc_percentage_protected=to_int(row["FVC%pred"]),
                is_serial_peak_flows_requested=to_bool(row["SerialPERF"]),
                has_spefr_variability=row["PERFVariablility"],
                is_returned=to_bool(row["Returned?"]),
                is_spefr_work_related=row["PERFWorkRelate"],
                ct_chest_scan=to_bool(row["CTChestScan"]),
                ct_chest_scan_date=to_date(row["CTdate"]),
                full_lung_function=to_bool(row["FullPulFunTest"]),
                full_lung_function_date=to_date(row["LFTdate"]),
            )

    def build_diagnostic_outcome(self, patientLUT, rows):
        for row in rows:
            patient = patientLUT.get(row["Patient_details.Patient_num"], None)

            if patient is None:
                continue

            yield DiagnosticOutcome(
                patient=patient,
                created=timezone.now(),
                diagnosis=row["Diagnosis"],
                diagnosis_date=to_date(row["Date of Diagnosis"]),
                referred_to=row["Diagnosis_referral"],
            )

    def convert_diagnostic_outcome(self, patient):
        """
        diagnosis -> Clinic Log.diagnosis_outcome
        referred_to -> Clinic Log.referred_to
        diagnosis date -> clinic date if not populated
        """
        episode = patient.episode_set.first()
        diagnosis_outcome = patient.diagnosticoutcome_set.all()[0]
        clinic_log = episode.cliniclog_set.all()[0]
        clinic_log.diagnosis_outcome = diagnosis_outcome.diagnosis
        clinic_log.referred_to = diagnosis_outcome.referred_to
        clinic_log.save()

    def build_diagnostic_asthma(self, patientLUT, rows):
        for row in rows:
            patient = patientLUT.get(row["Patient_details.Patient_num"], None)

            if patient is None:
                continue

            yield DiagnosticAsthma(
                patient=patient,
                created=timezone.now(),
                asthma=to_bool(row["DiagnosisAsthma"]),
                is_exacerbated_by_work=to_bool(row["AsthmaExacerbate"]),
                has_infant_induced_asthma=to_bool(row["AsthmaOccInt"]),
                occupational_asthma_caused_by_sensitisation=to_bool(
                    row["AsthmaOccSen"]
                ),
                sensitising_agent=row["AsthmaOccSenCause"],
                has_non_occupational_asthma=to_bool(row["AsthmaNonOcc"]),
            )

    def convert_to_diagnosis_asthma(self, patient):
        legacy_asthma = patient.diagnosticasthma_set.all()[0]

        if any([
            legacy_asthma.asthma,
            legacy_asthma.is_exacerbated_by_work,
            legacy_asthma.has_infant_induced_asthma,
            legacy_asthma.occupational_asthma_caused_by_sensitisation,
            legacy_asthma.has_non_occupational_asthma
        ]):
            asthma = models.AsthmaDetails(episode=patient.episode_set.first())

            asthma.sensitivities = clean_sensitivies(
                legacy_asthma.sensitising_agent
            )
            # order of priority for what overrides
            # occupational asthma caused by sensitisation > is exacerbated by work >
            # has irritant induced asthma > has non occupational asthma

            option = ""

            if legacy_asthma.occupational_asthma_caused_by_sensitisation:
                option = models.AsthmaDetails.OCCUPATIONAL_CAUSED_BY_SENSITISATION
            elif legacy_asthma.is_exacerbated_by_work:
                option = models.AsthmaDetails.EXACERBATED_BY_WORK
            elif legacy_asthma.has_infant_induced_asthma:
                option = models.AsthmaDetails.IRRITANT_INDUCED
            elif legacy_asthma.has_non_occupational_asthma:
                option = models.AsthmaDetails.NON_OCCUPATIONAL

            asthma.date = patient.diagnosticoutcome_set.all()[0].diagnosis_date
            asthma.trigger = option
            asthma.save()

    def build_diagnostic_rhinitis(self, patientLUT, rows):
        for row in rows:
            patient = patientLUT.get(row["Patient_details.Patient_num"], None)

            if patient is None:
                continue

            # FIXME: there is a single row where this field has the value "x"
            # in the data as of 2019/03/25.  The surrounding data makes it look
            # like this is a typo (since there is no surrounding data).
            RhinitisNonOcc = row["RhinitisNonOcc"]
            if RhinitisNonOcc != "x":
                has_non_occ_rhinitis = to_bool(RhinitisNonOcc)
            else:
                has_non_occ_rhinitis = None

            yield DiagnosticRhinitis(
                patient=patient,
                created=timezone.now(),
                rhinitis=to_bool(row["DiagnosisRhinitis"]),
                work_exacerbated=to_bool(row["RhinitisExacerbate"]),
                occupational_rhinitis_caused_by_sensitisation=to_bool(
                    row["RhinitisOccSen"]
                ),
                rhinitis_occupational_sensitisation_cause=row[
                    "RhinitisOccSenCause"
                ],
                has_non_occupational_rhinitis=has_non_occ_rhinitis,
            )

    def convert_to_diagnosis_rhinitis(self, patient):
        legacy_rhinitis = patient.diagnosticrhinitis_set.all()[0]

        if any([
            legacy_rhinitis.rhinitis,
            legacy_rhinitis.work_exacerbated,
            legacy_rhinitis.occupational_rhinitis_caused_by_sensitisation,
            legacy_rhinitis.has_non_occupational_rhinitis
        ]):
            rhinitis = models.RhinitisDetails(episode=patient.episode_set.first())

            # order of priority for what overrides
            # occupational_rhinitis_caused_by_sensitisation > work_exacerbated >
            # has non occupational asthma

            option = ""

            if legacy_rhinitis.occupational_rhinitis_caused_by_sensitisation:
                option = models.RhinitisDetails.OCCUPATIONAL_CAUSED_BY_SENSITISATION
            elif legacy_rhinitis.work_exacerbated:
                option = models.RhinitisDetails.EXACERBATED_BY_WORK
            elif legacy_rhinitis.has_non_occupational_rhinitis:
                option = models.RhinitisDetails.NON_OCCUPATIONAL

            rhinitis.trigger = option

            rhinitis.sensitivities = clean_sensitivies(
                legacy_rhinitis.rhinitis_occupational_sensitisation_cause
            )
            rhinitis.date = patient.diagnosticoutcome_set.all()[0].diagnosis_date
            rhinitis.save()

    def build_diagnostic_other(self, patientLUT, rows):
        for row in rows:
            patient = patientLUT.get(row["Patient_details.Patient_num"], None)

            if patient is None:
                continue

            yield DiagnosticOther(
                patient=patient,
                created=timezone.now(),
                copd=to_bool(row["ChronicAirFlow"]),
                emphysema=to_bool(row["Emphsema"]),
                copd_with_emphysema=to_bool(row["COPD&emph"]),
                # copd_is_occupational=row[""],
                malignancy=to_bool(row["Malignancy"]),
                malignancy_is_occupational=to_bool(row["MalignancyType"]),
                malignancy_type=row["MalignancyTypeChoice"],
                malignancy_type_other=row["MalignancyTypeChoiceOther"],
                NAD=to_bool(row["NAD"]),
                diffuse_lung_disease=to_bool(row["DiffuseLungDis"]),
                diffuse_lung_disease_is_occupational=to_bool(
                    row["DiffuseLungDisChoice"]
                ),
                diffuse_lung_disease_type=row["DiffuseLungDisType"],
                diffuse_lung_disease_type_other=row["DiffuseLungDisTypeOther"],
                benign_pleural_disease=to_bool(row["BenignPleuralDis"]),
                benign_pleural_disease_type=row["BenignPleuralDisType"],
                other_diagnosis=to_bool(row["OtherDiag"]),
                other_diagnosis_is_occupational=to_bool(
                    row["OtherDiagChoice"],
                ),
                other_diagnosis_type=row["OtherDiagChoiceType"],
                other_diagnosis_type_other=row["OtherDiagOther"],
            )

    def convert_to_diagnosis_other(self, patient):
        other = patient.diagnosticother_set.all()[0]
        episode = patient.episode_set.first()
        diagnosis_date = patient.diagnosticoutcome_set.all()[0].diagnosis_date
        if other.NAD:
            # As discussed with the user, in some instances of NAD
            # Diagnosis other was used as a comment field. This
            # is now added as a general note.
            if other.other_diagnosis_type_other:
                episode.actionlog_set.create(
                    general_notes="Diagnosis information: {}".format(
                        other.other_diagnosis_type_other
                    )
                )

            models.Diagnosis.objects.create(
                episode=episode,
                category=models.Diagnosis.NAD,
                date=diagnosis_date
            )
            return

        if any([
            other.copd,
            other.emphysema,
            other.copd_with_emphysema,
        ]):
            if other.copd_with_emphysema:
                models.Diagnosis.objects.create(
                    episode=episode,
                    condition="COPD",
                    category=models.Diagnosis.CHRONIC_AIR_FLOW_LIMITATION,
                    occupational=bool(other.copd_is_occupational),
                    date=diagnosis_date
                )
                models.Diagnosis.objects.create(
                    episode=episode,
                    condition="Emphysema",
                    category=models.Diagnosis.CHRONIC_AIR_FLOW_LIMITATION,
                    occupational=bool(other.copd_is_occupational),
                    date=diagnosis_date
                )
            elif other.copd:
                models.Diagnosis.objects.create(
                    episode=episode,
                    condition="COPD",
                    category=models.Diagnosis.CHRONIC_AIR_FLOW_LIMITATION,
                    occupational=bool(other.copd_is_occupational),
                    date=diagnosis_date
                )
            else:
                models.Diagnosis.objects.create(
                    episode=episode,
                    condition="Emphysema",
                    category=models.Diagnosis.CHRONIC_AIR_FLOW_LIMITATION,
                    occupational=bool(other.copd_is_occupational),
                    date=diagnosis_date
                )

        if any([
            other.malignancy,
            other.malignancy_type,
            other.malignancy_type_other
        ]):
            malignancy = other.malignancy_type_other.strip()

            if not malignancy:
                malignancy = other.malignancy_type.strip()

            models.Diagnosis.objects.create(
                episode=episode,
                condition=malignancy,
                category=models.Diagnosis.MALIGNANCY,
                occupational=bool(other.malignancy_is_occupational),
                date=diagnosis_date
            )

        if any([
            other.diffuse_lung_disease,
            other.diffuse_lung_disease_type,
            other.diffuse_lung_disease_type_other,
        ]):
            lung_disease_type = other.diffuse_lung_disease_type_other.strip()

            if not lung_disease_type:
                lung_disease_type = other.diffuse_lung_disease_type.strip()
            models.Diagnosis.objects.create(
                episode=episode,
                condition=lung_disease_type,
                category=models.Diagnosis.DIFFUSE_LUNG_DISEASE,
                occupational=bool(other.diffuse_lung_disease_is_occupational),
                date=diagnosis_date
            )

        if any([
            other.benign_pleural_disease,
            other.benign_pleural_disease_type,
        ]):
            disease_type = other.benign_pleural_disease_type.strip()
            if disease_type == "Difuse":
                disease_type = "Diffuse"

            models.Diagnosis.objects.create(
                episode=episode,
                condition=disease_type,
                category=models.Diagnosis.BENIGN_PLEURAL_DISEASE,
                date=diagnosis_date
            )

        if any([
            other.other_diagnosis_type,
            other.other_diagnosis_type_other,
            other.other_diagnosis,
        ]):
            condition = other.other_diagnosis_type_other.strip()

            if not condition:
                condition = other.other_diagnosis_type.strip()

            if condition.lower() == "acute pneumonitis":
                condition = "Chemical pneumonitis"

            if condition.lower() == "building related illness":
                condition = "Building related symptoms"

            if condition.lower() == "hyperventilation":
                condition = "Breathing pattern disorder"

            models.Diagnosis.objects.create(
                episode=episode,
                condition=condition,
                category=models.Diagnosis.OTHER,
                occupational=bool(other.other_diagnosis_is_occupational),
                date=diagnosis_date
            )

    def build_other(self, patientLUT, rows):
        for row in rows:
            patient = patientLUT.get(row["Patient_details.Patient_num"], None)

            if patient is None:
                continue

            yield OtherFields(
                patient=patient,
                created=timezone.now(),
                other_det_num=row["OtherDet_Num"],
                attendance_date=row["Attendance_date"],
                referral=row["referral"],
                # reason_other=row["reason_other"],
                # occupation_other=row["Occupation_other"],
                asthma_relate_work=row["AsthmaRelateWork"],
                chronic_air_flow=row["ChronicAirFlow"],
                chronic_air_flow_choice=row["ChronicAirFlowChoice"],
                chronic_obstructive_brinchitis=row[
                    "ChronicObstructiveBrinchitis"
                ],
            )

    def flush(self):
        Details.objects.filter(
            patient__patientnumber__source=PatientNumber.OCC_ASTHMA
        ).delete()
        SuspectOccupationalCategory.objects.filter(
            patient__patientnumber__source=PatientNumber.OCC_ASTHMA
        ).delete()
        DiagnosticTesting.objects.filter(
            patient__patientnumber__source=PatientNumber.OCC_ASTHMA
        ).delete()
        DiagnosticOutcome.objects.filter(
            patient__patientnumber__source=PatientNumber.OCC_ASTHMA
        ).delete()
        DiagnosticAsthma.objects.filter(
            patient__patientnumber__source=PatientNumber.OCC_ASTHMA
        ).delete()
        DiagnosticRhinitis.objects.filter(
            patient__patientnumber__source=PatientNumber.OCC_ASTHMA
        ).delete()
        DiagnosticOther.objects.filter(
            patient__patientnumber__source=PatientNumber.OCC_ASTHMA
        ).delete()
        OtherFields.objects.filter(
            patient__patientnumber__source=PatientNumber.OCC_ASTHMA
        ).delete()

    def build_patient_numbers(self, rows):
        for row in rows:
            patient_number = row["Patient_details.Patient_num"]
            hospital_number = row["Hospital Number"]
            patient_number_obj = PatientNumber.objects.filter(
                value=patient_number
            ).first()

            demographics = models.Demographics.objects.filter(
                hospital_number=hospital_number
            ).first()

            if not patient_number_obj and demographics:
                patient_number_obj = demographics.patient.patientnumber_set.get()
                patient_number_obj.value = patient_number
                patient_number_obj.source = PatientNumber.OCC_ASTHMA
                patient_number_obj.save()

    @transaction.atomic
    def create_legacy(self, file_name):
        self.flush()

        # Open with utf-8-sig encoding to avoid having a BOM in the first
        # header string.
        with open(file_name, encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))

        self.build_patient_numbers(rows)
        patient_nums = PatientNumber.objects.filter(
            source=PatientNumber.OCC_ASTHMA
        )
        patientLUT = {p.value: p.patient for p in patient_nums}

        # TODO: print missing patient IDs here

        # REMAINING FIELDS
        Details.objects.bulk_create(self.build_details(patientLUT, rows))

        SuspectOccupationalCategory.objects.bulk_create(
            self.build_suspect_occupational_category(patientLUT, rows)
        )
        DiagnosticTesting.objects.bulk_create(
            self.build_diagnostic_testing(patientLUT, rows)
        )
        DiagnosticOutcome.objects.bulk_create(
            self.build_diagnostic_outcome(patientLUT, rows)
        )
        DiagnosticAsthma.objects.bulk_create(
            self.build_diagnostic_asthma(patientLUT, rows)
        )
        DiagnosticRhinitis.objects.bulk_create(
            self.build_diagnostic_rhinitis(patientLUT, rows)
        )
        DiagnosticOther.objects.bulk_create(
            self.build_diagnostic_other(patientLUT, rows)
        )
        OtherFields.objects.bulk_create(self.build_other(patientLUT, rows))

        for row in rows:
            patient = patientLUT.get(row["Patient_details.Patient_num"], None)

            if patient is None:
                continue

            episode = patient.episode_set.first()

            # CONVERTED FIELDS

            demographics = patient.demographics_set.get()
            demographics.hospital_number = row["Hospital Number"]
            demographics.save()

            clinic_log = episode.cliniclog_set.get()
            clinic_log.clinic_date = to_date(row["Attendance_date"])

            seen_by = to_upper(row["Specialist_Dr"])
            if seen_by:
                clinic_log.seen_by = seen_by

            clinic_log.save()

            employment = episode.employment_set.get()
            employment.employer = row["Employer"]
            employment.save()

            referral = episode.referral_set.get()
            if not referral.referrer_name:
                referral.referrer_name = row["Referring_doctor"]
                referral.save()

        msg = "Imported {} other details rows".format(len(rows))
        self.stdout.write(self.style.SUCCESS(msg))

        # We deleted things that were singletons in the "Flush step"
        # call_command('create_singletons')

    def convert_diagnostic_testing(self, patient):
        legacy_diagnostic_testing = patient.diagnostictesting_set.all()[0]

        SPIROMETRY_FIELDS = [
            "fev_1", "fev_1_post_ventolin", "fev_1_percentage_protected",
            "fvc", "fvc_post_ventolin", "fvc_percentage_protected"
        ]
        if any([
            getattr(legacy_diagnostic_testing, i) for i in SPIROMETRY_FIELDS
        ]):
            spirometry  = lab_models.Spirometry(patient=patient)
            for field in SPIROMETRY_FIELDS:
                field_value = getattr(legacy_diagnostic_testing, field)
                setattr(spirometry, field, field_value)
            spirometry.date = patient.otherfields_set.all()[0].attendance_date_as_date()
            spirometry.save()

            ct_scan = legacy_diagnostic_testing.ct_chest_scan
            ct_scan_date = legacy_diagnostic_testing.ct_chest_scan_date
            lung_function = legacy_diagnostic_testing.full_lung_function
            lung_function_date = legacy_diagnostic_testing.full_lung_function_date

            if ct_scan or ct_scan_date:
                lab_models.OtherInvestigations.objects.create(
                    test=lab_models.OtherInvestigations.CT_CHEST_SCAN,
                    date=ct_scan_date,
                    patient=patient
                )

            if lung_function or lung_function_date:
                lab_models.OtherInvestigations.objects.create(
                    test=lab_models.OtherInvestigations.FULL_LUNG_FUNCTION,
                    date=lung_function_date,
                    patient=patient
                )

    @transaction.atomic
    def convert_legacy(self):
        qs = opal_models.Patient.objects.exclude(details=None).filter(
            patientnumber__source=PatientNumber.OCC_ASTHMA
        )
        qs = qs.prefetch_related(
            'diagnostictesting_set',
            "suspectoccupationalcategory_set",
            "diagnosticoutcome_set",
            "diagnosticother_set",
            "otherfields_set",
        )

        for patient in qs:
            self.convert_details(patient)
            self.convert_suspect_occupational_category(patient)
            self.convert_diagnostic_testing(patient)
            self.convert_to_diagnosis_asthma(patient)
            self.convert_to_diagnosis_rhinitis(patient)
            self.convert_diagnostic_outcome(patient)
            self.convert_to_diagnosis_other(patient)

    def handle(self, *args, **options):
        self.create_legacy(options["file_name"])
        before_ct = lab_models.OtherInvestigations.objects.filter(
            test=lab_models.OtherInvestigations.CT_CHEST_SCAN
        ).count()
        before_lung = lab_models.OtherInvestigations.objects.filter(
            test=lab_models.OtherInvestigations.FULL_LUNG_FUNCTION
        ).count()
        before_spirometry = lab_models.Spirometry.objects.all().count()
        self.convert_legacy()
        after_ct = lab_models.OtherInvestigations.objects.filter(
            test=lab_models.OtherInvestigations.CT_CHEST_SCAN
        ).count()
        after_lung = lab_models.OtherInvestigations.objects.filter(
            test=lab_models.OtherInvestigations.FULL_LUNG_FUNCTION
        ).count()
        after_spirometry = lab_models.Spirometry.objects.all().count()

        msg = "Created {} OtherInvestigation CT scans".format(
            after_ct - before_ct
        )
        self.stdout.write(self.style.SUCCESS(msg))

        msg = "Created {} OtherInvestigation lung function".format(
            after_lung - before_lung
        )
        self.stdout.write(self.style.SUCCESS(msg))

        msg = "Created {} Spirometry".format(
            after_spirometry - before_spirometry
        )
        self.stdout.write(self.style.SUCCESS(msg))
