import unittest

from tests.examples.app_lists import app_list
from tests.examples.windows import window
from tests.use_cases.mocked_list import desktop_showing
from tests.use_cases.starting_scene import Start
from tests.use_cases.terminal_examples import RULED_OUT


class AfterATerminalWasRuledOut(unittest.TestCase):
    def test_the_app_starts_plainly_without_being_watched_or_asked_about(self):
        start = Start(desktop_showing([]), app_list((2, [RULED_OUT])), stops=True, answers_yes=True)
        outcome = start.run()
        start.launches.new.assert_not_called()
        start.desktop.launch.assert_called_once_with(RULED_OUT.command, 2)
        self.assertEqual((outcome.stopped_without_window, outcome.unseen), ([], ["Editor"]))

    def test_a_window_that_takes_half_a_minute_is_still_placed(self):
        start = Start(desktop_showing([]), app_list((2, [RULED_OUT])), stops=True)
        start.window_appearing_after(30.0, window("e", "code", "harbour - Editor", 2))
        outcome = start.run()
        self.assertEqual((outcome.stopped_without_window, outcome.unseen), ([], []))


if __name__ == "__main__":
    unittest.main()
