from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe
from builder.source import TarballSource

class E2fsProgsRecipe(TargetRecipe):
    name = "e2fsprogs"
    version = "1.47.4"

    sources = [
        TarballSource(
            name="e2fsprogs",
            url=f"https://mirrors.edge.kernel.org/pub/linux/kernel/people/tytso/e2fsprogs/v{version}/e2fsprogs-{version}.tar.gz",
            md5hash="2c41cfdd6097c7731b35e88c59140c69"
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