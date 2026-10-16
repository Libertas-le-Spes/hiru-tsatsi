from dataclasses import dataclass

MODIFIER_ORDER = ("SUPER", "CTRL", "ALT", "SHIFT")


@dataclass(frozen=True)
class Keys:
    modifiers: frozenset[str]
    key: str

    @classmethod
    def parse(cls, text: str) -> "Keys":
        parts = [part.strip().upper() for part in text.split("+") if part.strip()]
        return cls(frozenset(parts[:-1]), parts[-1])

    def text(self) -> str:
        return " + ".join([m for m in MODIFIER_ORDER if m in self.modifiers] + [self.key])


PREFERRED = [Keys.parse("SUPER + CTRL + U"), Keys.parse("SUPER + ALT + U"), Keys.parse("SUPER + SHIFT + U")]


def first_free(preferred: list[Keys], taken: set[Keys]) -> Keys | None:
    return next((keys for keys in preferred if keys not in taken), None)
