from pathlib import Path

def rmtree(path: Path):
    """
    Recursively deletes entire filesystem tree with all children.

    Args:
        path (Path): The root folder to delete.
    """
    if path.is_file() or path.is_symlink():
        path.unlink(missing_ok=True)
    else:
        for child in path.iterdir():
            rmtree(child)
        path.rmdir()