from hiru_tsatsi.adapters.desktops.hyprctl import Run, listed
from hiru_tsatsi.work_apps.shortcut import Keys

MODIFIER_BITS = {"SHIFT": 1, "CTRL": 4, "ALT": 8, "SUPER": 64}


def keys_from_bind(bind: dict) -> Keys:
    mask = int(bind.get("modmask", 0))
    modifiers = set()
    for name, bit in MODIFIER_BITS.items():
        if mask & bit:
            modifiers.add(name)
    return Keys(frozenset(modifiers), str(bind.get("key", "")).upper())


def taken_keys(run: Run) -> set[Keys]:
    taken = set()
    for bind in listed(run, ["binds", "-j"]):
        if not bind.get("submap"):
            taken.add(keys_from_bind(bind))
    return taken
