from opal.templatetags.forms import extract_common_args, datepicker
from django import template

register = template.Library()


@register.inclusion_tag('templatetags/rbhl_forms/rbhl_number.html')
def rbhl_number(*args, **kwargs):
    """
    A number field similar to the opal fields input
    but accepts a label class and a field class for finer tuning
    """
    ctx = extract_common_args(kwargs)
    if "style" not in kwargs:
        ctx["style"] = "vertical"
    if ctx["style"] == "horizontal":
        ctx["label_class"] = kwargs.get("label_class", "control-label col-sm-3")
        ctx["field_class"] = kwargs.get("field_class", "col-sm-8")
    else:
        ctx["label_class"] = kwargs.get("label_class", "")
        ctx["field_class"] = kwargs.get("field_class", "")
    return ctx


@register.inclusion_tag('templatetags/rbhl_forms/rbhl_datepicker.html')
def rbhl_datepicker(*args, **kwargs):
    """
    A number field similar to the opal fields datepicker
    but accepts a label class and a field class for finer tuning
    """
    ctx = datepicker(**kwargs)
    if "style" not in kwargs:
        ctx["style"] = "vertical"
    if ctx["style"] == "horizontal":
        ctx["label_class"] = kwargs.get("label_class", "control-label col-sm-2")
        ctx["field_class"] = kwargs.get("field_class", "col-sm-10")
    else:
        ctx["label_class"] = kwargs.get("label_class", "control-label")
        ctx["field_class"] = kwargs.get("field_class", "")
    return ctx


@register.inclusion_tag('templatetags/rbhl_forms/rbhl_checkbox.html')
def rbhl_checkbox(*args, **kwargs):
    """
    A number field similar to the opal fields checkbox
    but accepts a label class and a field class for finer tuning
    """
    ctx = extract_common_args(kwargs)
    if "style" not in kwargs:
        ctx["style"] = "vertical"
    if ctx["style"] == "horizontal":
        ctx["label_class"] = kwargs.get("label_class", "col-sm-offset-3")
    else:
        ctx["label_class"] = kwargs.get("label_class", "")
    return ctx


@register.inclusion_tag('templatetags/rbhl_forms/rbhl_radio.html')
def rbhl_radio(*args, **kwargs):
    """
    A number field similar to the opal fields checkbox
    but accepts a label class for finer tuning
    """
    ctx = extract_common_args(kwargs)
    if "style" not in kwargs:
        ctx["style"] = "vertical"
    if ctx["style"] == "horizontal":
        ctx["label_class"] = kwargs.get("label_class", "control-label col-sm-3")
        ctx["field_class"] = kwargs.get("field_class", "col-sm-8")
    else:
        ctx["label_class"] = kwargs.get("label_class", "control-label")
        ctx["field_class"] = kwargs.get("field_class", "")
    return ctx
