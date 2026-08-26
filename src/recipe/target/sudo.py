from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe, BuildMethod
from source import TarballSource

class SudoRecipe(TargetRecipe):
    name = "sudo"
    version = "1.9.17p2"

    sources = [
        TarballSource(
            name="sudo",
            url=f"https://www.sudo.ws/dist/sudo-{version}.tar.gz",
            md5hash="dcbf46f739ae06b076e1a11cbb271a10"
        )
    ]

    build_system = Autotools(
        config_args=[
            "--prefix=/usr",
            "--with-pam"
        ]
    )

    def _config_args(self, ctx: BuildContext) -> list[str]:
        return [
            f"--build={ctx.build_machine.triple}",
            f"--host={ctx.target_machine.triple}"
        ]