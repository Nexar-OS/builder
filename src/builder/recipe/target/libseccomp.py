from builder.build.context import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe, BuildMethod
from builder.source import TarballSource
from builder.recipe.toolchain import GperfRecipe

class LibseccompRecipe(TargetRecipe):
    name = "libseccomp"
    version = "2.6.1"
    copy_to_toolchain = True

    depends_on = [
        GperfRecipe()
    ]

    sources = [
        TarballSource(
            name="libseccomp",
            url=f"https://github.com/seccomp/libseccomp/releases/download/v{version}/libseccomp-{version}.tar.gz",
            md5hash="33a3a5d4c526a739515ff4dc53cdc192"
        )
    ]

    build_system = Autotools(
        [
            "--prefix=/usr",
            "--disable-static"
        ]
    )

    def _config_args(self, ctx: BuildContext) -> list[str]:
        return [
            f"--host={ctx.target_machine.triple}",
            f"--build={ctx.build_machine.triple}"
        ]