from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe, BuildMethod
from source import TarballSource

class RfkillRecipe(TargetRecipe):
    name = "rfkill"
    version = "1.0"

    build_method = BuildMethod.IN_SOURCE

    sources = [
        TarballSource(
            name="rfkill",
            url=f"https://mirrors.edge.kernel.org/pub/software/network/rfkill/rfkill-{version}.tar.xz",
            md5hash="914fb2858b655db67d82c50fb77eb8ab"
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