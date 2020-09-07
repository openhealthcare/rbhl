from django.db import models as fields
from opal import models
from opal.core.fields import enum
from rbhl.models import RBHLSubrecord
from opal.core import lookuplists


COMMON_EXPOSURES = enum(
    "LAB ANIMALS",
    "FLOUR",
    "ISOCYANATES",
    "LATEX",
    "GEN ANIMALS",
    "ENZYMES",
    "HOUSE DUST MITES",
)


class Allergen(lookuplists.LookupList):
    pass


class Specimen(RBHLSubrecord, models.EpisodeSubrecord):
    _is_singleton = True
    sample_received = fields.DateField(blank=True, null=True)

    # an old id of the record.
    blood_number = fields.CharField(blank=True, null=True, max_length=200)
    blood_taken = fields.DateTimeField(blank=True, null=True)
    report_dt = fields.DateField(blank=True, null=True)
    report_st = fields.DateField(blank=True, null=True)
    store = fields.NullBooleanField(blank=True)


class Antigen(RBHLSubrecord, models.EpisodeSubrecord):
    _is_singleton = True

    # data has 193 different methods however more than half are made up
    # of 6 methods
    METHODS = enum(
        "ImmunoCAP",
        "UniCAP",
        "CAP",
        "RAST",
        "CAP & RAST",
        "RAST & UniCAP",
        "PRECIPITINS",
    )

    ANTIGEN_TYPE = enum("STANDARD", "BESPOKE")
    assay_no = fields.CharField(blank=True, null=True, max_length=200)
    assay_date = fields.DateField(blank=True, null=True)
    method = fields.CharField(blank=True, null=True, max_length=256, choices=METHODS)
    antigen_date = fields.DateField(blank=True, null=True)
    antigen_type = fields.CharField(
        blank=True, null=True, max_length=256, choices=ANTIGEN_TYPE
    )


class AllergenResult(RBHLSubrecord, models.EpisodeSubrecord):
    PRECIPITIN_CHOICES = enum("-ve", "+ve", "Weak +ve", '++ve')

    result = fields.TextField(blank=True, null=True, max_length=200)
    allergen = models.ForeignKeyOrFreeText(Allergen)
    antigen_no = fields.CharField(blank=True, null=True, max_length=200)
    # usually a float but can include '<' and '>'
    kul = fields.CharField(blank=True, null=True, max_length=200, verbose_name="KU/L")
    ige_class = fields.CharField(
        blank=True,
        null=True,
        max_length=200,
        verbose_name="IgE Class",
        choices=enum(*[str(i) for i in range(7)]),
    )
    rast = fields.FloatField(
        blank=True, null=True, verbose_name="RAST %B"
    )
    precipitin = fields.CharField(
        blank=True,
        null=True,
        max_length=200,
        verbose_name="Precipitin",
        choices=PRECIPITIN_CHOICES,
    )
    igg_mg = fields.FloatField(
        blank=True, null=True, verbose_name="mg/L"
    )
    # This has been filled in twice in the entire history, not sure if we need it.
    igg_class = fields.IntegerField(
        blank=True, null=True, verbose_name="IgG class"
    )
