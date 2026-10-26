import unittest
from unittest import mock

from tests.adapters.mocked_processes import Running, processes_running
from hiru_tsatsi.adapters import tagged_launch
from hiru_tsatsi.adapters.tagged_launch import TaggedLaunch

MINE = "HIRU_TSATSI_LAUNCH=mine"


def launch_among(running: dict[int, Running]) -> TaggedLaunch:
    return TaggedLaunch(processes_running(running), tag="mine")


class KnowingWhenALaunchHasStopped(unittest.TestCase):
    def test_stopped_once_no_process_carries_its_tag(self):
        running = {100: Running("helper", environment=["HOME=/home/sam", "HIRU_TSATSI_LAUNCH=other"])}
        self.assertTrue(launch_among(running).stopped())

    def test_running_while_any_process_carries_its_tag(self):
        running = {100: Running("bash", environment=["HOME=/home/sam"]),
                   101: Running("helper", environment=[MINE, "PATH=/usr/bin"])}
        self.assertFalse(launch_among(running).stopped())

    def test_a_tag_that_only_starts_the_same_does_not_count(self):
        self.assertTrue(launch_among({100: Running("helper", environment=[MINE + "-and-more"])}).stopped())

    def test_when_processes_cannot_be_listed_it_never_claims_the_launch_stopped(self):
        processes = processes_running({})
        processes.pids.return_value = None
        self.assertFalse(TaggedLaunch(processes, tag="mine").stopped())

    def test_each_launch_asks_for_a_fresh_random_tag_of_sixteen_bytes(self):
        with mock.patch.object(tagged_launch.secrets, "token_hex", return_value="f00d") as token_hex:
            launch = TaggedLaunch(processes_running({}))
        token_hex.assert_called_once_with(16)
        self.assertEqual(launch.entry, "HIRU_TSATSI_LAUNCH=f00d")

    def test_the_tag_is_set_before_the_command_runs(self):
        self.assertEqual(launch_among({}).tagged("cd code && helper"), "export HIRU_TSATSI_LAUNCH=mine\ncd code && helper")


if __name__ == "__main__":
    unittest.main()
