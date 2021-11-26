from opal.core.api import patient_from_pk
from opal.core.api import LoginRequiredViewset
from opal.core.views import json_response


class PatientEpisodes(LoginRequiredViewset):
    """
    An api for the bloods form to provide a list of
    episodes for the select drop down.

    It provides referrals, employment and clinic log
    for the episodes
    """
    basename = 'patient_episodes'

    @patient_from_pk
    def retrieve(self, request, patient):
        episodes = patient.episode_set.all().prefetch_related(
            'referral_set', 'employment_set', 'cliniclog_set'
        )
        user = request.user
        result = []
        for episode in episodes:
            referrals = episode.referral_set.all()
            employment = episode.employment_set.all()
            clinic_log = episode.cliniclog_set.all()

            result.append({
                'id': episode.id,
                'referral': [i.to_dict(user) for i in referrals],
                'employment': [i.to_dict(user) for i in employment],
                'clinic_log': [i.to_dict(user) for i in clinic_log],
            })
        return json_response(result)
