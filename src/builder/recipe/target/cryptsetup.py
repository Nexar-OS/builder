from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe
from builder.source import TarballSource
from .json_c import JsonCRecipe

class CryptsetupRecipe(TargetRecipe):
    name = "cryptsetup"
    version = "2.3.2"

    depends_on = [
        JsonCRecipe,
    ]

    sources = [
        TarballSource(
            name="cryptsetup",
            url=f"https://www.kernel.org/pub/linux/utils/cryptsetup/v{'.'.join(version.split('.')[:-1])}/cryptsetup-{version}.tar.xz",
            md5hash="6e4ffb6d35a73f7539a5d0c1354654cd"
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