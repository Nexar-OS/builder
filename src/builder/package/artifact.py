from pathlib import Path
from dataclasses import dataclass
from typing import Type
from .package import Package
from .exporter import PackageExporter

@dataclass
class Artifact:
    """
    Represents a serialized output produced by the build system.

    An ``Artifact`` is the result of exporting a Package into a final
    package representation.

    Attributes:
        path (Path): Path to the generated artifact.
        format (str): Identifier of the format used to produce the artifact.
        exporter (Type[PackageExporter]): The class of the exporter used to produce this artifact.
        package (Package): The logical package from which the artifact was produced.
    """

    path: Path
    format: str
    exporter: Type[PackageExporter]
    package: Package