from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe
from builder.source import TarballSource

class ElfutilsRecipe(TargetRecipe):
    name = "elfutils"
    version = "latest"

    sources = [
        TarballSource(
            name="elfutils",
            url=f"https://sourceware.org/elfutils/ftp/elfutils-{version}.tar.bz2",
            md5hash="8d3f6cf81a8d27d6fa917ac1b566d8ff"
        )
    ]

    build_system = Autotools(
        config_args=[
            "--prefix=/usr",
            "--without-libbsd"
        ]
    )

    def _config_args(self, ctx: BuildContext) -> list[str]:
        return [
            f"--build={ctx.build_machine.triple}",
            f"--host={ctx.target_machine.triple}"
        ]