from build.context import BuildContext
from ..recipe import ToolchainRecipe
from source import TarballSource
from build.system import Autotools

class BinutilsRecipe(ToolchainRecipe):
    name = "binutils"
    version = "2.47"

    sources = [
        TarballSource(
            name="binutils",
            url=f"https://ftp.gnu.org/gnu/binutils/binutils-2.47.tar.xz",
            md5hash=""
        )
    ]

    build_system = Autotools(
        config_args=[
            "--disable-gdb"
        ]
    )

    def _config_args(self, ctx: BuildContext) -> list[str]:
        return [
            f"--build={ctx.build_machine.triple}",
            f"--host={ctx.build_machine.triple}",
            f"--target={ctx.target_machine.triple}",
            f"--prefix={ctx.cross_toolchain_dir}",
            f"--with-sysroot={ctx.cross_toolchain_sysroot}"
        ]