import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import create_autospec

from hiru_tsatsi.entrypoints.install.linking import link_commands
from hiru_tsatsi.use_cases.installing import LinkCommands, Linked, NotOurs

INSTALL_SCRIPT = Path(__file__).resolve().parents[3] / "install.sh"
BIN = "/home/sam/.local/bin"


def run(linking) -> tuple[int, str, str]:
    printed = io.StringIO()
    errors = io.StringIO()
    with redirect_stdout(printed), redirect_stderr(errors):
        exit_code = link_commands(linking)
    return exit_code, printed.getvalue(), errors.getvalue()


class TheLinkingStep(unittest.TestCase):
    def test_says_what_it_linked_and_what_it_retired(self):
        linking = create_autospec(LinkCommands, instance=True)
        linking.run.return_value = Linked(f"{BIN}/hiru-tsatsi", f"{BIN}/tsatsi", f"{BIN}/hiru")
        exit_code, printed, _ = run(linking)
        self.assertEqual(exit_code, 0)
        self.assertEqual(printed, f"removed:  {BIN}/hiru, the old short name; type 'tsatsi' now\n"
                                  f"command:  {BIN}/hiru-tsatsi, and {BIN}/tsatsi for short\n")

    def test_a_refusal_fails_and_says_which_path(self):
        linking = create_autospec(LinkCommands, instance=True)
        linking.run.side_effect = NotOurs(f"{BIN}/tsatsi")
        exit_code, _, errors = run(linking)
        self.assertEqual(exit_code, 1)
        self.assertIn(f"{BIN}/tsatsi is already there and is not Hiru Tsatsi", errors)

    def test_the_installer_links_through_this_step_and_stops_if_it_fails(self):
        self.assertIn('python3 -P -m hiru_tsatsi.entrypoints.install "$bin_dir" "$here/backend/bin/hiru-tsatsi" || exit 1',
                      INSTALL_SCRIPT.read_text())


if __name__ == "__main__":
    unittest.main()
