import tarfile
from pathlib import Path
from builder.package import PackageExporter, Package, Artifact
from builder.utils.file import rmtree

class TarballExporter(PackageExporter):
    """
    Exports Packages into tarball-artifacts.

    The produced tarballs contain the complete root filesystem of the
    package.
    """
    format = "tarball"
    extension = "tar"
    
    def _create_tarball(self, paths: list[Path], tarball: Path) -> None:
        """
        Create a tarball containing the given filesystem paths.

        Args:
            paths (list[Path]): List of paths.
            tarball (Path): Output tarball archive.
        """

        paths = [ path.resolve() for path in paths ]

        common_root = Path(
            __import__("os").path.commonpath(str(path) for path in paths)
        )

        with tarfile.open(tarball, mode="w") as tar:
            for path in paths:
                arcname = path.relative_to(common_root)
                tar.add(path, arcname=arcname)

    def export(self, package: Package, destination: Path) -> Artifact:
        """
        Serialize a Package into the tarball.

        Args:
            package (Package): The logical package to serialize.
            destination (Path): Directory in which the resulting
                                artifact should be written into.
        """
        destination.mkdir(exist_ok=True, parents=True)
        destination_file = destination / f"{package.metadata.name}-{package.metadata.version}.{self.extension}"
        
        if destination_file.exists():
            rmtree(destination_file)

        self._create_tarball(
            paths=[
                package.rootfs
            ],
            tarball=destination_file
        )

        return Artifact(
            path=destination_file,
            format=self.format,
            exporter=type(self),
            package=package
        )