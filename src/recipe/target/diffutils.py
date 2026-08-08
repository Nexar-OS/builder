from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe
from source import TarballSource

class DiffutilsRecipe(TargetRecipe):
    name = "diffutils"
    version = "3.12"

    sources = [
        TarballSource(
            name="diffutils",
            url=f"https://ftp.gnu.org/gnu/diffutils/diffutils-{version}.tar.xz",
            md5hash="d1b18b20868fb561f77861cd90b05de4"
        )
    ]

    build_system = Autotools(
        config_args=[
            "--prefix=/usr",

            # Skip a check that tries to invoke the produced binary
            # This won't work if we're cross compiling to another architecture
            "gl_cv_func_strcasecmp_works=yes"
        ]
    )

    def _config_args(self, ctx: BuildContext) -> list[str]:
        return [
            f"--build={ctx.build_machine.triple}",
            f"--host={ctx.target_machine.triple}"
        ]