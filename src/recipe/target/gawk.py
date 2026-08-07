from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe
from source import TarballSource

class GawkRecipe(TargetRecipe):
    name = "gawk"
    version = "5.4.1"

    sources = [
        TarballSource(
            name="gawk",
            url=f"https://ftp.gnu.org/gnu/gawk/gawk-{version}.tar.xz",
            md5hash="d379c2110e7a3e15347dd5559a41ad64"
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