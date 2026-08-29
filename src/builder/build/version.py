from dataclasses import dataclass, asdict

@dataclass
class Version:
    """
    Represents a software version using major, minor, and optional patch components.
    """

    major: int
    minor: int | None = None
    patch: int | None = None

    @classmethod
    def from_version_string(cls, value: str) -> "Version | None":
        """
        Parse a version string such as '2.0.1'.

        Args:
            value (str): The string to parse.

        Returns:
            Version: The parsed version. None if invalid format.
        """
        parts = value.split(".")
        
        try:
            nums = [ int(part) for part in parts ]
        except ValueError:
            return None
        
        if not nums:
            return None
        
        return cls(
            *nums
        )

    def dict(self) -> dict[str, str]:
        """
        Returns a dictionary representation of this version.
        """
        return {
            f"version.{key}": f"{value}"
            for key, value in asdict(self).items()
        }