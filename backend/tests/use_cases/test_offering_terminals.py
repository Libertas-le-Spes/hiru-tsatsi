import unittest

from tests.examples.app_lists import app_list
from tests.examples.windows import window
from tests.use_cases.mocked_list import desktop_showing, saved_once
from tests.use_cases.starting_scene import HELPER, HELPERS_TERMINAL, STEAM, Start, appearing_once_launched
from tests.use_cases.terminal_examples import EDITOR, a_shell_waiting_in, helper_running_in
from hiru_tsatsi.use_cases.failures import AlreadyStarting
from hiru_tsatsi.use_cases.offering_terminals import ACTION, DECLINE, EXPLANATION, QUESTION_SECONDS, TerminalOffer
from hiru_tsatsi.use_cases.ports import Answer
from hiru_tsatsi.work_apps.app import App
from hiru_tsatsi.work_apps.windows import Window


class OfferingATerminal(unittest.TestCase):
    def test_a_folder_and_program_command_that_stops_without_a_window_asks_before_a_terminal(self):
        start = Start(desktop_showing([]), app_list((2, [HELPER])), stops=True, answers_yes=True)
        start.window_appearing_in_its_terminal(helper_running_in(HELPERS_TERMINAL, 2))
        outcome, offer = start.run_and_offer()
        start.notifier.ask_within.assert_called_once_with("Open Helper in a terminal?", EXPLANATION, ACTION,
                                                          DECLINE, QUESTION_SECONDS)
        self.assertTrue(start.opened_in_its_terminal(HELPER, 2))
        self.assertEqual((offer.now_opens_in_terminal, outcome.unseen), (["Helper"], []))

    def test_the_start_saves_what_it_learned_and_hands_over_what_stopped(self):
        start = Start(desktop_showing([]), app_list((2, [HELPER]), (6, [STEAM])), stops=True)
        appearing_once_launched(start.desktop, [], [window("s", "steam", "Steam", 6)])
        outcome = start.run()
        self.assertEqual(saved_once(start.store).placements()[1].app.learned_window, "steam")
        self.assertEqual(outcome.stopped_without_window, ["Helper"])
        self.assertEqual(outcome.for_the_offer.stopped, [app_list((2, [HELPER])).placements()[0]])

    def test_needing_a_terminal_is_saved_once_the_program_is_seen_running_in_it(self):
        start = Start(desktop_showing([]), app_list((2, [HELPER])), stops=True, answers_yes=True)
        start.window_appearing_in_its_terminal(helper_running_in(HELPERS_TERMINAL, 2))
        start.run_and_offer()
        remembered = saved_once(start.store).placements()[0].app
        self.assertEqual((remembered.opens_in_terminal, remembered.learned_window), (True, HELPERS_TERMINAL))

    def test_needing_a_terminal_is_saved_when_the_program_starts_a_moment_after_its_window(self):
        start = Start(desktop_showing([]), app_list((2, [HELPER])), stops=True, answers_yes=True)
        terminal_opened_at = []

        def shell_first_then_the_program() -> list[Window]:
            if not start.opened_in_terminal():
                return []
            if not terminal_opened_at:
                terminal_opened_at.append(start.clock.seconds)
            if start.clock.seconds < terminal_opened_at[0] + 2.0:
                return [a_shell_waiting_in(HELPERS_TERMINAL, 2)]
            return [helper_running_in(HELPERS_TERMINAL, 2)]

        start.desktop.windows.side_effect = shell_first_then_the_program
        _, offer = start.run_and_offer()
        self.assertEqual(offer.now_opens_in_terminal, ["Helper"])
        self.assertTrue(saved_once(start.store).placements()[0].app.opens_in_terminal)

    def test_saying_no_opens_no_terminal_and_is_remembered(self):
        start = Start(desktop_showing([]), app_list((2, [HELPER])), stops=True, answers_yes=False)
        _, offer = start.run_and_offer()
        self.assertEqual(start.opened_in_terminal(), [])
        self.assertTrue(saved_once(start.store).placements()[0].app.terminal_ruled_out)
        self.assertEqual(offer.not_offered_again, ["Helper"])

    def test_a_trial_whose_program_is_never_seen_in_it_is_never_tried_again(self):
        start = Start(desktop_showing([]), app_list((2, [HELPER])), stops=True, answers_yes=True)
        start.window_appearing_in_its_terminal(a_shell_waiting_in(HELPERS_TERMINAL, 2))
        _, offer = start.run_and_offer()
        remembered = saved_once(start.store).placements()[0].app
        self.assertEqual((remembered.opens_in_terminal, remembered.terminal_ruled_out), (False, True))
        self.assertEqual((offer.now_opens_in_terminal, offer.not_offered_again), ([], ["Helper"]))

    def test_a_trial_whose_window_shows_nothing_readable_inside_is_never_remembered(self):
        start = Start(desktop_showing([]), app_list((2, [HELPER])), stops=True, answers_yes=True)
        start.window_appearing_in_its_terminal(window("t", HELPERS_TERMINAL, "foot", 2, "", ""))
        _, offer = start.run_and_offer()
        remembered = saved_once(start.store).placements()[0].app
        self.assertEqual((remembered.opens_in_terminal, remembered.terminal_ruled_out), (False, True))
        self.assertEqual(offer.not_offered_again, ["Helper"])

    def test_a_trial_whose_terminal_never_appears_is_never_tried_again(self):
        start = Start(desktop_showing([]), app_list((2, [HELPER])), stops=True, answers_yes=True)
        _, offer = start.run_and_offer()
        self.assertEqual(len(start.opened_in_terminal()), 1)
        self.assertTrue(saved_once(start.store).placements()[0].app.terminal_ruled_out)
        self.assertEqual(offer.not_offered_again, ["Helper"])

    def test_an_app_changed_while_its_question_was_up_is_not_opened_in_a_terminal(self):
        start = Start(desktop_showing([]), app_list((2, [HELPER])), stops=True)
        outcome = start.run()

        def changed_then_clicked(summary: str, body: str, action: str, decline: str, seconds: float) -> Answer:
            start.store.load.return_value = app_list((2, [App("Helper", "cd code && other-helper")]))
            return Answer.YES

        start.notifier.ask_within.side_effect = changed_then_clicked
        offer = start.offering().run(outcome.for_the_offer)
        self.assertEqual(start.opened_in_terminal(), [])
        start.store.save.assert_not_called()
        self.assertEqual(offer, TerminalOffer())

    def test_a_window_it_knows_that_came_before_its_question_is_placed_and_never_asked_about(self):
        late_editor = window("e", "code", "harbour - Editor", 3)
        known_editor = App("Editor", "cd code && editor .", "code")
        start = Start(desktop_showing([]), app_list((2, [known_editor])), stops=True, answers_yes=True)
        outcome = start.run()
        start.desktop.windows.side_effect = None
        start.desktop.windows.return_value = [late_editor]
        offer = start.offering().run(outcome.for_the_offer)
        start.notifier.ask_within.assert_not_called()
        start.desktop.move.assert_called_once_with(late_editor, 2)
        self.assertEqual((offer.window_found_after_all, start.opened_in_terminal()), (["Editor"], []))

    def test_a_window_with_only_a_shell_left_in_it_is_never_taken_as_a_late_window(self):
        finished = window("e", "code", "harbour - Editor", 3, "bash", "/home/sam/code")
        known_editor = App("Editor", "cd code && editor .", "code")
        start = Start(desktop_showing([]), app_list((2, [known_editor])), stops=True)
        outcome = start.run()
        start.desktop.windows.side_effect = None
        start.desktop.windows.return_value = [finished]
        offer = start.offering().run(outcome.for_the_offer)
        start.desktop.move.assert_not_called()
        self.assertEqual(offer.window_found_after_all, [])

    def test_a_window_opened_by_hand_during_an_earlier_question_is_never_guessed_as_a_late_window(self):
        claude = App("Claude", "cd code && claude")
        start = Start(desktop_showing([]), app_list((2, [HELPER]), (3, [claude])), stops=True)
        outcome = start.run()
        by_hand = window("h", "foot", "~/code", 1, "", "")

        def opened_a_terminal_meanwhile(summary: str, body: str, action: str, decline: str,
                                        seconds: float) -> Answer:
            start.desktop.windows.side_effect = None
            start.desktop.windows.return_value = [by_hand]
            return Answer.NOT_ANSWERED

        start.notifier.ask_within.side_effect = opened_a_terminal_meanwhile
        offer = start.offering().run(outcome.for_the_offer)
        start.desktop.move.assert_not_called()
        self.assertEqual(start.notifier.ask_within.call_count, 2)
        self.assertEqual(offer.window_found_after_all, [])

    def test_a_window_the_start_gave_another_app_is_never_taken_as_a_late_window(self):
        editor_window = window("e", "code", "code", 3)
        claude = App("Claude", "cd code && claude")
        editor = App("Editor", "editor ~/code", "code")
        start = Start(desktop_showing([]), app_list((2, [claude]), (3, [editor])), stops=True, answers_yes=False)
        appearing_once_launched(start.desktop, [], [editor_window])
        outcome = start.run()
        start.names.record.reset_mock()
        offer = start.offering().run(outcome.for_the_offer)
        start.names.record.assert_not_called()
        start.desktop.move.assert_not_called()
        self.assertEqual(offer.window_found_after_all, [])
        start.notifier.ask_within.assert_called_once()

    def test_a_question_without_an_answer_decides_nothing_and_is_asked_again_next_time(self):
        start = Start(desktop_showing([]), app_list((2, [HELPER])), stops=True)
        start.notifier.ask_within.return_value = Answer.NOT_ANSWERED
        _, offer = start.run_and_offer()
        self.assertEqual(start.opened_in_terminal(), [])
        start.store.save.assert_not_called()
        self.assertEqual(offer, TerminalOffer())
        start.run_and_offer()
        self.assertEqual(start.notifier.ask_within.call_count, 2)

    def test_an_app_changed_before_its_question_is_not_asked_about(self):
        start = Start(desktop_showing([]), app_list((2, [HELPER])), stops=True, answers_yes=True)
        outcome = start.run()
        start.store.load.return_value = app_list((2, [App("Helper", "cd code && other-helper")]))
        offer = start.offering().run(outcome.for_the_offer)
        start.notifier.ask_within.assert_not_called()
        self.assertEqual(offer, TerminalOffer())

    def test_a_no_to_an_app_changed_while_its_question_was_up_rules_nothing_out(self):
        start = Start(desktop_showing([]), app_list((2, [HELPER])), stops=True)
        outcome = start.run()

        def changed_then_declined(summary: str, body: str, action: str, decline: str, seconds: float) -> Answer:
            start.store.load.return_value = app_list((2, [App("Helper", "cd code && other-helper")]))
            return Answer.NO

        start.notifier.ask_within.side_effect = changed_then_declined
        offer = start.offering().run(outcome.for_the_offer)
        start.store.save.assert_not_called()
        self.assertEqual(offer, TerminalOffer())

    def test_the_offer_asks_nothing_while_another_start_holds_the_lock(self):
        start = Start(desktop_showing([]), app_list((2, [HELPER])), stops=True)
        outcome = start.run()
        start.one_at_a_time.claimed.return_value = False
        with self.assertRaises(AlreadyStarting):
            start.offering().run(outcome.for_the_offer)
        start.notifier.ask_within.assert_not_called()

    def test_a_window_that_arrives_just_before_ten_seconds_is_placed(self):
        start = Start(desktop_showing([]), app_list((2, [HELPER])), stops=True)
        arriving = helper_running_in("foot", 2)
        start.window_appearing_after(9.8, arriving)
        outcome = start.run()
        start.names.record.assert_called_once_with(arriving, "Helper")
        self.assertEqual((outcome.stopped_without_window, outcome.unseen), ([], []))

    def test_a_window_that_arrives_after_its_launcher_stopped_is_still_placed(self):
        late_editor = window("e", "code", "harbour - Editor", 2)
        start = Start(desktop_showing([]), app_list((2, [EDITOR]), (6, [STEAM])), stops=True)

        def editor_at_fifteen_seconds_steam_at_twenty() -> list[Window]:
            shown = []
            if start.clock.seconds >= 15.0:
                shown.append(late_editor)
            if start.clock.seconds >= 20.0:
                shown.append(window("s", "steam", "Steam", 6))
            return shown

        start.desktop.windows.side_effect = editor_at_fifteen_seconds_steam_at_twenty
        outcome = start.run()
        start.names.record.assert_any_call(late_editor, "Editor")
        self.assertEqual((outcome.stopped_without_window, outcome.unseen), ([], []))


if __name__ == "__main__":
    unittest.main()
