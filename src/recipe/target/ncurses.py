from pathlib import Path
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

    def post_install(self, ctx: BuildContext, dest_dir: Path | None) -> None:
        """
        Create compatibility symlinks for ncursesw.
        Some recipes might expect a specific version of the library to be present.
        """

        assert dest_dir

        # Create ncursesw directory for headers
        ncursesw = dest_dir / "usr/include/ncursesw"
        ncursesw.mkdir(exist_ok=True, parents=True)
        for header in [ "curses.h", "term.h", "ncurses.h", "termcap.h" ]:
            link = ncursesw / header
            
            if link.exists() or link.is_symlink():
                link.unlink()
            
            link.symlink_to(f"../{header}")
        
        # Create symlinks for wide-character libraries
        for lib in [ "libform", "libmenu", "libncurses", "libpanel", "libtinfo" ]:
            wlib = f"{lib}w.so"
            lib = f"{lib}.so"

            link = dest_dir / "usr/lib" / lib

            if link.exists() or link.is_symlink():
                link.unlink()
            
            link.symlink_to(wlib)