from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe
from builder.source import TarballSource
from .libpipeline import LibpipelineRecipe
from .gdbm import GdbmRecipe

class ManDBRecipe(TargetRecipe):
    name = "mandb"
    version = "6.19.0"

    depends_on = [
        LibpipelineRecipe(),
        GdbmRecipe(),
    ]

    sources = [
        TarballSource(
            name="mandb",
            url=f"https://download.savannah.nongnu.org/releases/man-db/man-db-2.13.1.tar.xz",
            md5hash="b6335533cbeac3b24cd7be31fdee8c83"
        )
    ]

    build_system = Autotools(
        config_args=[
            "--prefix=/usr",
            "--with-db=gdbm",
            "--disable-setuid",
        ]
    )

    def _config_args(self, ctx: BuildContext) -> list[str]:
        return [
            f"--build={ctx.build_machine.triple}",
            f"--host={ctx.target_machine.triple}"
        ]