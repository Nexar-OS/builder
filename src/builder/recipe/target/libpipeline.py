from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe
from builder.source import TarballSource

class LibpipelineRecipe(TargetRecipe):
    name = "libpipeline"
    version = "20260512-3.1"

    copy_to_toolchain = True

    sources = [
        TarballSource(
            name="libpipeline",
            url=f"https://download.savannah.nongnu.org/releases/libpipeline/libpipeline-1.5.8.tar.gz",
            md5hash="17ac6969b2015386bcb5d278a08a40b5"
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