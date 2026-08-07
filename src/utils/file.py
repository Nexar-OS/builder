from pathlib import Path
import shutil

def rmtree(path: Path):
    """
    Recursively deletes entire filesystem tree with all children.

    Args:
        path (Path): The root folder to delete.
    """
    shutil.rmtree(path, ignore_errors=True)

def merge_trees(source: Path, dest: Path, copy: bool = False):
    """
    Merge the contents of one directory tree into another.

    - Files and symlinks are moved.
    - Existing files/symlinks/directories in the destination are overwritten.
    - Existing destination directories are merged recursively.

    Args:
        source (Path): Source tree to merge into destination.
        dest (Path): Destination tree to merge the source into.
        copy (bool): If True, content will be copied instead of being moved.
    """

    if not source.is_dir():
        return
    
    dest.mkdir(exist_ok=True, parents=True)

    for item in source.iterdir():
        dst = dest / item.name

        # Merge real directories recursively
        if dest.is_dir() and not item.is_symlink():
            merge_trees(item, dst, copy)
        
        else:
            # Remove whatever is currently at the destination
            if dst.exists():
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