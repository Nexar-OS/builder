from pathlib import Path
from .buildsystem import BuildSystem
from build.context import BuildContext

class LinuxHeaders(BuildSystem):
    """
    Abstraction for building the linux headers.
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
        # Not needed
        pass

    def install(self, ctx: BuildContext, build_dir: Path, dest_dir: Path | None = None):
        """
        Install the linux headers using ``make headers_install``.

        Args:
            ctx (BuildContext): Build context.
            dest_dir (Path | None, optional): Destination override. Defaults to None.
        """
        
        assert dest_dir, "dest_dir argument is required for LinuxHeaders"

        ctx.run(
            [
                ctx.toolchain.make,
                f"ARCH={ctx.target_machine.kernel_arch}",
                "headers_install",
                f"INSTALL_HDR_PATH={dest_dir / 'usr'}"
            ],
            cwd=build_dir
        )