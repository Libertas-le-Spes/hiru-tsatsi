import unittest

from tests.fakes.app_lists import app_list
from tests.fakes.desktop import FakeDesktop, window
from tests.fakes.notifying import FakeAnnouncer
from tests.fakes.window_names import FakeNames
from tests.use_cases.starting_examples import CHAT, MAIN, STEAM, start


class StartingWorkApps(unittest.TestCase):
    def test_an_open_app_on_its_workspace_is_left_alone(self):
        desktop = FakeDesktop([window("m", "jetbrains-rider", "harbour – x", 2)])
        outcome, _, _ = start(desktop, app_list((2, [MAIN])))
        self.assertEqual((desktop.launched, desktop.moves), ([], []))
        self.assertEqual(outcome.already_open, ["Rider Main"])

    def test_an_open_app_elsewhere_is_moved_not_opened_again(self):
        desktop = FakeDesktop([window("c", "chrome-chat.google.com__u_2-Default", "Chat", 4)])
        outcome, _, _ = start(desktop, app_list((1, [CHAT])))
        self.assertEqual(desktop.launched, [])
        self.assertEqual(desktop.moves, [("c", 1)])
        self.assertEqual(outcome.moved, ["Chat"])

    def test_says_which_apps_are_starting_before_launching_them(self):
        announcer = FakeAnnouncer()
        desktop = FakeDesktop([window("c", "chrome-chat.google.com-Default", "Chat", 1)])
        start(desktop, app_list((1, [CHAT]), (2, [MAIN, STEAM])), announcer)
        self.assertEqual(announcer.announced, [["Rider Main", "Steam"]])

    def test_says_nothing_up_front_when_every_app_is_already_open(self):
        announcer = FakeAnnouncer()
        start(FakeDesktop([window("c", "chrome-chat.google.com-Default", "Chat", 1)]), app_list((1, [CHAT])), announcer)
        self.assertEqual(announcer.announced, [])

    def test_every_missing_app_starts_before_any_window_appears(self):
        desktop = FakeDesktop([])
        start(desktop, app_list((1, [CHAT]), (2, [MAIN])))
        self.assertEqual(desktop.launched, [(CHAT.command, 1), (MAIN.command, 2)])

    def test_a_window_that_lands_on_the_wrong_workspace_is_moved(self):
        desktop = FakeDesktop([], {STEAM.command: [window("s", "steam", "Steam", 4)]})
        outcome, _, _ = start(desktop, app_list((6, [STEAM])))
        self.assertEqual(desktop.moves, [("s", 6)])
        self.assertEqual((outcome.started, outcome.unseen), (["Steam"], []))

    def test_an_unnamed_app_learns_its_window_and_saves_it(self):
        desktop = FakeDesktop([], {STEAM.command: [window("s", "steam", "Steam", 6)]})
        _, store, _ = start(desktop, app_list((6, [STEAM])))
        self.assertEqual(store.apps.placements()[0].app.learned_window, "steam")
        self.assertEqual(store.saves, 1)

    def test_an_unnamed_app_never_claims_a_window_that_was_already_open(self):
        desktop = FakeDesktop([window("old", "steam", "Steam", 4)])
        outcome, store, _ = start(desktop, app_list((6, [STEAM])))
        self.assertEqual(desktop.launched, [("steam", 6)])
        self.assertEqual((desktop.moves, outcome.unseen, store.saves), ([], ["Steam"], 0))

    def test_an_app_whose_window_never_shows_is_reported_after_a_minute(self):
        desktop = FakeDesktop([])
        outcome, _, clock = start(desktop, app_list((2, [MAIN])))
        self.assertEqual(outcome.unseen, ["Rider Main"])
        self.assertGreaterEqual(clock.now, 60)

    def test_every_window_given_to_an_app_is_named_after_it(self):
        names = FakeNames()
        desktop = FakeDesktop([window("m", "jetbrains-rider", "harbour – x", 2), window("c", "chrome-chat.google.com_x", "Chat", 4)],
                              {STEAM.command: [window("s", "steam", "Steam", 6)]})
        start(desktop, app_list((1, [CHAT]), (2, [MAIN]), (6, [STEAM])), names=names)
        self.assertEqual(names.recorded, {"m": "Rider Main", "c": "Chat", "s": "Steam"})

    def test_windows_that_belong_to_no_app_get_no_name(self):
        names = FakeNames()
        start(FakeDesktop([window("t", "foot", "~", 4)]), app_list((2, [MAIN])), names=names)
        self.assertEqual(names.recorded, {})





if __name__ == "__main__":
    unittest.main()
