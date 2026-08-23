from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe, BuildMethod
from source import TarballSource

class ShadowRecipe(TargetRecipe):
    name = "shadow"
    version = "4.20.2"

    sources = [
        TarballSource(
            name="shadow",
            url=f"https://github.com/shadow-maint/shadow/releases/download/{version}/shadow-{version}.tar.gz",
            md5hash="ad1e45eaa06bf2c61e406eaa0c771a8b"
        )
    ]

    build_system = Autotools(
        config_args=[
            "--prefix=/usr",
            "--without-libbsd"
        ]
    )

    def _config_args(self, ctx: BuildContext) -> list[str]:
        return [
            f"--build={ctx.build_machine.triple}",
            f"--host={ctx.target_machine.triple}"
        ]