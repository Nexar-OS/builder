from pathlib import Path
from abc import ABC, abstractmethod
from .package import Package

class PackageExporter(ABC):
    """
    Abstract base class for converting "Packages" into serialized artifacts.

    Exporters define the boundary between the builder's recipe model and a
    concrete package format.

    Implementations should not modify the Package itself.
    """

    @property
    @abstractmethod
    def format(self) -> str:
        """
        Return the unique identifier of this package format.
        """
        raise NotImplementedError
    
    @property
    @abstractmethod
    def extension(self) -> str:
        """
        Return the file extension used by this package format.
        """
        raise NotImplementedError
    
    @abstractmethod
    def export(self, package: Package, destination: Path) -> Path:
        """
        Serialize a Package into the target package format.

        Args:
            package (Package): The logical package to serialize.
            destination (Path): Directory in which the resulting
                                artifact should be written into.
        """
        raise NotImplementedError