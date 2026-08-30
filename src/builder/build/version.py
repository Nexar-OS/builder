from dataclasses import dataclass, asdict
import re

@dataclass
class Version:
    """
    Represents a software version using major, minor, and optional patch components.
    """

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
        match = re.search(r"(?<!\d)(\d+(?:\.\d+){1,2})(?!\d)", value)

        if not match:
            return None
        
        version = match.group(1)
        parts = [ int(part) for part in version.split(".") ]

        note = value[:match.start()] + value[match.end():]
        note.strip("-")
        
        return cls(
            *parts,
            note=note or None
        )

    def dict(self) -> dict[str, str]:
        """
        Returns a dictionary representation of this version.
        """
        return {
            f"version.{key}": f"{value}"
            for key, value in asdict(self).items()
        }