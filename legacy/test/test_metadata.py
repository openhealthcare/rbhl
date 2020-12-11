from rest_framework.reverse import reverse
from opal.core.test import OpalTestCase


class MetadataTestCase(OpalTestCase):
    def test_get(self):
        request = self.rf.get("/")
        url = reverse('metadata-list', request=request)
        self.assertTrue(
            self.client.login(
                username=self.user.username, password=self.PASSWORD
            )
        )
        result = self.client.get(url)
        self.assertIn("phadia_test_code", result.json())
