from django.contrib.auth.models import User
from opal.core.test import OpalTestCase
from rbhl import constants
from rbhl import Application


class SeenByMeTestCase(OpalTestCase):
    def setUp(self):
        super().setUp()
        not_doctor_user = User.objects.create(username="normal")
        not_doctor_user.set_password(self.PASSWORD)
        not_doctor_user.save()
        self.not_doctor_user = not_doctor_user
        doctor_user = User.objects.create(username="tb")
        doctor_user.set_password(self.PASSWORD)
        doctor_user.save()
        doctor_user.profile.roles.create(
            name=constants.DOCTOR_ROLE
        )
        self.doctor_user = doctor_user

    def test_get_menu_items_with_doctor(self):
        menu_items = Application().get_menu_items(self.doctor_user)
        item_names = [i.display for i in menu_items]
        self.assertIn(
            "Seen by me", item_names
        )

    def test_get_menu_items_without_doctor(self):
        menu_items = Application.get_menu_items(self.not_doctor_user)
        item_names = [i.display for i in menu_items]
        self.assertNotIn(
            "Seen by me", item_names
        )
