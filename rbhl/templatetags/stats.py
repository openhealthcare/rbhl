from django import template

register = template.Library()


@register.inclusion_tag(
    'templatetags/stats/value_display.html'
)
def value_display(value):
    if value is None:
        value = ""
    is_bool = False
    is_list = False

    if isinstance(value, list):
        is_list = True

    if isinstance(value, bool):
        is_bool = True

    return {
        "value": value,
        "is_bool": is_bool,
        "is_list": is_list
    }
