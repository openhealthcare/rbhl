import csv
import functools

import structlog
from django.core.management import BaseCommand
from django.db import transaction
from django.utils import timezone

from legacy.models import (
    DiagnosticOther,
    DiagnosticOutcome,
    DiagnosticTesting,
    OtherFields,
    PatientNumber,
)
from rbhl.models import SupportingDiagnosis, Exposure, History

from ..utils import to_bool, to_date, to_datetime, to_float, to_int, to_upper

log = structlog.get_logger("rbhl")


def update(row, obj, field, column, mutator=None):
    """
    Try to update the given obj.field with the given column value

    We're importing data from multiple sources, however those sources have
    overlapping value, eg Referral.referral_name (the referring doctor) can
    come from more than one source.  Often these values are only slightly
    different [to a human] but we still don't want to pick one source over
    another.  This function checks we're not going to wipe out existing data
    before assigning the new value.  When existing data is found it logs out
    the relevant information so we can fix the differences in the sources.
    """
    existing = getattr(obj, field)
    new = row[column]

    if mutator:
        new = mutator(new)

    if not new:
        # Don't overwrite target field with an empty value
        return

    if existing and new != existing:
        # Don't overwrite target field when it has a value and the new value
        # isn't the same.
        log.info(
            "Avoiding overwrite",
            model=obj.__class__.__name__,
            field=field,
            exising=existing,
            new=new,
        )
        return

    setattr(obj, field, new)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("file_name", help="Specify import file")

    def build_diagnostic_testing(self, patientLUT, rows):
        for row in rows:
            patient = patientLUT.get(row["Patient_num"], None)

            if patient is None:
                continue

            yield DiagnosticTesting(
                patient=patient,
                created=timezone.now(),
                antihistimines=to_bool(row["Antihistimines"]),
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
                ct_chest_scan_date=to_datetime(row["CTdate"]),
                full_lung_function=to_bool(row["FullPulFunTest"]),
                full_lung_function_date=to_datetime(row["LFTdate"]),
            )

    def build_diagnostic_outcome(self, patientLUT, rows):
        for row in rows:
            patient = patientLUT.get(row["Patient_num"], None)

            if patient is None:
                continue

            yield DiagnosticOutcome(
                patient=patient,
                created=timezone.now(),
                diagnosis=row["Diagnosis"],
                diagnosis_date=to_datetime(row["Date of Diagnosis"]),
                referred_to=row["Diagnosis_referral"],
            )

    def build_diagnostic_other(self, patientLUT, rows):
        for row in rows:
            patient = patientLUT.get(row["Patient_num"], None)

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

    def build_diagnoses(self, patientLUT, rows):
        for row in rows:
            patient = patientLUT.get(row["Patient_num"], None)

            if patient is None:
                continue

            episode = patient.episode_set.get()

            has_asthma = to_bool(row["DiagnosisAsthma"]),
            has_rhinitis = to_bool(row["DiagnosisRhinitis"])

            if has_asthma:
                yield SupportingDiagnosis(
                    episode=episode,
                    created=timezone.now(),
                    type="asthma",
                    is_work_exacerbated=to_bool(row["AsthmaExacerbate"]),
                    is_irritant_induced=to_bool(row["AsthmaOccInt"]),
                    is_caused_by_sensitisation=to_bool(row["AsthmaOccSen"]),
                    sensitising_agent=row["AsthmaOccSenCause"],
                    is_non_occupational=to_bool(row["AsthmaNonOcc"]),

                )

            if has_rhinitis:
                # FIXME: there is a single row where this field has the value
                # "x" in the data as of 2019/03/25.  The surrounding data makes
                # it look like this is a typo (since there is no surrounding
                # data).
                RhinitisNonOcc = row["RhinitisNonOcc"]
                if RhinitisNonOcc != "x":
                    has_non_occ_rhinitis = to_bool(RhinitisNonOcc)
                else:
                    has_non_occ_rhinitis = None

                yield SupportingDiagnosis(
                    episode=episode,
                    created=timezone.now(),
                    type="rhinitis",
                    is_work_exacerbated=to_bool(row["RhinitisExacerbate"]),
                    is_caused_by_sensitisation=to_bool(row["RhinitisOccSen"]),
                    sensitising_agent=row["RhinitisOccSenCause"],
                    is_non_occupational=has_non_occ_rhinitis,
                )

    def build_exposure(self, patientLUT, rows):
        for row in rows:
            patient = patientLUT.get(row["Patient_num"], None)

            if patient is None:
                continue

            episode = patient.episode_set.get()

            yield Exposure(
                episode=episode,
                created=timezone.now(),
                exposures=row["Exposures"],
                year_started=to_int(row["Dates_st_Exposure_Y"]),
            )

    def build_history(self, patientLUT, rows):
        for row in rows:
            patient = patientLUT.get(row["Patient_num"], None)

            if patient is None:
                continue

            yield History(
                patient=patient,
                created=timezone.now(),
                atopic_disease=row["AtopicDisease"],
                has_asthma=to_bool(row["Asthma"]),
                has_hayfever=to_bool(row["Hayfever"]),
                has_eczema=to_bool(row["Eczema"]),
                is_smoker=row["Smoker"],
                smokes_per_day=to_int(row["No_cigarettes"]),
            )

    def build_other(self, patientLUT, rows):
        for row in rows:
            patient = patientLUT.get(row["Patient_num"], None)

            if patient is None:
                continue

            yield OtherFields(
                patient=patient,
                created=timezone.now(),
                other_det_num=row["OtherDet_Num"],
                attendance_date=row["Attendance_date"],
                reason_other=row["reason_other"],
                asthma_relate_work=row["AsthmaRelateWork"],
                chronic_air_flow=row["ChronicAirFlow"],
                chronic_air_flow_choice=row["ChronicAirFlowChoice"],
                chronic_obstructive_brinchitis=row[
                    "ChronicObstructiveBrinchitis"
                ],
            )

    def flush(self):
        DiagnosticTesting.objects.all().delete()
        DiagnosticOutcome.objects.all().delete()
        DiagnosticOther.objects.all().delete()
        OtherFields.objects.all().delete()
        History.objects.all().delete()
        Exposure.objects.all().delete()
        SupportingDiagnosis.objects.all().delete()

        log.info("Deleted existing models")

    @transaction.atomic()
    def handle(self, *args, **options):
        log.info("Importing from other details CSV")
        self.flush()

        # Open with utf-8-sig encoding to avoid having a BOM in the first
        # header string.
        with open(options["file_name"], encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))

        csv_patient_ids = set(sorted(row["Patient_num"] for row in rows))
        patient_nums = PatientNumber.objects.filter(id__in=csv_patient_ids)
        patientLUT = {p.value: p.patient for p in patient_nums}

        db_patient_nums = set(str(p.id) for p in patient_nums)
        missing_patient_nums = csv_patient_ids - db_patient_nums
        if missing_patient_nums:
            missing = ", ".join(missing_patient_nums)
            log.error("Unknown Patient_nums: {}".format(missing))

        # REMAINING FIELDS
        DiagnosticTesting.objects.bulk_create(
            self.build_diagnostic_testing(patientLUT, rows)
        )
        DiagnosticOutcome.objects.bulk_create(
            self.build_diagnostic_outcome(patientLUT, rows)
        )
        DiagnosticOther.objects.bulk_create(
            self.build_diagnostic_other(patientLUT, rows)
        )
        SupportingDiagnosis.objects.bulk_create(
            self.build_diagnoses(patientLUT, rows),
        )
        Exposure.objects.bulk_create(self.build_exposure(patientLUT, rows))
        History.objects.bulk_create(self.build_history(patientLUT, rows))
        OtherFields.objects.bulk_create(self.build_other(patientLUT, rows))

        log.info("Updating existing models")
        for row in rows:
            patient = patientLUT.get(row["Patient_num"], None)

            if patient is None:
                continue

            episode = patient.episode_set.get()

            # Set up a short function name and save us some typing since this
            # will be used for each field being [potentially] updated.
            u = functools.partial(update, row)

            # CONVERTED FIELDS

            demographics = patient.demographics_set.get()
            u(demographics, "hospital_number", "Hospital Number")
            demographics.save()

            clinic_log = episode.cliniclog_set.get()
            u(clinic_log, "clinic_date", "Attendance_date", to_date)
            u(clinic_log, "seen_by", "Specialist_Dr", to_upper)
            clinic_log.save()

            employment = episode.employment_set.get()
            u(employment, "employer", "Employer")
            u(employment, "firefighter", "Fireapplicant", to_bool)
            u(employment, "is_currently_employed", "Employed")
            u(employment, "suspect_occupational_category", "Occupation_category")  # noqa: E501
            u(employment, "employment_is_suspect", "Current_employment")
            u(employment, "job_title", "Occupation_other")
            employment.save()

            referral = episode.referral_set.get()
            u(referral, "referrer_name", "Referring_doctor")
            u(referral, "date_referral_received", "Date referral written", to_date)  # noqa: E501
            u(referral, "referrer_name", "Referring_doctor")
            u(referral, "referral_type", "referral")
            u(referral, "reason", "Referral_reason")
            u(referral, "disease", "Referral_disease")
            u(referral, "geographical_area", "Geographical_area")
            referral.save()

        msg = "Imported {} other details rows".format(len(rows))
        self.stdout.write(self.style.SUCCESS(msg))
