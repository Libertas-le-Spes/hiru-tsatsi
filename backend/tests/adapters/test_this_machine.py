import unittest

from workbench.adapters import this_machine
from workbench.adapters.desktops.hyprland import Hyprland
from workbench.use_cases.ports import DesktopNotSupported


class PickingTheDesktop(unittest.TestCase):
    def test_hyprland_is_picked_inside_hyprland(self):
        self.assertIsInstance(this_machine.desktop({"HYPRLAND_INSTANCE_SIGNATURE": "x"}), Hyprland)

    def test_a_desktop_without_window_placing_is_refused_by_name(self):
        with self.assertRaises(DesktopNotSupported) as refused:
            this_machine.desktop({"XDG_CURRENT_DESKTOP": "GNOME"})
        self.assertEqual(refused.exception.desktop, "GNOME")


if __name__ == "__main__":
    unittest.main()
