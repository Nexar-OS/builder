from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe
from builder.source import TarballSource
from .libpipeline import LibpipelineRecipe

class GdbmRecipe(TargetRecipe):
    name = "gdbm"
    version = "1.26"

    copy_to_toolchain = True

    depends_on = [
        LibpipelineRecipe
    ]

    sources = [
        TarballSource(
            name="gdbm",
            url=f"https://ftp.gnu.org/gnu/gdbm/gdbm-{version}.tar.gz",
            md5hash="aaa600665bc89e2febb3c7bd90679115"
        )
    ]

    build_system = Autotools(
        config_args=[
            "--prefix=/usr"
        ]
    )

    def _config_args(self, ctx: BuildContext) -> list[str]:
        return [
            f"--build={ctx.build_machine.triple}",
            f"--host={ctx.target_machine.triple}"
        ]