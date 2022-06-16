import os
from pathlib import Path
from plugins.lab import models
import csv


def convert_boolean(x):
    """
    If x is truthy, return 1, else return an empty string
    """
    if not x:
        return ""
    return 1


def get_queryset(episodes):
    return (
        models.BloodResult.objects.filter(bloods__patient__episode__in=episodes)
        .distinct()
        .prefetch_related(
            "bloods__patient__demographics_set",
            "bloods__patient__episode_set__diagnosis_set",
            "bloods__patient__episode_set__asthmadetails_set",
            "bloods__patient__episode_set__rhinitisdetails_set",
            "bloods__patient__episode_set__cliniclog_set",
        )
        .select_related(
            "bloods__employment",
        )
    )


def write_extract(episodes, directory, *args, **kwargs):
    rows = []
    lab_tests = get_queryset(episodes)

    for lab_test in lab_tests:
        patient = lab_test.bloods.patient
        demographics = patient.demographics_set.all()[0]
        employment = lab_test.bloods.employment
        employer = ""
        oh_provider = ""
        if employment:
            employer = employment.employer
            oh_provider = employment.oh_provider
        diagnosis = {}
        asthma_trigger = []
        rhinitis_trigger = []
        first_visit = ""
        for episode in patient.episode_set.all():
            clinic_log = episode.cliniclog_set.get()
            if not first_visit:
                first_visit = clinic_log.clinic_date
            for d in episode.diagnosis_set.all():
                diagnosis[d.category.lower()] = True
                diagnosis[f"{d.category.lower()}_occupational"] = d.occupational
            for a in episode.asthmadetails_set.all():
                if a.trigger:
                    asthma_trigger.append(a.trigger)
            for r in episode.rhinitisdetails_set.all():
                if r.trigger:
                    rhinitis_trigger.append(r.trigger)
        pid = demographics.patient_id
        link = f"https://indigo-rbht.openhealthcare.org.uk/#/patient/{pid}"
        row = {
            "Patient": demographics.patient_id,
            "Indigo link": link,
            "Hospital number": demographics.hospital_number,
            "Name": demographics.name,
            "NHS number": demographics.nhs_number,
            "DOB": demographics.date_of_birth,
            "Gender": demographics.sex,
            "First visit": first_visit,
            "Employer": employer,
            "OH provider": oh_provider,
            "Asthma": convert_boolean(diagnosis.get("asthma")),
            "Asthma occupational": ", ".join(list(set([i for i in asthma_trigger]))),
            "Rhinitis": convert_boolean(diagnosis.get("rhinitis")),
            "Rhinitis occupational": ", ".join(
                list(set([i for i in rhinitis_trigger]))
            ),
            "Chronic air flow limitation": convert_boolean(
                diagnosis.get("chronic air flow limitation", "")
            ),
            "Chronic air flow limitation occupational": convert_boolean(
                diagnosis.get("chronic air flow limitation_occupational", "")
            ),
            "NAD": convert_boolean(diagnosis.get("nad", "")),
            "Malignancy": convert_boolean(diagnosis.get("malignancy", "")),
            "Malignancy occupational": convert_boolean(
                diagnosis.get("malignancy_occupational", "")
            ),
            "Benign pleural disease": convert_boolean(
                diagnosis.get("benign pleural disease")
            ),
            "Diffuse lung disease": convert_boolean(
                diagnosis.get("diffuse lung disease")
            ),
            "Diffuse lung disease occupational": convert_boolean(
                diagnosis.get("diffuse lung disease_occupational")
            ),
            "Breathing pattern dysfunction": convert_boolean(
                diagnosis.get("breathing pattern dysfunction")
            ),
            "Upper airway dysfunction": convert_boolean(
                diagnosis.get("upper airway dysfunction")
            ),
            "Irritant symptoms only": convert_boolean(
                diagnosis.get("irritant symptoms only", "")
            ),
            "Other": convert_boolean(diagnosis.get("other", "")),
            "Other occupational": convert_boolean(
                diagnosis.get("other_occupational", "")
            ),
            "Blood date": lab_test.bloods.blood_date,
            "Assay date": lab_test.bloods.assay_date,
            "Allergen": lab_test.allergen,
            "KU/L": lab_test.kul,
            "IgE Class": lab_test.klass,
            "RAST": lab_test.rast,
            "RAST score": lab_test.rast_score,
            "Precipitin": lab_test.precipitin,
            "IgG": lab_test.igg,
            "IgG Class": lab_test.iggclass,
        }
        rows.append(row)
    reports_dir = os.path.join(directory, "reports")
    if not os.path.exists(reports_dir):
        os.mkdir(reports_dir)
    file_name = os.path.join(reports_dir, "blood_results_and_key_facts.csv")
    if not rows:
        Path(file_name).touch()
        return

    with open(file_name, "w") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
