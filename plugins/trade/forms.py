"""
"""
from django.forms import FileField, Form

class ImportDataForm(Form):
    data_file = FileField()
