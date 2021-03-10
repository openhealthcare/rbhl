import json
import more_itertools
import random
color = "%06x" % random.randint(0, 0xFFFFFF)
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
    "#3DB8C4",
    "#C4685A",
    "#1F4178",
    "#9FC433",
]

for i in range(40):
    COLORS.append("#%06x" % random.randint(0, 0xFFFFFF))


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
    'templatetags/stats/category_bar_chart.html'
)
def category_bar_chart(
    title, x_axis, field_vals, subtitle=False
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
        "html_id": title.lower().replace(" ", "_").replace("/", ""),
        "subtitle": subtitle
    }
    return ctx


@register.inclusion_tag(
    "templatetags/stats/pie_chart.html"
)
def pie_chart(
    title, field_vals
):
    """
    Takes in a title then a list of lists 
    where the first item is the name of the pie
    chart like the c3 api.
    """
    colors = {}
    for idx, field_val in enumerate(field_vals):
        colors[field_val[0]] = COLORS[idx]
    return {
        "html_id": title.lower().replace(" ", "_"),
        "graph": {
            "field_vals": json.dumps(field_vals),
            "colors": json.dumps(colors)
        },
        "table": {
            "field_vals": dict(field_vals),
            "colors": json.dumps(colors)
        },
        "title": title,
    }


@register.filter
def color(idx):
    return COLORS[idx]


@register.filter
def chunked(value, chunk_length):
    """
    Breaks a list up into a list of lists of size <chunk_length>
    """
    return more_itertools.divide(chunk_length, value)
