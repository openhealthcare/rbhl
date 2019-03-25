# Generated by Django 2.0.13 on 2019-03-25 13:59

from django.db import migrations


def empty_strings_to_none(apps, schema_editor):
    DiagnosticOther = apps.get_model("legacy", "DiagnosticOther")
    DiagnosticOther.objects.filter(copd="").update(copd=None)
    DiagnosticOther.objects.filter(emphysema="").update(emphysema=None)
    DiagnosticOther.objects.filter(copd_with_emphysema="").update(
        copd_with_emphysema=None
    )
    DiagnosticOther.objects.filter(copd_is_occupational="").update(
        copd_is_occupational=None
    )
    DiagnosticOther.objects.filter(malignancy="").update(malignancy=None)
    DiagnosticOther.objects.filter(malignancy_is_occupational="").update(
        malignancy_is_occupational=None
    )
    DiagnosticOther.objects.filter(NAD="").update(NAD=None)
    DiagnosticOther.objects.filter(diffuse_lung_disease="").update(
        diffuse_lung_disease=None
    )
    DiagnosticOther.objects.filter(
        diffuse_lung_disease_is_occupational=""
    ).update(diffuse_lung_disease_is_occupational=None)
    DiagnosticOther.objects.filter(benign_pleural_disease="").update(
        benign_pleural_disease=None
    )
    DiagnosticOther.objects.filter(other_diagnosis="").update(
        other_diagnosis=None
    )
    DiagnosticOther.objects.filter(other_diagnosis_is_occupational="").update(
        other_diagnosis_is_occupational=None
    )


def none_to_empty_string(apps, schema_editor):
    DiagnosticOther = apps.get_model("legacy", "DiagnosticOther")
    DiagnosticOther.objects.filter(copd=None).update(copd="")
    DiagnosticOther.objects.filter(emphysema=None).update(emphysema="")
    DiagnosticOther.objects.filter(copd_with_emphysema=None).update(
        copd_with_emphysema=""
    )
    DiagnosticOther.objects.filter(copd_is_occupational=None).update(
        copd_is_occupational=""
    )
    DiagnosticOther.objects.filter(malignancy=None).update(malignancy="")
    DiagnosticOther.objects.filter(malignancy_is_occupational=None).update(
        malignancy_is_occupational=""
    )
    DiagnosticOther.objects.filter(NAD=None).update(NAD="")
    DiagnosticOther.objects.filter(diffuse_lung_disease=None).update(
        diffuse_lung_disease=""
    )
    DiagnosticOther.objects.filter(
        diffuse_lung_disease_is_occupational=None
    ).update(diffuse_lung_disease_is_occupational="")
    DiagnosticOther.objects.filter(benign_pleural_disease=None).update(
        benign_pleural_disease=""
    )
    DiagnosticOther.objects.filter(other_diagnosis=None).update(
        other_diagnosis=""
    )
    DiagnosticOther.objects.filter(
        other_diagnosis_is_occupational=None,
    ).update(
        other_diagnosis_is_occupational=""
    )


class Migration(migrations.Migration):

    dependencies = [("legacy", "0019_auto_20190325_1317")]

    operations = [
        migrations.RunPython(
            empty_strings_to_none, reverse_code=none_to_empty_string
        )
    ]
