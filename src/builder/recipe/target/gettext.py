from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe
from builder.source import TarballSource

class GettextRecipe(TargetRecipe):
    name = "gettext"
    version = "1.0"

    sources = [
        TarballSource(
            name="gettext",
            url=f"https://ftp.gnu.org/gnu/gettext/gettext-{version}.tar.xz",
            md5hash="dc8b2911535929cec1e263706b0a13a1"
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