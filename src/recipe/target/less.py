from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe
from source import TarballSource

class LessRecipe(TargetRecipe):
    name = "less"
    version = "704"

    sources = [
        TarballSource(
            name="less",
            url=f"https://ftp.gnu.org/gnu/less/less-{version}.tar.gz",
            md5hash="c4c9eea5b1862783b078c67ca67c9185"
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