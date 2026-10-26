import unittest

from tests.entrypoints.mocked_app import Typed, mocked_app
from hiru_tsatsi.work_apps.refusals import NumberTaken

TYPED_AND_CALLED = [
    (["add-workspace", "4", "Comms"], "add_workspace", (4, "Comms")),
    (["change-workspace", "4", "5", "Talk"], "change_workspace", (4, 5, "Talk")),
    (["remove-workspace", "4"], "remove_workspace", (4,)),
    (["add-app", "1", "Chat", "chat-app --new"], "add_app", (1, "Chat", "chat-app --new")),
    (["change-app", "1", "0", "Talk", "talk-app"], "change_app", (1, 0, "Talk", "talk-app")),
    (["remove-app", "1", "0"], "remove_app", (1, 0)),
    (["choose-window", "1", "0", "0xg"], "choose_window", (1, 0, "0xg")),
    (["forget-window", "1", "0"], "forget_window", (1, 0)),
]


class EditingFromTheCommandLine(unittest.TestCase):
    def test_each_command_makes_one_edit_with_what_was_typed(self):
        for argv, edit, arguments in TYPED_AND_CALLED:
            with self.subTest(command=argv[0]):
                app = mocked_app()
                typed = Typed(argv, app)
                getattr(app.edit, edit).assert_called_once_with(*arguments)
                self.assertEqual(typed.exit_code, 0)

    def test_a_refusal_is_said_in_words_and_fails(self):
        app = mocked_app()
        app.edit.add_workspace.side_effect = NumberTaken(1)
        typed = Typed(["add-workspace", "1", "Again"], app)
        self.assertEqual((typed.exit_code, typed.errors), (1, "Workspace 1 is already in use\n"))


if __name__ == "__main__":
    unittest.main()
