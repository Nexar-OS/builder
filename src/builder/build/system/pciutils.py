import shutil
from pathlib import Path
from .buildsystem import BuildSystem
from builder.build.context import BuildContext

class Pciutils(BuildSystem):
    """
    Abstraction for building pciutils.
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
        Builds pciutils using ``make``.

        The following command will be executed:
        ``make PREFIX=/usr HOST=$target CROSS_COMPILE=$target all``
        """

        ctx.run(
            [ ctx.toolchain.make, "PREFIX=/usr", f"HOST={ctx.target_machine.triple}", f"CROSS_COMPILE={ctx.target_machine.triple}-", "all" ],
            cwd=build_dir # build dir is source dir
        )

    def install(self, ctx: BuildContext, build_dir: Path, dest_dir: Path | None = None):
        """
        Install pciutils into the target destination.

        Args:
            dest_dir (Path | None, optional): Must be passed.
        """
        
        assert dest_dir, "dest_dir argument is required for pciutils"

        ctx.run(
            [ ctx.toolchain.make, "PREFIX=/usr", f"DESTDIR={str(dest_dir)}", "install" ],
            cwd=build_dir # build dir is source dir
        )