import tempfile
import unittest
from pathlib import Path

from hiru_tsatsi.adapters.tagged_launch import TaggedLaunch


def processes(*environments: bytes) -> Path:
    folder = Path(tempfile.mkdtemp())
    for number, environment in enumerate(environments, start=100):
        (folder / str(number)).mkdir()
        (folder / str(number) / "environ").write_bytes(environment)
    (folder / "self").mkdir()
    return folder


class KnowingWhenALaunchHasStopped(unittest.TestCase):
    def test_stopped_once_no_process_carries_its_tag(self):
        launch = TaggedLaunch(processes(b"HOME=/home/sam\0HIRU_TSATSI_LAUNCH=other\0"), tag="mine")
        self.assertTrue(launch.stopped())

    def test_running_while_any_process_carries_its_tag(self):
        launch = TaggedLaunch(processes(b"HOME=/home/sam\0", b"HIRU_TSATSI_LAUNCH=mine\0PATH=/usr/bin\0"), tag="mine")
        self.assertFalse(launch.stopped())

    def test_a_tag_that_only_starts_the_same_does_not_count(self):
        launch = TaggedLaunch(processes(b"HIRU_TSATSI_LAUNCH=mine-and-more\0"), tag="mine")
        self.assertTrue(launch.stopped())

    def test_when_processes_cannot_be_listed_it_never_claims_the_launch_stopped(self):
        self.assertFalse(TaggedLaunch(Path(tempfile.mkdtemp()) / "missing", tag="mine").stopped())

    def test_each_launch_gets_its_own_unguessable_tag(self):
        first, second = TaggedLaunch(), TaggedLaunch()
        self.assertNotEqual(first.entry, second.entry)
        self.assertGreaterEqual(len(first.entry.split("=", 1)[1]), 32)

    def test_the_tag_is_set_before_the_command_runs(self):
        self.assertEqual(TaggedLaunch(tag="mine").tagged("cd code && helper"),
                         "export HIRU_TSATSI_LAUNCH=mine\ncd code && helper")


if __name__ == "__main__":
    unittest.main()
