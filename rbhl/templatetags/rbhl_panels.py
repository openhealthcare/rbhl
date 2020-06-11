from opal.core import fields
from django.db import models
from opal.core.subrecords import get_subrecord_from_model_name
from opal.templatetags.forms import extract_common_args, _radio
from django import template

register = template.Library()


def _model_and_field_from_path(fieldname):
    model_name, field_name = fieldname.split(".")
    model = get_subrecord_from_model_name(model_name)
    field = None

    if hasattr(model, field_name):
        # this is true for lookuplists
        lookuplist_field = getattr(model, field_name)
        if isinstance(lookuplist_field, fields.ForeignKeyOrFreeText):
            field = lookuplist_field
    if not field:
        field = model._meta.get_field(field_name)
    return model, field


def is_date(field):
    return isinstance(field, (models.DateField, models.DateTimeField,))


def is_boolean(field):
    return isinstance(field, (models.BooleanField, models.NullBooleanField,))


@register.inclusion_tag(
    'templatetags/rbhl_panels/field_display.html',
    takes_context=True
)
def field_display(
    context, field, **kwargs
):
    ctx = {}
    model_and_field_name = field
    ctx["field_name"] = model_and_field_name.split(".")[1]
    model, field = _model_and_field_from_path(model_and_field_name)
    ctx["label"] = kwargs.get(
        "label", model._get_field_title(ctx["field_name"])
    )
    ctx["label_size"] = kwargs.get(
        "label_size", context.get("label_size", 8)
    )

    ctx["field_size"] = kwargs.get(
        "field_size", context.get("label_field_sizesize", 4)
    )
    ctx["is_boolean"] = is_boolean(field)
    ctx["is_date"] = is_date(field)
    return ctx


@register.inclusion_tag(
    'templatetags/rbhl_panels/add_button.html',
    takes_context=True
)
def add_button(context, subrecord, is_singleton=False, link=None):
    """
    A button to add a subrecord.
    """
    return {
        "subrecord": subrecord,
        "link": link
    }


@register.inclusion_tag(
    'templatetags/rbhl_panels/test_field.html',
    takes_context=True
)
def test_field(
    context, field, **kwargs
):
    ctx = {}
    model_and_field_name = field
    ctx["field_name"] = model_and_field_name.split(".")[1]
    model, field = _model_and_field_from_path(model_and_field_name)
    ctx["label"] = kwargs.get(
        "label", model._get_field_title(ctx["field_name"])
    )
    ctx["is_date"] = is_date(field)
    ctx["is_boolean"] = is_boolean(field)
    ctx["unit"] = kwargs.get("unit", "")
    return ctx


@register.inclusion_tag(
    'templatetags/rbhl_panels/add_to_text_button.html',
)
def add_to_text_button(
    field, text, **kwargs
):
    model_and_field_name = field
    field_name = model_and_field_name.split(".")[1]
    model, _ = _model_and_field_from_path(model_and_field_name)

    ctx = {
        "editing": "editing.{}.{}".format(
            model.get_api_name(), field_name
        ),
        "text": text
    }
    return ctx


@register.inclusion_tag(
    'templatetags/rbhl_panels/choice_or_other.html',
)
def choice_or_other(**kwargs):
    """
    Creates a radio box or other string field.

    It works by using a directive that means the input
    box is not directly updating the model field but instead
    only updating it on ng-change handler.

    The radio buttons do update the model but on change they
    set the field used on the radio button to an empty string.
    """
    ctx = extract_common_args(kwargs)
    model, field = _model_and_field_from_path(kwargs["field"])
    ctx["field_ame"] = kwargs["field"].split(".")[1]
    ctx["model_and_field"] = kwargs["field"]
    ctx["input_model"] = "editing.{}._client.{}".format(
        model.get_api_name(), kwargs["field"].split(".")[1]
    )
    ctx["columns"] = kwargs.get("columns")
    ctx["change_input"] = "{}=other.field".format(
        ctx["model"]
    )
    ctx["change_radio"] = "other.field=''"
    return ctx


@register.inclusion_tag('templatetags/rbhl_panels/radio_columns.html')
def radio_columns(*args, **kwargs):
    return _radio(*args, **kwargs)
