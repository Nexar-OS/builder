from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe, BuildMethod
from builder.source import TarballSource
from .bash import BashRecipe

class BashCompletionRecipe(TargetRecipe):
    name = "bash-completion"
    version = "2.18.0"

    depends_on = [
        BashRecipe,
    ]

    sources = [
        TarballSource(
            name="bash-completion",
            url=f"https://github.com/scop/bash-completion/releases/download/{version}/bash-completion-{version}.tar.xz",
            md5hash="aa401f77054a83bd45171a2d628dccb0"
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