import re

CONTROL_CHARACTER = re.compile(r"[\x00-\x1f\x7f]")


def _as_lua_number_escape(found: re.Match) -> str:
    code = ord(found.group())
    return f"\\{code:03d}"


def lua_string(text: str) -> str:
    quoted = text.replace("\\", "\\\\").replace('"', '\\"')
    escaped = CONTROL_CHARACTER.sub(_as_lua_number_escape, quoted)
    return f'"{escaped}"'
