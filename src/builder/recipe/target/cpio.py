from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe, BuildMethod
from builder.source import TarballSource

class CpioRecipe(TargetRecipe):
    name = "cpio"
    version = "2.15"

    sources = [
        TarballSource(
            name="cpio",
            url=f"https://ftp.gnu.org/gnu/cpio/cpio-{version}.tar.gz",
            md5hash="64130013fa9900f6b7de36de53573985"
        )
    ]

    build_system = Autotools(
        config_args=[
            "--prefix=/usr",
            "CFLAGS=-std=gnu11"
        ]
    )

    def _config_args(self, ctx: BuildContext) -> list[str]:
        return [
            f"--build={ctx.build_machine.triple}",
            f"--host={ctx.target_machine.triple}"
        ]