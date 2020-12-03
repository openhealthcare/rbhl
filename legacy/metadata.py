from legacy.models import Allergen
from opal.core import metadata


class AllergenAndAntigenNo(metadata.Metadata):
    slug = 'favourite-colour'

    @classmethod
    def to_dict(klass, **kwargs):
        return {
            'allergen': list(Allergen.objects.values('name', 'code'))
        }
