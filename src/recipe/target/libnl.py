from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe
from source import TarballSource

class LibnlRecipe(TargetRecipe):
    name = "libnl"
    version = "3.12.0"

    copy_to_toolchain = True

    sources = [
        TarballSource(
            name="libnl",
            url=f"https://github.com/thom311/libnl/releases/download/libnl{version.replace('.', '_')}/libnl-{version}.tar.gz",
            md5hash="f9112ca215807fe65eecd583d8f180cc"
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