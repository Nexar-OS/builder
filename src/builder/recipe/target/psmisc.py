from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe
from builder.source import TarballSource

class PsmiscRecipe(TargetRecipe):
    name = "psmisc"
    version = "23.7"

    sources = [
        TarballSource(
            name="psmisc",
            url=f"https://sourceforge.net/projects/psmisc/files/psmisc/psmisc-{version}.tar.xz/download",
            md5hash="53eae841735189a896d614cba440eb10"
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