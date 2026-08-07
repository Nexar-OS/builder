from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe
from source import TarballSource

class GZipRecipe(TargetRecipe):
    name = "gzip"
    version = "1.14"

    sources = [
        TarballSource(
            name="gzip",
            url=f"https://ftp.gnu.org/gnu/gzip/gzip-{version}.tar.xz",
            md5hash="4bf5a10f287501ee8e8ebe00ef62b2c2"
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