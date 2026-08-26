from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe, BuildMethod
from source import TarballSource

class HwdataRecipe(TargetRecipe):
    name = "hwdata"
    version = "0.410"

    build_method = BuildMethod.IN_SOURCE

    sources = [
        TarballSource(
            name="hwdata",
            url=f"https://github.com/vcrhonek/hwdata/archive/refs/tags/v{version}.tar.gz",
            md5hash="07f1de937ff5b830280f6157221164eb"
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