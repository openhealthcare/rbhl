from plugins.lab.models import Allergen
from opal.core import metadata


class AllergenAndAntigenNo(metadata.Metadata):
    slug = 'favourite-colour'

    @classmethod
    def to_dict(klass, **kwargs):
        return {
            'phadia_test_code': list(Allergen.objects.values('name', 'code'))
        }
