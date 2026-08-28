from pathlib import Path
from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe, BuildMethod
from builder.source import TarballSource

class GMPRecipe(TargetRecipe):
    name = "gmp"
    version = "6.3.0"

    copy_to_toolchain = True
    build_method = BuildMethod.IN_SOURCE

    sources = [
        TarballSource(
            name="gmp",
            url=f"https://ftp.gnu.org/gnu/gmp/gmp-{version}.tar.xz",
            md5hash="956dc04e864001a9c22429f761f2c283"
        )
    ]

    build_system = Autotools(
        config_args=[
            "--prefix=/usr",
            "CFLAGS=-std=c17"
        ],
        disable_fakeroot=True
    )

    def _config_args(self, ctx: BuildContext) -> list[str]:
        return [
            f"--build={ctx.build_machine.triple}",
            f"--host={ctx.target_machine.triple}"
        ]