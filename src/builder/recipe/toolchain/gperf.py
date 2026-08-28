from builder.build.context import BuildContext
from builder.build.system import Autotools
from builder.recipe import ToolchainRecipe
from builder.source import TarballSource

class GperfRecipe(ToolchainRecipe):
    name = "gperf"
    version = "3.3"

    sources = [
        TarballSource(
            name="gperf",
            url=f"https://ftp.gnu.org/gnu/gperf/gperf-{version}.tar.gz",
            md5hash="31753b021ea78a21f154bf9eecb8b079"
        )
    ]

    build_system = Autotools()

    def _config_args(self, ctx: BuildContext) -> list[str]:
        return [
            f"--build={ctx.build_machine.triple}",
            f"--host={ctx.build_machine.triple}",
            f"--target={ctx.target_machine.triple}",
            f"--prefix={ctx.cross_toolchain_dir}",
            f"--with-sysroot={ctx.cross_toolchain_sysroot}"
        ]