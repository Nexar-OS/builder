from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe
from builder.source import TarballSource

class FindutilsRecipe(TargetRecipe):
    name = "findutils"
    version = "4.11.0"

    sources = [
        TarballSource(
            name="findutils",
            url=f"https://ftp.gnu.org/gnu/findutils/findutils-{version}.tar.xz",
            md5hash="512c6875ed84034dca240c4bc9380b96"
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