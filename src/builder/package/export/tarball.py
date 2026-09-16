import tarfile
import json
import io
from dataclasses import asdict
from pathlib import Path
from builder.recipe import RecipeMetadata
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

    def _create_metadata(self, tarball: tarfile.TarFile, metadata: RecipeMetadata) -> tarfile.TarInfo:
        """
        Creates a metadata file for the final tarball.
        """

        data = json.dumps(
            asdict(metadata),
            indent=4
        ).encode("UTF-8")

        info = tarfile.TarInfo(name=".metadata")
        info.size = len(data)
        tarball.addfile(info, io.BytesIO(data))

        return info
    
    def _create_tarball(self, paths: list[Path], tarball: Path) -> tarfile.TarFile:
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

        tar = tarfile.open(tarball, mode="w")
        
        for path in paths:
            arcname = Path("rootfs" / path.relative_to(common_root))
            tar.add(path, arcname=arcname)

        return tar

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

        tarball = self._create_tarball(
            paths=[
                package.rootfs
            ],
            tarball=destination_file
        )
        self._create_metadata(tarball, package.metadata)
        tarball.close()

        return Artifact(
            path=destination_file,
            format=self.format,
            exporter=type(self),
            package=package
        )