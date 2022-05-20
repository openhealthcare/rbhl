from opal.core.search.queries import DatabaseQuery
from plugins.lab.models import Allergen, BloodResult
from django.db.models import Q
from opal.models import Episode


class RBHLQueryBackend(DatabaseQuery):
    def bloods_query(self, query):
        query_type = query['queryType']
        query_value = query['query']
        contains = '__iexact'
        if query_type == 'Contains':
            contains = '__icontains'
        allergen_fks = Allergen.objects.filter(**{f"name{contains}": query_value})
        ft_filter = {f"allergen_ft{contains}": query_value}
        results = BloodResult.objects.filter(
            Q(allergen_fk_id__in=allergen_fks) | Q(**ft_filter)
        )
        return Episode.objects.filter(
            patient__bloods__bloodresult__in=results
        ).distinct()

    def episodes_for_criteria(self, query_segment):
        if query_segment["column"] == 'blood_result_extract':
            return self.bloods_query(query_segment)
        return super().episodes_for_criteria(query_segment)
