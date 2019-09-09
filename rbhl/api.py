from collections import defaultdict
from decimal import Decimal
from opal.core.views import json_response
from opal.core.api import LoginRequiredViewset
from rbhl.models import PeakFlowDay, Demographics
from opal.core.api import OPALRouter


class PeakFlowGraphData(LoginRequiredViewset):
    base_name = "peak_flow_graph_data"

    def day_to_dict(self, peak_flow_day, demographics):
        aggregates = peak_flow_day.get_min_max_variability_completeness()
        pef_flow = None

        if peak_flow_day.date:
            pef_flow = demographics.get_pef(peak_flow_day.date)

        if not aggregates:
            return {
                "note": peak_flow_day.note,
                "treatment_taken": peak_flow_day.treatment_taken,
                "day_num": peak_flow_day.day_num,
            }
        else:
            (
                min_flow, max_flow, mean_flow, variabilty, completeness
            ) = aggregates

        return {
            "min_flow": min_flow,
            "mean_flow": mean_flow,
            "max_flow": max_flow,
            "day_num": peak_flow_day.day_num,
            "variabilty": variabilty,
            "pef_flow": pef_flow,
            "work_day": peak_flow_day.work_day,
            "complete": completeness,
            "note": peak_flow_day.note,
            "treatment_taken": peak_flow_day.treatment_taken
        }

    def get_queryset(self, *args, **kwargs):
        trial_num = self.request.GET["trial_num"]
        episode_id = self.request.GET["episode_id"]
        return PeakFlowDay.objects.filter(
            episode_id=episode_id,
            trial_num=trial_num
        ).order_by("day_num")

    def get_completeness(self, day_dicts):
        """
        A complete day is every day where the patient has
        added at least 6 entries.

        If they miss a day, that's a day counted as incomplete
        """

        total_days = max([i["day_num"] for i in day_dicts if "min_flow" in i])
        completed_days = len(
            [i for i in day_dicts if "complete" in i and i["complete"]]
        )
        if total_days:
            completeness = Decimal(completed_days)/Decimal(total_days)
        else:
            completeness = 0
        return round(completeness) * 100

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

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        demographics = Demographics.objects.get(
            patient__episode=self.request.GET["episode_id"]
        )

        days = [self.day_to_dict(i, demographics) for i in qs]
        return json_response({
            "days": days,
            "completeness": self.get_completeness(days),
            "treatments": self.get_treatments(days)
        })


indigo_router = OPALRouter()
indigo_router.register(PeakFlowGraphData.base_name, PeakFlowGraphData)
