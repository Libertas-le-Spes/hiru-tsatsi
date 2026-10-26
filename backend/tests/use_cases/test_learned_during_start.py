import unittest

from tests.examples.app_lists import app_list
from hiru_tsatsi.use_cases.learned_during_start import applied_to, learned_between
from hiru_tsatsi.work_apps.app import App

STEAM = App("Steam", "steam")
CHAT = App("Chat", "chat-app")
MAIL = App("Mail", "mail-app")


class CarryingOverWhatAStartLearned(unittest.TestCase):
    def setUp(self):
        self.before = app_list((6, [STEAM]), (1, [CHAT]))
        after = self.before.with_learned_window(self.before.placement(6, 0), "steam")
        self.learned = learned_between(self.before, after)

    def test_only_the_apps_that_changed_are_carried(self):
        self.assertEqual(len(self.learned), 1)
        self.assertEqual(self.learned[0].after.learned_window, "steam")

    def test_an_app_added_meanwhile_is_kept_and_the_learning_applied(self):
        edited = app_list((6, [STEAM]), (1, [CHAT, MAIL]))
        merged = applied_to(edited, self.learned)
        self.assertEqual(merged.workspace(1).apps, (CHAT, MAIL))
        self.assertEqual(merged.workspace(6).apps[0].learned_window, "steam")

    def test_an_app_changed_meanwhile_is_left_as_edited(self):
        edited = app_list((6, [App("Games", "steam-runtime")]), (1, [CHAT]))
        self.assertEqual(applied_to(edited, self.learned), edited)

    def test_an_app_removed_meanwhile_is_not_brought_back(self):
        edited = app_list((6, []), (1, [CHAT]))
        self.assertEqual(applied_to(edited, self.learned), edited)


if __name__ == "__main__":
    unittest.main()
