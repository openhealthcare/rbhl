from opal.core.pathway import Step, PagePathway
from legacy import models


class BloodBook(PagePathway):
    display_name = 'Blood book'
    slug = 'blood_book'
    template = "pathway/base/blood_book_form_base.html"
    steps = [
        Step(
            models.BloodBook,
            base_template="pathway/blood_book_form.html",
            step_controller="BloodBookStep"
        )
    ]

    def redirect_url(self, user=None, patient=None, episode=None):
        return "/#/patient/{0}/investigations".format(patient.id)


class BloodBookResult(PagePathway):
    display_name = 'Blood book results'
    slug = 'blood_book_result'
    template = "pathway/base/blood_book_form_base.html"
    steps = [
        Step(
            models.BloodBook,
            base_template="pathway/blood_book_result_form.html",
            step_controller="BloodBookStep"
        )
    ]

    def redirect_url(self, user=None, patient=None, episode=None):
        return "/#/patient/{0}/investigations".format(patient.id)
