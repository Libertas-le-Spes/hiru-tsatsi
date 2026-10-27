import unittest
from unittest import mock

from tests.adapters.mocked_processes import Running, processes_running
from hiru_tsatsi.adapters import tagged_launch
from hiru_tsatsi.adapters.tagged_launch import TaggedLaunch, TaggedLaunches

ACCOUNT = 1000
MINE = "HIRU_TSATSI_LAUNCH=mine"


def the_owner() -> int:
    return ACCOUNT


def launch_among(running: dict[int, Running]) -> TaggedLaunch:
    return TaggedLaunch(processes_running(running), "mine", ACCOUNT)


class KnowingWhenALaunchHasStopped(unittest.TestCase):
    def test_stopped_once_no_process_started_since_carries_its_tag(self):
        running = {100: Running("helper", environment=["HOME=/home/sam", "HIRU_TSATSI_LAUNCH=other"])}
        self.assertTrue(launch_among(running).stopped())

    def test_running_while_a_process_started_since_carries_its_tag(self):
        running = {100: Running("bash", environment=["HOME=/home/sam"]),
                   101: Running("helper", environment=[MINE, "PATH=/usr/bin"])}
        self.assertFalse(launch_among(running).stopped())

    def test_a_tag_that_only_starts_the_same_does_not_count(self):
        self.assertTrue(launch_among({100: Running("helper", environment=[MINE + "-and-more"])}).stopped())

    def test_a_process_started_since_whose_environment_cannot_be_read_means_it_cannot_tell(self):
        self.assertFalse(launch_among({100: Running("helper", environment=None)}).stopped())

    def test_a_process_started_before_the_launch_is_not_asked_even_if_unreadable(self):
        self.assertTrue(launch_among({1: Running("systemd", environment=None, started=17.0)}).stopped())

    def test_a_process_whose_start_cannot_be_read_is_asked_and_counts_while_it_carries_the_tag(self):
        self.assertFalse(launch_among({100: Running("helper", environment=[MINE], started=None)}).stopped())

    def test_a_process_whose_start_cannot_be_read_is_asked_and_does_not_count_without_the_tag(self):
        running = {100: Running("helper", environment=["HOME=/home/sam"], started=None)}
        self.assertTrue(launch_among(running).stopped())

    def test_a_process_whose_start_and_environment_cannot_be_read_means_it_cannot_tell(self):
        self.assertFalse(launch_among({100: Running("helper", environment=None, started=None)}).stopped())

    def test_when_the_time_since_boot_cannot_be_read_it_never_claims_the_launch_stopped(self):
        processes = processes_running({})
        processes.seconds_since_boot.return_value = None
        self.assertFalse(TaggedLaunch(processes, "mine", ACCOUNT).stopped())

    def test_looks_only_at_the_owners_processes(self):
        processes = processes_running({})
        TaggedLaunch(processes, "mine", ACCOUNT).stopped()
        processes.own_pids.assert_called_once_with(ACCOUNT)

    def test_when_processes_cannot_be_listed_it_never_claims_the_launch_stopped(self):
        processes = processes_running({})
        processes.own_pids.return_value = None
        self.assertFalse(TaggedLaunch(processes, "mine", ACCOUNT).stopped())

    def test_the_tag_is_set_before_the_command_runs(self):
        self.assertEqual(launch_among({}).wrapped("cd code && helper"), "export HIRU_TSATSI_LAUNCH=mine\ncd code && helper")


class MakingNewLaunches(unittest.TestCase):
    def test_each_launch_asks_for_a_fresh_random_tag_of_sixteen_bytes(self):
        with mock.patch.object(tagged_launch.secrets, "token_hex", return_value="f00d") as token_hex:
            launch = TaggedLaunches(processes_running({}), account=the_owner).new()
        token_hex.assert_called_once_with(16)
        self.assertEqual((launch.entry, launch.account), ("HIRU_TSATSI_LAUNCH=f00d", ACCOUNT))


if __name__ == "__main__":
    unittest.main()
