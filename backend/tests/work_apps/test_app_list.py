import unittest

from tests.fakes import app_list
from workbench.work_apps.app_list import App, AppList, Blank, NothingThere, NumberTaken

CHAT = App("Chat", "chat-app")


class EditingTheList(unittest.TestCase):
    def test_a_new_workspace_takes_its_place_in_number_order(self):
        apps = app_list((1, []), (5, [])).with_workspace(4, "Comms")
        self.assertEqual([s.number for s in apps.workspaces], [1, 4, 5])

    def test_a_number_already_in_use_or_below_one_is_refused(self):
        for number in (5, 0):
            with self.subTest(number=number), self.assertRaises(NumberTaken):
                app_list((5, [])).with_workspace(number, "Again")

    def test_a_workspace_can_be_renumbered_and_renamed(self):
        apps = app_list((1, [CHAT]), (5, [])).with_workspace_changed(1, 7, "Chat")
        self.assertEqual([(s.number, s.label, len(s.apps)) for s in apps.workspaces], [(5, "Space 5", 0), (7, "Chat", 1)])

    def test_renumbering_onto_a_taken_number_is_refused(self):
        with self.assertRaises(NumberTaken):
            app_list((1, []), (5, [])).with_workspace_changed(1, 5, "x")

    def test_blank_names_and_commands_are_refused(self):
        for app in (App(" ", "x"), App("x", "")):
            with self.subTest(app=app), self.assertRaises(Blank):
                app_list((1, [])).with_app(1, app)

    def test_apps_are_added_changed_and_removed_in_their_workspace(self):
        apps = app_list((1, [CHAT])).with_app(1, App("Mail", "mail"))
        apps = apps.with_app_changed(1, 0, "Google Chat", "chat-app --new")
        self.assertEqual([a.name for a in apps.workspace(1).apps], ["Google Chat", "Mail"])
        self.assertEqual([a.name for a in apps.without_app(1, 0).workspace(1).apps], ["Mail"])

    def test_changing_an_app_keeps_the_window_it_learned(self):
        apps = app_list((1, [App("Chat", "chat-app", "chat")])).with_app_changed(1, 0, "Chat", "chat-app --new")
        self.assertEqual(apps.workspace(1).apps[0].learned_window, "chat")

    def test_something_that_is_not_there_is_refused(self):
        for change in (lambda a: a.without_workspace(9), lambda a: a.without_app(1, 3), lambda a: a.with_app(9, CHAT)):
            with self.assertRaises(NothingThere):
                change(app_list((1, [CHAT])))


if __name__ == "__main__":
    unittest.main()
