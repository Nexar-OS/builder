from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe
from source import TarballSource

class UtilLinuxRecipe(TargetRecipe):
    name = "util-linux"
    version = "2.42.1"

    sources = [
        TarballSource(
            name="util-linux",
            url=f"https://www.kernel.org/pub/linux/utils/util-linux/v{'.'.join(version.split('.')[:-1])}/util-linux-{version}.tar.xz",
            md5hash="575bf65577d9bd0e65aeb073e8f61343"
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