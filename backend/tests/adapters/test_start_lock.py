import unittest
from pathlib import Path
from unittest import mock

from hiru_tsatsi.adapters import start_lock
from hiru_tsatsi.adapters.start_lock import OPENING, OWNER_ONLY, StartLock
from hiru_tsatsi.use_cases.failures import CannotTellIfStarting

LOCK = Path("/run/user/1000/hiru-tsatsi-start.lock")
ACCOUNT = 1000
OPENED = 7


def owned_by(account: int) -> mock.Mock:
    status = mock.Mock()
    status.st_uid = account
    return status


class OneStartAtATime(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.object(start_lock, "os", wraps=start_lock.os)
        self.os = patcher.start()
        self.addCleanup(patcher.stop)
        self.os.open = mock.Mock(return_value=OPENED)
        self.os.fstat = mock.Mock(return_value=owned_by(ACCOUNT))
        self.os.close = mock.Mock()
        flock_patcher = mock.patch.object(start_lock.fcntl, "flock")
        self.flock = flock_patcher.start()
        self.addCleanup(flock_patcher.stop)

    def test_the_first_start_claims_the_owner_only_lock_without_following_links(self):
        self.assertTrue(StartLock(LOCK, ACCOUNT).claimed())
        self.os.open.assert_called_once_with(LOCK, OPENING, OWNER_ONLY)
        self.flock.assert_called_once_with(OPENED, start_lock.fcntl.LOCK_EX | start_lock.fcntl.LOCK_NB)

    def test_a_start_while_another_holds_the_lock_is_refused(self):
        self.flock.side_effect = BlockingIOError()
        self.assertFalse(StartLock(LOCK, ACCOUNT).claimed())
        self.os.close.assert_called_once_with(OPENED)

    def test_claiming_again_in_the_same_start_keeps_the_lock_it_holds(self):
        lock = StartLock(LOCK, ACCOUNT)
        lock.claimed()
        self.assertTrue(lock.claimed())
        self.os.open.assert_called_once()

    def test_without_a_runtime_folder_it_cannot_tell(self):
        with self.assertRaises(CannotTellIfStarting):
            StartLock(None, ACCOUNT).claimed()

    def test_a_lock_that_cannot_be_opened_means_it_cannot_tell(self):
        self.os.open.side_effect = PermissionError(13, "Permission denied")
        with self.assertRaises(CannotTellIfStarting):
            StartLock(LOCK, ACCOUNT).claimed()

    def test_a_lock_of_another_account_means_it_cannot_tell(self):
        self.os.fstat.return_value = owned_by(1001)
        with self.assertRaises(CannotTellIfStarting):
            StartLock(LOCK, ACCOUNT).claimed()
        self.os.close.assert_called_once_with(OPENED)
        self.flock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
