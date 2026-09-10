from typing import Iterable
from builder.version.version import Version
from .source import VersionSource
from dataclasses import dataclass

@dataclass
class NestedVersionSource(VersionSource):
    """
    Discovers software versions by applying a child version source
    to each version discovered by a parent version source.

    This is useful for upstream sources where version discovery is a hierarchy.
    """
    parent: VersionSource
    child: VersionSource
    
    @property
    def versions(self) -> Iterable[Version]:
        """
        Discover verisons using the parent and child sources.

        Each version discovered by the parent source is passed as the
        ``version`` context to the child source.
        """
        for version in self.parent.versions:
            yield from self.child.with_context(
                version=version.raw
            ).versions