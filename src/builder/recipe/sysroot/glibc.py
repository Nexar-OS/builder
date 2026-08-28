from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import SysrootRecipe
from builder.source import TarballSource

class GlibCRecipe(SysrootRecipe):
    name = "glibc"
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
            "--enable-kernel=5.4",
            "libc_cv_slibdir=/usr/lib"
        ]
    )

    def _config_args(self, ctx: BuildContext) -> list[str]:
        return [
            f"--build={ctx.build_machine.triple}",
            f"--host={ctx.target_machine.triple}"
        ]