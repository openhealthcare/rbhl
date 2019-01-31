from opal.core import fields
from django.db import models
from opal.core.subrecords import get_subrecord_from_model_name
from django import template

register = template.Library()


def _model_and_field_from_path(fieldname):
    model_name, field_name = fieldname.split(".")
    model = get_subrecord_from_model_name(model_name)
    field = None

    if hasattr(model, field_name):
        # this is true for lookuplists
        lookuplist_field = getattr(model, field_name)
        if lookuplist_field.__class__ == fields.ForeignKeyOrFreeText:
            field = lookuplist_field

    if not field:
        field = model._meta.get_field(field_name)
    return model, field

def is_date(field):
    return isinstance(field, (models.DateField, models.DateTimeField,))

def is_boolean(field):
    return isinstance(field, (models.BooleanField, models.NullBooleanField,))


@register.inclusion_tag('templatetags/rbhl_panels/field_display.html')
def field_display(**kwargs):
    ctx = {}
    model_and_field_name = kwargs.pop("field")
    ctx["field_name"] = model_and_field_name.split(".")[1]
    model, field = _model_and_field_from_path(model_and_field_name)
    ctx["label"] = model._get_field_title(ctx["field_name"])
    ctx["is_boolean"] = is_boolean(field)
    ctx["is_date"] = is_date(field)
    return ctx