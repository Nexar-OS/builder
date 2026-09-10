from dataclasses import dataclass, asdict
import re

@dataclass(frozen=True)
class Version:
    """
    Represents a software version using major, minor, and optional patch components.
    """

    raw: str
    major: int
    minor: int | None = None
    patch: int | None = None
    note: str | None = None

    @classmethod
    def from_version_string(cls, value: str) -> "Version | None":
        """
        Parse a version string such as '2.0.1'.

        Args:
            value (str): The string to parse.

        Returns:
            Version: The parsed version. None if invalid format.
        """
        match = re.search(r"(?<!\d)(\d+(?:\.\d+){0,2})(?!\d)", value)

        if not match:
            return None
        
        version = match.group(1)
        parts = [ int(part) for part in version.split(".") ]

        note = value[:match.start()] + value[match.end():]
        note = note.strip().strip("-")
        
        return cls(
            value,
            *parts,
            note=note or None
        )
    
    def _key(self):
        return (
            self.major,
            self.minor if self.minor is not None else -1,
            self.patch if self.patch is not None else -1,
        )

    def __lt__(self, other: "Version") -> bool:
        """
        Compare two version instances.

        Args:
            other (Version): The other version to compare

        Returns:
            bool: True if ``self`` is a newer version than ``other``.
        """
        if not isinstance(other, Version):
            return NotImplemented
        
        return self._key() < other._key()

    def dict(self) -> dict[str, str]:
        """
        Returns a dictionary representation of this version.
        """
        return {
            f"version.{key}": f"{value}"
            for key, value in asdict(self).items()
        }