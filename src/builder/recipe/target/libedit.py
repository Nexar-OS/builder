from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe
from builder.source import TarballSource

class LibeditRecipe(TargetRecipe):
    name = "libedit"
    version = "20260512-3.1"

    copy_to_toolchain = True

    sources = [
        TarballSource(
            name="libedit",
            url=f"https://thrysoee.dk/editline/libedit-{version}.tar.gz",
            md5hash="2067df0d3b79b0f731994ad830d41a6d"
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