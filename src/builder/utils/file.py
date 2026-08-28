from pathlib import Path
import shutil
from .logger import debug

def rmtree(path: Path):
    """
    Recursively deletes entire filesystem tree with all children.

    Args:
        path (Path): The root folder to delete.
    """
    shutil.rmtree(path, ignore_errors=True)

def merge_trees(source: Path, dest: Path, copy: bool = False, skip_extensions: list[str]|None = None, skip_names: list[str]|None = None):
    """
    Merge the contents of one directory tree into another.

    - Files and symlinks are moved.
    - Existing files/symlinks/directories in the destination are overwritten.
    - Existing destination directories are merged recursively.

    Args:
        source (Path): Source tree to merge into destination.
        dest (Path): Destination tree to merge the source into.
        copy (bool): If True, content will be copied instead of being moved.
        skip_extensions (list[str]|None): If passed, all files with an extension in the list will be skipped.
    """

    if not source.is_dir():
        return
    
    dest.mkdir(exist_ok=True, parents=True)

    for item in source.iterdir():
        dst = dest / item.name

        # Skip extensions
        ext = item.name.split(".")[-1]
        if skip_extensions and ext in skip_extensions:
            debug(f"Skipping file '{item.name}' due to extension.")
            continue
        
        # Skip names
        if skip_names and item.name in skip_names:
            debug(f"Skipping file '{item.name}' due to name.")
            continue

        # Merge real directories recursively
        if item.is_dir() and not item.is_symlink():
            merge_trees(item, dst, copy)
        
        else:
            # Remove whatever is currently at the destination
            if dst.exists() or dst.is_symlink():
                dst.unlink()
            
            # Move or copy file or symlinks without dereferencing it
            if copy:
                shutil.copy2(str(item), str(dst), follow_symlinks=False)
            else:
                shutil.move(str(item), str(dst))
    
    # Finally remove source node
    if not copy:
        try:
            source.rmdir()
        except OSError:
            pass