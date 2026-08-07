from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe
from source import TarballSource

class BashRecipe(TargetRecipe):
    name = "bash"
    version = "5.3"

    sources = [
        TarballSource(
            name="bash",
            url=f"https://ftp.gnu.org/gnu/bash/bash-{version}.tar.gz",
            md5hash="977c8c0c5ae6309191e7768e28ebc951"
        )
    ]

    build_system = Autotools(
        config_args=[
            "--prefix=/usr",
            "--with-bash-malloc"
        ]
    )

    def _config_args(self, ctx: BuildContext) -> list[str]:
        return [
            f"--build={ctx.build_machine.triple}",
            f"--host={ctx.target_machine.triple}"
        ]