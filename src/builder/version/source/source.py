from typing import Iterable
from abc import ABC, abstractmethod
from ..version import Version

class VersionSource(ABC):
    """
    Abstract base class for discovering available upstream versions of software packets.

    A version source is responsible for retrieving and identifying available version
    candidates from an upstream source, such as a web page, git repo, etc.

    Actual implementation depends on sub-class.
    """

    @property
    @abstractmethod
    def versions(self) -> Iterable[Version]:
        """
        Discover available versions from the upstream source.

        Returns:
            Iterable[Version]: A stream yielding the versions discovered
                               from the upstream source.
        """
        raise NotImplementedError