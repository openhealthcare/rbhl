from opal.core.test import OpalTestCase
from rbhl.management.commands import aggregate_notes


class AggregateNotesTestCase(OpalTestCase):
    def setUp(self):
        self.command = aggregate_notes.Command()
        _, self.episode = self.new_patient_and_episode_please()

    def test_aggregate_notes(self):
        self.episode.peakflowday_set.create(
            day_num=1, trial_num=1, note="hello"
        )
        self.command.handle()
        self.assertEqual(
            self.episode.peakflowday_set.get().note, "Day 1: hello"
        )

    def test_aggregate_notes_by_trial_num(self):
        self.episode.peakflowday_set.create(
            day_num=1, trial_num=1, note="hello"
        )
        self.episode.peakflowday_set.create(
            day_num=1, trial_num=2, note="there"
        )
        self.command.handle()
        self.assertEqual(
            self.episode.peakflowday_set.first().note, "Day 1: hello"
        )
        self.assertEqual(
            self.episode.peakflowday_set.last().note, "Day 1: there"
        )

    def test_aggregate_notes_by_day_num(self):
        self.episode.peakflowday_set.create(
            day_num=1, trial_num=1, note="hello"
        )
        self.episode.peakflowday_set.create(
            day_num=2, trial_num=1, note="there"
        )
        self.command.handle()
        self.assertEqual(
            self.episode.peakflowday_set.first().note,
            "Day 1: hello\nDay 2: there"
        )
        self.assertEqual(
            self.episode.peakflowday_set.last().note, ""
        )

    def test_ignores_empty_notes(self):
        self.episode.peakflowday_set.create(
            day_num=1, trial_num=1, note="hello"
        )
        self.episode.peakflowday_set.create(
            day_num=2, trial_num=1
        )
        self.episode.peakflowday_set.create(
            day_num=3, trial_num=1, note="there"
        )
        self.command.handle()
        self.assertEqual(
            self.episode.peakflowday_set.first().note,
            "Day 1: hello\nDay 3: there"
        )
        self.assertEqual(
            self.episode.peakflowday_set.last().note, ""
        )
