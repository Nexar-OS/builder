from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe, BuildMethod
from source import TarballSource

class IpRoute2Recipe(TargetRecipe):
    name = "iproute2"
    version = "6.19.0"

    build_method = BuildMethod.IN_SOURCE

    sources = [
        TarballSource(
            name="iproute2",
            url=f"https://www.kernel.org/pub/linux/utils/net/iproute2/iproute2-{version}.tar.xz",
            md5hash="90590c3c593a33d7d8eca997c2c18d1c"
        )
    ]

    build_system = Autotools(
        config_args=[
            "--prefix=/usr/"
        ]
    )

    def _config_args(self, ctx: BuildContext) -> list[str]:
        return [
            f"--build={ctx.build_machine.triple}",
            f"--host={ctx.target_machine.triple}"
        ]