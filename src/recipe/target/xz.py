from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe
from source import TarballSource

class XZRecipe(TargetRecipe):
    name = "xz"
    version = "5.8.3"

    sources = [
        TarballSource(
            name="xz",
            url=f"https://github.com/tukaani-project/xz/releases/download/v{version}/xz-{version}.tar.gz",
            md5hash="6dcfcd102e25b31ae30467498b3eeeab"
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