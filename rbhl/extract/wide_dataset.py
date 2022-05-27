import csv
import os
from django.db.models import Count
from opal.models import Patient
from plugins.lab.models import Spirometry, Bloods
from django.core.exceptions import FieldDoesNotExist

from rbhl.models import RhinitisDetails, AsthmaDetails, Employment, Referral, Diagnosis


FIELDS_TO_IGNORE = (
    "id",
    "episode_id",
    "patient_id",
    "consistency_token",
    "created",
    "updated",
    "created_by",
    "updated_by",
    "patient",
    "episode",
    "bloodresult",
    "created_by_id",
    "updated_by_id",
)


def get_field_title(instance, name):
    """
    Get the verbose name of a field off an instance
    """
    model = instance.__class__
    try:
        return model._meta.get_field(name).verbose_name
    except FieldDoesNotExist:
        return getattr(model, name).verbose_name


def extract_demographics(patient):
    demographics = patient.demographics_set.all()[0]
    pid = demographics.patient_id
    link = f"https://indigo-rbht.openhealthcare.org.uk/#/patient/{pid}"
    return {
        "Patient": demographics.patient_id,
        "Indigo link": link,
        "Hospital number": demographics.hospital_number,
        "Name": demographics.name,
        "NHS number": demographics.nhs_number,
        "DOB": demographics.date_of_birth,
        "Gender": demographics.sex,
        "Height": demographics.height,
    }


def extract_social_history(patient):
    social_history = patient.episode_set.all()[0].socialhistory_set.all()[0]
    return {
        "Smoker": social_history.smoker,
        "Cigarettes per day": social_history.cigarettes_per_day,
    }


def extract_referrals(patient, counts):
    referrals = []
    for episode in patient.episode_set.all():
        referrals.extend(list(episode.referral_set.all()))
    fields = [
        "referrer_name",
        "reference_number",
        "date_of_referral",
        "date_first_appointment",
        "geographical_area",
        "occld",
    ]
    result = {}
    for idx, referral in enumerate(referrals, 1):
        for field in fields:
            field_name = referral.__class__._get_field_title(field)
            if counts > 1:
                result[f"{field_name} {idx}"] = getattr(referral, field)
            else:
                result[f"{field_name}"] = getattr(referral, field)
    return result


def extract_employment(patient, counts):
    fields = [
        "employer",
        "oh_provider",
        "job_title",
        "employment_category",
        "employed_in_suspect_occupation",
        "exposures",
        "firefighter",
    ]
    result = {}
    employment_set = []
    for episode in patient.episode_set.all():
        employment_set.extend(list(episode.employment_set.all()))
    for idx, employment in enumerate(employment_set, 1):
        for field in fields:
            field_name = employment.__class__._get_field_title(field)
            if counts > 1:
                result[f"{field_name} {idx}"] = getattr(employment, field)
            else:
                result[f"{field_name}"] = getattr(employment, field)
    return result


def extract_asthma_diagnosis(patient, counts):
    result = {}
    asthma_details = []
    for episode in patient.episode_set.all():
        asthma_details.extend(list(episode.asthmadetails_set.all()))
    for idx, asthma_detail in enumerate(asthma_details, 1):
        for field in ["date", "trigger", "sensitivities"]:
            if counts > 1:
                result[f"Asthma diagnosis {idx} {field}"] = getattr(
                    asthma_detail, field
                )
            else:
                result[f"Asthma diagnosis {field}"] = getattr(asthma_detail, field)
    return result


def extract_rhinitis_diagnosis(patient, counts):
    result = {}
    rhinitis_details = []
    for episode in patient.episode_set.all():
        rhinitis_details.extend(list(episode.rhinitisdetails_set.all()))
    for idx, rhinitis_detail in enumerate(rhinitis_details, 1):
        for field in ["date", "trigger", "sensitivities"]:
            if counts > 1:
                result[f"Rhinitis diagnosis {idx} {field}"] = getattr(
                    rhinitis_detail, field
                )
            else:
                result[f"Rhinitis diagnosis {field}"] = getattr(rhinitis_detail, field)
    return result


def extract_other_diagnosis(patient, counts):
    result = {}
    other_diagnoses = Diagnosis.objects.filter(episode__patient=patient).exclude(
        category__in=(
            "Rhinitis",
            "Asthma",
        )
    )
    fields = ["date", "category", "condition", "occupational"]
    for idx, other_diagnosis in enumerate(other_diagnoses, 1):
        for field in fields:
            if counts > 1:
                result[f"Other diagnosis {idx} {field}"] = getattr(
                    other_diagnosis, field
                )
            else:
                result[f"Other diagnosis {field}"] = getattr(other_diagnosis, field)
    return result


def extract_spirometry(patient, counts):
    fields = [
        i for i in Spirometry._get_fieldnames_to_extract() if i not in FIELDS_TO_IGNORE
    ]
    spirometries = patient.spirometry_set.all()
    result = {}
    for idx, spirometry in enumerate(spirometries, 1):
        for field in fields:
            if counts > 1:
                result[f"Spirometry {idx} {field}"] = getattr(spirometry, field)
            else:
                result[f"Spirometry {field}"] = getattr(spirometry, field)
    return result


def extract_clinic_log(patient):
    episode = patient.episode_set.all()[0]
    clinic_log = episode.cliniclog_set.all()[0]
    fields = (
        "clinic_date",
        "seen_by",
        "clinic_site",
        "cns",
        "diagnosis_outcome",
        "referred_to",
        "active",
        "sword",
        "peak_flow_requested",
        "external_spirometry_done",
        "immunology_oem",
        "other_rbh_bloods",
        "outstanding_tests_required",
    )
    result = {}
    for field in fields:
        result[clinic_log.__class__._get_field_title(field)] = getattr(
            clinic_log, field
        )
        if field == "peak_flow_requested":
            result["Peak flow received"] = bool(episode.peakflowday_set.all())
    return result


def extract_blood_results(patient, counts):
    bloods = patient.bloods_set.all()
    bloods_fields = [
        i for i in Bloods._get_fieldnames_to_extract() if i not in FIELDS_TO_IGNORE
    ]

    result = {}

    for idx, blood in enumerate(bloods, 1):
        for blood_field in bloods_fields:
            result[get_csv_field_name(Bloods, blood_field, idx, counts)] = getattr(
                blood, blood_field
            )

        for result_idx, blood_result in enumerate(blood.bloodresult_set.all(), 1):
            blood_result_fields = blood_result.get_fields()
            blood_result_fields.remove("allergen")
            blood_result_fields = ["allergen"] + blood_result_fields
            for blood_field in blood_result_fields:
                field_title = get_field_title(blood_result, blood_field)
                if counts > 1:
                    field_name = f"Bloods {idx} result {result_idx} {field_title}"
                else:
                    field_name = f"Bloods result {result_idx} {field_title}"
                result[field_name] = getattr(blood_result, blood_field)
    return result


def get_csv_field_name(subrecord_class, field_name, idx, counts):
    display_name = subrecord_class.get_display_name()
    field_name = subrecord_class._get_field_title(field_name)
    if getattr(subrecord_class, "_is_singleton", False) or counts == 1:
        csv_field_name = f"{display_name} {field_name}"
    else:
        csv_field_name = f"{display_name} {idx} {field_name}"
    return csv_field_name


def row_for_subrecords(subrecords, counts):
    if not subrecords:
        return {}
    subrecord_class = subrecords[0].__class__
    fields = subrecord_class._get_fieldnames_to_extract()
    fields = [i for i in fields if i not in FIELDS_TO_IGNORE]
    result = {}
    for idx, subrecord in enumerate(subrecords, 1):
        for field_name in fields:
            csv_field_name = get_csv_field_name(
                subrecord_class, field_name, idx, counts
            )
            result[csv_field_name] = getattr(subrecord, field_name)
    return result


def get_field_names(row_type, patient_id_to_row):
    """
    So we pass in a dict of dicts of dicts that looks something like
    patient_id: {subrecord_type: key_value_results_for_subrecord_types}
    we are looking for the row with the largest keys because that will
    be something like

    diagnosis_1_condition,
    diagnosis_2_condition,
    diagnosis_3_condition,
    diagnosis_4_condition,
    diagnosis_5_condition,

    so we can populate an empty field for rows that do no have this.
    """
    patient_dicts_for_subrecords = []
    for subrecord_to_values in patient_id_to_row.values():
        patient_dicts_for_subrecords.append(subrecord_to_values[row_type])

    patient_dicts_for_subrecords = sorted(
        list(patient_dicts_for_subrecords), key=lambda x: len(x.keys()), reverse=True
    )
    return list(patient_dicts_for_subrecords[0].keys())


def blood_sorting_function(key):
    splitted = key.split("result")
    if len(splitted) == 1:
        return (
            int(key.split(" ")[1]),
            0,
        )
    blood_int = int(key.split(" ")[1])
    result_int = int(splitted[1].split(" ")[1])
    return (
        blood_int,
        result_int,
    )


def get_bloods_field_names(patient_id_to_row):
    """
    So this is complicated...
    we have possible field names e.g.
    ['blood_1_result_1', 'blood_1_result_2']
    ['blood_1_result_1, 'blood_2_result_1']
    and we want to return
    ['blood_1_result_1', 'blood_1_result_2', 'blood_2_result_1']
    we can do this via sorting
    """
    blood_fields = set()
    for patient_id, row in patient_id_to_row.items():
        blood_fields = blood_fields.union(row["bloods"].keys())
        if "Bloods 9 result 7 RAST score" in row["bloods"].keys():
            print("=====")
            print(patient_id)
            print("=====")
    return sorted(list(blood_fields), key=blood_sorting_function)


def get_data(patient_qs, counts):
    rows = []
    patient_id_to_rows = {}

    for patient in patient_qs:
        row = {
            "demographics": extract_demographics(patient),
            "referral": extract_referrals(patient, counts["referral"]),
            "employment": extract_employment(patient, counts["employment"]),
            "social_history": extract_social_history(patient),
            "clinic_log": extract_clinic_log(patient),
            "asthma_details": extract_asthma_diagnosis(
                patient, counts["asthmadetails"]
            ),
            "rhinitis_details": extract_rhinitis_diagnosis(
                patient, counts["rhinitisdetails"]
            ),
            "other_diagnosis": extract_other_diagnosis(patient, counts["diagnosis"]),
            "spirometry": row_for_subrecords(
                patient.spirometry_set.all(), counts["spirometry"]
            ),
            "skinpricktest": row_for_subrecords(
                patient.skinpricktest_set.all(), counts["skinpricktest"]
            ),
            "bronchialtest": row_for_subrecords(
                patient.bronchialtest_set.all(), counts["bronchialtest"]
            ),
            "otherinvestigations": row_for_subrecords(
                patient.otherinvestigations_set.all(), counts["otherinvestigations"]
            ),
            "bloods": extract_blood_results(patient, counts["bloods"]),
        }
        patient_id_to_rows[patient.id] = row

    subrecords = list(patient_id_to_rows.values())[0].keys()
    subrecord_to_field_names = {
        subrecord: get_field_names(subrecord, patient_id_to_rows)
        for subrecord in subrecords
        if not subrecord == "bloods"
    }
    subrecord_to_field_names["bloods"] = get_bloods_field_names(patient_id_to_rows)
    rows = []
    for subrecord_to_row in patient_id_to_rows.values():
        row = {}
        for subrecord, subrecord_dict in subrecord_to_row.items():
            field_names = subrecord_to_field_names[subrecord]
            for field_name in field_names:
                row[field_name] = subrecord_dict.get(field_name, "")
        rows.append(row)
    return rows


def write_csv(patients, counts, directory):
    file_name = os.path.join(directory, "wide_dataset.csv")
    rows = get_data(patients, counts)
    with open(file_name, "w") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"written to {file_name}")


def prefetch_related(patient_qs):
    return patient_qs.prefetch_related(
        "episode_set__asthmadetails_set",
        "episode_set__rhinitisdetails_set",
        "episode_set__diagnosis_set",
        "episode_set__employment_set",
        "episode_set__referral_set",
        "spirometry_set",
        "skinpricktest_set",
        "bronchialtest_set",
        "otherinvestigations_set",
        "bloods_set",
        "bloods_set__bloodresult_set",
    )


def write_extract(episodes, directory, *args):
    reports_dir = os.path.join(directory, 'reports')
    if not os.path.exists(reports_dir):
        os.mkdir(reports_dir)
    patient_ids = set(
        Patient.objects.filter(episode__in=episodes)
        .distinct()
        .values_list("id", flat=True)
    )
    patient_qs = prefetch_related(Patient.objects.filter(id__in=patient_ids))
    counts = {}
    for field, model in [
        (
            "asthmadetails",
            AsthmaDetails,
        ),
        (
            "rhinitisdetails",
            RhinitisDetails,
        ),
        (
            "employment",
            Employment,
        ),
        (
            "referral",
            Referral,
        ),
    ]:
        qs = model.objects.filter(episode_id__patient_id__in=patient_ids)
        counts[field] = (
            qs.values("episode_id")
            .annotate(cnt=Count("episode_id"))
            .order_by("-cnt")[0]["cnt"]
        )

    counts["diagnosis"] = (
        Diagnosis.objects.filter(episode_id__patient_id__in=patient_ids)
        .filter(category__in=["Rhinitis", "Asthma"])
        .values("episode_id")
        .annotate(cnt=Count("episode_id"))
        .order_by("-cnt")[0]["cnt"]
    )

    for field in [
        "spirometry",
        "skinpricktest",
        "bronchialtest",
        "otherinvestigations",
        "bloods",
    ]:
        p = patient_qs.annotate(**{f"{field}_cnt": Count(field)}).order_by(
            f"-{field}_cnt"
        )[0]
        counts[field] = getattr(p, f"{field}_cnt")

    return write_csv(patient_qs, counts, reports_dir)
