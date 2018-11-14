"""
Episode Category for OCLD
"""
from opal.core import episodes

class OccupationalLungDiseaseEpisode(episodes.EpisodeCategory):
    display_name    = 'OCLD'
    detail_template = 'detail/ocld.html'
