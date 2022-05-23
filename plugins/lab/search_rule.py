from opal.core.search.search_rule import SearchRuleField, SearchRule
from plugins.lab.models import Allergen, BloodResult
from django.db.models import Q
from opal.models import Episode


class AllergenSearchField(SearchRuleField):
    """
    Allow the users to search via BloodResult.allergen as they would any
    subrecord free text or foreign key field
    """
    lookup_list = "allergen"
    field_type = "string"
    display_name = "Allergen"

    def query(self, query):
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


class BloodResults(SearchRule):
    """
    Adds blood results as an option in the advanced search column section.
    """
    display_name = "Blood Results"
    slug = "blood_results"
    fields = (AllergenSearchField,)
