class Failure(Exception):
    exit_code = 1

    def explained(self) -> str:
        return str(self)


class DesktopNotSupported(Failure):
    exit_code = 2

    def __init__(self, desktop: str):
        super().__init__(desktop)
        self.desktop = desktop

    def explained(self) -> str:
        return (f"Hiru Tsatsi can't place windows on {self.desktop} yet, so it did nothing. "
                "Apps opened without being put on their workspaces would only need sorting by hand.")


class SetUpFailed(Failure):
    def explained(self) -> str:
        return f"The desktop reported a problem after setting up, so check its config:\n{self}"


class NotSaved(Failure):
    def explained(self) -> str:
        return f"Nothing was saved: {self}."


class ChangedMeanwhile(NotSaved):
    pass


class NotReadable(Failure):
    def explained(self) -> str:
        return f"Nothing was changed: {self}."


class NotOurs(Failure):
    def __init__(self, path: str):
        super().__init__(path)
        self.path = path

    def explained(self) -> str:
        return (f"hiru-tsatsi install: {self.path} is already there and is not Hiru Tsatsi; "
                "move it away and run install.sh again")
