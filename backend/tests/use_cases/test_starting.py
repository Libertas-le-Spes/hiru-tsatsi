import unittest
from unittest.mock import call

from tests.examples.app_lists import app_list
from tests.examples.windows import window
from tests.use_cases.mocked_list import desktop_showing, saved_once
from tests.use_cases.starting_scene import CHAT, MAIN, STEAM, Start, appearing_once_launched
from hiru_tsatsi.use_cases.failures import ChangedMeanwhile, NotSaved


class StartingWorkApps(unittest.TestCase):
    def test_an_open_app_on_its_workspace_is_left_alone(self):
        desktop = desktop_showing([window("m", "jetbrains-rider", "harbour – x", 2)])
        outcome = Start(desktop, app_list((2, [MAIN]))).run()
        desktop.launch.assert_not_called()
        desktop.move.assert_not_called()
        self.assertEqual(outcome.already_open, ["Rider Main"])

    def test_an_open_app_elsewhere_is_moved_not_opened_again(self):
        chat_window = window("c", "chrome-chat.google.com__u_2-Default", "Chat", 4)
        desktop = desktop_showing([chat_window])
        outcome = Start(desktop, app_list((1, [CHAT]))).run()
        desktop.launch.assert_not_called()
        desktop.move.assert_called_once_with(chat_window, 1)
        self.assertEqual(outcome.moved, ["Chat"])

    def test_every_missing_app_starts_before_it_looks_for_windows_again(self):
        desktop = desktop_showing([])
        Start(desktop, app_list((1, [CHAT]), (2, [MAIN]))).run()
        self.assertEqual(desktop.mock_calls[:4], [call.windows(), call.launch(CHAT.command, 1),
                                                  call.launch(MAIN.command, 2), call.windows()])

    def test_a_window_that_lands_on_the_wrong_workspace_is_moved(self):
        steam_window = window("s", "steam", "Steam", 4)
        desktop = desktop_showing([])
        appearing_once_launched(desktop, [], [steam_window])
        outcome = Start(desktop, app_list((6, [STEAM]))).run()
        desktop.move.assert_called_once_with(steam_window, 6)
        self.assertEqual((outcome.started, outcome.unseen), (["Steam"], []))

    def test_an_unnamed_app_learns_its_window_and_saves_it_once(self):
        desktop = desktop_showing([])
        appearing_once_launched(desktop, [], [window("s", "steam", "Steam", 6)])
        start = Start(desktop, app_list((6, [STEAM])))
        start.run()
        self.assertEqual(saved_once(start.store).placements()[0].app.learned_window, "steam")

    def test_an_unnamed_app_never_claims_a_window_that_was_already_open(self):
        desktop = desktop_showing([window("old", "steam", "Steam", 4)])
        start = Start(desktop, app_list((6, [STEAM])))
        outcome = start.run()
        desktop.launch.assert_called_once_with("steam", 6)
        desktop.move.assert_not_called()
        start.store.save.assert_not_called()
        self.assertEqual(outcome.unseen, ["Steam"])

    def test_an_app_whose_window_never_shows_is_reported_after_a_minute(self):
        start = Start(desktop_showing([]), app_list((2, [MAIN])))
        outcome = start.run()
        self.assertEqual(outcome.unseen, ["Rider Main"])
        self.assertGreaterEqual(start.clock.now, 60)

    def test_every_window_given_to_an_app_is_named_after_it(self):
        rider = window("m", "jetbrains-rider", "harbour – x", 2)
        chat = window("c", "chrome-chat.google.com_x", "Chat", 4)
        steam = window("s", "steam", "Steam", 6)
        desktop = desktop_showing([])
        appearing_once_launched(desktop, [rider, chat], [rider, chat, steam])
        start = Start(desktop, app_list((1, [CHAT]), (2, [MAIN]), (6, [STEAM])))
        start.run()
        self.assertCountEqual(start.names.record.call_args_list,
                              [call(rider, "Rider Main"), call(chat, "Chat"), call(steam, "Steam")])

    def test_windows_that_belong_to_no_app_get_no_name(self):
        start = Start(desktop_showing([window("t", "foot", "~", 4)]), app_list((2, [MAIN])))
        start.run()
        start.names.record.assert_not_called()

    def test_a_list_edited_during_the_start_keeps_the_edit_and_gets_what_was_learned(self):
        desktop = desktop_showing([])
        appearing_once_launched(desktop, [], [window("s", "steam", "Steam", 6)])
        start = Start(desktop, app_list((6, [STEAM])))
        edited_meanwhile = app_list((6, [STEAM]), (1, [CHAT]))
        start.store.load.side_effect = [app_list((6, [STEAM])), edited_meanwhile]
        start.store.save.side_effect = [ChangedMeanwhile("the list changed meanwhile"), None]
        start.run()
        saved_again = start.store.save.call_args.args[0]
        self.assertEqual(start.store.save.call_count, 2)
        self.assertEqual(saved_again.workspace(1).apps, (CHAT,))
        self.assertEqual(saved_again.workspace(6).apps[0].learned_window, "steam")

    def test_a_save_refused_for_another_reason_is_not_retried(self):
        desktop = desktop_showing([])
        appearing_once_launched(desktop, [], [window("s", "steam", "Steam", 6)])
        start = Start(desktop, app_list((6, [STEAM])))
        start.store.save.side_effect = NotSaved("other accounts can write to the folder")
        with self.assertRaises(NotSaved):
            start.run()
        start.store.save.assert_called_once()
        start.store.load.assert_called_once()

    def test_says_which_apps_are_starting_before_launching_them(self):
        start = Start(desktop_showing([window("c", "chrome-chat.google.com-Default", "Chat", 1)]),
                      app_list((1, [CHAT]), (2, [MAIN, STEAM])))
        start.run()
        start.announcer.announce.assert_called_once_with(["Rider Main", "Steam"])

    def test_says_nothing_up_front_when_every_app_is_already_open(self):
        start = Start(desktop_showing([window("c", "chrome-chat.google.com-Default", "Chat", 1)]), app_list((1, [CHAT])))
        start.run()
        start.announcer.announce.assert_not_called()


if __name__ == "__main__":
    unittest.main()
