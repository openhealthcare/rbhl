"""
API endpoints for RBHL
"""
from collections import defaultdict
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

    def day_to_dict(self, peak_flow_day, demographics, pef):
        aggregates = peak_flow_day.get_min_max_variability_completeness()

        result = {
            "note": peak_flow_day.note,
            "treatment_taken": peak_flow_day.treatment_taken,
            "day_num": peak_flow_day.day_num,
            "date": peak_flow_day.date,
            "work_day": peak_flow_day.work_day,
            "pef_flow": pef
        }

        if not aggregates:
            return result
        else:
            (
                min_flow, max_flow, mean_flow, variabilty, completeness
            ) = aggregates

        result["min_flow"] = min_flow
        result["mean_flow"] = mean_flow
        result["max_flow"] = max_flow
        result["variabilty"] = variabilty
        result["completeness"] = completeness
        return result

    def get_completeness(self, day_dicts):
        """
        A complete day is every day where the patient has
        added at least 6 entries.

        If they miss a day, that's a day counted as incomplete
        """

        all_total_days = [i["day_num"] for i in day_dicts if "min_flow" in i]

        if not all_total_days:
            return

        total_days = max(all_total_days)

        completed_days = len(
            [i for i in day_dicts if "completeness" in i and i["completeness"]]
        )
        if total_days:
            completeness = Decimal(completed_days)/Decimal(total_days)
        else:
            completeness = 0

        return round(completeness) * 100

    def get_overrall_mean(self, day_dicts):
        means = [i["mean_flow"] for i in day_dicts if "mean_flow" in i]
        if means:
            return round(sum(means)/len(means))

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

    def get_notes(self, pfds):
        return [{
            "date": pfd.date,
            "trial_num": pfd.trial_num,
            "detail": pfd.note
        } for pfd in pfds if pfd.note]

    def trial_data(self, trial_num, demographics, pfds):
        if pfds:
            pef = demographics.get_pef(pfds[0].date)
            days = [self.day_to_dict(i, demographics, pef) for i in pfds]

        return {
            "days": days,
            "completeness": self.get_completeness(days),
            "treatments": self.get_treatments(days),
            "overrall_mean": self.get_overrall_mean(days),
            "pef_mean": pef,
            "notes": self.get_notes(pfds)
        }

    @episode_from_pk
    def retrieve(self, request, episode):
        trial_num_to_peak_flow_day = defaultdict(list)
        for pfd in episode.peakflowday_set.order_by("day_num"):
            trial_num_to_peak_flow_day[pfd.trial_num].append(pfd)

        demographics = Demographics.objects.get(
            patient__episode=episode
        )
        result = {}
        for trial_num, pfds in trial_num_to_peak_flow_day.items():
            result[trial_num] = self.trial_data(
                trial_num, demographics, pfds
            )
        return json_response(result)


indigo_router = OPALRouter()
indigo_router.register(PeakFlowGraphData.base_name, PeakFlowGraphData)
