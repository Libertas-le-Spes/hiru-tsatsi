import json


def json_object(text: str) -> dict:
    try:
        content = json.loads(text)
    except json.JSONDecodeError:
        return {}
    if not isinstance(content, dict):
        return {}
    return content


def json_text(content: dict) -> str:
    return json.dumps(content, indent=2) + "\n"
