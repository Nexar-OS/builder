from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe, BuildMethod
from builder.source import TarballSource

class KmodRecipe(TargetRecipe):
    name = "kmod"
    version = "34.2"

    sources = [
        TarballSource(
            name="kmod",
            url=f"https://www.kernel.org/pub/linux/utils/kernel/kmod/kmod-{version}.tar.gz",
            md5hash="c34c4d5566bd69b1972879ff5498979a"
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