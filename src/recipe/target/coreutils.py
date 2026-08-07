from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe
from source import TarballSource

class CoreutilsRecipe(TargetRecipe):
    name = "coreutils"
    version = "9.11"

    sources = [
        TarballSource(
            name="coreutils",
            url=f"https://ftp.gnu.org/gnu/coreutils/coreutils-{version}.tar.gz",
            md5hash="b49641aa883b5a05cd6156d3cba82853"
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