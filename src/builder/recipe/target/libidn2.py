from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe
from builder.source import TarballSource

class Libidn2Recipe(TargetRecipe):
    name = "libidn2"
    version = "2.3.8"

    copy_to_toolchain = True

    sources = [
        TarballSource(
            name="libidn2",
            url=f"https://ftp.gnu.org/gnu/libidn/libidn2-{version}.tar.gz",
            md5hash="a8e113e040d57a523684e141970eea7a"
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