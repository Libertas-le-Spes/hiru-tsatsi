from pathlib import Path

from hiru_tsatsi.use_cases.failures import NotReadable


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""
    except (OSError, UnicodeDecodeError) as unreadable:
        raise NotReadable(f"{path} could not be read ({unreadable})") from unreadable
