"""
Management command that provides the most complete model
"""
import collections
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from legacy.models import Details

ohc = User.objects.get(username='ohc')


class Command(BaseCommand):
    def handle(self, *a, **k):
        value_counts = collections.defaultdict(list)
        for detail in Details.objects.all():
            num_values = sum([1 for x in detail.to_dict(user=ohc).values() if x])
            value_counts[num_values].append(detail)

        for key in sorted(value_counts.keys())[-1:]:
            for detail in value_counts[key]:
                print("{}".format(detail.patient.demographics().name))
        return
