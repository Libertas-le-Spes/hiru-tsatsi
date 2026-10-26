class Refused(Exception):
    exit_code = 1

    def explained(self) -> str:
        return str(self)


class NumberTaken(Refused):
    def __init__(self, number: int):
        super().__init__(self._reason(number))
        self.number = number

    @staticmethod
    def _reason(number: int) -> str:
        if number < 1:
            return "Workspace numbers start at 1"
        return f"Workspace {number} is already in use"


class NothingThere(Refused):
    def __init__(self):
        super().__init__("That is no longer there; the list has changed since it was last shown")


class Blank(Refused):
    def __init__(self, field: str):
        super().__init__(f"The {field} can't be empty")
        self.field = field


def required(field: str, value: str) -> str:
    if not value.strip():
        raise Blank(field)
    return value.strip()
