from rbhl.models import (
    Referral, RBHReferrer, Employment, Employer, OHProvider
)
from django.core.management import BaseCommand
from django.db.models import Count
from django.conf import settings
import json
import os


FIELDS = {
    Referral: [
        ("referrer_name", RBHReferrer)
    ],
    Employment: [
        ("employer", Employer),
        ("oh_provider", OHProvider)
    ]
}

LOOKUP_LIST_PATH = "{}/data/lookuplists/{}.json"


def get_common(model, field):
    qs = model.objects.exclude(**{field: ""})
    qs = qs.values(field).annotate(count=Count(field))
    qs = qs.exclude(count__lte=3)
    return [i[field] for i in qs]


def create_look_list(lookup_list, common):
    lookup_list_path = LOOKUP_LIST_PATH.format(
        settings.PROJECT_PATH,
        lookup_list.get_api_name()
    )

    if os.path.exists(lookup_list_path):
        print("Found {}, deleting".format(lookup_list_path))
        os.remove(lookup_list_path)
    with open(lookup_list_path, "w+") as ll_file:
        ll_list = {
            lookup_list.__name__.lower(): [
                {"name": i} for i in common
            ]
        }

        json.dump(ll_list, ll_file)
        print("Writing {} results to {}".format(
            len(common), ll_file
        ))


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for model, x in FIELDS.items():
            for field, lookup_list in x:
                common = get_common(model, field)
                create_look_list(lookup_list, common)
