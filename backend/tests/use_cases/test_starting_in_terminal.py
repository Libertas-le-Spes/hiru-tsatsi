import unittest

from tests.examples.app_lists import app_list
from tests.examples.windows import window
from tests.use_cases.mocked_list import desktop_showing, saved_once
from tests.use_cases.starting_scene import CHAT, HELPER, HELPERS_TERMINAL, STEAM, Start, appearing_once_launched
from hiru_tsatsi.use_cases.offering_terminals import ACTION, EXPLANATION
from hiru_tsatsi.work_apps.app import App
from hiru_tsatsi.work_apps.windows import Window

KNOWN_HELPER = App("Helper", "cd code && helper", HELPERS_TERMINAL, opens_in_terminal=True)
EDITOR = App("Editor", "cd code && editor .")
RULED_OUT = App("Editor", "cd code && editor .", terminal_ruled_out=True)
FAILING = App("Failing", "chromiun --app=https://example.org/")


def helper_running_in(window_class: str, workspace: int) -> Window:
    return window("t", window_class, "✳ Helper", workspace, "helper", "/home/sam/code")


def a_shell_waiting_in(window_class: str, workspace: int) -> Window:
    return window("t", window_class, "foot", workspace, "sh", "/home/sam")


class OfferingATerminal(unittest.TestCase):
    def test_a_folder_and_program_command_that_stops_without_a_window_asks_before_a_terminal(self):
        start = Start(desktop_showing([]), app_list((2, [HELPER])), stops=True, answers_yes=True)
        start.window_appearing_in_its_terminal(helper_running_in(HELPERS_TERMINAL, 2))
        outcome = start.run()
        start.notifier.ask.assert_called_once_with("Open Helper in a terminal?", EXPLANATION, ACTION)
        self.assertTrue(start.opened_in_its_terminal(HELPER, 2))
        self.assertEqual((outcome.now_opens_in_terminal, outcome.unseen), (["Helper"], []))

    def test_needing_a_terminal_is_saved_once_the_program_is_seen_running_in_it(self):
        start = Start(desktop_showing([]), app_list((2, [HELPER])), stops=True, answers_yes=True)
        start.window_appearing_in_its_terminal(helper_running_in(HELPERS_TERMINAL, 2))
        start.run()
        remembered = saved_once(start.store).placements()[0].app
        self.assertEqual((remembered.opens_in_terminal, remembered.learned_window), (True, HELPERS_TERMINAL))

    def test_needing_a_terminal_is_saved_when_the_program_starts_a_moment_after_its_window(self):
        start = Start(desktop_showing([]), app_list((2, [HELPER])), stops=True, answers_yes=True)
        terminal_opened_at = []

        def shell_first_then_the_program() -> list[Window]:
            if not start.opened_in_terminal():
                return []
            if not terminal_opened_at:
                terminal_opened_at.append(start.clock.now)
            if start.clock.now < terminal_opened_at[0] + 2.0:
                return [a_shell_waiting_in(HELPERS_TERMINAL, 2)]
            return [helper_running_in(HELPERS_TERMINAL, 2)]

        start.desktop.windows.side_effect = shell_first_then_the_program
        outcome = start.run()
        self.assertEqual(outcome.now_opens_in_terminal, ["Helper"])
        self.assertTrue(saved_once(start.store).placements()[0].app.opens_in_terminal)

    def test_saying_no_opens_no_terminal_and_is_remembered(self):
        start = Start(desktop_showing([]), app_list((2, [HELPER])), stops=True, answers_yes=False)
        outcome = start.run()
        self.assertEqual(start.opened_in_terminal(), [])
        self.assertTrue(saved_once(start.store).placements()[0].app.terminal_ruled_out)
        self.assertEqual(outcome.unseen, ["Helper"])

    def test_a_trial_whose_program_is_never_seen_in_it_is_never_tried_again(self):
        start = Start(desktop_showing([]), app_list((2, [HELPER])), stops=True, answers_yes=True)
        start.window_appearing_in_its_terminal(a_shell_waiting_in(HELPERS_TERMINAL, 2))
        outcome = start.run()
        remembered = saved_once(start.store).placements()[0].app
        self.assertEqual((remembered.opens_in_terminal, remembered.terminal_ruled_out), (False, True))
        self.assertEqual(outcome.now_opens_in_terminal, [])

    def test_a_trial_whose_terminal_never_appears_is_never_tried_again(self):
        start = Start(desktop_showing([]), app_list((2, [HELPER])), stops=True, answers_yes=True)
        outcome = start.run()
        self.assertEqual(len(start.opened_in_terminal()), 1)
        self.assertTrue(saved_once(start.store).placements()[0].app.terminal_ruled_out)
        self.assertEqual((outcome.now_opens_in_terminal, outcome.unseen), ([], ["Helper"]))

    def test_a_window_that_arrives_just_before_ten_seconds_is_placed_without_asking(self):
        start = Start(desktop_showing([]), app_list((2, [HELPER])), stops=True)
        start.window_appearing_after(9.8, helper_running_in("foot", 2))
        outcome = start.run()
        start.notifier.ask.assert_not_called()
        self.assertEqual((outcome.started, outcome.unseen), (["Helper"], []))

    def test_a_window_that_arrives_after_its_launcher_stopped_is_still_placed_without_asking(self):
        late_editor = window("e", "code", "harbour - Editor", 2)
        start = Start(desktop_showing([]), app_list((2, [EDITOR]), (6, [STEAM])), stops=True)

        def editor_at_fifteen_seconds_steam_at_twenty() -> list[Window]:
            shown = []
            if start.clock.now >= 15.0:
                shown.append(late_editor)
            if start.clock.now >= 20.0:
                shown.append(window("s", "steam", "Steam", 6))
            return shown

        start.desktop.windows.side_effect = editor_at_fifteen_seconds_steam_at_twenty
        outcome = start.run()
        start.notifier.ask.assert_not_called()
        self.assertEqual(start.opened_in_terminal(), [])
        self.assertEqual(outcome.unseen, [])


class AfterATerminalWasRuledOut(unittest.TestCase):
    def test_the_app_starts_plainly_without_being_watched_or_asked_about(self):
        start = Start(desktop_showing([]), app_list((2, [RULED_OUT])), stops=True, answers_yes=True)
        start.run()
        start.launches.new.assert_not_called()
        start.notifier.ask.assert_not_called()
        start.desktop.launch.assert_called_once_with(RULED_OUT.command, 2)

    def test_a_window_that_takes_half_a_minute_is_still_placed(self):
        start = Start(desktop_showing([]), app_list((2, [RULED_OUT])))
        start.window_appearing_after(30.0, window("e", "code", "harbour - Editor", 2))
        outcome = start.run()
        self.assertEqual(outcome.unseen, [])


class NeverTryingATerminal(unittest.TestCase):
    def test_a_folder_and_program_editor_with_its_own_window_still_learns_that_window(self):
        desktop = desktop_showing([])
        appearing_once_launched(desktop, [], [window("e", "code", "harbour - Editor", 2)])
        start = Start(desktop, app_list((2, [EDITOR])), stops=True)
        start.run()
        self.assertEqual(start.opened_in_terminal(), [])
        self.assertEqual(saved_once(start.store).placements()[0].app.learned_window, "code")

    def test_a_command_of_any_other_shape_is_never_put_in_a_terminal_even_when_it_stops(self):
        start = Start(desktop_showing([]), app_list((1, [FAILING])), stops=True)
        outcome = start.run()
        self.assertEqual(start.opened_in_terminal(), [])
        self.assertEqual(outcome.unseen, ["Failing"])

    def test_a_command_of_any_other_shape_is_launched_without_being_watched(self):
        start = Start(desktop_showing([]), app_list((1, [CHAT])))
        start.run()
        start.launches.new.assert_not_called()
        start.desktop.launch.assert_called_once_with(CHAT.command, 1)

    def test_a_folder_and_program_command_still_running_is_never_put_in_a_terminal(self):
        start = Start(desktop_showing([]), app_list((2, [HELPER])), stops=False)
        outcome = start.run()
        self.assertEqual(start.opened_in_terminal(), [])
        self.assertEqual(outcome.unseen, ["Helper"])

    def test_an_app_known_to_need_a_terminal_opens_in_one_at_once_without_a_plain_try(self):
        start = Start(desktop_showing([]), app_list((2, [KNOWN_HELPER])))
        start.window_appearing_in_its_terminal(helper_running_in(HELPERS_TERMINAL, 2))
        outcome = start.run()
        self.assertTrue(start.opened_in_its_terminal(KNOWN_HELPER, 2))
        start.launches.new.assert_not_called()
        self.assertEqual(outcome.unseen, [])
        self.assertEqual(len(start.desktop.launch.call_args_list), 1)


class FindingSessionsOpenedByHand(unittest.TestCase):
    def test_a_session_in_the_right_folder_counts_as_open_and_is_moved(self):
        by_hand = window("h", "foot", "✳ Some talk", 4, "helper", "/home/sam/code")
        start = Start(desktop_showing([by_hand]), app_list((2, [HELPER])))
        outcome = start.run()
        start.desktop.launch.assert_not_called()
        start.desktop.move.assert_called_once_with(by_hand, 2)
        start.store.save.assert_not_called()
        self.assertEqual(outcome.already_open, ["Helper"])

    def test_a_terminal_app_finds_its_session_opened_by_hand(self):
        start = Start(desktop_showing([window("h", "foot", "✳ Some talk", 2, "helper", "/home/sam/code")]),
                      app_list((2, [KNOWN_HELPER])))
        outcome = start.run()
        start.desktop.launch.assert_not_called()
        self.assertEqual(outcome.already_open, ["Helper"])

    def test_a_session_of_the_same_program_in_another_folder_is_never_taken_by_its_title(self):
        other_project = window("o", "foot", "✳ Claude Code", 4, "helper", "/home/sam/other")
        start = Start(desktop_showing([]), app_list((2, [App("Helper", "cd code && helper")])))
        appearing_once_launched(start.desktop, [], [other_project])
        outcome = start.run()
        start.desktop.move.assert_not_called()
        start.store.save.assert_not_called()
        self.assertEqual(outcome.unseen, ["Helper"])

    def test_a_hand_edited_terminal_mark_on_another_kind_of_command_starts_it_plainly(self):
        marked = App("Chat", CHAT.command, "hiru-tsatsi.chat-1a2b3c4d", opens_in_terminal=True)
        start = Start(desktop_showing([]), app_list((1, [marked])))
        start.run()
        self.assertEqual(start.opened_in_terminal(), [])
        start.desktop.launch.assert_called_once_with(CHAT.command, 1)

    def test_an_app_that_is_itself_a_terminal_learns_its_window_with_a_shell_inside(self):
        own = window("f", "foot", "sam@desk:/tmp", 9, "bash", "/tmp")
        start = Start(desktop_showing([]), app_list((9, [App("Own terminal", "cd /tmp && foot")])))
        appearing_once_launched(start.desktop, [], [own])
        outcome = start.run()
        self.assertEqual(outcome.unseen, [])
        self.assertEqual(saved_once(start.store).placements()[0].app.learned_window, "foot")


if __name__ == "__main__":
    unittest.main()
