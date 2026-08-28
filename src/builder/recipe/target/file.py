from pathlib import Path
from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe
from builder.source import TarballSource
from builder.toolchain import NativeToolchain

class FileRecipe(TargetRecipe):
    name = "file"
    version = "5.48"

    sources = [
        TarballSource(
            name="file",
            url=f"https://astron.com/pub/file/file-{version}.tar.gz",
            md5hash="423686e97f731d8c24e9cd1a22b03dec"
        )
    ]

    build_system = Autotools(
        config_args=[
            "--prefix=/usr"
        ],
        disable_fakeroot=True # ``file -C -m magic`` core dumps when using fakeroot
    )

    def _config_args(self, ctx: BuildContext) -> list[str]:
        return [
            f"--build={ctx.build_machine.triple}",
            f"--host={ctx.target_machine.triple}"
        ]
    
    def prepare(self, ctx: BuildContext, source_dir: Path, build_dir: Path) -> None:
        """
        When compiling file tries to use itself in order to generate the
        magic database file. This can cause crashes when the version of
        file installed on the build system doesn't match the one we are
        trying to build.

        This method compiles a separate (host) version of file that the
        target file can later use to generate said database.
        """

        host_build_dir = build_dir / "host-tools"
        host_build_dir.mkdir(exist_ok=True, parents=True)

        old_toolchain = ctx.toolchain

        # Switch to native toolchain since file will be compiled for the host
        ctx.toolchain = NativeToolchain()

        # Build file
        host_build_system = Autotools([ f"--prefix={host_build_dir}/install" ], disable_fakeroot=True)
        host_build_system.configure(ctx, source_dir, build_dir)
        host_build_system.build(ctx, build_dir)

        # Switch back to cross compiler
        ctx.toolchain = old_toolchain