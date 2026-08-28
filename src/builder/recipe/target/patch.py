from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe
from builder.source import TarballSource

class PatchRecipe(TargetRecipe):
    name = "patch"
    version = "2.8"

    sources = [
        TarballSource(
            name="patch",
            url=f"https://ftp.gnu.org/gnu/patch/patch-{version}.tar.xz",
            md5hash="149327a021d41c8f88d034eab41c039f"
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