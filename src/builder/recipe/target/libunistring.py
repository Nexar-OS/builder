from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe
from builder.source import TarballSource

class LibunistringRecipe(TargetRecipe):
    name = "libunistring"
    version = "1.4.2"

    copy_to_toolchain = True

    sources = [
        TarballSource(
            name="libunistring",
            url=f"https://ftp.gnu.org/gnu/libunistring/libunistring-{version}.tar.gz",
            md5hash="a1b88d4c0f3b0504d10cfe2a76a7bee7"
        )
    ]

    build_system = Autotools(
        config_args=[
            "--prefix=/usr",
            "--with-openssl"
        ]
    )

    def _config_args(self, ctx: BuildContext) -> list[str]:
        return [
            f"--build={ctx.build_machine.triple}",
            f"--host={ctx.target_machine.triple}"
        ]