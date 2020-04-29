import csv
from django.core.management import BaseCommand, call_command
from django.db import transaction
from django.utils import timezone
from opal.models import Patient

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

from ..utils import to_bool, to_date, to_float, to_int


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("file_name", help="Specify import file")

    def build_details(self, patientLUT, rows):

        for row in rows:

            patient = patientLUT.get(row["Patient_num"], None)

            if patient is None:
                continue

            date_referral_received = to_date(row["Date referral written"])
            if date_referral_received:
                date_referral_received = date_referral_received.date()

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
                referring_doctor=row["Referring_doctor"],
                specialist_doctor=row["Specialist_Dr"],

            )

    def build_suspect_occupational_category(self, patientLUT, rows):
        for row in rows:
            patient = patientLUT.get(row["Patient_num"], None)

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
                employer_name=row["Employer"],
                suspect_occupational_category=row["Occupation_category"],
                job_title=row["Occupation_other"],
                exposures=row["Exposures"],
                is_employed_in_suspect_occupation=row["Current_employment"],
                month_started_exposure=none_if_0(row["Date started"]),
                year_started_exposure=get_year(none_if_0(row["Dates_st_Exposure_Y"])),
                month_finished_exposure=none_if_0(row["Date Finished"]),
                year_finished_exposure=get_year(none_if_0(row["Dates_f_Exposure_Y"])),
            )

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
                ct_chest_scan_date=to_date(row["CTdate"]),
                full_lung_function=to_bool(row["FullPulFunTest"]),
                full_lung_function_date=to_date(row["LFTdate"]),
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
                diagnosis_date=to_date(row["Date of Diagnosis"]),
                referred_to=row["Diagnosis_referral"],
            )

    def build_diagnostic_asthma(self, patientLUT, rows):
        for row in rows:
            patient = patientLUT.get(row["Patient_num"], None)

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

    def build_diagnostic_rhinitis(self, patientLUT, rows):
        for row in rows:
            patient = patientLUT.get(row["Patient_num"], None)

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

    def build_patient_number(self, rows):
        patient_numbers = []
        for row in rows:
            patient = Patient.objects.filter(
                demographics__hospital_number=row["Hospital Number"]
            ).first()
            if not patient:
                msg = "failed to find {}".format(row["Hospital Number"])
                self.stdout.write(self.style.ERROR(msg))
            else:
                patient_number = PatientNumber(
                    patient=patient,
                    value=row["Patient_num"]
                )
                patient_numbers.append(patient_number)
        return patient_numbers

    def flush(self):
        PatientNumber.objects.all().delete()
        Details.objects.all().delete()
        SuspectOccupationalCategory.objects.all().delete()
        DiagnosticTesting.objects.all().delete()
        DiagnosticOutcome.objects.all().delete()
        DiagnosticAsthma.objects.all().delete()
        DiagnosticRhinitis.objects.all().delete()
        DiagnosticOther.objects.all().delete()
        OtherFields.objects.all().delete()

    def report_count(self, model):
        msg = "Imported {} {}".format(
            model.objects.count(), model.__name__
        )
        self.stdout.write(self.style.SUCCESS(msg))

    # Conversion functions that transfer legacy data to rbhl data
    def convert_details(self, patient):
        """
        Maps
        Details.date_referral_received" -> "Referral.date_referral_received
        Details.referral_type -> Referral.referral_type
        Details.date_referral_received -> Referral.date_referral_received
        Details.referral_type -> Referral.referral_type
        Details.referral_reason -> Referral.referral_reason
        Details.fire_service_applicant -> Employment.firefighter
        Details.systems_presenting_compliant -> Referral.comments
        Details.referral_disease -> Referral.referral_disease
        Details.specialist_doctor -> ClinicLog.seen_by
        Details.referring_doctor -> Referral.referrer_name

        TODO
        Details.geographic_area
        Details.geographic_area_other
        Details.is_smoker
        Details.smokes_per_day
        """

        details = patient.details_set.first()
        clinic_log = patient.episode_set.get().cliniclog_set.get()

        if not clinic_log.seen_by:
            if details.specialist_doctor:
                clinic_log.seen_by = details.specialist_doctor
                clinic_log.save()

        if details and details.site_of_clinic:
            if details.site_of_clinic == "Other":
                clinic_log.clinic_site = details.site_of_clinic
            else:
                clinic_log.clinic_set = details.other_clinic_site
            clinic_log.save()

        REFERRAL_FIELDS = [
            "date_referral_received",
            "referral_type",
            "referral_reason",
            "referral_disease"
        ]

        referral = patient.episode_set.get().referral_set.get()

        for referral_field in REFERRAL_FIELDS:
            if not getattr(referral, referral_field):
                details_value = getattr(details, referral_field)
                if details_value:
                    setattr(referral, details_value)
                    referral.save()

        if not referral.referrer_name:
            if details.referring_doctor:
                referral.referrer_name = details.referring_doctor
                referral.save()

        employment = patient.episode_set.get().employment_set.get()
        if employment.firefighter is None:
            fsa = details.fire_service_applicant
            if fsa:
                fire_service_lut = {"no": False, "yes": True}
                employment.firefighter = fire_service_lut.get(fsa.lower())
                employment.save()

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
        # TODO this sometimes returns multiple
        suspect_occupational_category = patient.suspectoccupationalcategory_set.first()
        employment = patient.episode_set.get().employment_set.get()
        if not employment.job_title:
            employment.job_title = suspect_occupational_category.job_title

        if not employment.employment_category:
            emp_cat = suspect_occupational_category.suspect_occupational_category
            employment.employment_category = emp_cat

        if not employment.employer:
            emp_name = suspect_occupational_category.employer_name
            employment.employment_category = emp_name

        if employment.employed_in_suspect_occupation is None:
            employed_lut = {
                'Yes-employed in suspect occupation': True,
                'Yes': True,
                'Yes-other occupation': False,  # Only used very few times
                'No': False,
                '': None
            }
            sus = suspect_occupational_category.is_employed_in_suspect_occupation
            employment.employed_in_suspect_occupation = employed_lut[sus]

        if employment.exposures is None:
            exposures = suspect_occupational_category.exposures
            employment.is_employed_in_suspect_occupation = exposures
        employment.save()

    def convert_diagnostic_testing(self, patient):
        """
        Maps

        DiagnosticTesting.height
            -> Demographics.height
        DiagnosticTesting.antihistimines
            -> RbhlDiagnosticTesting.antihistimines
        DiagnosticTesting.skin_prick_test
            -> RbhlDiagnosticTesting.employment_category
        DiagnosticTesting.atopic
            -> RbhlDiagnosticTesting.atopic
        DiagnosticTesting.specific_skin_prick
            -> RbhlDiagnosticTesting.specific_skin_prick
        DiagnosticTesting.serum_antibodies
            -> RbhlDiagnosticTesting.immunology_oem
        DiagnosticTesting.fev_1
            -> RbhlDiagnosticTesting.fev_1
        DiagnosticTesting.fev_1_post_ventolin
            -> RbhlDiagnosticTesting.fev_1_post_ventolin
        DiagnosticTesting.fev_1_percentage_protected
            -> RbhlDiagnosticTesting.fev_1_percentage_protected
        DiagnosticTesting.fvc
            -> RbhlDiagnosticTesting.fvc
        DiagnosticTesting.fvc_post_ventolin
            -> RbhlDiagnosticTesting.fvc_post_ventolin
        DiagnosticTesting.ct_chest_scan
            -> RbhlDiagnosticTesting.ct_chest_scan
        DiagnosticTesting.ct_chest_scan_date
            -> RbhlDiagnosticTesting.ct_chest_scan_date
        DiagnosticTesting.full_lung_function
            -> RbhlDiagnosticTesting.full_lung_function
        DiagnosticTesting.full_lung_function_date
            -> RbhlDiagnosticTesting.full_lung_function_date
        """
        # TODO this sometimes returns multiple
        legacy_diagnostic_testing = patient.diagnostictesting_set.first()
        diagnosistic_testing = patient.episode_set.get().rbhldiagnostictesting_set.get()

        if patient.demographics_set.filter(height=None).exists():
            if legacy_diagnostic_testing.height:
                patient.demographics_set.update(
                    height=legacy_diagnostic_testing.height
                )

        FIELDS = [
            "antihistimines",
            "skin_prick_test",
            "atopic",
            "specific_skin_prick",
            "fev_1",
            "fev_1_post_ventolin",
            "fev_1_percentage_protected",
            "fvc",
            "fvc_post_ventolin",
            "fvc_percentage_protected",
            "ct_chest_scan",
            "ct_chest_scan_date",
            "full_lung_function",
            "full_lung_function_date"
        ]

        for field in FIELDS:
            legacy_value = getattr(legacy_diagnostic_testing, field)
            setattr(diagnosistic_testing, field, legacy_value)
        diagnosistic_testing.immunology_oem = legacy_diagnostic_testing.serum_antibodies
        diagnosistic_testing.save()

    @transaction.atomic()
    def transfer_to_rbhl(self):
        total = 0
        for patient in Patient.objects.filter(
            id__in=set(Details.objects.values_list("patient_id", flat=True))
        ):
            self.convert_details(patient)
            self.convert_suspect_occupational_category(patient)
            self.convert_diagnostic_testing(patient)
            total += 1
        self.stdout.write(self.style.SUCCESS("Mapped {}".format(total)))

    @transaction.atomic()
    def create_legacy(self, file_name):
        # Open with utf-8-sig encoding to avoid having a BOM in the first
        # header string.
        self.flush()
        with open(file_name, encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))

        PatientNumber.objects.bulk_create(
            self.build_patient_number(rows)
        )
        self.stdout.write(self.style.ERROR("Failed to find {} patients".format(
            len(rows) - PatientNumber.objects.count()
        )))

        patientLUT = {p.value: p.patient for p in PatientNumber.objects.all()}

        Details.objects.bulk_create(self.build_details(patientLUT, rows))
        self.report_count(Details)

        SuspectOccupationalCategory.objects.bulk_create(
            self.build_suspect_occupational_category(patientLUT, rows)
        )
        self.report_count(SuspectOccupationalCategory)

        DiagnosticTesting.objects.bulk_create(
            self.build_diagnostic_testing(patientLUT, rows)
        )
        self.report_count(DiagnosticTesting)

        DiagnosticOutcome.objects.bulk_create(
            self.build_diagnostic_outcome(patientLUT, rows)
        )
        self.report_count(DiagnosticOutcome)

        DiagnosticAsthma.objects.bulk_create(
            self.build_diagnostic_asthma(patientLUT, rows)
        )
        self.report_count(DiagnosticAsthma)

        DiagnosticRhinitis.objects.bulk_create(
            self.build_diagnostic_rhinitis(patientLUT, rows)
        )
        self.report_count(DiagnosticRhinitis)

        DiagnosticOther.objects.bulk_create(
            self.build_diagnostic_other(patientLUT, rows)
        )
        self.report_count(DiagnosticOther)

        OtherFields.objects.bulk_create(self.build_other(patientLUT, rows))
        self.report_count(OtherFields)

        msg = "Imported {} other details rows".format(len(rows))
        self.stdout.write(self.style.SUCCESS(msg))

    def handle(self, *args, **options):
        self.create_legacy(options["file_name"])
        self.transfer_to_rbhl()

        # We deleted things that were singletons in the "Flush step"
        call_command('create_singletons')
