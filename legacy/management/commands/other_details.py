import csv

from django.core.management import BaseCommand
from django.db import transaction
from django.utils import timezone
from opal.models import Patient

from legacy.models import PatientNumber


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("file_name", help="Specify import file")

    @transaction.atomic()
    def handle(self, *args, **options):
        # Open with utf-8-sig encoding to avoid having a BOM in the first
        # header string.
        with open(options["file_name"], encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))

        for row in rows:
            try:
                p_num = PatientNumber.objects.get(value=row["Patient_num"])
                patient = p_num.patient
            except PatientNumber.DoesNotExist:
                patient = Patient.objects.create()
                patient.patientnumber_set.get().update_from_dict(
                    {"created": timezone.now(), "value": row["Patient_num"]}, user=None
                )

            patient.details_set.get().update_from_dict(
                {
                    "created": timezone.now(),
                    "hospital_number": row["Hospital Number"],
                    "date_first_attended": row["Attendance_date"],
                    "referring_doctor": row["Referring_doctor"],
                    "date_referral_received": row["Date referral written"],
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
                    "has_asthma": row["Asthma"],
                    "has_hayfever": row["Hayfever"],
                    "has_eczema": row["Eczema"],
                    "is_smoker": row["Smoker"],
                    "smokes_per_day": row["No_cigarettes"],
                },
                user=None,
            )

            patient.suspectoccupationalcategory_set.get().update_from_dict(
                {
                    "created": timezone.now(),
                    "is_currently_employed": row["Employed"],
                    "suspect_occupational_category": row["Occupation_category"],
                    "job_title": row["Current_employment"],
                    "exposures": row["Exposures"],
                    "employer_name": row["Employer"],
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
                    "antihistimines": row["Antihistimines"],
                    "skin_prick_test": row["SkinPrick_test"],
                    "atopic": row["Atopic"],
                    "specific_skin_prick": row["SpecificSkinPrick"],
                    "serum_antibodies": row["Serum_antibodies"],
                    "bronchial_prov_test": row["BronchialProvTest"],
                    "change_pc_20": row["ChangePC20"],
                    "nasal_prov_test": row["NasalProvTest"],
                    "positive_reaction": row["PositiveReaction"],
                    "height": row["Height"],
                    "fev_1": row["FEV1"],
                    "fev_1_post_ventolin": row["FEV1PostVentolin"],
                    "fev_1_percentage_protected": row["FEV1%pred"],
                    "fvc": row["FVCpPreVentolin"],
                    "fvc_post_ventolin": row["FVCPostVentolin"],
                    "fvc_percentage_protected": row["FVC%pred"],
                    # "is_serial_peak_flows_requested": row[""],
                    # "has_spefr_variability": row[""],
                    "is_returned": row["Returned?"],
                    # "is_spefr_work_related": row[""],
                    "ct_chest_scan": row["CTChestScan"],
                    "ct_chest_scan_date": row["CTdate"],
                    # "full_lung_function": row[""],
                    # "full_lung_function_date": row[""],
                },
                user=None,
            )

            patient.diagnosticoutcome_set.get().update_from_dict(
                {
                    "created": timezone.now(),
                    "diagnosis": row["Diagnosis"],
                    "diagnosis_date": row["Date of Diagnosis"],
                    "referred_to": row["Diagnosis_referral"],
                },
                user=None,
            )

            patient.diagnosticasthma_set.get().update_from_dict(
                {
                    "created": timezone.now(),
                    "asthma": row["DiagnosisAsthma"],
                    "is_exacerbated_by_work": row["AsthmaExacerbate"],
                    "has_infant_induced_asthma": row["AsthmaOccInt"],
                    "occupational_asthma_caused_by_sensitisation": row["AsthmaOccSen"],
                    "sensitising_agent": row["AsthmaOccSenCause"],
                    "has_non_occupational_asthma": row["AsthmaNonOcc"],
                },
                user=None,
            )

            patient.diagnosticrhinitis_set.get().update_from_dict(
                {
                    "created": timezone.now(),
                    "rhinitis": row["DiagnosisRhinitis"],
                    "work_exacerbated": row["RhinitisExacerbate"],
                    "occupational_rhinitis_caused_by_sensitisation": row[
                        "RhinitisOccSen"
                    ],
                    "rhinitis_occupational_sensitisation_cause": row[
                        "RhinitisOccSenCause"
                    ],
                    "has_non_occupational_rhinitis": row["RhinitisNonOcc"],
                },
                user=None,
            )

            patient.diagnosticother_set.get().update_from_dict(
                {
                    "created": timezone.now(),
                    "copd": row["ChronicAirFlow"],
                    "emphysema": row["Emphsema"],
                    "copd_with_emphysema": row["COPD&emph"],
                    # "copd_is_occupational": row[""],
                    "malignancy": row["Malignancy"],
                    "malignancy_is_occupational": row["MalignancyType"],
                    "malignancy_type": row["MalignancyTypeChoice"],
                    "malignancy_type_other": row["MalignancyTypeChoiceOther"],
                    "NAD": row["NAD"],
                    "diffuse_lung_disease": row["DiffuseLungDis"],
                    "diffuse_lung_disease_is_occupational": row["DiffuseLungDisChoice"],
                    "diffuse_lung_disease_type": row["DiffuseLungDisType"],
                    "diffuse_lung_disease_type_other": row["DiffuseLungDisTypeOther"],
                    "benign_pleural_disease": row["BenignPleuralDis"],
                    "benign_pleural_disease_type": row["BenignPleuralDisType"],
                    "other_diagnosis": row["OtherDiag"],
                    "other_diagnosis_is_occupational": row["OtherDiagChoice"],
                    "other_diagnosis_type": row["OtherDiagChoiceType"],
                    "other_diagnosis_type_other": row["OtherDiagOther"],
                },
                user=None,
            )

            # patient.skinpricktest_set.get().update_from_dict({
            # }, user=None)

            patient.otherfields_set.get().update_from_dict(
                {
                    "created": timezone.now(),
                    "other_det_num": row["OtherDet_Num"],
                    "attendance_date": row["Attendance_date"],
                    "specialist_doctor": row["Specialist_Dr"],
                    "referral": row["referral"],
                    "reason_other": row["reason_other"],
                    "occupation_other": row["Occupation_other"],
                    "ige_results": row["IgEresults"],
                    "serum_results_num": row["Serum_resultsnum"],
                    "ssp_test_num": row["SSPTest_Num"],
                    "serial_perf": row["SerialPERF"],
                    "perf_variability": row["PERFVariablility"],
                    "perf_work_relate": row["PERFWorkRelate"],
                    "outcome_num": row["outcome_num"],
                    "full_pul_fun_test": row["FullPulFunTest"],
                    "lft_date": row["LFTdate"],
                    "asthma_relate_work": row["AsthmaRelateWork"],
                    "chronic_air_flow": row["ChronicAirFlow"],
                    "chronic_air_flow_choice": row["ChronicAirFlowChoice"],
                    "chronic_obstructive_brinchitis": row[
                        "ChronicObstructiveBrinchitis"
                    ],
                    "exposure_dates": row["Exposure_dates"],
                    "bronch_prov_test_type": row["BronchProvTest_type"],
                },
                user=None,
            )
