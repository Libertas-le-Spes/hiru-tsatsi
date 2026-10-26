from pathlib import Path
from unittest.mock import Mock, create_autospec

from hiru_tsatsi.adapters.storage.files import Files


class Contents:
    def __init__(self, held: dict[Path, str]):
        self.held = held

    def read(self, path: Path) -> str:
        return self.held.get(path, "")

    def exists(self, path: Path) -> bool:
        return path in self.held


def files_holding(held: dict[Path, str]) -> Mock:
    contents = Contents(held)
    files = create_autospec(Files, instance=True)
    files.read.side_effect = contents.read
    files.exists.side_effect = contents.exists
    return files


def written(files: Mock, path: Path) -> list[str]:
    texts = []
    for write in files.write.call_args_list:
        if write.args[0] == path:
            texts.append(write.args[1])
    return texts
