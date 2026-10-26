import unittest
from unittest import mock

from hiru_tsatsi.adapters import command_links
from hiru_tsatsi.adapters.command_links import SymbolicLinks
from hiru_tsatsi.use_cases.failures import NotSaved

TSATSI = "/home/sam/.local/bin/tsatsi"


def a_link_to(target: str | None) -> mock.MagicMock:
    place = mock.MagicMock(name="place")
    place.is_symlink.return_value = target is not None
    place.readlink.return_value = target
    return place


class TellingWhetherALinkIsOurs(unittest.TestCase):
    def test_a_link_to_any_hiru_tsatsi_launcher_is_ours(self):
        with mock.patch.object(command_links, "Path", return_value=a_link_to("/elsewhere/hiru-tsatsi/backend/bin/hiru-tsatsi")):
            self.assertTrue(SymbolicLinks().is_ours(TSATSI))

    def test_a_link_to_something_else_is_not(self):
        with mock.patch.object(command_links, "Path", return_value=a_link_to("/usr/bin/another-tool")):
            self.assertFalse(SymbolicLinks().is_ours(TSATSI))

    def test_a_file_that_is_not_a_link_is_not(self):
        with mock.patch.object(command_links, "Path", return_value=a_link_to(None)):
            self.assertFalse(SymbolicLinks().is_ours(TSATSI))


class LinkingACommand(unittest.TestCase):
    def test_a_link_that_cannot_be_made_is_reported_as_not_saved(self):
        place = a_link_to(None)
        place.symlink_to.side_effect = NotADirectoryError("~/.local/bin is a file")
        with mock.patch.object(command_links, "Path", return_value=place):
            with self.assertRaises(NotSaved):
                SymbolicLinks().link(TSATSI, "/home/sam/apps/hiru-tsatsi/backend/bin/hiru-tsatsi")


if __name__ == "__main__":
    unittest.main()
