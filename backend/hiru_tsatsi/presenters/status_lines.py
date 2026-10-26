from hiru_tsatsi.use_cases.overview import AppView


class OpenInPlace:
    @staticmethod
    def fits(view: AppView) -> bool:
        return view.window is not None and view.window.workspace == view.placement.workspace

    @staticmethod
    def text(view: AppView) -> str:
        return f"✓ {view.window.title}, open on workspace {view.window.workspace}"


class OpenElsewhere:
    @staticmethod
    def fits(view: AppView) -> bool:
        return view.window is not None

    @staticmethod
    def text(view: AppView) -> str:
        return (f"✓ {view.window.title}, open on workspace {view.window.workspace} "
                f"(moved to {view.placement.workspace} when you start)")


class KnownButClosed:
    @staticmethod
    def fits(view: AppView) -> bool:
        return view.placement.app.knows_window

    @staticmethod
    def text(view: AppView) -> str:
        return "Recognised when it opens"


class NotYetKnown:
    @staticmethod
    def fits(view: AppView) -> bool:
        return True

    @staticmethod
    def text(view: AppView) -> str:
        return "Will be recognised the first time Hiru Tsatsi starts it"


STATUS_LINES = [OpenInPlace, OpenElsewhere, KnownButClosed, NotYetKnown]


def status_line(view: AppView) -> str:
    for line in STATUS_LINES:
        if line.fits(view):
            return line.text(view)
    return NotYetKnown.text(view)
