from pathlib import Path
from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe
from builder.source import TarballSource

class LibexpatRecipe(TargetRecipe):
    name = "libexpat"
    version = "2.44"

    # Libgcc is built directly with gcc
    sources = [
        TarballSource(
            name="libexpat",
            url="https://github.com/libexpat/libexpat/releases/download/R_2_8_3/expat-2.8.3.tar.gz",
            md5hash="6ea4b2b8f50bafd1d6e2fd63024ab0d8"
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