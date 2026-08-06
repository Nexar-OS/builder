from build import BuildContext
from build.system import Autotools
from recipe import SysrootRecipe
from source import TarballSource

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
            f"--host={ctx.build_machine.triple}"
        ]