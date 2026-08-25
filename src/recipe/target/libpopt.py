from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe
from source import TarballSource

class LibpoptRecipe(TargetRecipe):
    name = "libpopt"
    version = "1.19"

    copy_to_toolchain = True

    sources = [
        TarballSource(
            name="libpopt",
            url=f"https://ftp.osuosl.org/pub/rpm/popt/releases/popt-{version.split('.')[0]}.x/popt-{version}.tar.gz",
            md5hash="eaa2135fddb6eb03f2c87ee1823e5a78"
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