from hiru_tsatsi.use_cases.setting_up import SetUp

ASKED_AT_LOGIN = "At login, a notification asks whether to start your work apps."


def _starts(kept: bool) -> str:
    if kept:
        return "still starts"
    return "now starts"


def set_up_text(set_up: SetUp) -> str:
    if set_up.keys is None:
        return ("Every shortcut Hiru Tsatsi would pick is taken, so none was added; "
                f"bind `hiru-tsatsi start` yourself. {ASKED_AT_LOGIN}")
    return f"{set_up.keys.text()} {_starts(set_up.kept)} your work apps. {ASKED_AT_LOGIN}"
