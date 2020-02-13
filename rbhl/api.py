"""
API endpoints for RBHL
"""
from collections import defaultdict
import itertools
from decimal import Decimal
from opal.core.views import json_response
from opal.core.api import LoginRequiredViewset, episode_from_pk
from rbhl.models import Demographics
from opal.core.api import OPALRouter


def get_ranges(numbers):
    if len(numbers) == 0:
        return []

    # compare the sequential range e.g [2, 3, 4] with the numbers entered
    # when they are different, we know we've varied
    sequential_range = range(numbers[0], numbers[0] + len(numbers))

    for idx, i in enumerate(sequential_range):
        if not i == numbers[idx]:
            sequence = {"start": numbers[0], "end": numbers[idx-1]}
            return [sequence] + get_ranges(numbers[idx:])

    return [{"start": numbers[0], "end": numbers[-1]}]


class PeakFlowGraphData(LoginRequiredViewset):
    base_name = "peak_flow_graph_data"

    def day_to_dict(self, peak_flow_day, pef):
        aggregates = peak_flow_day.get_aggregate_data()

        # if we have no peak flow days aggregates is None
        if aggregates is None:
            aggregates = {}

        result = {
            "treatment_taken": peak_flow_day.treatment_taken,
            "day_num": peak_flow_day.day_num,
            "date": peak_flow_day.date,
            "work_day": peak_flow_day.work_day,
            "pef_flow": pef,
            "min_flow": aggregates.get("min_flow"),
            "mean_flow": aggregates.get("mean_flow"),
            "max_flow": aggregates.get("max_flow"),
            "variabilty": aggregates.get("variabilty"),
            "num_entries": aggregates.get("num_entries")
        }

        return result

    def get_completeness(self, day_dicts):
        """
        A complete day is every day where the patient has
        added at least 6 entries.

        If they miss a day, that's a day counted as incomplete
        """

        all_total_days = [i["day_num"] for i in day_dicts]
        if not day_dicts:
            return
        total_days = max(all_total_days)

        entries = sum(
            [i["num_entries"] for i in day_dicts if i["num_entries"]]
        )

        completeness = Decimal(entries)/Decimal(total_days*6)
        return min(100, round(completeness * 100))

    def get_complete_days(self, day_dicts):
        """
        The data is considered significant if there are more than
        4 results (ideally there are at least 6)
        """
        return len([
            i for i in day_dicts if i["num_entries"] and i["num_entries"] >= 4
        ])

    def get_overrall_mean(self, days):
        nested_flow_values = [i.get_flow_values() for i in days]
        flow_values = list(itertools.chain(*nested_flow_values))
        if flow_values:
            return round(sum(flow_values)/len(flow_values))

    def get_treatments(self, days):
        """
        Looks at all treatments on the day dicts and tries
        to change them into a continuous timeline.

        End dates are inclusive.

        We aggregate by dru

        For example
        {
            'Aspirin': [
                {
                    start: 1,
                    end: 3
                },
                {
                    start: 4,
                    end: 4
                }
            ],
            'Paracetomol': [
                {
                    start: 2,
                    end: 2
                }
            ]
        }

        """
        treatments = defaultdict(list)
        treatment_days = [
            day for day in days if day.get('treatment_taken', None)
        ]
        if len(treatment_days) == 0:
            return {}

        for day in treatment_days:
            treatments[day['treatment_taken']].append(day['day_num'])

        return {t: get_ranges(treatments[t]) for t in treatments}

    def get_notes(self, peak_flow_days):
        return peak_flow_days[0].note

    def trial_data(self, demographics, peak_flow_days):
        if peak_flow_days:
            pef = demographics.get_pef(peak_flow_days[0].date)
            days = [self.day_to_dict(i, pef) for i in peak_flow_days]
        return {
            "days": days,
            "completeness": self.get_completeness(days),
            "complete_days": self.get_complete_days(days),
            "treatments": self.get_treatments(days),
            "overrall_mean": self.get_overrall_mean(peak_flow_days),
            "pef_mean": pef,
            "notes": self.get_notes(peak_flow_days)
        }

    @episode_from_pk
    def retrieve(self, request, episode):
        demographics = Demographics.objects.get(
            patient__episode=episode
        )

        groups = itertools.groupby(
            episode.peakflowday_set.order_by("trial_num", "day_num"),
            key=lambda x: x.trial_num
        )
        result = {
            k: self.trial_data(demographics, list(group))
            for k, group in groups
        }
        return json_response(result)


indigo_router = OPALRouter()
indigo_router.register(PeakFlowGraphData.base_name, PeakFlowGraphData)
