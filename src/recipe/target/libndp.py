from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe
from source import TarballSource

class LibndpRecipe(TargetRecipe):
    name = "libndp"
    version = "1.9"

    copy_to_toolchain = True

    sources = [
        TarballSource(
            name="libndp",
            url=f"http://libndp.org/files/libndp-{version}.tar.gz",
            md5hash="9d486750569e7025e5d0afdcc509b93c"
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