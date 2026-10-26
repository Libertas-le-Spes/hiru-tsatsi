from pathlib import Path


class SymbolicLinks:
    def present(self, path: str) -> bool:
        place = Path(path)
        return place.is_symlink() or place.exists()

    def points_at(self, path: str) -> str:
        place = Path(path)
        if not place.is_symlink():
            return ""
        return str(place.readlink())

    def link(self, path: str, target: str) -> None:
        place = Path(path)
        place.parent.mkdir(parents=True, exist_ok=True)
        if place.is_symlink():
            place.unlink()
        place.symlink_to(target)

    def remove(self, path: str) -> None:
        Path(path).unlink()
