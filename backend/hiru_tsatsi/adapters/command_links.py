from pathlib import Path

OUR_LAUNCHER = "/backend/bin/hiru-tsatsi"


class SymbolicLinks:
    def present(self, path: str) -> bool:
        place = Path(path)
        return place.is_symlink() or place.exists()

    def is_ours(self, path: str) -> bool:
        place = Path(path)
        if not place.is_symlink():
            return False
        return str(place.readlink()).endswith(OUR_LAUNCHER)

    def link(self, path: str, target: str) -> None:
        place = Path(path)
        place.parent.mkdir(parents=True, exist_ok=True)
        if place.is_symlink():
            place.unlink()
        place.symlink_to(target)

    def remove(self, path: str) -> None:
        Path(path).unlink()
