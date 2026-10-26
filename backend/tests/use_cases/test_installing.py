import unittest
from unittest.mock import Mock, call, create_autospec

from hiru_tsatsi.use_cases.installing import LinkCommands, NotOurs
from hiru_tsatsi.use_cases.ports import CommandLinks

BIN = "/home/sam/.local/bin"
LAUNCHER = "/home/sam/apps/hiru-tsatsi/backend/bin/hiru-tsatsi"
EARLIER_INSTALL = "/elsewhere/hiru-tsatsi/backend/bin/hiru-tsatsi"


class Links:
    def __init__(self, present: dict[str, str]):
        self.present_now = present

    def present(self, path: str) -> bool:
        return path in self.present_now

    def points_at(self, path: str) -> str:
        return self.present_now.get(path, "")


def links_with(present: dict[str, str]) -> Mock:
    held = Links(present)
    links = create_autospec(CommandLinks, instance=True)
    links.present.side_effect = held.present
    links.points_at.side_effect = held.points_at
    return links


class LinkingTheCommands(unittest.TestCase):
    def test_links_both_names_to_the_launcher_when_they_are_free(self):
        links = links_with({})
        linked = LinkCommands(links, BIN, LAUNCHER).run()
        self.assertEqual(links.link.call_args_list, [call(f"{BIN}/hiru-tsatsi", LAUNCHER), call(f"{BIN}/tsatsi", LAUNCHER)])
        self.assertIsNone(linked.retired)

    def test_replaces_a_link_to_an_earlier_install(self):
        links = links_with({f"{BIN}/tsatsi": EARLIER_INSTALL})
        LinkCommands(links, BIN, LAUNCHER).run()
        links.link.assert_any_call(f"{BIN}/tsatsi", LAUNCHER)

    def test_refuses_another_tool_of_the_same_name_and_links_nothing(self):
        links = links_with({f"{BIN}/tsatsi": ""})
        with self.assertRaises(NotOurs) as refused:
            LinkCommands(links, BIN, LAUNCHER).run()
        self.assertEqual(refused.exception.path, f"{BIN}/tsatsi")
        links.link.assert_not_called()
        links.remove.assert_not_called()

    def test_refuses_a_link_that_points_at_something_else(self):
        links = links_with({f"{BIN}/hiru-tsatsi": "/usr/bin/another-tool"})
        with self.assertRaises(NotOurs):
            LinkCommands(links, BIN, LAUNCHER).run()
        links.link.assert_not_called()

    def test_removes_the_old_short_name_once_when_it_is_ours(self):
        links = links_with({f"{BIN}/hiru": EARLIER_INSTALL})
        linked = LinkCommands(links, BIN, LAUNCHER).run()
        links.remove.assert_called_once_with(f"{BIN}/hiru")
        self.assertEqual(linked.retired, f"{BIN}/hiru")

    def test_keeps_another_tool_called_hiru(self):
        links = links_with({f"{BIN}/hiru": ""})
        LinkCommands(links, BIN, LAUNCHER).run()
        links.remove.assert_not_called()


if __name__ == "__main__":
    unittest.main()
