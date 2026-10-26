import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import Mock, create_autospec

from tests.entrypoints.mocked_services import mocked_services
from hiru_tsatsi.entrypoints.install.install_command import install
from hiru_tsatsi.use_cases.failures import DesktopNotSupported, SetUpFailed
from hiru_tsatsi.use_cases.failures import NotOurs
from hiru_tsatsi.use_cases.installing import LinkCommands, Linked
from hiru_tsatsi.use_cases.setting_up import SetUp
from hiru_tsatsi.work_apps.shortcut import Keys

BIN = "/home/sam/.local/bin"
LAUNCHER = "/home/sam/apps/hiru-tsatsi/backend/bin/hiru-tsatsi"


def linking_that_links(retired: str | None = None) -> Mock:
    linking = create_autospec(LinkCommands, instance=True)
    linking.run.return_value = Linked(f"{BIN}/hiru-tsatsi", f"{BIN}/tsatsi", retired)
    return linking


class Installed:
    def __init__(self, linking: Mock, opening: Mock):
        self.linking_for = Mock(return_value=linking)
        self.opening = opening
        printed = io.StringIO()
        errors = io.StringIO()
        with redirect_stdout(printed), redirect_stderr(errors):
            self.exit_code = install([BIN, LAUNCHER], self.linking_for, opening)
        self.printed = printed.getvalue()
        self.errors = errors.getvalue()


def services_that_set_up() -> Mock:
    services = mocked_services()
    services.set_up.run.return_value = SetUp(Keys.parse("SUPER + CTRL + U"), kept=False)
    return Mock(return_value=services)


class InstallingTheCommand(unittest.TestCase):
    def test_links_for_the_given_folder_and_launcher_then_sets_up_once(self):
        opening = services_that_set_up()
        installed = Installed(linking_that_links(), opening)
        installed.linking_for.assert_called_once_with(BIN, LAUNCHER)
        opening.return_value.set_up.run.assert_called_once_with()
        self.assertEqual(installed.exit_code, 0)
        self.assertIn(f"command:  {BIN}/hiru-tsatsi, and {BIN}/tsatsi for short", installed.printed)

    def test_says_when_it_retired_the_old_short_name(self):
        installed = Installed(linking_that_links(retired=f"{BIN}/hiru"), services_that_set_up())
        self.assertIn(f"removed:  {BIN}/hiru, the old short name; type 'tsatsi' now", installed.printed)

    def test_a_refused_link_fails_in_words_and_sets_nothing_up(self):
        linking = create_autospec(LinkCommands, instance=True)
        linking.run.side_effect = NotOurs(f"{BIN}/tsatsi")
        opening = services_that_set_up()
        installed = Installed(linking, opening)
        opening.assert_not_called()
        self.assertEqual(installed.exit_code, 1)
        self.assertIn(f"{BIN}/tsatsi is already there and is not Hiru Tsatsi", installed.errors)

    def test_an_unsupported_desktop_skips_set_up_and_still_succeeds(self):
        opening = Mock(side_effect=DesktopNotSupported("GNOME"))
        installed = Installed(linking_that_links(), opening)
        self.assertEqual(installed.exit_code, 0)
        self.assertIn("skipped:  the shortcut and the login question, as Hiru Tsatsi can't place windows on GNOME yet; "
                      "the command itself is installed", installed.printed)

    def test_a_real_set_up_problem_still_fails_the_install(self):
        opening = services_that_set_up()
        opening.return_value.set_up.run.side_effect = SetUpFailed("hiru-tsatsi.lua:1: bad")
        installed = Installed(linking_that_links(), opening)
        self.assertEqual(installed.exit_code, 1)


    def test_run_by_hand_without_its_two_arguments_it_says_how_to_use_it(self):
        errors = io.StringIO()
        with redirect_stderr(errors):
            exit_code = install([], Mock(), Mock())
        self.assertEqual(exit_code, 2)
        self.assertIn("usage:", errors.getvalue())

if __name__ == "__main__":
    unittest.main()
