from build import BuildContext
from build.system import Autotools
from recipe import ToolchainRecipe
from source import TarballSource

class GCCSecondPassRecipe(ToolchainRecipe):
    name = "gcc-second"
    version = "16.1.0"

    sources = [
        TarballSource(
            name="gcc",
            url=f"https://ftp.gnu.org/gnu/gcc/gcc-{version}/gcc-{version}.tar.xz",
            md5hash="9b016416f8e2dce4a0ef8759d1936446"
        )
    ]

    build_system = Autotools(
        config_args=[
            "--with-native-system-header-dir=/usr/include",
            "--disable-nls",
            "--disable-multilib",
            "--disable-libatomic",
            "--disable-libssp",
            "--enable-languages=c,c++"
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