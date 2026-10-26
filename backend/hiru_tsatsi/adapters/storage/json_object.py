import json
from pathlib import Path

from hiru_tsatsi.use_cases.failures import NotReadable


def json_object(text: str, path: Path) -> dict:
    if text.strip() == "":
        return {}
    try:
        content = json.loads(text)
    except json.JSONDecodeError as broken:
        raise NotReadable(f"{path} is not valid JSON ({broken})") from broken
    if not isinstance(content, dict):
        raise NotReadable(f"{path} does not hold a JSON object")
    return content


def json_text(content: dict) -> str:
    return json.dumps(content, indent=2) + "\n"
