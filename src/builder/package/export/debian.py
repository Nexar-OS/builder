import tempfile
import subprocess
from pathlib import Path
from builder.recipe import RecipeMetadata
from builder.package import PackageExporter, Package, Artifact
from builder.utils.file import rmtree, merge_trees

class DebianExporter(PackageExporter):
    """
    Exports Packages into the debian package format (.deb).

    This exporter produces .deb-packages that can later be installed
    by using the dpkg-commandline-utility.
    """
    format = "debian"
    extension = "deb"

    ARCH_MAP = {
        "x86": "amd64"
    }

    def _create_metadata(self, metadata: RecipeMetadata) -> dict[str, str]:
        """
        Create the debian metadata for ``DEBIAN/control``.

        Returns:
            dict[str, str]: The metadata key-value mapping.
        """

        result: dict[str, str] = dict()

        def _add(field: str, content: str | None):
            if not content:
                return

            result[field] = content

        _add("Package", metadata.name)
        _add("Description", metadata.description)
        _add("Version", metadata.version)
        _add("Maintainer", ", ".join(metadata.maintainers or []))

        if metadata.dependencies:
            required = metadata.dependencies.required or []
            _add("Depends", ", ".join(required))
        
        arch = metadata.architecture.kernel_arch
        _add("Architecture", DebianExporter.ARCH_MAP.get(
            arch, arch
        ))

        return result

    def _prepare_package(self, prepdir: Path, metadata: RecipeMetadata):
        """
        Prepares the packages layout in a real directory.

        Args:
            prepdir (Path): The directory to prepare in.
            metadata (RecipeMetadata): The packages metadata to write
        """

        debian = prepdir / "DEBIAN"
        debian.mkdir(exist_ok=True, parents=True)

        # Write metadata
        debian_metadata: dict[str, str] = self._create_metadata(metadata)
        (debian / "control").write_text(
            "\n".join(
                f"{key}: {val}"
                for key, val in debian_metadata.items()
            )
            + "\n"
        )

    def export(self, package: Package, destination: Path) -> Artifact:
        """
        Serialize a Package into the .deb package.

        Args:
            package (Package): The logical package to serialize.
            destination (Path): Directory in which the resulting
                                artifact should be written into.
        """
        destination.mkdir(exist_ok=True, parents=True)
        destination_file = destination / f"{package.metadata.name}-{package.metadata.version}.{self.extension}"
        
        if destination_file.exists():
            rmtree(destination_file)

        with tempfile.TemporaryDirectory("builder", package.metadata.name) as tmp_dir:
            tmp_dir = Path(tmp_dir)
            
            # Prepare tmpdir
            self._prepare_package(tmp_dir, package.metadata)
        
            # Copy package files
            merge_trees(
                source=package.rootfs,
                dest=tmp_dir,
                copy=True
            )

            # Build .deb file
            subprocess.call([
                "dpkg-deb", "--build", tmp_dir, str(destination_file)
            ], cwd=destination)

        return Artifact(
            path=destination_file,
            format=self.format,
            exporter=type(self),
            package=package
        )