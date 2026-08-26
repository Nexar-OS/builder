from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe
from source import TarballSource

class DosfstoolsRecipe(TargetRecipe):
    name = "dosfstools"
    version = "4.2"

    sources = [
        TarballSource(
            name="dosfstools",
            url=f"https://github.com/dosfstools/dosfstools/releases/download/v{version}/dosfstools-{version}.tar.gz",
            md5hash="49c8e457327dc61efab5b115a27b087a"
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