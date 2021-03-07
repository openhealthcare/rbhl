import json
from django import template

register = template.Library()

COLORS = [
    "#4676c5",
    "#d01c17",
    "#2e993e",
    "#e18400",
    "#3a8a8a",
    "#785713",
    "#75AAFF",
    "#C4B233",
    "#3DB8C4"
]


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


@register.inclusion_tag(
    'templatetags/stats/category_bar_chart.html',
    takes_context=True,
)
def category_bar_chart(
    context, title, x_axis, field_vals
):
    """
    Takes in a title, the x_axis, then a list of the
    other values with the first value being the name
    of the name of the row.

    Essentially the same as the c3 api.
    """
    colors = {}
    for idx, field_val in enumerate(field_vals):
        colors[field_val[0]] = COLORS[idx]
    ctx = {
        "table": {
            "x_axis": x_axis,
            "field_vals": field_vals,
        },
        "graph": {
            "x_axis": json.dumps(x_axis),
            "field_vals": json.dumps(field_vals),
            "colors": json.dumps(colors)
        },
        "title": title,
        "html_id": title.lower().replace(" ", "_")
    }
    return ctx


@register.filter
def color(idx):
    return COLORS[idx]
