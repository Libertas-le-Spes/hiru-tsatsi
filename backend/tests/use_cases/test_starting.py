import unittest
from unittest.mock import call

from tests.examples.app_lists import app_list
from tests.examples.windows import window
from tests.use_cases.starting_scene import CHAT, MAIN, STEAM, Start, appearing_once_launched, mocked_desktop


class StartingWorkApps(unittest.TestCase):
    def test_an_open_app_on_its_workspace_is_left_alone(self):
        desktop = mocked_desktop([window("m", "jetbrains-rider", "harbour – x", 2)])
        outcome = Start(desktop, app_list((2, [MAIN]))).run()
        desktop.launch.assert_not_called()
        desktop.move.assert_not_called()
        self.assertEqual(outcome.already_open, ["Rider Main"])

    def test_an_open_app_elsewhere_is_moved_not_opened_again(self):
        chat_window = window("c", "chrome-chat.google.com__u_2-Default", "Chat", 4)
        desktop = mocked_desktop([chat_window])
        outcome = Start(desktop, app_list((1, [CHAT]))).run()
        desktop.launch.assert_not_called()
        desktop.move.assert_called_once_with(chat_window, 1)
        self.assertEqual(outcome.moved, ["Chat"])

    def test_every_missing_app_starts_before_it_looks_for_windows_again(self):
        desktop = mocked_desktop([])
        Start(desktop, app_list((1, [CHAT]), (2, [MAIN]))).run()
        self.assertEqual(desktop.mock_calls[:4], [call.windows(), call.launch(CHAT.command, 1),
                                                  call.launch(MAIN.command, 2), call.windows()])

    def test_a_window_that_lands_on_the_wrong_workspace_is_moved(self):
        steam_window = window("s", "steam", "Steam", 4)
        desktop = mocked_desktop([])
        appearing_once_launched(desktop, [], [steam_window])
        outcome = Start(desktop, app_list((6, [STEAM]))).run()
        desktop.move.assert_called_once_with(steam_window, 6)
        self.assertEqual((outcome.started, outcome.unseen), (["Steam"], []))

    def test_an_unnamed_app_learns_its_window_and_saves_it_once(self):
        desktop = mocked_desktop([])
        appearing_once_launched(desktop, [], [window("s", "steam", "Steam", 6)])
        start = Start(desktop, app_list((6, [STEAM])))
        start.run()
        self.assertEqual(start.saved().placements()[0].app.learned_window, "steam")

    def test_an_unnamed_app_never_claims_a_window_that_was_already_open(self):
        desktop = mocked_desktop([window("old", "steam", "Steam", 4)])
        start = Start(desktop, app_list((6, [STEAM])))
        outcome = start.run()
        desktop.launch.assert_called_once_with("steam", 6)
        desktop.move.assert_not_called()
        start.store.save.assert_not_called()
        self.assertEqual(outcome.unseen, ["Steam"])

    def test_an_app_whose_window_never_shows_is_reported_after_a_minute(self):
        start = Start(mocked_desktop([]), app_list((2, [MAIN])))
        outcome = start.run()
        self.assertEqual(outcome.unseen, ["Rider Main"])
        self.assertGreaterEqual(start.clock.now, 60)

    def test_every_window_given_to_an_app_is_named_after_it(self):
        rider = window("m", "jetbrains-rider", "harbour – x", 2)
        chat = window("c", "chrome-chat.google.com_x", "Chat", 4)
        steam = window("s", "steam", "Steam", 6)
        desktop = mocked_desktop([])
        appearing_once_launched(desktop, [rider, chat], [rider, chat, steam])
        start = Start(desktop, app_list((1, [CHAT]), (2, [MAIN]), (6, [STEAM])))
        start.run()
        self.assertCountEqual(start.names.record.call_args_list,
                              [call(rider, "Rider Main"), call(chat, "Chat"), call(steam, "Steam")])

    def test_windows_that_belong_to_no_app_get_no_name(self):
        start = Start(mocked_desktop([window("t", "foot", "~", 4)]), app_list((2, [MAIN])))
        start.run()
        start.names.record.assert_not_called()


if __name__ == "__main__":
    unittest.main()
