from django.core.management import BaseCommand
from collections import defaultdict
from opal.models import Episode


class Command(BaseCommand):
    def get_queryset(self):
        return Episode.objects.all().prefetch_related("peakflowday_set")

    def get_peak_flow_days_by_trial(self, peak_flow_days):
        result = defaultdict(list)
        peak_flow_days = sorted(peak_flow_days, key=lambda x: x.day_num)
        for i in peak_flow_days:
            result[i.trial_num].append(i)
        return result

    def aggregate_notes_to_strings(self, pfds):
        pfd_strs = [
            "Day {}: {}".format(
                pfd.day_num, pfd.note
            ) for pfd in pfds if pfd.note
        ]
        return ", ".join(pfd_strs)

    def handle(self, *args, **kwargs):
        episodes = self.get_queryset()
        for episode in episodes:
            peak_flow_days_by_trial = self.get_peak_flow_days_by_trial(
                episode.peakflowday_set.all()
            )
            for pfds in peak_flow_days_by_trial.values():
                pfd = pfds[0]
                pfd.note = self.aggregate_notes_to_strings(pfds)
                pfd.save()
                for pfd in pfds[1:]:
                    pfd.note = ""
                    pfd.save()
