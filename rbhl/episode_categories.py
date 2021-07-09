"""
Episode Category for OCCLD
"""
from opal.core import episodes


class OccupationalLungDiseaseEpisode(episodes.EpisodeCategory):
    display_name    = 'OCCLD'
    detail_template = 'detail/occld.html'
