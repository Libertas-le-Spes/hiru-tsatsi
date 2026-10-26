import unittest
from unittest.mock import Mock, call, create_autospec

from hiru_tsatsi.use_cases.installing import LinkCommands, NotOurs
from hiru_tsatsi.use_cases.ports import CommandLinks

BIN = "/home/sam/.local/bin"
LAUNCHER = "/home/sam/apps/hiru-tsatsi/backend/bin/hiru-tsatsi"
OURS = True
ANOTHER_TOOL = False


class AlreadyThere:
    def __init__(self, present: dict[str, bool]):
        self.present_now = present

    def present(self, path: str) -> bool:
        return path in self.present_now

    def is_ours(self, path: str) -> bool:
        return self.present_now.get(path, False)


def links_with(present: dict[str, bool]) -> Mock:
    there = AlreadyThere(present)
    links = create_autospec(CommandLinks, instance=True)
    links.present.side_effect = there.present
    links.is_ours.side_effect = there.is_ours
    return links


class LinkingTheCommands(unittest.TestCase):
    def test_links_both_names_to_the_launcher_when_they_are_free(self):
        links = links_with({})
        linked = LinkCommands(links, BIN, LAUNCHER).run()
        self.assertEqual(links.link.call_args_list, [call(f"{BIN}/hiru-tsatsi", LAUNCHER), call(f"{BIN}/tsatsi", LAUNCHER)])
        self.assertIsNone(linked.retired)

    def test_replaces_a_link_to_an_earlier_install(self):
        links = links_with({f"{BIN}/tsatsi": OURS})
        LinkCommands(links, BIN, LAUNCHER).run()
        links.link.assert_any_call(f"{BIN}/tsatsi", LAUNCHER)

    def test_refuses_another_tool_of_the_same_name_and_changes_nothing(self):
        links = links_with({f"{BIN}/tsatsi": ANOTHER_TOOL})
        with self.assertRaises(NotOurs) as refused:
            LinkCommands(links, BIN, LAUNCHER).run()
        self.assertEqual(refused.exception.path, f"{BIN}/tsatsi")
        links.link.assert_not_called()
        links.remove.assert_not_called()

    def test_removes_the_old_short_name_once_when_it_is_ours(self):
        links = links_with({f"{BIN}/hiru": OURS})
        linked = LinkCommands(links, BIN, LAUNCHER).run()
        links.remove.assert_called_once_with(f"{BIN}/hiru")
        self.assertEqual(linked.retired, f"{BIN}/hiru")

    def test_keeps_another_tool_called_hiru(self):
        links = links_with({f"{BIN}/hiru": ANOTHER_TOOL})
        LinkCommands(links, BIN, LAUNCHER).run()
        links.remove.assert_not_called()


if __name__ == "__main__":
    unittest.main()
