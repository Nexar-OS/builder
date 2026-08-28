from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe
from builder.source import TarballSource

class ProcpsRecipe(TargetRecipe):
    name = "procps"
    version = "4.0.6"

    sources = [
        TarballSource(
            name="procps",
            url=f"https://sourceforge.net/projects/procps-ng/files/Production/procps-ng-{version}.tar.xz/download",
            md5hash="20c23dc3dd1569a2bb1d1fa93de213ed"
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