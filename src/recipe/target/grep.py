from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe
from source import TarballSource

class GrepRecipe(TargetRecipe):
    name = "grep"
    version = "3.12"

    sources = [
        TarballSource(
            name="grep",
            url=f"https://ftp.gnu.org/gnu/grep/grep-{version}.tar.xz",
            md5hash="5d9301ed9d209c4a88c8d3a6fd08b9ac"
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