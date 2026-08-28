from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe
from builder.source import TarballSource

class M4Recipe(TargetRecipe):
    name = "m4"
    version = "1.4.21"

    sources = [
        TarballSource(
            name="m4",
            url=f"https://ftp.gnu.org/gnu/m4/m4-{version}.tar.xz",
            md5hash="8051eef7239b2f187791f2ab0034d6b7"
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