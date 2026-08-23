from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe
from source import TarballSource

class StraceRecipe(TargetRecipe):
    name = "strace"
    version = "7.2"

    sources = [
        TarballSource(
            name="strace",
            url=f"https://strace.io/files/{version}/strace-{version}.tar.xz",
            md5hash="a91403939a36a75e9be4a95f5b8ffb8b"
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