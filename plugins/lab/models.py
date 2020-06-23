"""
Models for lab
"""
from rbhl.models import RBHLSubrecord as RbhlSubrecord
from django.db import models as fields
from opal import models
from opal.core.fields import enum
from opal.core import lookuplists


class Spirometry(RbhlSubrecord, models.PatientSubrecord):
    _icon = "fa fa-crosshairs"

    date = fields.DateField(blank=True, null=True)
    fev_1 = fields.FloatField(
        null=True, blank=True, verbose_name="FEV 1"
    )
    fev_1_post_ventolin = fields.FloatField(
        null=True, blank=True, verbose_name="FEV post ventolin"
    )
    fev_1_percentage_predicted = fields.IntegerField(
        null=True, blank=True, verbose_name="FEV 1 % predicted"
    )
    fvc = fields.FloatField(null=True, blank=True, verbose_name="FVC")
    fvc_post_ventolin = fields.FloatField(
        null=True, blank=True, verbose_name="FVC post ventolin"
    )
    fvc_percentage_predicted = fields.IntegerField(
        null=True, blank=True, verbose_name="FVC % predicted"
    )


class SkinPrickTest(RbhlSubrecord, models.PatientSubrecord):
    _icon = "fa fa-crosshairs"
    NEG_CONTROL = "Neg control"
    POS_CONTROL = "Pos control"
    ASP_FUMIGATUS = "Asp. fumigatus"
    GRASS_POLLEN = "Grass pollen"
    CAT = "Cat"
    HOUSE_DUST_MITE = "House dust mite"

    # This is the order the tests are taken
    # so the order they would like to enter/see them
    ROUTINE_TESTS = [
        NEG_CONTROL,
        POS_CONTROL,
        ASP_FUMIGATUS,
        GRASS_POLLEN,
        CAT,
        HOUSE_DUST_MITE
    ]

    antihistimines = fields.NullBooleanField(null=True, blank=True)
    substance = fields.TextField(
        blank=True, verbose_name="SPT", default=""
    )
    wheal = fields.FloatField(null=True, blank=True)
    date = fields.DateField(null=True, blank=True)


class BronchialChallengeSubstance(lookuplists.LookupList):
    pass


class BronchialTest(RbhlSubrecord, models.PatientSubrecord):
    _icon = "fa fa-crosshairs"

    BRONCHIAL_TEST_RESULTS = enum(
        'Positive',
        'Negative',
        'Inconclusive',
    )

    IMMEDIATE = 'Immediate'

    BRONCHIAL_RESPONSE_TYPES = enum(
        IMMEDIATE,
        'Dual',
        'Late',
        'Early',
        'Other',
    )

    result = fields.CharField(
        blank=True, default="", choices=BRONCHIAL_TEST_RESULTS, max_length=256
    )
    response_type = fields.CharField(
        blank=True,
        max_length=256,
        default=IMMEDIATE,
        choices=BRONCHIAL_RESPONSE_TYPES
    )
    last_exposed = fields.DateTimeField(null=True, blank=True)
    duration_exposed = fields.TextField(default="", blank=True)
    date = fields.DateField(null=True, blank=True)
    substance = models.ForeignKeyOrFreeText(BronchialChallengeSubstance)
    baseline_pc20 = fields.CharField(
        verbose_name="Baseline PC20", blank=True, default="", max_length=256
    )
    lowest_pc20 = fields.CharField(
        verbose_name="Lowest PC20", blank=True, default="", max_length=256
    )


class OtherInvestigations(RbhlSubrecord, models.PatientSubrecord):
    _icon = "fa fa-crosshairs"

    CT_CHEST_SCAN = "CT chest scan"
    FULL_LUNG_FUNCTION = "Full lung function"
    TEST_TYPE = enum(CT_CHEST_SCAN, FULL_LUNG_FUNCTION)

    date = fields.DateField(null=True, blank=True)
    test = fields.CharField(
        choices=TEST_TYPE, blank=True, default="", max_length=256
    )
    details = fields.TextField(blank=True, default="")
