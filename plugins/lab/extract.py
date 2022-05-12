import os
from . import models
import csv
from collections import defaultdict
from django.core.exceptions import FieldDoesNotExist


def get_field_title(instance, name):
    """
    Get the verbose name of a field off an instance
    """
    model = instance.__class__
    try:
        return model._meta.get_field(name).verbose_name
    except FieldDoesNotExist:
        return getattr(model, name).verbose_name


def get_blood_result_rows(episodes):
    """
    Serialize blood results to a list of dicts that contain
    the full serialized version of their parent bloods
    and their own fields.
    """
    blood_results = models.BloodResult.objects.filter(
        bloods__patient__episode__in=episodes
    ).select_related("bloods")
    rows = []
    patient_id_to_episodes = defaultdict(set)
    for episode in episodes:
        patient_id_to_episodes[episode.patient_id].add(episode)

    bloods_fields_to_ignore = set(["id", "bloodresult", 'consistency_token'])
    bloods_fields = [
        i
        for i in models.Bloods._get_fieldnames_to_extract()
        if i not in bloods_fields_to_ignore
    ]

    for blood_result in blood_results:
        bloods = blood_result.bloods
        episodes = patient_id_to_episodes[bloods.patient_id]
        for episode in list(episodes):
            row = {"Episode": episode.id}
            for bloods_field in bloods_fields:
                bloods_field_title = bloods.__class__._get_field_title(bloods_field)
                row[bloods_field_title] = getattr(bloods, bloods_field)

            result_fields = blood_result.get_fields()
            result_fields = sorted(
                [i for i in result_fields if not i == "id"],
                key=lambda x: get_field_title(blood_result, x),
            )
            for result_field in result_fields:
                row[get_field_title(blood_result, result_field)] = getattr(
                    blood_result, result_field
                )
            rows.append(row)
    return rows


def write_rows(directory, rows):
    """
    Write a list of dicts to a file called blood_results.csv in
    the directory provided.
    """
    with open(os.path.join(directory, "blood_results.csv"), "w") as br:
        field_names = list(rows[0].keys())
        writer = csv.DictWriter(br, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(rows)


def add_blood_results(episodes, directory, *args):
    """
    Add in blood_results.csv which contains one row
    per blood result and all the fields on the blood_result
    and its parent bloods.
    """
    rows = get_blood_result_rows(episodes)
    if rows:
        write_rows(directory, rows)
