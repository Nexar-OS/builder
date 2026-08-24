from pathlib import Path
from .file import FileSource
from dataclasses import dataclass

import tarfile
from utils.file import rmtree

def _extract_flat_tar(tarball: Path, dest: Path, strip_top_level_dir: bool = True):
    """
    Extracts a tar archive into a destination directory, flattening
    the archive if it contains a single top-level directory.

    Args:
        tarball (Path): The path to the tarfile.
        dest (Path): The destination path to extract the tarfile into.
        strip_top_level_dir (bool): If set to true, a single top-level-directory will be stripped when extracting.
    """
    with tarfile.open(tarball, "r:*") as tar:
        members = tar.getmembers()

        if not strip_top_level_dir:
            strip_prefix = None
        else:
            # Get a list of the top-level directory names
            top_levels = set( m.name.split("/", 1)[0] for m in members if m.name )

            # If there is only one top-level component, strip it in extraction
            strip_prefix = None
            if len(top_levels) == 1:
                strip_prefix = next(iter(top_levels)) + "/"
        
        # Extract tarball
        for member in members:
            # Flatten member names
            if strip_prefix and member.name.startswith(strip_prefix):
                member.name = member.name.removeprefix(strip_prefix)
            
            # Flatten symlink / hardlink targets
            if strip_prefix and member.linkname.startswith(strip_prefix):
                member.linkname = member.linkname.removeprefix(strip_prefix)
            
            # Handle already extracted files (e.g. from another run)
            file = dest / member.name
            if file.exists():
                # Assume same file size == same file
                if file.stat().st_size == member.size:
                    continue

                # Only extract if real file differs from the compressed
                rmtree(file)
            
            tar.extract(member, dest)

@dataclass
class TarballSource(FileSource):
    
    """
    If set to True, a top-level directory will be stripped when
    extracting the tarball.
    """
    strip_top_level: bool = True

    def prepare(self, download_dir: Path, dest_dir: Path):
        """Extract the tarball into an optionally differing destination directory.

        Args:
            download_dir (Path): The directory the tarball was downloaded into.
            dest_dir (Path): The destination for the contents of the tarball.
        """
        file = self.local_file(download_dir)

        _extract_flat_tar(file, dest_dir, self.strip_top_level)