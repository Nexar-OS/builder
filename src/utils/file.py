from pathlib import Path
import shutil

def rmtree(path: Path):
    """
    Recursively deletes entire filesystem tree with all children.

    Args:
        path (Path): The root folder to delete.
    """
    shutil.rmtree(path, ignore_errors=True)