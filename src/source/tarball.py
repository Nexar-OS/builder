from pathlib import Path
from .source import Source
from dataclasses import dataclass

import tarfile
import hashlib

from utils.download import download_url

def _extract_flat_tar(tarball: Path, dest: Path):
    """
    Extracts a tar archive into a destination directory, flattening
    the archive if it contains a single top-level directory.

    Args:
        tarball (Path): The path to the tarfile.
        dest (Path): The destination path to extract the tarfile into.
    """
    with tarfile.open(tarball, "r:*") as tar:
        members = tar.getmembers()

        # Get a list of the top-level directory names
        top_levels = set( m.name.split("/", 1)[0] for m in members if m.name )

        # If there is only one top-level component, strip it in extraction
        strip_prefix = None
        if len(top_levels) == 1:
            strip_prefix = next(iter(top_levels)) + "/"
        
        for member in members:
            if strip_prefix and member.name.startswith(strip_prefix):
                member.name = member.name.removeprefix(strip_prefix)
            
            tar.extract(member, dest)


@dataclass
class TarballSource(Source):
    filename: str|None = None
    md5hash: str|None = None

    def local_file(self, download_dir: Path) -> Path:
        filename = self.filename

        # Default to url filename
        if not filename:
            filename = self.url.split("/")[-1]
        
        return download_dir / filename

    def validate(self, download_dir: Path) -> bool | None:
        """Validate the tarball with its md5 checksum.

        Args:
            download_dir (Path): The directory the tarball was downloaded into

        Returns:
            bool | None: True if check was successful, None if no md5hash was given
        """
        file = self.local_file(download_dir)

        if not self.md5hash:
            return None
        
        # Can fail early if file doesn't even exist
        if not file.exists() or not file.is_file():
            return False
        
        # Compute hash
        md5 = hashlib.md5()
        with file.open("rb") as file:
            for chunk in iter(lambda: file.read(8912), b""):
                md5.update(chunk)
        
        computed = md5.hexdigest().lower()

        print(computed)

        return computed == self.md5hash.lower()

    def download(self, download_dir: Path):
        """Download the tarball into the download directory.

        Args:
            download_dir (Path): The directory for the tarball to be downloaded into.
        """
        file = self.local_file(download_dir)
        download_url(self.url, file)

    def prepare(self, download_dir: Path, dest_dir: Path):
        """Extract the tarball into an optionally differing destination directory.

        Args:
            download_dir (Path): The directory the tarball was downloaded into.
            dest_dir (Path): The destination for the contents of the tarball.
        """
        file = self.local_file(download_dir)
        _extract_flat_tar(file, dest_dir)