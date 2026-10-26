import json
import unittest

from hiru_tsatsi.adapters.desktops.hyprland import Hyprland, lua_string
from hiru_tsatsi.adapters.tagged_launch import TaggedLaunch
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
        hyprland = Hyprland(hyprctl, lambda: TaggedLaunch(tag="t1"))
        hyprland.launch('omarchy-launch-webapp "https://x"', 1)
        hyprland.move(Window("0xa", "steam", "Steam", 4), 6)
        self.assertEqual(hyprctl.calls, [
            ["dispatch", 'hl.dsp.exec_cmd("export HIRU_TSATSI_LAUNCH=t1\\010omarchy-launch-webapp \\"https://x\\"", '
                         '{ workspace = "1 silent" })'],
            ["dispatch", 'hl.dsp.window.move({ workspace = "6", follow = false, window = "address:0xa" })'],
        ])

    def test_a_terminal_app_opens_in_a_terminal_window_with_its_own_name(self):
        hyprctl = FakeHyprctl()
        Hyprland(hyprctl).launch_in_terminal("cd code && helper", 2, "hiru-tsatsi.2-0-helper")
        self.assertEqual(len(hyprctl.calls), 1)
        self.assertIn('hl.dsp.exec_cmd("xdg-terminal-exec --app-id=hiru-tsatsi.2-0-helper -- sh -c ', hyprctl.calls[0][1])
        self.assertTrue(hyprctl.calls[0][1].endswith('{ workspace = "2 silent" })'))

    def test_each_window_says_what_runs_inside_it(self):
        hyprland = Hyprland(lambda arguments: json.dumps([{"address": "0xb", "class": "foot", "title": "t", "pid": 77,
                                                            "workspace": {"id": 2}}]),
                            front=lambda pid: ("helper", f"/home/sam/code-{pid}"))
        self.assertEqual(hyprland.windows(), [Window("0xb", "foot", "t", 2, "helper", "/home/sam/code-77")])

    def test_unreadable_output_means_no_windows(self):
        self.assertEqual(Hyprland(lambda arguments: "not json").windows(), [])


class QuotingForLua(unittest.TestCase):
    def test_every_character_that_could_end_or_break_the_string_is_escaped(self):
        cases = {
            'say "hi"': '"say \\"hi\\""',
            "ends with \\": '"ends with \\\\"',
            "line one\nline two": '"line one\\010line two"',
            "a\rb": '"a\\013b"',
            "a\x00b": '"a\\000b"',
            "a\n7": '"a\\0107"',
            "a\x7fb": '"a\\127b"',
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(lua_string(text), expected)


if __name__ == "__main__":
    unittest.main()
