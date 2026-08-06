from pathlib import Path
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class Source(ABC):
    """Abstract base class for build sources.

    A ``Source`` represents an installable upstream source such as a git
    repository, a tarball, or another downloadable source artifact.

    Subclasses implement the source-specific logic for downloading and installing
    their type of source into their final destinations.
    """

    name: str
    url: str

    def install(self, download_dir: Path, dest_dir: Path|None = None) -> None:
        """Download the source and install it into an optionally differing destination directory.

        Args:
            download_dir (Path): The directory to download the source into.
            dest_dir (Path): The final destination directory for the source to be installed into.
        """

        # Fallback to download directory
        dest_dir = dest_dir or download_dir

        download_dir.mkdir(exist_ok=True, parents=True)
        dest_dir.mkdir(exist_ok=True, parents=True)

        self.download(download_dir)
        self.prepare(download_dir, dest_dir)

    @abstractmethod
    def download(self, download_dir: Path):
        """Download the source into the download directory.

        Args:
            download_dir (Path): The download directory
        """
        raise NotImplementedError()
    
    @abstractmethod
    def prepare(self, download_dir: Path, dest_dir: Path):
        """Install the source into the final directory

        Args:
            download_dir (Path): The download directory
            dest_dir (Path): The final destination for the source
        """
        raise NotImplementedError()