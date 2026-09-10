from typing import Iterable, Any
from abc import ABC, abstractmethod
from ..version import Version
from dataclasses import dataclass, fields

@dataclass
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

    def with_context(self, **context: Any) -> "VersionSource":
        """
        Return a copy of this source with template values substituted.
        """
        values = {}

        for field in fields(self):
            value = getattr(self, field.name)

            if isinstance(value, str):
                value = value.format(**context)
            
            values[field.name] = value
        
        return type(self)(**values)