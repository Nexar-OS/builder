from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe
from source import TarballSource

class WhichRecipe(TargetRecipe):
    name = "which"
    version = "2.25"

    sources = [
        TarballSource(
            name="which",
            url=f"https://ftp.gnu.org/gnu/which/which-{version}.tar.gz",
            md5hash="60140cb2637634e4f4e68c2e98c6a07b"
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