from pathlib import Path
from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe
from builder.source import TarballSource
from builder.toolchain import NativeToolchain

class LibpslRecipe(TargetRecipe):
    name = "libpsl"
    version = "0.23.3"

    copy_to_toolchain = True

    sources = [
        TarballSource(
            name="libpsl",
            url=f"https://github.com/rockdaboot/libpsl/releases/download/{version}/libpsl-{version}.tar.gz",
            md5hash="596df43f3c2a8f1d4a677b032ccbc820"
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