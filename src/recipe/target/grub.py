from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe
from source import TarballSource

class GrubRecipe(TargetRecipe):
    name = "grub"
    version = "2.14"

    sources = [
        TarballSource(
            name="grub",
            url=f"https://ftp.gnu.org/gnu/grub/grub-{version}.tar.xz",
            md5hash="383f9effad01c235d2535357ff717543"
        )
    ]

    build_system = Autotools(
        config_args=[
            "--prefix=/usr"
        ],
        build_args=[
            'CFLAGS="$CFLAGS -Wno-error=discarded-qualifiers"'
        ]
    )

    def _config_args(self, ctx: BuildContext) -> list[str]:
        return [
            f"--build={ctx.build_machine.triple}",
            f"--host={ctx.target_machine.triple}"
        ]