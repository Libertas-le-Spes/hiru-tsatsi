import subprocess
import unittest
from unittest import mock

from hiru_tsatsi.adapters import notify_send
from hiru_tsatsi.adapters.notify_send import NotifySend

QUESTION_PROCESS = subprocess.Popen


def asking_answered(first_line: str, answer: str) -> mock.Mock:
    asking = mock.create_autospec(QUESTION_PROCESS, instance=True)
    asking.stdout = mock.Mock()
    asking.stdout.readline.return_value = first_line
    asking.communicate.return_value = (answer, "")
    return asking


class AskingWithADeadline(unittest.TestCase):
    def setUp(self):
        which = mock.patch.object(notify_send.shutil, "which", return_value="/usr/bin/notify-send")
        which.start()
        self.addCleanup(which.stop)
        popen = mock.patch.object(notify_send.subprocess, "Popen")
        self.popen = popen.start()
        self.addCleanup(popen.stop)
        run = mock.patch.object(notify_send.subprocess, "run")
        self.run = run.start()
        self.addCleanup(run.stop)

    def test_a_click_is_a_yes_within_the_time_given(self):
        self.popen.return_value = asking_answered("42\n", "start\n")
        self.assertTrue(NotifySend().ask_within("Open Helper?", "Why", "Open", 60))
        self.popen.return_value.communicate.assert_called_once_with(timeout=60)
        self.run.assert_not_called()

    def test_a_dismissal_is_a_no(self):
        self.popen.return_value = asking_answered("42\n", "")
        self.assertFalse(NotifySend().ask_within("Open Helper?", "Why", "Open", 60))

    def test_no_answer_in_time_is_a_no_and_the_question_is_taken_off_the_screen(self):
        asking = asking_answered("42\n", "")
        asking.communicate.side_effect = subprocess.TimeoutExpired("notify-send", 60)
        self.popen.return_value = asking
        self.assertFalse(NotifySend().ask_within("Open Helper?", "Why", "Open", 60))
        asking.kill.assert_called_once_with()
        closing = self.run.call_args.args[0]
        self.assertEqual(closing[-2:], ["org.freedesktop.Notifications.CloseNotification", "42"])


if __name__ == "__main__":
    unittest.main()
