from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe, BuildMethod
from builder.source import TarballSource

class ScreenRecipe(TargetRecipe):
    name = "screen"
    version = "5.0.2"

    build_method = BuildMethod.IN_SOURCE

    sources = [
        TarballSource(
            name="screen",
            url=f"https://ftp.gnu.org/gnu/screen/screen-{version}.tar.gz",
            md5hash="76c4f967284c1879f0a1423d318471b3"
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