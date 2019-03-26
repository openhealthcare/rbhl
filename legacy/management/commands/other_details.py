import csv

from django.core.management import BaseCommand, call_command
from django.db import transaction
from django.utils import timezone

from legacy.models import (
    Details,
    DiagnosticAsthma,
    DiagnosticOther,
    DiagnosticOutcome,
    DiagnosticRhinitis,
    DiagnosticTesting,
    OtherFields,
    PatientNumber,
    SkinPrickTest,
    SuspectOccupationalCategory,
)

from ..utils import to_bool, to_date, to_float, to_int


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("file_name", help="Specify import file")

    def flush(self):
        Details.objects.all().delete()
        SuspectOccupationalCategory.objects.all().delete()
        DiagnosticTesting.objects.all().delete()
        DiagnosticOutcome.objects.all().delete()
        DiagnosticAsthma.objects.all().delete()
        DiagnosticRhinitis.objects.all().delete()
        DiagnosticOther.objects.all().delete()
        SkinPrickTest.objects.all().delete()
        OtherFields.objects.all().delete()

    @transaction.atomic()
    def handle(self, *args, **options):
        self.flush()
        call_command("create_singletons")

        # Open with utf-8-sig encoding to avoid having a BOM in the first
        # header string.
        with open(options["file_name"], encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))

        self.stdout.write(self.style.SUCCESS("Importing other details rows"))
        for row in rows:
            try:
                p_num = PatientNumber.objects.get(value=row["Patient_num"])
                patient = p_num.patient
            except PatientNumber.DoesNotExist:
                msg = "Unknown Patient: {}".format(row["Patient_num"])
                self.stderr.write(self.style.ERROR(msg))
                continue

            episode = patient.episode_set.get()

            # CONVERTED FIELDS

            demographics = patient.demographics_set.get()
            demographics.hospital_number = row["Hospital Number"]
            demographics.save()

            clinic_log = episode.cliniclog_set.get()
            clinic_log.clinic_date = to_date(row["Attendance_date"])
            clinic_log.save()

            employment = episode.employment_set.get()
            employment.employer = row["Employer"]
            employment.save()

            referral = episode.referral_set.get()
            referral.referral_name = row["Referring_doctor"]
            referral.save()

            # REMAINING FIELDS

            date_referral_received = to_date(row["Date referral written"])
            patient.details_set.get().update_from_dict(
                {
                    "created": timezone.now(),
                    "date_referral_received": date_referral_received,
                    "referral_type": row["Referral_reason"],
                    "fire_service_applicant": row["Fireapplicant"],
                    # "systems_presenting_compliant": row[""],
                    "referral_disease": row["Referral_disease"],
                    "geographical_area": row["Geographical_area"],
                    "geographical_area_other": row["Geographical_area"],
                    "site_of_clinic": row["Site of Clinic"],
                    "other_clinic_site": row["Other Clinic Site"],
                    "clinic_status": row["Clinic_status"],
                    # "seen_by_dr": row[""],
                    "previous_atopic_disease": row["AtopicDisease"],
                    "has_asthma": to_bool(row["Asthma"]),
                    "has_hayfever": to_bool(row["Hayfever"]),
                    "has_eczema": to_bool(row["Eczema"]),
                    "is_smoker": row["Smoker"],
                    "smokes_per_day": to_int(row["No_cigarettes"]),
                },
                user=None,
            )

            patient.suspectoccupationalcategory_set.get().update_from_dict(
                {
                    "created": timezone.now(),
                    "is_currently_employed": to_bool(row["Employed"]),
                    "suspect_occupational_category": row[
                        "Occupation_category"
                    ],
                    "job_title": row["Current_employment"],
                    "exposures": row["Exposures"],
                    # "is_employed_in_suspect_occupation": row[""],
                    "month_started_exposure": row["Date started"],
                    "year_started_exposure": row["Dates_st_Exposure_Y"],
                    "month_finished_exposure": row["Date Finished"],
                    "year_finished_exposure": row["Dates_f_Exposure_Y"],
                },
                user=None,
            )

            patient.diagnostictesting_set.get().update_from_dict(
                {
                    "created": timezone.now(),
                    "antihistimines": to_bool(row["Antihistimines"]),
                    "skin_prick_test": to_bool(row["SkinPrick_test"]),
                    "atopic": row["Atopic"],
                    "specific_skin_prick": to_bool(row["SpecificSkinPrick"]),
                    "serum_antibodies": to_bool(row["Serum_antibodies"]),
                    "bronchial_prov_test": to_bool(row["BronchialProvTest"]),
                    "change_pc_20": row["ChangePC20"],
                    "nasal_prov_test": to_bool(row["NasalProvTest"]),
                    "positive_reaction": to_bool(row["PositiveReaction"]),
                    "height": row["Height"],
                    "fev_1": to_float(row["FEV1"]),
                    "fev_1_post_ventolin": to_float(row["FEV1PostVentolin"]),
                    "fev_1_percentage_protected": to_int(row["FEV1%pred"]),
                    "fvc": to_float(row["FVCpPreVentolin"]),
                    "fvc_post_ventolin": to_float(row["FVCPostVentolin"]),
                    "fvc_percentage_protected": to_int(row["FVC%pred"]),
                    "is_serial_peak_flows_requested": to_bool(row["SerialPERF"]),
                    "has_spefr_variability": row["PERFVariablility"],
                    "is_returned": to_bool(row["Returned?"]),
                    "is_spefr_work_related": row["PERFWorkRelate"],
                    "ct_chest_scan": to_bool(row["CTChestScan"]),
                    "ct_chest_scan_date": to_date(row["CTdate"]),
                    # "full_lung_function": row[""],
                    "full_lung_function_date": to_date(row["LFTdate"]),
                },
                user=None,
            )

            patient.diagnosticoutcome_set.get().update_from_dict(
                {
                    "created": timezone.now(),
                    "diagnosis": row["Diagnosis"],
                    "diagnosis_date": to_date(row["Date of Diagnosis"]),
                    "referred_to": row["Diagnosis_referral"],
                },
                user=None,
            )

            patient.diagnosticasthma_set.get().update_from_dict(
                {
                    "created": timezone.now(),
                    "asthma": to_bool(row["DiagnosisAsthma"]),
                    "is_exacerbated_by_work": to_bool(row["AsthmaExacerbate"]),
                    "has_infant_induced_asthma": to_bool(row["AsthmaOccInt"]),
                    "occupational_asthma_caused_by_sensitisation": to_bool(
                        row["AsthmaOccSen"]
                    ),
                    "sensitising_agent": row["AsthmaOccSenCause"],
                    "has_non_occupational_asthma": to_bool(
                        row["AsthmaNonOcc"]
                    ),
                },
                user=None,
            )

            # FIXME: there is a single row where this field has the value "x"
            # in the data as of 2019/03/25.  The surrounding data makes it look
            # like this is a typo (since there is no surrounding data).
            RhinitisNonOcc = row["RhinitisNonOcc"]
            if RhinitisNonOcc != "x":
                has_non_occ_rhinitis = to_bool(RhinitisNonOcc)
            else:
                has_non_occ_rhinitis = None
            patient.diagnosticrhinitis_set.get().update_from_dict(
                {
                    "created": timezone.now(),
                    "rhinitis": to_bool(row["DiagnosisRhinitis"]),
                    "work_exacerbated": to_bool(row["RhinitisExacerbate"]),
                    "occupational_rhinitis_caused_by_sensitisation": to_bool(
                        row["RhinitisOccSen"]
                    ),
                    "rhinitis_occupational_sensitisation_cause": row[
                        "RhinitisOccSenCause"
                    ],
                    "has_non_occupational_rhinitis": has_non_occ_rhinitis,
                },
                user=None,
            )

            patient.diagnosticother_set.get().update_from_dict(
                {
                    "created": timezone.now(),
                    "copd": to_bool(row["ChronicAirFlow"]),
                    "emphysema": to_bool(row["Emphsema"]),
                    "copd_with_emphysema": to_bool(row["COPD&emph"]),
                    # "copd_is_occupational": row[""],
                    "malignancy": to_bool(row["Malignancy"]),
                    "malignancy_is_occupational": to_bool(
                        row["MalignancyType"]
                    ),
                    "malignancy_type": row["MalignancyTypeChoice"],
                    "malignancy_type_other": row["MalignancyTypeChoiceOther"],
                    "NAD": to_bool(row["NAD"]),
                    "diffuse_lung_disease": to_bool(row["DiffuseLungDis"]),
                    "diffuse_lung_disease_is_occupational": to_bool(
                        row["DiffuseLungDisChoice"]
                    ),
                    "diffuse_lung_disease_type": row["DiffuseLungDisType"],
                    "diffuse_lung_disease_type_other": row[
                        "DiffuseLungDisTypeOther"
                    ],
                    "benign_pleural_disease": to_bool(row["BenignPleuralDis"]),
                    "benign_pleural_disease_type": row["BenignPleuralDisType"],
                    "other_diagnosis": to_bool(row["OtherDiag"]),
                    "other_diagnosis_is_occupational": to_bool(
                        row["OtherDiagChoice"]
                    ),
                    "other_diagnosis_type": row["OtherDiagChoiceType"],
                    "other_diagnosis_type_other": row["OtherDiagOther"],
                },
                user=None,
            )

            patient.otherfields_set.get().update_from_dict(
                {
                    "created": timezone.now(),
                    "other_det_num": row["OtherDet_Num"],
                    "attendance_date": row["Attendance_date"],
                    "specialist_doctor": row["Specialist_Dr"],
                    "referral": row["referral"],
                    "reason_other": row["reason_other"],
                    "occupation_other": row["Occupation_other"],
                    "full_pul_fun_test": to_bool(row["FullPulFunTest"]),
                    "asthma_relate_work": row["AsthmaRelateWork"],
                    "chronic_air_flow": row["ChronicAirFlow"],
                    "chronic_air_flow_choice": row["ChronicAirFlowChoice"],
                    "chronic_obstructive_brinchitis": row[
                        "ChronicObstructiveBrinchitis"
                    ],
                },
                user=None,
            )

        msg = "Imported {} other details rows".format(len(rows))
        self.stdout.write(self.style.SUCCESS(msg))
