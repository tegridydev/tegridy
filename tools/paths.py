"""Filesystem layout shared by the local tools and exported build."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def infrastructure(root: Path) -> Path:
    return root / 'tools'
def releases(root: Path) -> Path:
    path = root.parent / 'releases'
    if path.is_symlink():
        raise ValueError('Release directory must not be a symlink')
    path.mkdir(parents=True, exist_ok=True)
    return path
