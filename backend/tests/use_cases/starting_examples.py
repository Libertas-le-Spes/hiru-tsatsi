from tests.fakes.app_lists import FakeStore
from tests.fakes.clock import FakeClock
from tests.fakes.notifying import FakeAnnouncer
from tests.fakes.recognising import RECOGNISING
from tests.fakes.window_names import FakeNames
from hiru_tsatsi.use_cases.starting import StartApps
from hiru_tsatsi.work_apps.app import App


CHAT = App("Chat", "omarchy-launch-webapp https://chat.google.com/", "chrome-chat.google.com")
MAIN = App("Rider Main", "rider ~/RiderProjects/harbour", "harbour")
STEAM = App("Steam", "steam")
HELPER = App("Helper", "cd code && helper")


def start(desktop, apps, announcer=None, names=None):
    store = FakeStore(apps)
    clock = FakeClock()
    if announcer is None:
        announcer = FakeAnnouncer()
    if names is None:
        names = FakeNames()
    outcome = StartApps(desktop, store, names, clock, clock.wait, announcer, RECOGNISING).run()
    return outcome, store, clock
