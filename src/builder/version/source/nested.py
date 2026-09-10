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
    only_latest: bool = False
    
    @property
    def latest_version(self) -> Version:
        """
        Get the latest upstream version of this source.

        Returns:
            Version: The latest upstream version.
        """
        _only_latest = self.only_latest
        self.only_latest = True

        versions = list(self.versions)

        self.only_latest = _only_latest

        return max(versions)

    @property
    def versions(self) -> Iterable[Version]:
        """
        Discover verisons using the parent and child sources.

        Each version discovered by the parent source is passed as the
        ``version`` context to the child source.
        """
        versions = self.parent.versions

        if self.only_latest:
            versions = [ max(versions) ]

        for version in versions:
            yield from self.child.with_context(
                version=version.raw
            ).versions