import unittest

from tests.examples.app_lists import app_list
from tests.examples.windows import window
from tests.use_cases.mocked_list import desktop_showing, saved_once
from tests.use_cases.starting_scene import CHAT, HELPER, HELPERS_TERMINAL, Start, appearing_once_launched
from tests.use_cases.terminal_examples import EDITOR, FAILING, KNOWN_HELPER, helper_running_in


class NeverTryingATerminal(unittest.TestCase):
    def test_a_folder_and_program_editor_with_its_own_window_still_learns_that_window(self):
        desktop = desktop_showing([])
        appearing_once_launched(desktop, [], [window("e", "code", "harbour - Editor", 2)])
        start = Start(desktop, app_list((2, [EDITOR])), stops=True, answers_yes=True)
        start.run_and_offer()
        start.notifier.ask_within.assert_not_called()
        self.assertEqual(start.opened_in_terminal(), [])
        self.assertEqual(saved_once(start.store).placements()[0].app.learned_window, "code")

    def test_a_command_of_any_other_shape_is_never_put_in_a_terminal_even_when_it_stops(self):
        start = Start(desktop_showing([]), app_list((1, [FAILING])), stops=True, answers_yes=True)
        outcome, _ = start.run_and_offer()
        start.notifier.ask_within.assert_not_called()
        self.assertEqual(start.opened_in_terminal(), [])
        self.assertEqual(outcome.unseen, ["Failing"])

    def test_a_command_of_any_other_shape_is_launched_without_being_watched(self):
        start = Start(desktop_showing([]), app_list((1, [CHAT])))
        start.run()
        start.launches.new.assert_not_called()
        start.desktop.launch.assert_called_once_with(CHAT.command, 1)

    def test_a_folder_and_program_command_still_running_is_never_put_in_a_terminal(self):
        start = Start(desktop_showing([]), app_list((2, [HELPER])), stops=False, answers_yes=True)
        outcome, _ = start.run_and_offer()
        start.notifier.ask_within.assert_not_called()
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


if __name__ == "__main__":
    unittest.main()
