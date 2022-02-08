from opal.core.test import OpalTestCase
from rbhl.models import Employment, EmploymentCategory
from legacy import build_lookup_list


class BuildLookupListTestCase(OpalTestCase):
    def setUp(self):
        _, self.episode = self.new_patient_and_episode_please()

    def test_distinct_count(self):
        """
        Should return a case insensitive count
        keyed by the most popular case sensitive result
        """
        case_insensitive_count = {
            "Horse": 10,
            "Cat": 11,
            "horse": 3
        }
        expected = {
            "Horse": 13,
            "Cat": 11
        }
        self.assertEqual(
            build_lookup_list.get_distinct_count(case_insensitive_count),
            expected
        )

    def test_get_values_to_add(self):
        """
        Should return the value that is greater than or
        equal to the threshold
        """
        for i in range(build_lookup_list.THRESHOLD):
            emp = Employment.objects.create(episode=self.episode)
            emp.employment_category = "some job"
            emp.save()
        emp = Employment.objects.create(episode=self.episode)
        emp.employment_category = "no job"
        emp.save()

        result = build_lookup_list.get_values_to_add(
            Employment, Employment.employment_category
        )
        self.assertEqual(result, ["some job"])

    def test_add_values_to_lookup_lists(self):
        EmploymentCategory.objects.create(name="Baker")
        build_lookup_list.add_values_to_lookup_lists(
            EmploymentCategory, ["baker", "candle stick maker"]
        )
        self.assertEqual(
            list(EmploymentCategory.objects.order_by('name').values_list(
                'name', flat=True)
            ),
            ["Baker", "candle stick maker"]
        )

    def test_resave_models(self):
        emp = self.episode.employment_set.create()
        emp.employment_category = "baker"
        emp.save()
        category = EmploymentCategory.objects.create(name="baker")
        build_lookup_list.resave_models(Employment, Employment.employment_category)
        self.assertEqual(
            Employment.objects.get().employment_category_fk_id,
            category.id
        )
