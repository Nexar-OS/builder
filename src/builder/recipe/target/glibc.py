from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe
from builder.source import TarballSource

class GlibCRuntimeRecipe(TargetRecipe):
    name = "glibc-runtime"
    version = "2.44"

    sources = [
        TarballSource(
            name="glibc",
            url=f"https://ftp.gnu.org/gnu/glibc/glibc-{version}.tar.xz",
            md5hash="7677da43ef759c68e005f5d4c37986a6"
        )
    ]

    build_system = Autotools(
        config_args=[
            "--prefix=/usr",
            "--disable-nscd",
            "--enable-kernel=5.4"
        ]
    )

    def _config_args(self, ctx: BuildContext) -> list[str]:
        return [
            f"--host={ctx.target_machine.triple}"
        ]