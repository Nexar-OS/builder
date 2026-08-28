from pathlib import Path
import shutil
from .source import Source
from dataclasses import dataclass

import hashlib

from builder.utils.download import download_url
from builder.utils.logger import debug, warn
from builder.utils.file import merge_trees

@dataclass
class FileSource(Source):
    filename: str|None = None
    md5hash: str|None = None

    def local_file(self, download_dir: Path) -> Path:
        filename = self.filename

        # Default to url filename
        if not filename:
            filename = self.url.split("/")[-1]
        
        return download_dir / filename

    def validate(self, download_dir: Path) -> bool | None:
        """Validate the file with its md5 checksum.

        Args:
            download_dir (Path): The directory the file was downloaded into

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

        passed = computed == self.md5hash.lower()

        if not passed:
            debug(f"Computed md5hash for '{self.name}': {computed}")

        return passed

    def download(self, download_dir: Path):
        """Download the file into the download directory.

        Args:
            download_dir (Path): The directory for the file to be downloaded into.
        """
        file = self.local_file(download_dir)

        # Local file
        if self.url.startswith("file://"):
            path = Path(self.url.removeprefix("file://")).resolve()

            if path.is_file():
                shutil.copy2(path, download_dir)
            
            elif path.is_dir():
                merge_trees(
                    path,
                    download_dir,
                    copy=True
                )
            
            else:
                warn(f"Failed to find local file: '{path}'")

        # File from web
        else:
            download_url(self.url, file)