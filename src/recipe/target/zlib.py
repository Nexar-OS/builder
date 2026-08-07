from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe
from source import TarballSource

class ZlibRecipe(TargetRecipe):
    name = "zlib"
    version = "1.3.2"

    sources = [
        TarballSource(
            name="zlib",
            url=f"https://zlib.net/zlib-{version}.tar.gz",
            md5hash="a1e6c958597af3c67d162995a342138a"
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