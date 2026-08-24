from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe
from source import TarballSource

class PkgconfRecipe(TargetRecipe):
    name = "pkgconf"
    version = "3.12"

    sources = [
        TarballSource(
            name="pkgconf",
            url=f"https://github.com/pkgconf/pkgconf/releases/download/pkgconf-3.0.6/pkgconf-3.0.6.tar.gz",
            md5hash="e0df3475746e05614d2be0e2fafd5b68"
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