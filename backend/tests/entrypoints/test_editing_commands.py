import unittest

from tests.entrypoints.mocked_services import Typed, mocked_services
from hiru_tsatsi.use_cases.ports import NotSaved
from hiru_tsatsi.work_apps.refusals import NumberTaken

TYPED_AND_CALLED = [
    (["add-workspace", "4", "Comms"], "add_workspace", (4, "Comms")),
    (["change-workspace", "4", "5", "Talk"], "change_workspace", (4, 5, "Talk")),
    (["remove-workspace", "4"], "remove_workspace", (4,)),
    (["add-services", "1", "Chat", "chat-services --new"], "add_app", (1, "Chat", "chat-services --new")),
    (["change-services", "1", "0", "Talk", "talk-services"], "change_app", (1, 0, "Talk", "talk-services")),
    (["remove-services", "1", "0"], "remove_app", (1, 0)),
    (["choose-window", "1", "0", "0xg"], "choose_window", (1, 0, "0xg")),
    (["forget-window", "1", "0"], "forget_window", (1, 0)),
]


class EditingFromTheCommandLine(unittest.TestCase):
    def test_each_command_makes_one_edit_with_what_was_typed(self):
        for argv, edit, arguments in TYPED_AND_CALLED:
            with self.subTest(command=argv[0]):
                services = mocked_services()
                typed = Typed(argv, services)
                getattr(services.edit, edit).assert_called_once_with(*arguments)
                self.assertEqual(typed.exit_code, 0)

    def test_a_refusal_is_said_in_words_and_fails(self):
        services = mocked_services()
        services.edit.add_workspace.side_effect = NumberTaken(1)
        typed = Typed(["add-workspace", "1", "Again"], services)
        self.assertEqual((typed.exit_code, typed.errors), (1, "Workspace 1 is already in use\n"))


    def test_a_list_that_could_not_be_saved_fails_in_words_not_a_crash(self):
        services = mocked_services()
        services.edit.add_workspace.side_effect = NotSaved("/home/sam/.config belongs to another account")
        typed = Typed(["add-workspace", "4", "Comms"], services)
        self.assertEqual((typed.exit_code, typed.errors),
                         (1, "Nothing was saved: /home/sam/.config belongs to another account.\n"))


if __name__ == "__main__":
    unittest.main()
