from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe, BuildMethod
from builder.source import TarballSource

class LibmnlRecipe(TargetRecipe):
    name = "libmnl"
    version = "1.0.5"

    copy_to_toolchain = True

    sources = [
        TarballSource(
            name="libmnl",
            url=f"https://www.netfilter.org/pub/libmnl/libmnl-{version}.tar.bz2",
            md5hash="0bbb70573119ec5d49435114583e7a49"
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