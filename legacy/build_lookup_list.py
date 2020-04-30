from collections import defaultdict
from django.db.models import Count
from opal.core.fields import ForeignKeyOrFreeText


THRESHOLD = 5


def get_distinct_count(case_sensitive_count):
    """
    Returns a case insensitive count, keyed
    by the most popular case sensitive value
    Takes in e.g. {
        Horse: 10,
        Cat 11,
        horse: 3
    }

    return {
        Horse: 13,
        Cat: 11
    }
    """
    as_tuple = case_sensitive_count.items()
    case_insensitive_count = defaultdict(int)

    for k, v in as_tuple:
        case_insensitive_count[k.lower()] += v

    by_popularity = sorted(as_tuple, key=lambda x: x[1], reverse=True)
    result = {}
    seen = set()
    for case_sensitive_value, _ in by_popularity:
        lower_case = case_sensitive_value.lower()
        if lower_case in seen:
            continue
        seen.add(lower_case)
        result[case_sensitive_value] = case_insensitive_count[lower_case]
    return result


def get_values_to_add(model, field):
    """
    Returns a list of values to be added to the lookup lists
    """
    qs = model.objects.values(field.ft_field_name).annotate(
        count=Count(field.ft_field_name)
    )
    case_sensitive_count = {i[field.ft_field_name]: i["count"] for i in qs}

    # Remove none and empty string
    case_sensitive_count = {k: v for k, v in case_sensitive_count.items() if k}

    # Count of distinct case insensitive values,
    # keyed by the most popular case sensitive value
    distinct_count = get_distinct_count(case_sensitive_count)
    popular_values = [k for k, v in distinct_count.items() if v >= THRESHOLD]
    return popular_values


def add_values_to_lookup_lists(lookup_list, values):
    """
    Creates instance of the lookup list if the value is are not already there
    """
    to_create = []
    existing_values = set([i.lower() for i in lookup_list.objects.values_list(
        'name', flat=True)
    ])
    for value in values:
        if value.lower() not in existing_values:
            to_create.append(lookup_list(name=value))
    lookup_list.objects.bulk_create(to_create)
    return len(to_create)


def resave_models(model, field):
    """
    Resaves the models if they have a value that it now in the lookup list
    """
    saved = 0
    ft_field = field.ft_field_name
    fk_field = field.fk_field_name
    qs = model.objects.filter(**{fk_field: None})
    for instance in qs:
        if getattr(instance, fk_field):
            continue
        value = getattr(instance, ft_field)
        if not value:
            continue
        setattr(instance, field.name, value)
        if getattr(instance, fk_field):
            instance.save()
            saved += 1
    return saved


def build_lookup_list(model, field):
    """
    Add to the fields lookup list based on the values in
    model.field. Resave the model.field when appropriate
    to use the lookup list.

    Return number of values added to the LL, number of models
    updated
    """
    if not isinstance(field, ForeignKeyOrFreeText):
        raise ValueError("{} is not an FKorFT field".format(field))
    lookup_list = field.foreign_model
    new_values = get_values_to_add(model, field)
    added = add_values_to_lookup_lists(lookup_list, new_values)
    updated = resave_models(model, field)
    return added, updated
