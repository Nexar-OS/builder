from pathlib import Path
from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe, BuildMethod
from builder.source import TarballSource
from builder.utils.file import merge_trees

class OpenSSHRecipe(TargetRecipe):
    name = "openssh"
    version = "9.9p2"

    sources = [
        TarballSource(
            name="openssh",
            url=f"https://cdn.openbsd.org/pub/OpenBSD/OpenSSH/portable/openssh-{version}.tar.gz",
            md5hash="f617b95fe278bfea8d004589c7a68a85"
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