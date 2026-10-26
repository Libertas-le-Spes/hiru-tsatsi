class FakeSettings:
    def __init__(self, window_titles: bool | None = None):
        self.titles = window_titles

    def window_titles(self) -> bool | None:
        return self.titles

    def set_window_titles(self, on: bool) -> None:
        self.titles = on
