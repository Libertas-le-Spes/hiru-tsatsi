import json
import subprocess
from typing import Callable, Mapping

Run = Callable[[list[str]], str]


def run_hyprctl(arguments: list[str]) -> str:
    done = subprocess.run(["hyprctl", *arguments], capture_output=True, text=True, check=False)
    return done.stdout


def inside_hyprland(env: Mapping[str, str]) -> bool:
    return bool(env.get("HYPRLAND_INSTANCE_SIGNATURE"))


def listed(run: Run, arguments: list[str]) -> list[dict]:
    reply = run(arguments)
    if not reply:
        return []
    try:
        content = json.loads(reply)
    except json.JSONDecodeError:
        return []
    if not isinstance(content, list):
        return []
    entries = []
    for entry in content:
        if isinstance(entry, dict):
            entries.append(entry)
    return entries
