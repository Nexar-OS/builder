from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe
from source import TarballSource

class SedRecipe(TargetRecipe):
    name = "sed"
    version = "3.12"

    sources = [
        TarballSource(
            name="sed",
            url=f"https://ftp.gnu.org/gnu/sed/sed-4.10.tar.xz",
            md5hash="c70dc5372db95c816442ffedf77a0d0f"
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