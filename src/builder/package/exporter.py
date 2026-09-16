from pathlib import Path
from abc import ABC, abstractmethod
from .package import Package

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .artifact import Artifact

class PackageExporter(ABC):
    """
    Abstract base class for converting "Packages" into serialized artifacts.

    Exporters define the boundary between the builder's recipe model and a
    concrete package format.

    Implementations should not modify the Package itself.
    """

    format: str
    extension: str
    
    @abstractmethod
    def export(self, package: Package, destination: Path) -> "Artifact":
        """
        Serialize a Package into the target package format.

        Args:
            package (Package): The logical package to serialize.
            destination (Path): Directory in which the resulting
                                artifact should be written into.
        """
        raise NotImplementedError