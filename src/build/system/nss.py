from utils.file import merge_trees
from pathlib import Path
from .buildsystem import BuildSystem
from build.context import BuildContext

class NSS(BuildSystem):
    """
    Abstraction for building nss.
    """

    def prepare(self, ctx: BuildContext, source_dir: Path, build_dir: Path) -> None:
        # Not needed
        pass

    def configure(self,
                  ctx: BuildContext,
                  source_dir: Path,
                  build_dir: Path,
                  config_args: list[str] | None = None):
        # Not needed
        pass

    def build(self, ctx: BuildContext, build_dir: Path):
        """
        Builds nss using ``./build``.
        """

        nss_arch = {
            "x86_64": "x64",
            "amd64": "x64"
        }.get(ctx.target_machine.arch, ctx.target_machine.arch)

        ctx.run(
            [
               "./build.sh", 
                "--disable-tests",
                "--opt",
                "--target",
                nss_arch,
                "--gcc"
            ],
            cwd=build_dir / "nss"
        )

    def install(self, ctx: BuildContext, build_dir: Path, dest_dir: Path | None = None):
        """
        Install nss into the target destination.

        Args:
            dest_dir (Path | None, optional): Must be passed.
        """
        
        assert dest_dir, "dest_dir argument is required for nss"

        (dest_dir / "usr").mkdir(exist_ok=True, parents=True)

        merge_trees(
            build_dir / "dist" / "Release",
            dest_dir / "usr"
        )