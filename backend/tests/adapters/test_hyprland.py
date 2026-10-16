import json
import unittest

from hiru_tsatsi.adapters.desktops.hyprland import Hyprland
from hiru_tsatsi.work_apps.windows import Window

CLIENTS = [{"address": "0xa", "class": "steam", "title": "Steam", "workspace": {"id": 4}}]


class FakeHyprctl:
    def __init__(self):
        self.calls: list[list[str]] = []

    def __call__(self, arguments: list[str]) -> str:
        self.calls.append(arguments)
        return json.dumps(CLIENTS) if arguments[:2] == ["clients", "-j"] else "ok"


class TalkingToHyprland(unittest.TestCase):
    def test_found_only_inside_hyprland(self):
        self.assertIsNone(Hyprland.found({}))
        self.assertIsInstance(Hyprland.found({"HYPRLAND_INSTANCE_SIGNATURE": "x"}), Hyprland)

    def test_lists_windows(self):
        self.assertEqual(Hyprland(FakeHyprctl()).windows(), [Window("0xa", "steam", "Steam", 4)])

    def test_launches_and_moves_without_following_the_window(self):
        hyprctl = FakeHyprctl()
        hyprland = Hyprland(hyprctl)
        hyprland.launch('omarchy-launch-webapp "https://x"', 1)
        hyprland.move(Window("0xa", "steam", "Steam", 4), 6)
        self.assertEqual(hyprctl.calls, [
            ["dispatch", 'hl.dsp.exec_cmd("omarchy-launch-webapp \\"https://x\\"", { workspace = "1 silent" })'],
            ["dispatch", 'hl.dsp.window.move({ workspace = "6", follow = false, window = "address:0xa" })'],
        ])

    def test_unreadable_output_means_no_windows(self):
        self.assertEqual(Hyprland(lambda arguments: "not json").windows(), [])


if __name__ == "__main__":
    unittest.main()
