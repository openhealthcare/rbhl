from decimal import Decimal
from opal.core.views import json_response
from opal.core.api import LoginRequiredViewset
from rbhl.models import PeakFlowDay
from opal.core.api import OPALRouter


class PeakFlowGraphData(LoginRequiredViewset):
    base_name = "peak_flow_graph_data"

    def day_to_dict(self, peak_flow_day):
        flow_values = peak_flow_day.flow_values()
        if not flow_values:
            return {
                "note": peak_flow_day.note,
                "treatment_taken": peak_flow_day.treatment_taken
            }
        min_flow = min(flow_values)
        max_flow = max(flow_values)
        variabilty = Decimal(max_flow - min_flow)/Decimal(max_flow)
        variabilty_perc = round(variabilty * 100)
        mean_flow = round(Decimal(sum(flow_values))/Decimal(len(flow_values)))
        return {
            "min_flow": min_flow,
            "max_flow": max_flow,
            "variabilty": variabilty_perc,
            "mean_flow": mean_flow,
            "day_num": peak_flow_day.day_num,
            "work_day": peak_flow_day.work_day,
            "complete": len(flow_values) > 5,
            "note": peak_flow_day.note,
            "treatment_taken": peak_flow_day.treatment_taken
        }

    def get_queryset(self, *args, **kwargs):
        trial_num = self.request.GET["trial_num"]
        episode_id = self.request.GET["episode_id"]
        return PeakFlowDay.objects.filter(
            episode_id=episode_id,
            trial_num=trial_num
        ).order_by("work_day")

    def get_completeness(self, day_dicts):
        """
        A complete day is every day where the patient has
        added at least 6 entries.

        If they miss a day, that's a day counted as incomplete
        """

        days_with_flows = len([i for i in day_dicts if "min_flow" in i])
        completed_days = len([i for i in day_dicts if i["complete"]])
        if days_with_flows:
            completeness = Decimal(completed_days)/Decimal(days_with_flows)
        else:
            completeness = 0
        return round(completeness) * 100

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        days = [self.day_to_dict(i) for i in qs]
        return json_response({
            "days": days,
            "completeness": self.get_completeness(days)
        })


indigo_router = OPALRouter()
indigo_router.register(PeakFlowGraphData.base_name, PeakFlowGraphData)
