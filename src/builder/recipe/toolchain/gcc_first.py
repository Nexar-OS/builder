from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import ToolchainRecipe
from builder.source import TarballSource

class GCCFirstPassRecipe(ToolchainRecipe):
    name = "gcc-first"
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
            "--with-glibc-version=2.43",
            "--with-newlib",
            "--without-headers",
            "--enable-default-pie",
            "--enable-default-ssp",
            "--disable-nls",
            "--disable-shared",
            "--disable-multilib",
            "--disable-threads",
            "--disable-libatomic",
            "--disable-libgomp",
            "--disable-libquadmath",
            "--disable-libssp",
            "--disable-libvtv",
            "--enable-languages=c"
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