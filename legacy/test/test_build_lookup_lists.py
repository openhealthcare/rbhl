from opal.core.test import OpalTestCase
from rbhl.models import ClinicLog, ClinicSite
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
            cl = ClinicLog.objects.create(episode=self.episode)
            cl.clinic_site = "somewhere"
            cl.save()
        cl = ClinicLog.objects.create(episode=self.episode)
        cl.clinic_site = "nowhere"
        cl.save()

        result = build_lookup_list.get_values_to_add(
            ClinicLog, ClinicLog.clinic_site
        )
        self.assertEqual(result, ["somewhere"])

    def test_add_values_to_lookup_lists(self):
        ClinicSite.objects.create(name="Scunthorpe")
        build_lookup_list.add_values_to_lookup_lists(
            ClinicSite, ["scunthorpe", "Blackpool"]
        )
        self.assertEqual(
            list(ClinicSite.objects.order_by('name').values_list('name', flat=True)),
            ["Blackpool", "Scunthorpe"]
        )

    def test_resave_models(self):
        cl = self.episode.cliniclog_set.get()
        cl.clinic_site = "scunthorpe"
        cl.save()
        cs = ClinicSite.objects.create(name="Scunthorpe")
        build_lookup_list.resave_models(ClinicLog, ClinicLog.clinic_site)
        self.assertEqual(
            ClinicLog.objects.get().clinic_site_fk_id,
            cs.id
        )
