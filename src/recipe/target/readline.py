from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe
from source import TarballSource

class ReadlineRecipe(TargetRecipe):
    name = "readline"
    version = "8.3"

    copy_to_toolchain = True

    sources = [
        TarballSource(
            name="readline",
            url=f"https://ftp.gnu.org/gnu/readline/readline-{version}.tar.gz",
            md5hash="25a73bfb2a3ad7146c5e9d4408d9f6cd"
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