from dataclasses import dataclass

MODIFIER_ORDER = ("SUPER", "CTRL", "ALT", "SHIFT")


@dataclass(frozen=True)
class Keys:
    modifiers: frozenset[str]
    key: str

    @classmethod
    def parse(cls, text: str) -> "Keys":
        parts = []
        for part in text.split("+"):
            if part.strip():
                parts.append(part.strip().upper())
        key = parts[-1]
        modifiers = parts[:-1]
        return cls(frozenset(modifiers), key)

    def text(self) -> str:
        ordered = []
        for modifier in MODIFIER_ORDER:
            if modifier in self.modifiers:
                ordered.append(modifier)
        ordered.append(self.key)
        return " + ".join(ordered)


PREFERRED = [Keys.parse("SUPER + CTRL + U"), Keys.parse("SUPER + ALT + U"), Keys.parse("SUPER + SHIFT + U")]


def first_free(preferred: list[Keys], taken: set[Keys]) -> Keys | None:
    for keys in preferred:
        if keys not in taken:
            return keys
    return None
