from dataclasses import dataclass, asdict
import re

_VERSION_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])"
    r"(?P<version>[vV]?\d+(?:\.\d+){0,2})"
    r"(?![A-Za-z0-9.]|\.\d)",
    re.IGNORECASE
)

@dataclass(frozen=True)
class Version:
    """
    Represents a software version using major, minor, and optional patch components.
    """

    raw: str
    major: int
    minor: int
    patch: int
    note: str | None = None

    @classmethod
    def parse(cls, value: str) -> "Version | None":
        """Extract a version from a string.

        Args:
            value (str): The string to use.

        Returns:
            Version | None: Returns None if no valid version was found.
                            Otherwise the parsed version will be returned.
        """
        if not isinstance(value, str) or not value.strip():
            return None
        
        value = value.strip().replace("_", ".")
        match = _VERSION_PATTERN.search(value)

        if not match:
            return None
        
        version = match.group("version").lstrip("vV")

        parts = [ int(part) for part in version.split(".") ]
        note = (
            value[:match.start()] + value[match.end():]
        ).strip(" -_.")

        return cls(
            raw=value,
            major=parts[0],
            minor=parts[1] if len(parts) > 1 else 0,
            patch=parts[2] if len(parts) > 2 else 0,
            note=note or None
        )
    

    @classmethod
    def from_version_string(cls, value: str) -> "Version | None":
        """
        Parse a version string such as '2.0.1'.

        Args:
            value (str): The string to parse.

        Returns:
            Version: The parsed version. None if invalid format.
        """
        return cls.parse(value)
    
    @property
    def components(self) -> tuple[int, int, int]:
        return self.major, self.minor, self.patch

    def __eq__(self, value: object) -> bool:
        """
        Compare two version instances.

        Args:
            value (Version): The other version to compare

        Returns:
            bool: True if ``self`` is equal to ``value``.
        """
        if not isinstance(value, Version):
            return NotImplemented
        
        return self.components == value.components

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
        
        return self.components < other.components

    def __str__(self) -> str:
        return ".".join(map(str, self.components))

    def dict(self) -> dict[str, str]:
        """
        Returns a dictionary representation of this version.
        """
        return {
            f"version.{key}": f"{value}"
            for key, value in asdict(self).items()
        }