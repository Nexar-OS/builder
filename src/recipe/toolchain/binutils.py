from build import BuildContext
from build.system import Autotools
from recipe import ToolchainRecipe
from source import TarballSource

class BinutilsRecipe(ToolchainRecipe):
    name = "binutils"
    version = "2.47"

    sources = [
        TarballSource(
            name="binutils",
            url=f"https://ftp.gnu.org/gnu/binutils/binutils-{version}.tar.xz",
            md5hash="d772acfbd55a81644e9fe7b8189cd2a5"
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