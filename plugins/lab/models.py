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


class Allergen(lookuplists.LookupList):
    pass


class Exposure(lookuplists.LookupList):
    pass


class BloodBook(RbhlSubrecord, models.PatientSubrecord):
    ANTIGEN_TYPE = enum("STANDARD", "BESPOKE")
    METHODS = enum(
        "ImmunoCAP",
        "UniCAP",
        "CAP",
        "RAST",
        "CAP & RAST",
        "RAST & UniCAP",
        "PRECIPITINS",
    )

    # we're storing this because it comes in, but won't display it
    # on the front end
    reference_number = fields.CharField(blank=True, null=True, max_length=256)

    # Blood details

    # This is called Blooddat
    sample_received = fields.DateField(blank=True, null=True)
    # an old id of the blood result.
    blood_number = fields.CharField(blank=True, null=True, max_length=200)
    blood_taken = fields.DateTimeField(blank=True, null=True)
    store = fields.NullBooleanField(blank=True)

    # antigen test details
    assay_number = fields.CharField(blank=True, null=True, max_length=200)
    assay_date = fields.DateField(blank=True, null=True)
    method = fields.CharField(blank=True, null=True, max_length=256, choices=METHODS)
    antigen_type = fields.CharField(
        blank=True, null=True, max_length=256, choices=ANTIGEN_TYPE
    )
    antigen_date = fields.DateField(blank=True, null=True)

    # report information these fields don't appear on the
    # front end so first version won't display them.

    # this is the field in the csv called reportdt
    report_date = fields.DateField(blank=True, null=True)

    # this is the field in the csv called reportst
    report_submitted = fields.DateField(blank=True, null=True)

    # A free text box for additional information
    information = fields.TextField(blank=True, default="")

    def get_result_fields(self):
        fields = [
            i.name for i in BloodBookResult._meta.get_fields()
        ]
        fields.remove("allergen_fk")
        fields.remove("allergen_ft")
        fields.remove("blood_book")
        fields.append("allergen")
        return fields

    def to_dict(self, user, fields=None):
        if fields is None:
            fields = self._get_fieldnames_to_serialize()
        if "bloodbookresult_set" in fields:
            fields.remove("bloodbookresult_set")
        as_dict = super().to_dict(user, fields=fields)
        as_dict["bloodbookresult_set"] = []

        for blood_book_result_set in self.bloodbookresult_set.all():
            result = {}
            for field in self.get_result_fields():
                result[field] = getattr(blood_book_result_set, field)
            as_dict["bloodbookresult_set"].append(result)
        return as_dict

    def update_from_dict(self, data, *args, **kwargs):
        if "bloodbookresult_set" in data:
            bloodbookresult_set = data.pop("bloodbookresult_set")
        else:
            bloodbookresult_set = []
        super().update_from_dict(data, *args, **kwargs)
        update_ids = [i["id"] for i in bloodbookresult_set]

        # delete the ones that have been removed
        self.bloodbookresult_set.exclude(id__in=update_ids).delete()

        for result_dict in bloodbookresult_set:
            if "id" in result_dict:
                result = self.bloodbookresult_set.get(id=result_dict["id"])
            else:
                result = BloodBookResult(blood_book=self)
            for field in self.get_result_fields():
                update_value = result_dict.get(field, None)
                setattr(result, field, update_value)
            result.save()


class BloodBookResult(fields.Model):
    PRECIPITIN_CHOICES = enum("-ve", "+ve", "Weak +ve", '++ve')

    blood_book = fields.ForeignKey(BloodBook, on_delete=fields.CASCADE)
    result = fields.TextField(blank=True, null=True, max_length=200)
    allergen = models.ForeignKeyOrFreeText(Allergen)
    antigen_number = fields.CharField(blank=True, null=True, max_length=200)

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
