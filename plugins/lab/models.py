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
        null=True, blank=True, verbose_name="FEV 1 predicted"
    )
    fvc = fields.FloatField(null=True, blank=True, verbose_name="FVC")
    fvc_post_ventolin = fields.FloatField(
        null=True, blank=True, verbose_name="FVC post ventolin"
    )
    fvc_percentage_predicted = fields.IntegerField(
        null=True, blank=True, verbose_name="FVC predicted"
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

    antihistamines = fields.NullBooleanField(null=True, blank=True)
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


class SerializeRelated(object):
    """
    If a model has a ManyToOneRel with this object,
    ie an object has a foreign key to it, then serialize
    allow to_dict, update_from_dict models to cascade into
    that model.
    """
    def get_related_fields(self):
        related = []
        for field in self._meta.get_fields():
            if isinstance(field, fields.ManyToOneRel):
                related.append(field.name)
        return related

    def to_dict(self, *args, **kwargs):
        result = super().to_dict(*args, **kwargs)
        related_fields = self.get_related_fields()
        for field in related_fields:
            set_name = "{}_set".format(field)
            related_models = getattr(self, set_name).all()
            result[set_name] = [
                i.to_dict(*args, **kwargs) for i in related_models
            ]
        return result

    def update_related_field(self, field, data, user):
        set_name = "{}_set".format(field)
        update_set = data.pop(set_name, [])
        qs = getattr(self, set_name).all()

        update_ids = [i["id"] for i in update_set if "id" in i]

        # delete existing ids
        qs.exclude(id__in=update_ids).delete()

        for update_data in update_set:
            if "id" in update_data:
                instance = qs.get(id=update_data["id"])
            else:
                instance = getattr(self, set_name).create()
            instance.update_from_dict(update_data, user)

    def update_from_dict(self, data, user=None):
        fields = self.get_related_fields()
        for field in fields:
            self.update_related_field(field, data, user)
        return super().update_from_dict(data, user)


class Specimen(SerializeRelated, models.PatientSubrecord):
    # data has 193 different methods however more than half are made up
    # of 6 methods
    METHODS = enum(
        'ImmunoCAP',
        'UniCAP',
        'CAP',
        'RAST',
        'CAP & RAST',
        'RAST & UniCAP',
        'PRECIPITINS'
    )

    # There are 413 different exposures but with a long tail
    # they are usually...
    COMMON_EXPOSURES = enum(
        'LAB ANIMALS',
        'FLOUR',
        'ISOCYANATES',
        'LATEX',
        'GEN ANIMALS',
        'ENZYMES',
        'HOUSE DUST MITES'
    )

    ANTIGEN_TYPE = enum(
        'STANDARD', 'BESPOKE'
    )

    reference_number = fields.CharField(blank=True, default="", max_length=200)
    blood_date = fields.DateField(blank=True, null=True)
    blood_number = fields.CharField(blank=True, default="", max_length=200)
    method = fields.fields.CharField(
        blank=True, default="", max_length=256, choices=METHODS
    )
    information = fields.CharField(
        blank=True, default="", max_length=200
    )
    # usually a number but sometimes 2 numbers joined with an
    # ampersand
    assay_no = fields.CharField(
        blank=True, default="", max_length=256
    )
    assay_date = fields.DateField(blank=True, null=True)
    blood_taken = fields.DateField(blank=True, null=True)

    report_dt = fields.DateField(blank=True, null=True)
    report_st = fields.DateField(blank=True, null=True)

    store = fields.NullBooleanField(blank=True)
    exposure = fields.CharField(
        default="", blank=True, choices=COMMON_EXPOSURES, max_length=256
    )
    antigen_type = fields.CharField(
        default="", blank=True, choices=ANTIGEN_TYPE, max_length=256
    )
    comment = fields.TextField(blank=True, null=True)
    vials = fields.FloatField(blank=True, null=True)


class LabTest(
    SerializeRelated, models.UpdatesFromDictMixin, models.ToDictMixin, fields.Model
):
    _icon = "fa fa-crosshairs"
    consistency_token = fields.CharField(max_length=8)
    clinical_info = fields.TextField(null=True, blank=True)
    status = fields.CharField(max_length=256, blank=True, null=True)
    # the allergen
    test_name = fields.CharField(max_length=256, blank=True, null=True)
    # the allergen code
    test_code = fields.CharField(max_length=256, blank=True, null=True)
    created_at = fields.DateTimeField(auto_now_add=True)
    updated_at = fields.DateTimeField(auto_now=True)
    specimen = fields.ForeignKey(Specimen, on_delete=fields.CASCADE)


class Observation(
    models.UpdatesFromDictMixin, models.ToDictMixin, fields.Model
):
    consistency_token = fields.CharField(max_length=8)
    last_updated = fields.DateTimeField(blank=True, null=True)
    observation_name = fields.CharField(max_length=256, blank=True, null=True)
    observation_number = fields.CharField(max_length=256, blank=True, null=True)
    observation_value = fields.TextField(null=True, blank=True)
    reference_range = fields.CharField(max_length=256, blank=True, null=True)
    units = fields.CharField(max_length=256, blank=True, null=True)
    test = fields.ForeignKey(LabTest, on_delete=fields.CASCADE)
