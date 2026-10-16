import unittest

from hiru_tsatsi.work_apps.shortcut import PREFERRED, Keys, first_free


class ChoosingAShortcut(unittest.TestCase):
    def test_keys_read_the_same_whatever_the_order_or_case(self):
        self.assertEqual(Keys.parse("ctrl + SUPER + u"), Keys.parse("SUPER + CTRL + U"))
        self.assertEqual(Keys.parse("ctrl+super+u").text(), "SUPER + CTRL + U")

    def test_the_first_preference_nobody_uses_is_chosen(self):
        self.assertEqual(first_free(PREFERRED, {Keys.parse("SUPER + CTRL + U")}), Keys.parse("SUPER + ALT + U"))

    def test_nothing_when_every_preference_is_taken(self):
        self.assertIsNone(first_free(PREFERRED, set(PREFERRED)))


if __name__ == "__main__":
    unittest.main()
