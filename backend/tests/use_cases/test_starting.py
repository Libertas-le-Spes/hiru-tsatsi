import unittest

from tests.fakes import BlindDesktop, FakeClock, FakeDesktop, FakeStore, app_list, window
from workbench.use_cases.starting import StartApps
from workbench.work_apps.app_list import App

CHAT = App("Chat", "omarchy-launch-webapp https://chat.google.com/", "chrome-chat.google.com")
MAIN = App("Rider Main", "rider ~/RiderProjects/onplia", "onplia")
STEAM = App("Steam", "steam")


def start(desktop, apps):
    store = FakeStore(apps)
    clock = FakeClock()
    outcome = StartApps(desktop, store, clock, clock.wait).run()
    return outcome, store, clock


class StartingWorkApps(unittest.TestCase):
    def test_an_open_app_on_its_workspace_is_left_alone(self):
        desktop = FakeDesktop([window("m", "jetbrains-rider", "onplia – x", 2)])
        outcome, _, _ = start(desktop, app_list((2, [MAIN])))
        self.assertEqual((desktop.launched, desktop.moves), ([], []))
        self.assertEqual(outcome.already_open, ["Rider Main"])

    def test_an_open_app_elsewhere_is_moved_not_opened_again(self):
        desktop = FakeDesktop([window("c", "chrome-chat.google.com__u_2-Default", "Chat", 4)])
        outcome, _, _ = start(desktop, app_list((1, [CHAT])))
        self.assertEqual(desktop.launched, [])
        self.assertEqual(desktop.moves, [("c", 1)])
        self.assertEqual(outcome.moved, ["Chat"])

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
        self.assertEqual(store.apps.placements()[0].app.window, "steam")
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

    def test_a_desktop_that_cannot_see_windows_launches_without_waiting(self):
        desktop = BlindDesktop([])
        outcome, _, clock = start(desktop, app_list((2, [MAIN])))
        self.assertEqual(desktop.launched, [(MAIN.command, 2)])
        self.assertEqual((clock.now, outcome.unplaceable), (0, ["Rider Main"]))


if __name__ == "__main__":
    unittest.main()
