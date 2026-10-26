import unittest
from unittest import mock

from hiru_tsatsi.adapters import command_links
from hiru_tsatsi.adapters.command_links import SymbolicLinks

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


if __name__ == "__main__":
    unittest.main()
