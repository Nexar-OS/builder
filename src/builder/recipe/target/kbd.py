from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe
from builder.source import TarballSource

class KBDRecipe(TargetRecipe):
    name = "kbd"
    version = "2.9.0"

    sources = [
        TarballSource(
            name="kbd",
            url=f"https://www.kernel.org/pub/linux/utils/kbd/kbd-{version}.tar.xz",
            md5hash="7be7c6f658f5fb9512e2c490349a8eeb"
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