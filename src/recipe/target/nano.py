from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe
from source import TarballSource

class NanoRecipe(TargetRecipe):
    name = "nano"
    version = "9.2"

    sources = [
        TarballSource(
            name="nano",
            url=f"https://www.nano-editor.org/dist/v{version.split('.')[0]}/nano-{version}.tar.xz",
            md5hash="9bb0f37945afa964d16bffd9e4da3106"
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