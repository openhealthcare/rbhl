from collections import defaultdict
from decimal import Decimal
from opal.core.views import json_response
from opal.core.api import LoginRequiredViewset, episode_from_pk
from rbhl.models import Demographics
from opal.core.api import OPALRouter


class PeakFlowGraphData(LoginRequiredViewset):
    base_name = "peak_flow_graph_data"

    def day_to_dict(self, peak_flow_day, demographics):
        aggregates = peak_flow_day.get_min_max_variability_completeness()
        pef_flow = None

        if peak_flow_day.date:
            pef_flow = demographics.get_pef(peak_flow_day.date)

        result = {
            "note": peak_flow_day.note,
            "treatment_taken": peak_flow_day.treatment_taken,
            "day_num": peak_flow_day.day_num,
            "date": peak_flow_day.date,
            "pef_flow": pef_flow,
            "work_day": peak_flow_day.work_day,
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
            [i for i in day_dicts if "complete" in i and i["complete"]]
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

    def get_pef_mean(self, day_dicts):
        pefs = [i["pef_flow"] for i in day_dicts if "pef_flow" in i]
        if pefs:
            return round(sum(pefs)/len(pefs))

    def get_treatments(self, day_dicts):
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
        treatments = []
        treatment = {}

        for day_dict in day_dicts:
            if day_dict["treatment_taken"]:
                if treatment.get("treatment") == day_dict["treatment_taken"]:
                    continue
                elif treatment:
                    treatment["end"] = day_dict["day_num"] - 1
                    treatments.append(treatment)
                    treatment = {}
                treatment["start"] = day_dict["day_num"]
                treatment["treatment"] = day_dict["treatment_taken"]
            elif treatment:
                treatment["end"] = day_dict["day_num"] - 1
                treatments.append(treatment)
                treatment = {}

        if treatment:
            treatment["end"] = day_dict["day_num"]
            treatments.append(treatment)
        result = defaultdict(list)
        for treatment in treatments:
            result[treatment["treatment"]].append({
                "start": treatment["start"],
                "end": treatment["end"],
            })
        return result

    def get_notes(self, pfds):
        return [{
            "date": pfd.date,
            "trial_num": pfd.trial_num,
            "detail": pfd.note
        } for pfd in pfds if pfd.note]

    def trial_data(self, trial_num, demographics, pfds):
        days = [self.day_to_dict(i, demographics) for i in pfds]
        return {
            "days": days,
            "completeness": self.get_completeness(days),
            "treatments": self.get_treatments(days),
            "overrall_mean": self.get_overrall_mean(days),
            "pef_mean": self.get_pef_mean(days),
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
