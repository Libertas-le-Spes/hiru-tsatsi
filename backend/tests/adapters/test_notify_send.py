import subprocess
import unittest
from unittest import mock

from hiru_tsatsi.adapters import notify_send
from hiru_tsatsi.adapters.notify_send import NotifySend
from hiru_tsatsi.use_cases.ports import Answer

QUESTION_PROCESS = subprocess.Popen
CLOSING = ["gdbus", "call", "--session", "--dest", "org.freedesktop.Notifications",
           "--object-path", "/org/freedesktop/Notifications",
           "--method", "org.freedesktop.Notifications.CloseNotification", "42"]


def asking_that_prints(printed: str, exit_code: int = 0) -> mock.Mock:
    asking = mock.create_autospec(QUESTION_PROCESS, instance=True)
    asking.communicate.return_value = (printed, None)
    asking.returncode = exit_code
    return asking


class AskingWithADeadline(unittest.TestCase):
    def setUp(self):
        which = mock.patch.object(notify_send.shutil, "which", autospec=True, return_value="/usr/bin/notify-send")
        self.which = which.start()
        self.addCleanup(which.stop)
        popen = mock.patch.object(notify_send.subprocess, "Popen", autospec=True)
        self.popen = popen.start()
        self.addCleanup(popen.stop)
        run = mock.patch.object(notify_send.subprocess, "run", autospec=True)
        self.run = run.start()
        self.addCleanup(run.stop)

    def test_asks_with_its_number_shown_and_the_action_on_both_click_and_button(self):
        self.popen.return_value = asking_that_prints("42\n")
        NotifySend().ask_within("Open Helper?", "Why", "Open", "Never", 60)
        self.popen.assert_called_once_with(
            ["notify-send", "-a", "Hiru Tsatsi", "--urgency=critical", "--print-id", "--action=never=Never",
             "--action=default=Open", "--action=start=Open", "--", "Open Helper?", "Why"],
            stdout=subprocess.PIPE, text=True)

    def test_a_click_is_a_yes_within_the_time_given(self):
        self.popen.return_value = asking_that_prints("42\nstart\n")
        self.assertEqual(NotifySend().ask_within("Open Helper?", "Why", "Open", "Never", 60), Answer.YES)
        self.popen.return_value.communicate.assert_called_once_with(timeout=60)
        self.run.assert_not_called()

    def test_only_the_button_that_says_never_is_a_no(self):
        self.popen.return_value = asking_that_prints("42\nnever\n")
        self.assertEqual(NotifySend().ask_within("Open Helper?", "Why", "Open", "Never", 60), Answer.NO)

    def test_without_notify_send_nothing_is_asked_and_there_is_no_answer(self):
        self.which.return_value = None
        self.assertEqual(NotifySend().ask_within("Open Helper?", "Why", "Open", "Never", 60), Answer.NOT_ANSWERED)
        self.popen.assert_not_called()

    def test_a_question_no_service_could_show_has_no_answer(self):
        self.popen.return_value = asking_that_prints("", exit_code=1)
        self.assertEqual(NotifySend().ask_within("Open Helper?", "Why", "Open", "Never", 60), Answer.NOT_ANSWERED)

    def test_a_question_closed_without_a_click_is_no_answer(self):
        self.popen.return_value = asking_that_prints("42\n")
        self.assertEqual(NotifySend().ask_within("Open Helper?", "Why", "Open", "Never", 60), Answer.NOT_ANSWERED)

    def test_a_click_landing_at_the_deadline_still_counts(self):
        asking = asking_that_prints("42\n")
        asking.communicate.side_effect = [subprocess.TimeoutExpired("notify-send", 60), ("42\nstart\n", None)]
        self.popen.return_value = asking
        self.assertEqual(NotifySend().ask_within("Open Helper?", "Why", "Open", "Never", 60), Answer.YES)

    def test_no_answer_in_time_is_no_answer_and_the_question_is_taken_off_the_screen(self):
        asking = asking_that_prints("42\n")
        asking.communicate.side_effect = [subprocess.TimeoutExpired("notify-send", 60), ("42\n", None)]
        self.popen.return_value = asking
        self.assertEqual(NotifySend().ask_within("Open Helper?", "Why", "Open", "Never", 60), Answer.NOT_ANSWERED)
        asking.kill.assert_called_once_with()
        self.run.assert_called_once_with(CLOSING, capture_output=True, check=False)


if __name__ == "__main__":
    unittest.main()
