def line(label: str, names: list[str]) -> list[str]:
    if not names:
        return []
    return [f"{label}: {', '.join(names)}"]
