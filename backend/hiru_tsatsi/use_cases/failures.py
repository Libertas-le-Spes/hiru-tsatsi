class DesktopNotSupported(Exception):
    def __init__(self, desktop: str):
        super().__init__(desktop)
        self.desktop = desktop


class SetUpFailed(Exception):
    pass


class NotSaved(Exception):
    pass


class NotReadable(Exception):
    pass


class NotOurs(Exception):
    def __init__(self, path: str):
        super().__init__(path)
        self.path = path
