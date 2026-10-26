import json
import unittest
from pathlib import Path

from tests.adapters.mocked_files import files_holding
from hiru_tsatsi.adapters.storage.app_list_file import AppListFile
from hiru_tsatsi.adapters.storage.app_list_format import from_omastart, from_saved, to_saved
from hiru_tsatsi.adapters.storage.json_object import json_text
from hiru_tsatsi.use_cases.ports import NotReadable
from hiru_tsatsi.work_apps.app import App
from hiru_tsatsi.work_apps.app_list import AppList
from hiru_tsatsi.work_apps.workspace import Workspace

LIST = Path("/home/sam/.config/hiru-tsatsi/apps.json")
WORKBENCH = Path("/home/sam/.config/workbench/apps.json")
OMASTART = Path("/home/sam/.local/state/omarchy/settings/omastart.json")
OMASTART_CONTENT = {"workspaces": [{"id": 2, "label": "Rider Main",
                                    "apps": [{"name": "Rider Main", "cmd": "rider ~/code/harbour", "window": None}]}]}
FROM_OMASTART = AppList((Workspace(2, "Rider Main", (App("Rider Main", "rider ~/code/harbour"),)),))
FROM_WORKBENCH = AppList((Workspace(1, "Browser", (App("Chat", "chat-app", "chrome-chat"),)),))


def app_list_file(files) -> AppListFile:
    return AppListFile(LIST, [(WORKBENCH, from_saved), (OMASTART, from_omastart)], files)


class KeepingTheAppList(unittest.TestCase):
    def test_nothing_saved_anywhere_is_an_empty_list_and_nothing_is_written(self):
        files = files_holding({})
        self.assertEqual(app_list_file(files).load(), AppList())
        files.write.assert_not_called()

    def test_the_omastart_list_is_imported_and_saved_once(self):
        files = files_holding({OMASTART: json.dumps(OMASTART_CONTENT)})
        self.assertEqual(app_list_file(files).load(), FROM_OMASTART)
        files.write.assert_called_once_with(LIST, json_text(to_saved(FROM_OMASTART)), read_before="")

    def test_the_list_kept_under_the_old_name_comes_before_omastart(self):
        files = files_holding({OMASTART: json.dumps(OMASTART_CONTENT), WORKBENCH: json.dumps(to_saved(FROM_WORKBENCH))})
        self.assertEqual(app_list_file(files).load(), FROM_WORKBENCH)

    def test_a_saved_list_wins_over_earlier_lists_and_is_not_written_again(self):
        saved = AppList((Workspace(4, "Comms", (App("Chat", "chat-app", "chat"),)),))
        files = files_holding({LIST: json.dumps(to_saved(saved)), OMASTART: json.dumps(OMASTART_CONTENT)})
        self.assertEqual(app_list_file(files).load(), saved)
        files.write.assert_not_called()

    def test_saving_a_list_never_read_writes_it_once_without_a_check(self):
        files = files_holding({})
        app_list_file(files).save(FROM_WORKBENCH)
        files.write.assert_called_once_with(LIST, json_text(to_saved(FROM_WORKBENCH)), read_before=None)

    def test_saving_after_reading_refuses_to_overwrite_a_list_changed_meanwhile(self):
        read = json.dumps(to_saved(FROM_WORKBENCH))
        files = files_holding({LIST: read})
        kept = app_list_file(files)
        kept.load()
        kept.save(FROM_OMASTART)
        files.write.assert_called_once_with(LIST, json_text(to_saved(FROM_OMASTART)), read_before=read)

    def test_a_second_save_checks_against_what_the_first_one_wrote(self):
        files = files_holding({})
        kept = app_list_file(files)
        kept.load()
        kept.save(FROM_WORKBENCH)
        kept.save(FROM_OMASTART)
        self.assertEqual(files.write.call_args.kwargs["read_before"], json_text(to_saved(FROM_WORKBENCH)))


class TheSavedFormat(unittest.TestCase):
    def test_an_app_and_its_learned_window_come_back_unchanged(self):
        saved = AppList((Workspace(4, "Comms", (App("Chat", "chat-app", "chrome-chat"),)),))
        self.assertEqual(from_saved(to_saved(saved)), saved)


class AListThatCannotBeRead(unittest.TestCase):
    def test_a_list_with_a_stray_comma_is_refused_and_nothing_is_written(self):
        files = files_holding({LIST: '{"workspaces": [],}'})
        with self.assertRaises(NotReadable):
            app_list_file(files).load()
        files.write.assert_not_called()

    def test_a_list_that_is_not_an_object_is_refused(self):
        with self.assertRaises(NotReadable):
            app_list_file(files_holding({LIST: "[]"})).load()

if __name__ == "__main__":
    unittest.main()
