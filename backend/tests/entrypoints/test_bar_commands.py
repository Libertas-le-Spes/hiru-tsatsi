import json
import unittest

from tests.entrypoints.mocked_services import Typed, mocked_services
from tests.examples.windows import window
from hiru_tsatsi.work_apps.refusals import NothingThere


class WhatTheBarPanelAsks(unittest.TestCase):
    def test_overview_prints_the_bar_state_once_as_json(self):
        services = mocked_services()
        services.overview.run.return_value = []
        typed = Typed(["overview"], services)
        services.overview.run.assert_called_once_with()
        self.assertEqual(json.loads(typed.printed), {"workspaces": []})

    def test_windows_for_asks_for_that_apps_candidates_and_prints_them(self):
        services = mocked_services()
        services.overview.candidates.return_value = [window("0xg", "chrome-gitlab.com-Default", "Issue Boards", 4)]
        typed = Typed(["windows-for", "1", "0"], services)
        services.overview.candidates.assert_called_once_with(1, 0)
        self.assertEqual(json.loads(typed.printed), [{"address": "0xg", "title": "Issue Boards", "workspace": 4}])

    def test_windows_for_an_app_that_is_gone_fails_in_words(self):
        services = mocked_services()
        services.overview.candidates.side_effect = NothingThere()
        typed = Typed(["windows-for", "1", "9"], services)
        self.assertEqual(typed.exit_code, 1)
        self.assertIn("no longer there", typed.errors)


if __name__ == "__main__":
    unittest.main()
