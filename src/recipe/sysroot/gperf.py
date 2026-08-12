from build.context import BuildContext
from build.system import Autotools
from recipe import SysrootRecipe
from source import TarballSource

class GperfRecipe(SysrootRecipe):
    name = "gperf"
    version = "3.3"

    sources = [
        TarballSource(
            name="gperf",
            url=f"https://ftp.gnu.org/gnu/gperf/gperf-{version}.tar.gz",
            md5hash="31753b021ea78a21f154bf9eecb8b079"
        )
    ]

    build_system = Autotools([
        "--prefix=/usr"
    ])

    def _config_args(self, ctx: BuildContext) -> list[str]:
        return [
            f"--host={ctx.target_machine.triple}",
            f"--build={ctx.build_machine.triple}"
        ]