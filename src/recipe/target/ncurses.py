from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe
from source import TarballSource

class NcursesRecipe(TargetRecipe):
    name = "ncurses"
    version = "6.6"
    copy_to_toolchain = True

    sources = [
        TarballSource(
            name="ncurses",
            url=f"https://ftp.gnu.org/gnu/ncurses/ncurses-{version}.tar.gz",
            md5hash="dd45bf6854430af403452a7a6a40652c"
        )
    ]

    build_system = Autotools(
        config_args=[
            "--prefix=/usr",
            "--with-termlib",
            "--with-shared",
            "--enable-widec",
            "--enable-pc-files",
            "--with-pkg-config-libdir=/usr/lib/pkgconfig"
        ]
    )

    def _config_args(self, ctx: BuildContext) -> list[str]:
        return [
            f"--build={ctx.build_machine.triple}",
            f"--host={ctx.target_machine.triple}"
        ]