from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe
from source import TarballSource

class TarRecipe(TargetRecipe):
    name = "tar"
    version = "1.35"

    sources = [
        TarballSource(
            name="tar",
            url=f"https://ftp.gnu.org/gnu/tar/tar-{version}.tar.xz",
            md5hash="a2d8042658cfd8ea939e6d911eaf4152"
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