from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe, BuildMethod
from source import TarballSource
from .util_linux import UtilLinuxRecipe
from .lvm2 import Lvm2Recipe
from .readline import ReadlineRecipe

class PartedRecipe(TargetRecipe):
    name = "parted"
    version = "3.7"

    depends_on = [
        UtilLinuxRecipe(),
        Lvm2Recipe(),
        ReadlineRecipe(),
    ]

    sources = [
        TarballSource(
            name="parted",
            url=f"https://ftp.gnu.org/gnu/parted/parted-{version}.tar.xz",
            md5hash="b56ec0cf7bc89d61da1585f88fc8ef5e"
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