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


class Bloods(RbhlSubrecord, models.PatientSubrecord):
    _exclude_from_extract = True
    _advanced_searchable = False

    ANTIGEN_TYPE = enum("STANDARD", "BESPOKE")
    METHODS = enum(
        "ImmunoCAP",
        "RAST",
        "RAST Score",
        "Precipitins"
    )

    blood_date         = fields.DateField(
        blank=True, null=True, verbose_name="Sample received"
    )
    blood_number       = fields.CharField(blank=True, null=True,
                                          max_length=200)
    method             = fields.CharField(
        blank=True, null=True, max_length=200, choices=METHODS
    )
    blood_collected    = fields.CharField(
        verbose_name='EDTA blood collected',
        blank=True, null=True,
        max_length=200)
    date_dna_extracted = fields.CharField(blank=True, null=True,
                                          max_length=200)
    assayno            = fields.CharField(
        blank=True, null=True, max_length=200, verbose_name="Assay number"
    )
    assay_date         = fields.DateField(blank=True, null=True)
    blood_taken        = fields.DateField(blank=True, null=True)
    blood_tm           = fields.CharField(blank=True, null=True, max_length=200)
    report_dt          = fields.DateField(
        blank=True, null=True, verbose_name="Report date"
    )
    report_st          = fields.DateField(
        blank=True, null=True, verbose_name="Report submitted"
    )
    store              = fields.NullBooleanField()
    exposure           = models.ForeignKeyOrFreeText(Exposure)
    antigen_date       = fields.DateField(blank=True, null=True)
    antigen_type       = fields.CharField(
        blank=True, null=True, choices=ANTIGEN_TYPE, max_length=200
    )
    comment            = fields.TextField(blank=True, null=True)
    # Batches was only ever used 10 times and hasn't been
    # used for 6 years. User says they don't need it.
    batches            = fields.TextField(blank=True, null=True)
    room               = fields.TextField(blank=True, null=True)
    freezer            = fields.TextField(blank=True, null=True)
    shelf              = fields.TextField(blank=True, null=True)
    tray               = fields.TextField(blank=True, null=True)
    vials              = fields.TextField(blank=True, null=True)

    @classmethod
    def _get_fieldnames_to_serialize(cls):
        result = super()._get_fieldnames_to_serialize()
        result.append("bloodresult")
        return result

    def get_bloodresult(self, user):
        result = []
        for bb_result in self.bloodresult_set.all():
            result.append(bb_result.to_dict())
        return result

    def set_bloodresult(self, value, user, data):
        existing_ids = [i["id"] for i in value if "id" in i]
        # you cannot save foriegn keys if the parent model (ie this)
        # does not have an id (ie has no id)
        if not self.id:
            self.save()
        self.bloodresult_set.exclude(id__in=existing_ids).delete()
        for result_dict in value:
            result_id = result_dict.get("id", None)
            if result_id:
                result = self.bloodresult_set.get(id=result_id)
            else:
                result = BloodResult(bloods=self)
            result.update_from_dict(result_dict)

    def get_employment(self):
        return self.patient.episode_set.last().employment_set.last()

    def get_referral(self):
        return self.patient.episode_set.last().referral_set.last()


class BloodResult(fields.Model):
    _exclude_from_extract = True
    _advanced_searchable = False

    NEGATIVE = "-ve"
    PRECIPITIN_CHOICES = enum(NEGATIVE, "+ve", "Weak +ve", '++ve')
    bloods = fields.ForeignKey(Bloods, on_delete=fields.CASCADE)
    result     = fields.CharField(blank=True, null=True, max_length=200)
    allergen   = models.ForeignKeyOrFreeText(Allergen)
    phadia_test_code  = fields.CharField(
        blank=True, null=True, max_length=200, verbose_name="Antigen number"
    )
    kul        = fields.CharField(
        blank=True, null=True, max_length=200, verbose_name="KU/L"
    )
    klass      = fields.IntegerField(
        blank=True,
        null=True,
        verbose_name="IgE Class",
    )
    rast        = fields.FloatField(blank=True, null=True)
    rast_score  = fields.FloatField(
        blank=True, null=True, verbose_name="RAST score"
    )
    precipitin  = fields.CharField(
        blank=True, null=True, max_length=200, choices=PRECIPITIN_CHOICES
    )
    igg         = fields.FloatField(blank=True, null=True)
    iggclass    = fields.IntegerField(
        blank=True, null=True, verbose_name="IgG Class"
    )

    def get_fields(self):
        blood_result_fields_to_dict = [
            i.name for i in self._meta.get_fields()
        ]
        blood_result_fields_to_dict.remove("allergen_fk")
        blood_result_fields_to_dict.remove("allergen_ft")
        blood_result_fields_to_dict.remove("bloods")
        blood_result_fields_to_dict.append("allergen")
        return blood_result_fields_to_dict

    def is_significant(self):
        # we are waiting for the exact details from the user
        if self.rast_score:
            return True
        if self.precipitin:
            if not self.precipitin == self.NEGATIVE:
                return True
        if self.rast and self.rast >= 2:
            return True
        if self.kul:
            # sometimes the user puts in < 0.1, < 0.35, > 100
            lt = False
            if "<" in self.kul:
                lt = True
            kul = self.kul.strip(" <>")
            try:
                kul = float(kul)
            except ValueError:
                return False
            if lt:
                if kul <= 0.35:
                    return False
            if kul >= 0.35:
                return True
        if self.igg:
            # any igg is significant
            return True
        return False

    def to_dict(self):
        fields = self.get_fields()
        result = {}
        for field in fields:
            result[field] = getattr(self, field)
        result["significant"] = self.is_significant()
        return result

    def update_from_dict(self, data):
        fields = self.get_fields()
        for field in fields:
            setattr(self, field, data.get(field))
        self.save()
